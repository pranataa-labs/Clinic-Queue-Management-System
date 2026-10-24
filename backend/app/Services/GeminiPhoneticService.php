<?php

namespace App\Services;

use App\Models\Counter;
use App\Models\Poliklinik;
use App\Models\Queue;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class GeminiPhoneticService
{
    protected ?string $apiKey;
    protected string $model = 'gemini-2.5-flash';

    public function __construct()
    {
        $this->apiKey = config('services.gemini.api_key', env('GEMINI_API_KEY'));
    }

    /**
     * Generate speech script using Gemini 2.5 Flash Structured Output,
     * or fallback seamlessly to deterministic Indonesian phonetic builder.
     */
    public function generateAnnouncementScript(Queue $queue, Counter $counter, Poliklinik $poliklinik): array
    {
        if (empty($this->apiKey)) {
            return $this->getDeterministicFallback($queue, $counter, $poliklinik, 'Standard Template (API Key Not Set)');
        }

        try {
            $prompt = $this->buildPrompt($queue, $counter, $poliklinik);

            $response = Http::timeout(4.0)->post(
                "https://generativelanguage.googleapis.com/v1beta/models/{$this->model}:generateContent?key={$this->apiKey}",
                [
                    'contents' => [
                        [
                            'parts' => [
                                ['text' => $prompt]
                            ]
                        ]
                    ],
                    'generationConfig' => [
                        'responseMimeType' => 'application/json',
                        'responseSchema' => [
                            'type' => 'OBJECT',
                            'properties' => [
                                'call_script' => [
                                    'type' => 'STRING',
                                    'description' => 'Naskah audio lengkap yang siap diucapkan Web Speech API secara natural dan sopan dalam Bahasa Indonesia'
                                ],
                                'phonetic_spelling' => [
                                    'type' => 'STRING',
                                    'description' => 'Ejaan nomor antrean dengan jeda koma, contoh: A, kosong, dua, empat'
                                ],
                                'chime_tone' => [
                                    'type' => 'STRING',
                                    'enum' => ['standard_bell', 'urgent_chime']
                                ],
                                'display_headline' => [
                                    'type' => 'STRING',
                                    'description' => 'Judul ringkas untuk TV display'
                                ],
                                'repeat_count' => [
                                    'type' => 'INTEGER',
                                    'description' => 'Jumlah perulangan panggilan (default 1 atau 2)'
                                ],
                                'additional_notes' => [
                                    'type' => 'STRING',
                                    'description' => 'Catatan arahan untuk pasien atau keluarga'
                                ]
                            ],
                            'required' => ['call_script', 'phonetic_spelling', 'chime_tone', 'display_headline', 'repeat_count']
                        ]
                    ]
                ]
            );

            if ($response->successful()) {
                $data = $response->json();
                $rawJson = $data['candidates'][0]['content']['parts'][0]['text'] ?? null;
                if ($rawJson) {
                    $structured = json_decode($rawJson, true);
                    if (is_array($structured) && !empty($structured['call_script'])) {
                        $structured['generator_type'] = 'gemini-2.5-flash';
                        return $structured;
                    }
                }
            }

            Log::warning('Gemini API returned unsuccessful status or empty response: ' . $response->body());
        } catch (\Throwable $e) {
            Log::error('Gemini 2.5 Flash announcement generation failed: ' . $e->getMessage());
        }

        return $this->getDeterministicFallback($queue, $counter, $poliklinik, 'Fallback Rule Engine');
    }

    /**
     * Deterministic, zero-latency Indonesian announcement builder.
     */
    public function getDeterministicFallback(Queue $queue, Counter $counter, Poliklinik $poliklinik, string $source = 'Local Template'): array
    {
        $codeParts = explode('-', $queue->nomor_antrean);
        $prefix = $codeParts[0] ?? 'A';
        $numberPart = $codeParts[1] ?? (string)$queue->nomor_urut;

        // Convert number characters to spaced spoken Indonesian
        $phoneticDigits = [];
        $digitMap = [
            '0' => 'kosong',
            '1' => 'satu',
            '2' => 'dua',
            '3' => 'tiga',
            '4' => 'empat',
            '5' => 'lima',
            '6' => 'enam',
            '7' => 'tujuh',
            '8' => 'delapan',
            '9' => 'sembilan',
        ];

        foreach (str_split($numberPart) as $char) {
            $phoneticDigits[] = $digitMap[$char] ?? $char;
        }

        $phoneticNumber = strtoupper($prefix) . ', ' . implode(', ', $phoneticDigits);
        $poliName = $poliklinik->nama_fonetik ?: $poliklinik->nama;
        $counterName = $counter->nomor_bilik;
        $doctorName = $counter->nama_petugas ? 'bersama ' . $counter->nama_petugas : '';

        $script = "Nomor antrean, {$phoneticNumber}. Silakan menuju ke {$poliName}, {$counterName}";
        if ($doctorName) {
            $script .= ", {$doctorName}";
        }
        $script .= ". Terima kasih.";

        return [
            'call_script' => $script,
            'phonetic_spelling' => $phoneticNumber,
            'chime_tone' => ($queue->jenis_pasien === 'prioritas') ? 'urgent_chime' : 'standard_bell',
            'display_headline' => "{$poliklinik->nama} ({$counter->nomor_bilik})",
            'repeat_count' => ($queue->call_count > 1) ? 1 : 2,
            'additional_notes' => $queue->catatan_khusus ?: 'Harap siapkan kartu identitas atau BPJS Anda.',
            'generator_type' => $source,
        ];
    }

    protected function buildPrompt(Queue $queue, Counter $counter, Poliklinik $poliklinik): string
    {
        return <<<PROMPT
Anda adalah sistem pemanggil antrean otomatis (Audio Announcement Engine) rumah sakit / poliklinik terpercaya.
Buat skrip pengumuman audio suara yang sangat ramah, sopan, natural, dan mudah dilafalkan oleh Web Speech Synthesis API Bahasa Indonesia (id-ID).

Informasi Antrean:
- Nomor Antrean: {$queue->nomor_antrean}
- Poliklinik: {$poliklinik->nama} (Fonetik: {$poliklinik->nama_fonetik})
- Ruangan: {$counter->nomor_bilik}
- Dokter / Petugas: {$counter->nama_petugas} ({$counter->gelar_petugas})
- Kategori Pasien: {$queue->jenis_pasien}
- Panggilan ke-: {$queue->call_count}
- Catatan Khusus: {$queue->catatan_khusus}

Pedoman Khusus:
1. 'call_script' harus menggunakan intonasi kalimat sopan. Sisipkan tanda koma (,) untuk jeda hembusan napas alami pada TTS.
2. Eja nomor antrean secara jelas (contoh: 'A, kosong, satu, dua' bukan 'A strip 12').
3. Sesuaikan dengan status prioritas jika ada catatan khusus (misal lansia atau ibu hamil).
4. Hindari singkatan medis yang membingungkan pendengar awam.
PROMPT;
    }
}
