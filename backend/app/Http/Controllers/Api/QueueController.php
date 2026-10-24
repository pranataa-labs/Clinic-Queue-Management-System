<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Counter;
use App\Models\Poliklinik;
use App\Models\Queue;
use App\Services\QueueCallingService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;

class QueueController extends Controller
{
    public function __construct(
        protected QueueCallingService $callingService
    ) {}

    /**
     * Get aggregated display state for TV Monitor.
     */
    public function getDisplayState(): JsonResponse
    {
        $state = $this->callingService->getDisplayState();
        return response()->json([
            'success' => true,
            'message' => 'State antrean display berhasil dimuat.',
            'data' => $state,
        ]);
    }

    /**
     * Get queue list for a specific poliklinik / counter console.
     */
    public function getClinicQueues(int $poliId): JsonResponse
    {
        $poli = Poliklinik::with('counters')->findOrFail($poliId);

        $waiting = Queue::where('poliklinik_id', $poliId)
            ->where('status', 'waiting')
            ->orderBy('nomor_urut', 'asc')
            ->get();

        $callingOrActive = Queue::where('poliklinik_id', $poliId)
            ->whereIn('status', ['calling', 'in_consultation'])
            ->with('counter')
            ->orderBy('waktu_dipanggil', 'desc')
            ->get();

        $completed = Queue::where('poliklinik_id', $poliId)
            ->where('status', 'completed')
            ->orderBy('waktu_selesai', 'desc')
            ->limit(10)
            ->get();

        return response()->json([
            'success' => true,
            'message' => 'Data antrean poliklinik berhasil dimuat.',
            'data' => [
                'poliklinik' => $poli,
                'waiting' => $waiting,
                'calling_or_active' => $callingOrActive,
                'recent_completed' => $completed,
            ],
        ]);
    }

    /**
     * Call next waiting ticket.
     */
    public function callNext(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'counter_id' => 'required|integer|exists:counters,id',
        ]);

        $result = $this->callingService->callNext($validated['counter_id']);

        if (!$result['success']) {
            return response()->json([
                'success' => false,
                'message' => $result['message'],
                'data' => null,
            ], 404);
        }

        return response()->json([
            'success' => true,
            'message' => $result['message'],
            'data' => $result['data'],
        ]);
    }

    /**
     * Recall a specific ticket.
     */
    public function recall(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'queue_id' => 'required|integer|exists:queues,id',
            'counter_id' => 'required|integer|exists:counters,id',
        ]);

        $result = $this->callingService->recall($validated['queue_id'], $validated['counter_id']);

        return response()->json([
            'success' => true,
            'message' => $result['message'],
            'data' => $result['data'],
        ]);
    }

    /**
     * Start doctor examination/consultation.
     */
    public function startConsultation(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'queue_id' => 'required|integer|exists:queues,id',
        ]);

        $queue = $this->callingService->startConsultation($validated['queue_id']);

        return response()->json([
            'success' => true,
            'message' => 'Pemeriksaan pasien dimulai.',
            'data' => $queue,
        ]);
    }

    /**
     * Skip absent ticket.
     */
    public function skip(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'queue_id' => 'required|integer|exists:queues,id',
        ]);

        $queue = $this->callingService->skip($validated['queue_id']);

        return response()->json([
            'success' => true,
            'message' => 'Antrean berhasil dilewati.',
            'data' => $queue,
        ]);
    }

    /**
     * Complete consultation.
     */
    public function complete(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'queue_id' => 'required|integer|exists:queues,id',
        ]);

        $queue = $this->callingService->complete($validated['queue_id']);

        return response()->json([
            'success' => true,
            'message' => 'Pemeriksaan selesai.',
            'data' => $queue,
        ]);
    }

    /**
     * Register a new queue ticket (Kiosk).
     */
    public function takeTicket(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'poliklinik_id' => 'required|integer|exists:polikliniks,id',
            'nama_pasien' => 'required|string|max:150',
            'jenis_pasien' => ['required', Rule::in(['umum', 'bpjs', 'prioritas'])],
            'catatan_khusus' => 'nullable|string|max:255',
        ]);

        $ticket = $this->callingService->registerTicket(
            $validated['poliklinik_id'],
            $validated['nama_pasien'],
            $validated['jenis_pasien'],
            $validated['catatan_khusus'] ?? null
        );

        return response()->json([
            'success' => true,
            'message' => 'Nomor antrean berhasil dicetak.',
            'data' => $ticket->load('poliklinik'),
        ], 201);
    }

    /**
     * Toggle counter break status (Ishoma / Jeda Layanan).
     */
    public function toggleBreak(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'counter_id' => 'required|integer|exists:counters,id',
            'status' => 'required|string|in:active,break',
        ]);

        $counter = Counter::findOrFail($validated['counter_id']);
        $counter->status = $validated['status'];
        $counter->save();

        return response()->json([
            'success' => true,
            'message' => $counter->status === 'break'
                ? 'Ruangan beralih ke mode jeda istirahat/ishoma.'
                : 'Ruangan kembali aktif melayani.',
            'data' => $counter,
        ]);
    }
}
