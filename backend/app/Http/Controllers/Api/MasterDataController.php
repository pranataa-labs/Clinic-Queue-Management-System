<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Counter;
use App\Models\Poliklinik;
use Illuminate\Http\JsonResponse;

class MasterDataController extends Controller
{
    /**
     * Get list of polikliniks with counters.
     */
    public function getPolikliniks(): JsonResponse
    {
        $polikliniks = Poliklinik::with(['counters' => function ($query) {
            $query->where('status', 'active');
        }])->where('status', 'active')->get();

        return response()->json([
            'success' => true,
            'message' => 'Daftar poliklinik berhasil diambil.',
            'data' => $polikliniks,
        ]);
    }

    /**
     * Get list of counters.
     */
    public function getCounters(): JsonResponse
    {
        $counters = Counter::with('poliklinik')->where('status', 'active')->get();

        return response()->json([
            'success' => true,
            'message' => 'Daftar bilik loket berhasil diambil.',
            'data' => $counters,
        ]);
    }
}
