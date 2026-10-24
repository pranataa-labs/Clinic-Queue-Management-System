<?php

namespace App\Services;

use App\Models\Counter;
use App\Models\Poliklinik;
use App\Models\Queue;
use App\Models\QueueCallLog;
use Illuminate\Support\Facades\DB;
use InvalidArgumentException;

class QueueCallingService
{
    public function __construct(
        protected GeminiPhoneticService $geminiService
    ) {}

    /**
     * Call the next waiting patient in the queue for a given counter.
     */
    public function callNext(int $counterId): array
    {
        return DB::transaction(function () use ($counterId) {
            $counter = Counter::with('poliklinik')->lockForUpdate()->findOrFail($counterId);

            // Fetch the earliest waiting ticket for this clinic
            $nextQueue = Queue::where('poliklinik_id', $counter->poliklinik_id)
                ->where('status', 'waiting')
                ->orderBy('nomor_urut', 'asc')
                ->lockForUpdate()
                ->first();

            if (!$nextQueue) {
                return [
                    'success' => false,
                    'message' => 'Tidak ada antrean yang menunggu untuk poliklinik ini.',
                    'data' => null,
                ];
            }

            // Update queue status
            $nextQueue->status = 'calling';
            $nextQueue->counter_id = $counter->id;
            $nextQueue->call_count = ($nextQueue->call_count ?? 0) + 1;
            $nextQueue->waktu_dipanggil = now();
            $nextQueue->save();

            // Generate structured phonetic announcement
            $announcement = $this->geminiService->generateAnnouncementScript($nextQueue, $counter, $counter->poliklinik);

            // Save to call log
            QueueCallLog::create([
                'queue_id' => $nextQueue->id,
                'counter_id' => $counter->id,
                'teks_panggilan' => $announcement['call_script'],
                'tipe_panggilan' => ($announcement['generator_type'] === 'gemini-2.5-flash') ? 'gemini_phonetic' : 'auto_tts',
                'gemini_metadata' => $announcement,
            ]);

            return [
                'success' => true,
                'message' => 'Berhasil memanggil nomor antrean berikutnya.',
                'data' => [
                    'queue' => $nextQueue->fresh(['poliklinik', 'counter']),
                    'announcement' => $announcement,
                    'counter' => $counter,
                ],
            ];
        });
    }

    /**
     * Recall a specific queue ticket.
     */
    public function recall(int $queueId, int $counterId): array
    {
        return DB::transaction(function () use ($queueId, $counterId) {
            $queue = Queue::with('poliklinik')->lockForUpdate()->findOrFail($queueId);
            $counter = Counter::with('poliklinik')->findOrFail($counterId);

            $queue->status = 'calling';
            $queue->counter_id = $counter->id;
            $queue->call_count += 1;
            $queue->waktu_dipanggil = now();
            $queue->save();

            $announcement = $this->geminiService->generateAnnouncementScript($queue, $counter, $queue->poliklinik);

            QueueCallLog::create([
                'queue_id' => $queue->id,
                'counter_id' => $counter->id,
                'teks_panggilan' => $announcement['call_script'],
                'tipe_panggilan' => ($announcement['generator_type'] === 'gemini-2.5-flash') ? 'gemini_phonetic' : 'auto_tts',
                'gemini_metadata' => $announcement,
            ]);

            return [
                'success' => true,
                'message' => 'Panggilan ulang antrean berhasil.',
                'data' => [
                    'queue' => $queue->fresh(['poliklinik', 'counter']),
                    'announcement' => $announcement,
                    'counter' => $counter,
                ],
            ];
        });
    }

    /**
     * Mark queue as in consultation (doctor is examining the patient).
     */
    public function startConsultation(int $queueId): Queue
    {
        $queue = Queue::findOrFail($queueId);
        $queue->status = 'in_consultation';
        $queue->save();
        return $queue;
    }

    /**
     * Mark queue as skipped (patient did not show up).
     */
    public function skip(int $queueId): Queue
    {
        $queue = Queue::findOrFail($queueId);
        $queue->status = 'skipped';
        $queue->save();
        return $queue;
    }

    /**
     * Complete consultation for the queue.
     */
    public function complete(int $queueId): Queue
    {
        $queue = Queue::findOrFail($queueId);
        $queue->status = 'completed';
        $queue->waktu_selesai = now();
        $queue->save();
        return $queue;
    }

    /**
     * Register a new queue ticket (kiosk registration).
     */
    public function registerTicket(int $poliklinikId, string $namaPasien, string $jenisPasien = 'umum', ?string $catatan = null): Queue
    {
        return DB::transaction(function () use ($poliklinikId, $namaPasien, $jenisPasien, $catatan) {
            $poli = Poliklinik::lockForUpdate()->findOrFail($poliklinikId);

            // Determine next sequence number for today
            $today = now()->startOfDay();
            $lastQueue = Queue::where('poliklinik_id', $poli->id)
                ->where('waktu_daftar', '>=', $today)
                ->orderBy('nomor_urut', 'desc')
                ->lockForUpdate()
                ->first();

            $nextNumber = ($lastQueue ? $lastQueue->nomor_urut : 0) + 1;
            $prefix = strtoupper(substr($poli->kode, 0, 1));
            if (empty($prefix)) {
                $prefix = 'A';
            }
            $formattedCode = sprintf('%s-%03d', $prefix, $nextNumber);

            return Queue::create([
                'poliklinik_id' => $poli->id,
                'nomor_antrean' => $formattedCode,
                'nomor_urut' => $nextNumber,
                'nama_pasien' => $namaPasien,
                'jenis_pasien' => $jenisPasien,
                'status' => 'waiting',
                'call_count' => 0,
                'catatan_khusus' => $catatan,
                'waktu_daftar' => now(),
            ]);
        });
    }

    /**
     * Get aggregated state for TV Display.
     */
    public function getDisplayState(): array
    {
        // 1. Most recently called active ticket
        $activeCallLog = QueueCallLog::with(['queue.poliklinik', 'counter'])
            ->orderBy('id', 'desc')
            ->first();

        // 2. Poliklinik list with currently called and waiting counts
        $polikliniks = Poliklinik::with(['counters'])->where('status', 'active')->get()->map(function ($poli) {
            $currentCalling = Queue::where('poliklinik_id', $poli->id)
                ->whereIn('status', ['calling', 'in_consultation'])
                ->orderBy('waktu_dipanggil', 'desc')
                ->with('counter')
                ->first();

            $nextWaiting = Queue::where('poliklinik_id', $poli->id)
                ->where('status', 'waiting')
                ->orderBy('nomor_urut', 'asc')
                ->first();

            $waitingCount = Queue::where('poliklinik_id', $poli->id)
                ->where('status', 'waiting')
                ->count();

            $totalToday = Queue::where('poliklinik_id', $poli->id)
                ->whereDate('waktu_daftar', now()->toDateString())
                ->count();

            return [
                'id' => $poli->id,
                'kode' => $poli->kode,
                'nama' => $poli->nama,
                'gedung_lantai' => $poli->gedung_lantai,
                'current_queue' => $currentCalling ? [
                    'id' => $currentCalling->id,
                    'nomor_antrean' => $currentCalling->nomor_antrean,
                    'nama_pasien' => $currentCalling->nama_pasien,
                    'jenis_pasien' => $currentCalling->jenis_pasien,
                    'nomor_bilik' => $currentCalling->counter ? $currentCalling->counter->nomor_bilik : '-',
                    'nama_petugas' => $currentCalling->counter ? $currentCalling->counter->nama_petugas : '-',
                    'status' => $currentCalling->status,
                ] : null,
                'next_queue' => $nextWaiting ? [
                    'id' => $nextWaiting->id,
                    'nomor_antrean' => $nextWaiting->nomor_antrean,
                    'nama_pasien' => $nextWaiting->nama_pasien,
                    'jenis_pasien' => $nextWaiting->jenis_pasien,
                    'status' => 'waiting',
                ] : null,
                'waiting_count' => $waitingCount,
                'total_today' => $totalToday,
            ];
        });

        // 3. Last 5 recent calls history
        $recentCalls = QueueCallLog::with(['queue.poliklinik', 'counter'])
            ->orderBy('id', 'desc')
            ->limit(5)
            ->get()
            ->map(function ($log) {
                return [
                    'id' => $log->id,
                    'nomor_antrean' => $log->queue ? $log->queue->nomor_antrean : '-',
                    'poliklinik' => $log->queue && $log->queue->poliklinik ? $log->queue->poliklinik->nama : '-',
                    'bilik' => $log->counter ? $log->counter->nomor_bilik : '-',
                    'waktu' => $log->created_at->format('H:i:s'),
                ];
            });

        return [
            'active_call' => $activeCallLog ? [
                'call_log_id' => $activeCallLog->id,
                'queue_id' => $activeCallLog->queue_id,
                'status' => $activeCallLog->queue ? $activeCallLog->queue->status : 'calling',
                'nomor_antrean' => $activeCallLog->queue ? $activeCallLog->queue->nomor_antrean : '-',
                'poliklinik' => $activeCallLog->queue && $activeCallLog->queue->poliklinik ? $activeCallLog->queue->poliklinik->nama : '-',
                'poliklinik_fonetik' => $activeCallLog->queue && $activeCallLog->queue->poliklinik ? ($activeCallLog->queue->poliklinik->nama_fonetik ?: $activeCallLog->queue->poliklinik->nama) : '-',
                'bilik' => $activeCallLog->counter ? $activeCallLog->counter->nomor_bilik : '-',
                'nama_petugas' => $activeCallLog->counter ? $activeCallLog->counter->nama_petugas : '-',
                'teks_panggilan' => $activeCallLog->teks_panggilan,
                'gemini_metadata' => $activeCallLog->gemini_metadata,
                'called_at' => $activeCallLog->created_at->toIso8601String(),
            ] : null,
            'polikliniks' => $polikliniks,
            'recent_calls' => $recentCalls,
            'server_time' => now()->toIso8601String(),
        ];
    }
}
