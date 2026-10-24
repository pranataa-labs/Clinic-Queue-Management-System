<?php

namespace Database\Seeders;

use App\Models\Poliklinik;
use App\Services\QueueCallingService;
use Illuminate\Database\Seeder;

class PatientBatchSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(QueueCallingService $callingService): void
    {
        $batchPatients = [
            // 1. Poli Umum & Dewasa
            1 => [
                [
                    'nama_pasien' => 'Bambang Haryanto',
                    'jenis_pasien' => 'bpjs',
                    'catatan' => 'Keluhan demam dan flu sejak 3 hari yang lalu',
                ],
                [
                    'nama_pasien' => 'Hj. Aminah (Lansia)',
                    'jenis_pasien' => 'prioritas',
                    'catatan' => 'Pasien lansia 74 tahun, kontrol rutin hipertensi & diabetes',
                ],
                [
                    'nama_pasien' => 'Dimas Prasetyo Nugraha',
                    'jenis_pasien' => 'umum',
                    'catatan' => 'Pemeriksaan kesehatan surat keterangan sehat (MCU)',
                ],
                [
                    'nama_pasien' => 'Retno Wulandari',
                    'jenis_pasien' => 'bpjs',
                    'catatan' => 'Keluhan migrain dan pusing berputar',
                ],
            ],

            // 2. Poli Spesialis Anak
            2 => [
                [
                    'nama_pasien' => 'Ananda Kenzo Alvaro (Balita)',
                    'jenis_pasien' => 'prioritas',
                    'catatan' => 'Jadwal imunisasi DPT lanjutan dan konsultasi gizi',
                ],
                [
                    'nama_pasien' => 'Clarissa Putri Maheswari',
                    'jenis_pasien' => 'bpjs',
                    'catatan' => 'Batuk berdahak dan nafsu makan menurun',
                ],
                [
                    'nama_pasien' => 'Raffasya Al-Ghifari (Bayi 8 Bulan)',
                    'jenis_pasien' => 'prioritas',
                    'catatan' => 'Pemeriksaan tumbuh kembang dan ruam alergi susu',
                ],
                [
                    'nama_pasien' => 'Zahra Amelia',
                    'jenis_pasien' => 'umum',
                    'catatan' => 'Demam berulang dan radang tenggorokan',
                ],
            ],

            // 3. Poli Gigi & Mulut
            3 => [
                [
                    'nama_pasien' => 'Hendro Wicaksono',
                    'jenis_pasien' => 'umum',
                    'catatan' => 'Pembersihan karang gigi berkala (Scaling)',
                ],
                [
                    'nama_pasien' => 'Siti Nurhaliza',
                    'jenis_pasien' => 'bpjs',
                    'catatan' => 'Penambalan gigi geraham bawah berlubang',
                ],
                [
                    'nama_pasien' => 'Raden Mochammad Surya',
                    'jenis_pasien' => 'umum',
                    'catatan' => 'Pencabutan sisa akar gigi bungsu',
                ],
                [
                    'nama_pasien' => 'Ibu Maryam (Lansia)',
                    'jenis_pasien' => 'prioritas',
                    'catatan' => 'Pemasangan & penyesuaian gigi tiruan lepasan',
                ],
            ],

            // 4. Poli Kebidanan & Kandungan
            4 => [
                [
                    'nama_pasien' => 'Ny. Shinta Dewi (Bumil Trimester 3)',
                    'jenis_pasien' => 'prioritas',
                    'catatan' => 'USG 4D dan evaluasi posisi janin menjelang persalinan',
                ],
                [
                    'nama_pasien' => 'Ny. Anisa Fitriani',
                    'jenis_pasien' => 'bpjs',
                    'catatan' => 'Pemeriksaan rutin trimester 1 dan mual muntah',
                ],
                [
                    'nama_pasien' => 'Ny. Rina Marlina',
                    'jenis_pasien' => 'umum',
                    'catatan' => 'Konsultasi program kehamilan (Promil)',
                ],
                [
                    'nama_pasien' => 'Ny. Fitri Handayani',
                    'jenis_pasien' => 'bpjs',
                    'catatan' => 'Kontrol pasca operasi sesar (SC) minggu ke-2',
                ],
            ],

            // 5. Poli Spesialis Mata
            5 => [
                [
                    'nama_pasien' => 'Bapak H. Soetrisno (Lansia)',
                    'jenis_pasien' => 'prioritas',
                    'catatan' => 'Pemeriksaan katarak senilis dan tajam penglihatan',
                ],
                [
                    'nama_pasien' => 'Annisa Rahmadani',
                    'jenis_pasien' => 'umum',
                    'catatan' => 'Uji refraksi kacamata dan mata lelah silinder',
                ],
                [
                    'nama_pasien' => 'Wahyu Kurniawan',
                    'jenis_pasien' => 'bpjs',
                    'catatan' => 'Iritasi mata merah dan infeksi konjungtivitis',
                ],
                [
                    'nama_pasien' => 'Drs. Subagyo (Lansia)',
                    'jenis_pasien' => 'prioritas',
                    'catatan' => 'Pemeriksaan tekanan bola mata (Tonometri / Glaukoma)',
                ],
            ],
        ];

        $polis = Poliklinik::all()->keyBy('id');

        foreach ($batchPatients as $poliId => $patients) {
            $poli = $polis->get($poliId);
            if (!$poli) {
                continue;
            }

            foreach ($patients as $item) {
                $callingService->registerTicket(
                    $poli->id,
                    $item['nama_pasien'],
                    $item['jenis_pasien'],
                    $item['catatan']
                );
            }
        }
    }
}
