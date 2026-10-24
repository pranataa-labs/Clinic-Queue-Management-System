<?php

use App\Http\Controllers\Api\AdminController;
use App\Http\Controllers\Api\MasterDataController;
use App\Http\Controllers\Api\QueueController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Route;

// Display Screen Aggregated State
Route::get('/display-state', [QueueController::class, 'getDisplayState']);

// Queue Operations
Route::prefix('queues')->group(function () {
    Route::get('/poli/{poliId}', [QueueController::class, 'getClinicQueues']);
    Route::post('/call-next', [QueueController::class, 'callNext']);
    Route::post('/recall', [QueueController::class, 'recall']);
    Route::post('/start-consultation', [QueueController::class, 'startConsultation']);
    Route::post('/skip', [QueueController::class, 'skip']);
    Route::post('/complete', [QueueController::class, 'complete']);
    Route::post('/take-ticket', [QueueController::class, 'takeTicket']);
    Route::post('/toggle-break', [QueueController::class, 'toggleBreak']);
});

// Master Data
Route::prefix('master')->group(function () {
    Route::get('/polikliniks', [MasterDataController::class, 'getPolikliniks']);
    Route::get('/counters', [MasterDataController::class, 'getCounters']);
});

// Admin Management
Route::prefix('admin')->group(function () {
    Route::get('/stats', [AdminController::class, 'getStats']);
    Route::get('/counters', [AdminController::class, 'getCounters']);
    Route::post('/counters', [AdminController::class, 'storeCounter']);
    Route::put('/counters/{id}', [AdminController::class, 'updateCounter']);
    Route::delete('/counters/{id}', [AdminController::class, 'deleteCounter']);

    Route::get('/polikliniks', [AdminController::class, 'getPolikliniks']);
    Route::post('/polikliniks', [AdminController::class, 'storePoliklinik']);
    Route::put('/polikliniks/{id}', [AdminController::class, 'updatePoliklinik']);
    Route::delete('/polikliniks/{id}', [AdminController::class, 'deletePoliklinik']);

    Route::get('/settings', [AdminController::class, 'getSettings']);
    Route::post('/settings', [AdminController::class, 'updateSettings']);

    Route::get('/queues', [AdminController::class, 'getQueues']);
    Route::post('/queues/reset', [AdminController::class, 'resetTodayQueues']);
});

// WebRTC Signaling Relay (for Intercom between Doctor Console and TV Display)
Route::post('/webrtc/offer', function (Request $request) {
    $validated = $request->validate([
        'channel' => 'required|string',
        'sdp' => 'required|string',
        'type' => 'required|string',
        'doctor_name' => 'nullable|string',
        'room_name' => 'nullable|string',
        'clinic_name' => 'nullable|string',
    ]);
    Cache::put("webrtc_offer_{$validated['channel']}", $validated, 60);
    return response()->json(['success' => true, 'message' => 'Offer saved']);
});

Route::get('/webrtc/offer/{channel}', function (string $channel) {
    $offer = Cache::get("webrtc_offer_{$channel}");
    return response()->json(['success' => true, 'data' => $offer]);
});

Route::post('/webrtc/answer', function (Request $request) {
    $validated = $request->validate([
        'channel' => 'required|string',
        'sdp' => 'required|string',
        'type' => 'required|string',
    ]);
    Cache::put("webrtc_answer_{$validated['channel']}", $validated, 60);
    return response()->json(['success' => true, 'message' => 'Answer saved']);
});

Route::get('/webrtc/answer/{channel}', function (string $channel) {
    $answer = Cache::get("webrtc_answer_{$channel}");
    return response()->json(['success' => true, 'data' => $answer]);
});

Route::post('/webrtc/ice', function (Request $request) {
    $validated = $request->validate([
        'channel' => 'required|string',
        'sender' => 'required|string', // 'operator' or 'display'
        'candidate' => 'required|array',
    ]);
    $existing = Cache::get("webrtc_ice_{$validated['channel']}_{$validated['sender']}", []);
    $existing[] = $validated['candidate'];
    Cache::put("webrtc_ice_{$validated['channel']}_{$validated['sender']}", $existing, 60);
    return response()->json(['success' => true, 'message' => 'Candidate queued']);
});

Route::get('/webrtc/ice/{channel}/{sender}', function (string $channel, string $sender) {
    $candidates = Cache::get("webrtc_ice_{$channel}_{$sender}", []);
    return response()->json(['success' => true, 'data' => $candidates]);
});

Route::post('/webrtc/reset/{channel}', function (string $channel) {
    Cache::forget("webrtc_offer_{$channel}");
    Cache::forget("webrtc_answer_{$channel}");
    Cache::forget("webrtc_ice_{$channel}_operator");
    Cache::forget("webrtc_ice_{$channel}_display");
    return response()->json(['success' => true, 'message' => 'WebRTC channel reset']);
});
