<?php

namespace Database\Seeders;

use App\Models\Counter;
use App\Models\Poliklinik;
use App\Models\Queue;
use App\Models\QueueSetting;
use Illuminate\Database\Seeder;

class ClinicQueueSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // 1. Settings
        QueueSetting::updateOrCreate(
            ['key' => 'clinic_name'],
            ['value' => 'Poliklinik Terpadu Husada Medika', 'deskripsi' => 'Nama faskes / rumah sakit']
        );
        QueueSetting::updateOrCreate(
            ['key' => 'running_text'],
            ['value' => 'Selamat datang di Poliklinik Terpadu Husada Medika. Harap memperhatikan nomor antrean dan menyiapkan berkas BPJS / identitas Anda. Budayakan antre dengan tertib demi kenyamanan bersama.', 'deskripsi' => 'Teks berjalan pada layar display TV']
        );
        QueueSetting::updateOrCreate(
            ['key' => 'audio_chime'],
            ['value' => 'bell', 'deskripsi' => 'Tipe nada pembuka panggilan (bell/dingdong)']
        );

        // 2. Clinics & Counters
        $clinicsData = [
            [
                'kode' => 'A-UMUM',
                'nama' => 'Poli Umum & Dewasa',
                'nama_fonetik' => 'Poliklinik Umum dan Dewasa',
                'gedung_lantai' => 'Lantai 1 - Sayap Barat',
                'counters' => [
                    [
                        'nomor_bilik' => 'Ruangan 1',
                        'nama_petugas' => 'dr. Hendra Pratama',
                        'gelar_petugas' => 'Dokter Umum',
                    ],
                    [
                        'nomor_bilik' => 'Ruangan 2',
                        'nama_petugas' => 'dr. Siti Rahmawati',
                        'gelar_petugas' => 'Dokter Umum',
                    ],
                ],
                'patients' => [
                    ['nama' => 'Bambang Supriyanto', 'jenis' => 'bpjs', 'catatan' => null],
                    ['nama' => 'Sri Wahyuni (Lansia)', 'jenis' => 'prioritas', 'catatan' => 'Pasien Lansia 72 Tahun, butuh kursi roda'],
                    ['nama' => 'Rian Hidayat', 'jenis' => 'umum', 'catatan' => null],
                    ['nama' => 'Dewi Lestari', 'jenis' => 'bpjs', 'catatan' => null],
                    ['nama' => 'Agus Santoso', 'jenis' => 'umum', 'catatan' => null],
                ],
            ],
            [
                'kode' => 'B-ANAK',
                'nama' => 'Poli Spesialis Anak',
                'nama_fonetik' => 'Poliklinik Spesialis Anak',
                'gedung_lantai' => 'Lantai 1 - Sayap Timur',
                'counters' => [
                    [
                        'nomor_bilik' => 'Ruangan 2',
                        'nama_petugas' => 'dr. Farida Zahra',
                        'gelar_petugas' => 'Spesialis Anak (Sp.A)',
                    ],
                ],
                'patients' => [
                    ['nama' => 'Ananda Al Fatih (Balita)', 'jenis' => 'prioritas', 'catatan' => 'Imunisasi campak dan polio'],
                    ['nama' => 'Keisha Aurelia', 'jenis' => 'umum', 'catatan' => 'Batuk pilek demam 3 hari'],
                    ['nama' => 'Muhammad Rayyan', 'jenis' => 'bpjs', 'catatan' => null],
                ],
            ],
            [
                'kode' => 'C-GIGI',
                'nama' => 'Poli Gigi & Mulut',
                'nama_fonetik' => 'Poliklinik Gigi dan Mulut',
                'gedung_lantai' => 'Lantai 2 - Ruang 204',
                'counters' => [
                    [
                        'nomor_bilik' => 'Ruangan 3',
                        'nama_petugas' => 'drg. Budi Hartono',
                        'gelar_petugas' => 'Dokter Gigi Spesialis Konservasi Gigi',
                    ],
                ],
                'patients' => [
                    ['nama' => 'Eko Prasetyo', 'jenis' => 'umum', 'catatan' => 'Pembersihan karang gigi / Scaling'],
                    ['nama' => 'Nurul Hidayati', 'jenis' => 'bpjs', 'catatan' => 'Penambalan gigi geraham'],
                    ['nama' => 'Fajar Nugroho', 'jenis' => 'umum', 'catatan' => null],
                ],
            ],
            [
                'kode' => 'D-OBGYN',
                'nama' => 'Poli Kebidanan & Kandungan',
                'nama_fonetik' => 'Poliklinik Kebidanan dan Kandungan',
                'gedung_lantai' => 'Lantai 2 - Ruang 208',
                'counters' => [
                    [
                        'nomor_bilik' => 'Ruangan 4',
                        'nama_petugas' => 'dr. Ratna Kusumastuti',
                        'gelar_petugas' => 'Spesialis Obstetri dan Ginekologi (Sp.OG)',
                    ],
                ],
                'patients' => [
                    ['nama' => 'Ny. Maya Indah (Bumil Trimester 3)', 'jenis' => 'prioritas', 'catatan' => 'USG 4 Dimensi dan kontrol rutin kehamilan'],
                    ['nama' => 'Ny. Kartika Sari', 'jenis' => 'bpjs', 'catatan' => 'Pemeriksaan pasca persalinan'],
                ],
            ],
            [
                'kode' => 'E-MATA',
                'nama' => 'Poli Spesialis Mata',
                'nama_fonetik' => 'Poliklinik Spesialis Mata',
                'gedung_lantai' => 'Lantai 2 - Ruang 212',
                'counters' => [
                    [
                        'nomor_bilik' => 'Ruangan 5',
                        'nama_petugas' => 'dr. Taufik Ismail',
                        'gelar_petugas' => 'Spesialis Mata (Sp.M)',
                    ],
                ],
                'patients' => [
                    ['nama' => 'H. Mulyono', 'jenis' => 'prioritas', 'catatan' => 'Skrining katarak'],
                    ['nama' => 'Dinda Puspita', 'jenis' => 'umum', 'catatan' => 'Pemeriksaan visus kacamata'],
                ],
            ],
        ];

        foreach ($clinicsData as $cIdx => $clinicItem) {
            $poli = Poliklinik::create([
                'kode' => $clinicItem['kode'],
                'nama' => $clinicItem['nama'],
                'nama_fonetik' => $clinicItem['nama_fonetik'],
                'gedung_lantai' => $clinicItem['gedung_lantai'],
                'status' => 'active',
            ]);

            $createdCounters = [];
            foreach ($clinicItem['counters'] as $counterItem) {
                $createdCounters[] = Counter::create([
                    'poliklinik_id' => $poli->id,
                    'nomor_bilik' => $counterItem['nomor_bilik'],
                    'nama_petugas' => $counterItem['nama_petugas'],
                    'gelar_petugas' => $counterItem['gelar_petugas'],
                    'status' => 'active',
                ]);
            }

            // Seed patients
            $prefixLetter = substr($clinicItem['kode'], 0, 1);
            foreach ($clinicItem['patients'] as $pIdx => $pat) {
                $nomorUrut = $pIdx + 1;
                $formattedCode = sprintf('%s-%03d', $prefixLetter, $nomorUrut);

                Queue::create([
                    'poliklinik_id' => $poli->id,
                    'counter_id' => ($pIdx === 0 && !empty($createdCounters)) ? $createdCounters[0]->id : null,
                    'nomor_antrean' => $formattedCode,
                    'nomor_urut' => $nomorUrut,
                    'nama_pasien' => $pat['nama'],
                    'jenis_pasien' => $pat['jenis'],
                    'status' => 'waiting',
                    'call_count' => 0,
                    'catatan_khusus' => $pat['catatan'],
                    'waktu_daftar' => now()->subMinutes(30 - ($pIdx * 5)),
                ]);
            }
        }
    }
}
