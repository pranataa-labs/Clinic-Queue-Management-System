<?php

namespace Tests\Feature;

use App\Models\Counter;
use App\Models\Poliklinik;
use Database\Seeders\ClinicQueueSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class QueueApiTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seed(ClinicQueueSeeder::class);
    }

    public function test_can_fetch_display_state(): void
    {
        $response = $this->getJson('/api/display-state');

        $response->assertStatus(200)
            ->assertJsonStructure([
                'success',
                'message',
                'data' => [
                    'active_call',
                    'polikliniks',
                    'recent_calls',
                    'server_time',
                ],
            ]);
    }

    public function test_can_call_next_queue_and_generate_phonetic_script(): void
    {
        $counter = Counter::first();
        $this->assertNotNull($counter);

        $response = $this->postJson('/api/queues/call-next', [
            'counter_id' => $counter->id,
        ]);

        $response->assertStatus(200)
            ->assertJsonStructure([
                'success',
                'message',
                'data' => [
                    'queue' => [
                        'id',
                        'nomor_antrean',
                        'status',
                        'call_count',
                    ],
                    'announcement' => [
                        'call_script',
                        'phonetic_spelling',
                        'chime_tone',
                        'display_headline',
                        'repeat_count',
                    ],
                ],
            ]);

        $this->assertDatabaseHas('queues', [
            'counter_id' => $counter->id,
            'status' => 'calling',
        ]);
    }

    public function test_can_take_new_queue_ticket(): void
    {
        $poli = Poliklinik::first();

        $response = $this->postJson('/api/queues/take-ticket', [
            'poliklinik_id' => $poli->id,
            'nama_pasien' => 'Pasien Uji Coba',
            'jenis_pasien' => 'umum',
            'catatan_khusus' => 'Pemeriksaan tensi',
        ]);

        $response->assertStatus(201)
            ->assertJsonStructure([
                'success',
                'data' => [
                    'id',
                    'nomor_antrean',
                    'nama_pasien',
                    'status',
                ],
            ]);
    }
}
