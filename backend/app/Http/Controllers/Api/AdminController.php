<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Counter;
use App\Models\Poliklinik;
use App\Models\Queue;
use App\Models\QueueSetting;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class AdminController extends Controller
{
    /**
     * Get system statistics for dashboard KPI cards.
     */
    public function getStats(): JsonResponse
    {
        $today = now()->startOfDay();

        return response()->json([
            'success' => true,
            'message' => 'Statistik admin berhasil dimuat.',
            'data' => [
                'total_rooms' => Counter::count(),
                'active_rooms' => Counter::where('status', 'active')->count(),
                'total_polikliniks' => Poliklinik::count(),
                'active_polikliniks' => Poliklinik::where('status', 'active')->count(),
                'total_queues_today' => Queue::where('created_at', '>=', $today)->count(),
                'waiting_today' => Queue::where('created_at', '>=', $today)->where('status', 'waiting')->count(),
                'in_consultation_today' => Queue::where('created_at', '>=', $today)->where('status', 'in_consultation')->count(),
                'completed_today' => Queue::where('created_at', '>=', $today)->where('status', 'completed')->count(),
                'skipped_today' => Queue::where('created_at', '>=', $today)->where('status', 'skipped')->count(),
            ],
        ]);
    }

    /**
     * Get all counters (with poliklinik) for admin management.
     */
    public function getCounters(): JsonResponse
    {
        $counters = Counter::with('poliklinik')->orderBy('id', 'asc')->get();

        return response()->json([
            'success' => true,
            'message' => 'Daftar semua ruangan berhasil dimuat.',
            'data' => $counters,
        ]);
    }

    /**
     * Store a new counter / room.
     */
    public function storeCounter(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'poliklinik_id' => 'required|integer|exists:polikliniks,id',
            'nomor_bilik' => 'required|string|max:50',
            'nama_petugas' => 'required|string|max:100',
            'gelar_petugas' => 'nullable|string|max:100',
            'status' => 'nullable|string|in:active,inactive',
        ]);

        $counter = Counter::create([
            'poliklinik_id' => $validated['poliklinik_id'],
            'nomor_bilik' => $validated['nomor_bilik'],
            'nama_petugas' => $validated['nama_petugas'],
            'gelar_petugas' => $validated['gelar_petugas'] ?? null,
            'status' => $validated['status'] ?? 'active',
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Ruangan baru berhasil ditambahkan.',
            'data' => $counter->load('poliklinik'),
        ], 201);
    }

    /**
     * Update an existing counter / room.
     */
    public function updateCounter(Request $request, int $id): JsonResponse
    {
        $counter = Counter::findOrFail($id);

        $validated = $request->validate([
            'poliklinik_id' => 'sometimes|required|integer|exists:polikliniks,id',
            'nomor_bilik' => 'sometimes|required|string|max:50',
            'nama_petugas' => 'sometimes|required|string|max:100',
            'gelar_petugas' => 'nullable|string|max:100',
            'status' => 'sometimes|required|string|in:active,inactive',
        ]);

        $counter->update($validated);

        return response()->json([
            'success' => true,
            'message' => 'Data ruangan berhasil diperbarui.',
            'data' => $counter->load('poliklinik'),
        ]);
    }

    /**
     * Delete a counter / room.
     */
    public function deleteCounter(int $id): JsonResponse
    {
        $counter = Counter::findOrFail($id);
        $counter->delete();

        return response()->json([
            'success' => true,
            'message' => 'Ruangan berhasil dihapus.',
        ]);
    }

    /**
     * Get all polikliniks for admin management.
     */
    public function getPolikliniks(): JsonResponse
    {
        $polikliniks = Poliklinik::with('counters')->orderBy('id', 'asc')->get();

        return response()->json([
            'success' => true,
            'message' => 'Daftar poliklinik berhasil dimuat.',
            'data' => $polikliniks,
        ]);
    }

    /**
     * Store a new poliklinik.
     */
    public function storePoliklinik(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'kode' => 'required|string|max:20|unique:polikliniks,kode',
            'nama' => 'required|string|max:100',
            'nama_fonetik' => 'nullable|string|max:150',
            'gedung_lantai' => 'required|string|max:100',
            'status' => 'nullable|string|in:active,inactive',
        ]);

        $poli = Poliklinik::create([
            'kode' => strtoupper($validated['kode']),
            'nama' => $validated['nama'],
            'nama_fonetik' => $validated['nama_fonetik'] ?? $validated['nama'],
            'gedung_lantai' => $validated['gedung_lantai'],
            'status' => $validated['status'] ?? 'active',
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Poliklinik baru berhasil ditambahkan.',
            'data' => $poli,
        ], 201);
    }

    /**
     * Update an existing poliklinik.
     */
    public function updatePoliklinik(Request $request, int $id): JsonResponse
    {
        $poli = Poliklinik::findOrFail($id);

        $validated = $request->validate([
            'kode' => "sometimes|required|string|max:20|unique:polikliniks,kode,{$id}",
            'nama' => 'sometimes|required|string|max:100',
            'nama_fonetik' => 'nullable|string|max:150',
            'gedung_lantai' => 'sometimes|required|string|max:100',
            'status' => 'sometimes|required|string|in:active,inactive',
        ]);

        $poli->update($validated);

        return response()->json([
            'success' => true,
            'message' => 'Data poliklinik berhasil diperbarui.',
            'data' => $poli,
        ]);
    }

    /**
     * Delete a poliklinik.
     */
    public function deletePoliklinik(int $id): JsonResponse
    {
        $poli = Poliklinik::findOrFail($id);
        $poli->delete();

        return response()->json([
            'success' => true,
            'message' => 'Poliklinik berhasil dihapus.',
        ]);
    }

    /**
     * Get system settings.
     */
    public function getSettings(): JsonResponse
    {
        $settings = QueueSetting::all()->pluck('value', 'key');

        return response()->json([
            'success' => true,
            'message' => 'Pengaturan sistem berhasil dimuat.',
            'data' => $settings,
        ]);
    }

    /**
     * Update system settings.
     */
    public function updateSettings(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'clinic_name' => 'nullable|string|max:150',
            'running_text' => 'nullable|string',
            'audio_chime' => 'nullable|string|in:bell,dingdong,standard_bell,urgent_chime',
        ]);

        foreach ($validated as $key => $value) {
            if ($value !== null) {
                QueueSetting::updateOrCreate(
                    ['key' => $key],
                    ['value' => $value]
                );
            }
        }

        return response()->json([
            'success' => true,
            'message' => 'Pengaturan berhasil diperbarui.',
            'data' => QueueSetting::all()->pluck('value', 'key'),
        ]);
    }

    /**
     * Get all queues for live monitoring.
     */
    public function getQueues(): JsonResponse
    {
        $queues = Queue::with(['poliklinik', 'counter'])
            ->orderBy('id', 'desc')
            ->limit(100)
            ->get();

        return response()->json([
            'success' => true,
            'message' => 'Daftar antrean berhasil dimuat.',
            'data' => $queues,
        ]);
    }

    /**
     * Reset today's queues for fresh operational day.
     */
    public function resetTodayQueues(): JsonResponse
    {
        Queue::truncate();

        return response()->json([
            'success' => true,
            'message' => 'Seluruh antrean berhasil direset untuk hari operasional baru.',
        ]);
    }
}
