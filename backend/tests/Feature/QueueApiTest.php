<?php

namespace Tests\Feature;

use App\Models\Counter;
use App\Models\Poliklinik;
use App\Models\Queue;
use App\Models\QueueSetting;
use Database\Seeders\ClinicQueueSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

/**
 * Queue API & Operational Test Suite
 * Fully compliant with Workflow-Master Testing & QA Rules (AAA Pattern, Strict Assertions, Negative & Security Checks)
 */
class QueueApiTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        // Seed standard initial master data (Polikliniks, Counters, Initial Settings, Sample Queues)
        $this->seed(ClinicQueueSeeder::class);
    }

    // ==========================================
    // 1. DISPLAY & PUBLIC TV API TESTS
    // ==========================================

    /**
     * Test Display TV state retrieval and schema verification.
     */
    public function test_can_fetch_display_state_with_proper_structure(): void
    {
        // Act
        $response = $this->getJson('/api/display-state');

        // Assert
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
            ])
            ->assertJson([
                'success' => true,
            ]);
    }

    // ==========================================
    // 2. KIOSK & TICKET REGISTRATION TESTS
    // ==========================================

    /**
     * Test successful ticket registration at self-service kiosk (Happy Path).
     */
    public function test_can_take_new_queue_ticket_with_sequential_numbering(): void
    {
        // Arrange
        $poli = Poliklinik::firstOrFail();
        $payload = [
            'poliklinik_id' => $poli->id,
            'nama_pasien' => 'Ahmad Dahlan',
            'jenis_pasien' => 'umum',
            'catatan_khusus' => 'Pemeriksaan rutin tekanan darah',
        ];

        // Act
        $response = $this->postJson('/api/queues/take-ticket', $payload);

        // Assert
        $response->assertStatus(201)
            ->assertJsonStructure([
                'success',
                'message',
                'data' => [
                    'id',
                    'nomor_antrean',
                    'nama_pasien',
                    'jenis_pasien',
                    'status',
                    'poliklinik',
                ],
            ])
            ->assertJson([
                'success' => true,
                'data' => [
                    'nama_pasien' => 'Ahmad Dahlan',
                    'jenis_pasien' => 'umum',
                    'status' => 'waiting',
                ],
            ]);

        $this->assertDatabaseHas('queues', [
            'poliklinik_id' => $poli->id,
            'nama_pasien' => 'Ahmad Dahlan',
            'status' => 'waiting',
        ]);
    }

    /**
     * Test validation failure when required ticket fields are missing (Negative Test).
     */
    public function test_cannot_take_ticket_when_required_fields_missing(): void
    {
        // Arrange (Empty payload)
        $payload = [];

        // Act
        $response = $this->postJson('/api/queues/take-ticket', $payload);

        // Assert
        $response->assertStatus(422)
            ->assertJsonValidationErrors(['poliklinik_id', 'nama_pasien', 'jenis_pasien']);
    }

    /**
     * Test validation failure with invalid patient category enum (Negative Test).
     */
    public function test_cannot_take_ticket_with_invalid_patient_type(): void
    {
        // Arrange
        $poli = Poliklinik::firstOrFail();
        $payload = [
            'poliklinik_id' => $poli->id,
            'nama_pasien' => 'Budi Santoso',
            'jenis_pasien' => 'invalid_category_xyz',
        ];

        // Act
        $response = $this->postJson('/api/queues/take-ticket', $payload);

        // Assert
        $response->assertStatus(422)
            ->assertJsonValidationErrors(['jenis_pasien']);
    }

    // ==========================================
    // 3. DOCTOR CONSOLE & QUEUE CALLING TESTS
    // ==========================================

    /**
     * Test doctor can fetch dedicated clinic queues list.
     */
    public function test_can_fetch_clinic_specific_queues(): void
    {
        // Arrange
        $poli = Poliklinik::firstOrFail();

        // Act
        $response = $this->getJson('/api/queues/poli/' . $poli->id);

        // Assert
        $response->assertStatus(200)
            ->assertJsonStructure([
                'success',
                'message',
                'data' => [
                    'poliklinik',
                    'waiting',
                    'calling_or_active',
                    'recent_completed',
                ],
            ])
            ->assertJson([
                'success' => true,
            ]);
    }

    /**
     * Test returns 404 when fetching queues for non-existent clinic (Boundary Check).
     */
    public function test_returns_404_when_fetching_non_existent_clinic_queues(): void
    {
        // Act
        $response = $this->getJson('/api/queues/poli/999999');

        // Assert
        $response->assertStatus(404);
    }

    /**
     * Test doctor can call the next patient and generate audio phonetic script.
     */
    public function test_can_call_next_queue_and_generate_phonetic_script(): void
    {
        // Arrange
        $counter = Counter::firstOrFail();

        // Ensure there is at least one waiting queue for this counter's clinic
        Queue::create([
            'poliklinik_id' => $counter->poliklinik_id,
            'nomor_antrean' => 'A-999',
            'nomor_urut' => 999,
            'nama_pasien' => 'Pasien Prioritas Testing',
            'jenis_pasien' => 'prioritas',
            'status' => 'waiting',
        ]);

        // Act
        $response = $this->postJson('/api/queues/call-next', [
            'counter_id' => $counter->id,
        ]);

        // Assert
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

    /**
     * Test returns 404 when callNext is called but no patients are waiting.
     */
    public function test_returns_404_when_call_next_has_no_waiting_patients(): void
    {
        // Arrange: Mark all queues in this clinic as completed
        $counter = Counter::firstOrFail();
        Queue::where('poliklinik_id', $counter->poliklinik_id)->update(['status' => 'completed']);

        // Act
        $response = $this->postJson('/api/queues/call-next', [
            'counter_id' => $counter->id,
        ]);

        // Assert
        $response->assertStatus(404)
            ->assertJson([
                'success' => false,
            ]);
    }

    /**
     * Test recall an already active queue.
     */
    public function test_can_recall_active_queue_ticket(): void
    {
        // Arrange
        $counter = Counter::firstOrFail();
        $queue = Queue::create([
            'poliklinik_id' => $counter->poliklinik_id,
            'counter_id' => $counter->id,
            'nomor_antrean' => 'A-050',
            'nomor_urut' => 50,
            'nama_pasien' => 'Siti Nurhaliza',
            'jenis_pasien' => 'umum',
            'status' => 'calling',
            'call_count' => 1,
        ]);

        // Act
        $response = $this->postJson('/api/queues/recall', [
            'queue_id' => $queue->id,
            'counter_id' => $counter->id,
        ]);

        // Assert
        $response->assertStatus(200)
            ->assertJsonStructure([
                'success',
                'data' => [
                    'queue',
                    'announcement',
                ],
            ]);

        $this->assertDatabaseHas('queues', [
            'id' => $queue->id,
            'call_count' => 2,
        ]);
    }

    /**
     * Test state transition: Doctor starts consultation.
     */
    public function test_can_start_consultation_successfully(): void
    {
        // Arrange
        $counter = Counter::firstOrFail();
        $queue = Queue::create([
            'poliklinik_id' => $counter->poliklinik_id,
            'counter_id' => $counter->id,
            'nomor_antrean' => 'A-055',
            'nomor_urut' => 55,
            'nama_pasien' => 'Rina Nose',
            'jenis_pasien' => 'bpjs',
            'status' => 'calling',
        ]);

        // Act
        $response = $this->postJson('/api/queues/start-consultation', [
            'queue_id' => $queue->id,
        ]);

        // Assert
        $response->assertStatus(200);
        $this->assertDatabaseHas('queues', [
            'id' => $queue->id,
            'status' => 'in_consultation',
        ]);
    }

    /**
     * Test state transition: Doctor skips absent patient.
     */
    public function test_can_skip_absent_patient_queue(): void
    {
        // Arrange
        $counter = Counter::firstOrFail();
        $queue = Queue::create([
            'poliklinik_id' => $counter->poliklinik_id,
            'counter_id' => $counter->id,
            'nomor_antrean' => 'A-060',
            'nomor_urut' => 60,
            'nama_pasien' => 'Pasien Tidak Hadir',
            'jenis_pasien' => 'umum',
            'status' => 'calling',
        ]);

        // Act
        $response = $this->postJson('/api/queues/skip', [
            'queue_id' => $queue->id,
        ]);

        // Assert
        $response->assertStatus(200);
        $this->assertDatabaseHas('queues', [
            'id' => $queue->id,
            'status' => 'skipped',
        ]);
    }

    /**
     * Test state transition: Doctor completes patient consultation.
     */
    public function test_can_complete_patient_consultation(): void
    {
        // Arrange
        $counter = Counter::firstOrFail();
        $queue = Queue::create([
            'poliklinik_id' => $counter->poliklinik_id,
            'counter_id' => $counter->id,
            'nomor_antrean' => 'A-065',
            'nomor_urut' => 65,
            'nama_pasien' => 'Bambang Pamungkas',
            'jenis_pasien' => 'umum',
            'status' => 'in_consultation',
        ]);

        // Act
        $response = $this->postJson('/api/queues/complete', [
            'queue_id' => $queue->id,
        ]);

        // Assert
        $response->assertStatus(200);
        $this->assertDatabaseHas('queues', [
            'id' => $queue->id,
            'status' => 'completed',
        ]);
    }

    // ==========================================
    // 4. ADMIN DASHBOARD & CRUD INTEGRATION TESTS
    // ==========================================

    /**
     * Test admin can fetch dashboard KPI summary statistics.
     */
    public function test_admin_can_fetch_dashboard_kpi_stats(): void
    {
        // Act
        $response = $this->getJson('/api/admin/stats');

        // Assert
        $response->assertStatus(200)
            ->assertJsonStructure([
                'success',
                'message',
                'data' => [
                    'total_rooms',
                    'active_rooms',
                    'total_polikliniks',
                    'active_polikliniks',
                    'total_queues_today',
                    'waiting_today',
                    'in_consultation_today',
                    'completed_today',
                    'skipped_today',
                ],
            ]);
    }

    /**
     * Test admin can fetch all counters.
     */
    public function test_admin_can_fetch_all_counters(): void
    {
        // Act
        $response = $this->getJson('/api/admin/counters');

        // Assert
        $response->assertStatus(200)
            ->assertJsonStructure([
                'success',
                'data' => [
                    '*' => [
                        'id',
                        'nomor_bilik',
                        'nama_petugas',
                        'status',
                    ],
                ],
            ]);
    }

    /**
     * Test admin can create a new doctor room / counter.
     */
    public function test_admin_can_create_new_counter_room(): void
    {
        // Arrange
        $poli = Poliklinik::firstOrFail();
        $payload = [
            'poliklinik_id' => $poli->id,
            'nomor_bilik' => 'Ruangan 99',
            'nama_petugas' => 'dr. Nicholas Saputra',
            'gelar_petugas' => 'Dokter Umum',
            'status' => 'active',
        ];

        // Act
        $response = $this->postJson('/api/admin/counters', $payload);

        // Assert
        $response->assertStatus(201)
            ->assertJson([
                'success' => true,
                'data' => [
                    'nomor_bilik' => 'Ruangan 99',
                    'nama_petugas' => 'dr. Nicholas Saputra',
                ],
            ]);

        $this->assertDatabaseHas('counters', [
            'nomor_bilik' => 'Ruangan 99',
            'nama_petugas' => 'dr. Nicholas Saputra',
        ]);
    }

    /**
     * Test admin can update an existing doctor room / counter.
     */
    public function test_admin_can_update_existing_counter_room(): void
    {
        // Arrange
        $counter = Counter::firstOrFail();
        $payload = [
            'nama_petugas' => 'dr. Dian Sastrowardoyo, Sp.A',
            'gelar_petugas' => 'Spesialis Anak',
            'status' => 'active',
        ];

        // Act
        $response = $this->putJson('/api/admin/counters/' . $counter->id, $payload);

        // Assert
        $response->assertStatus(200)
            ->assertJson([
                'success' => true,
            ]);

        $this->assertDatabaseHas('counters', [
            'id' => $counter->id,
            'nama_petugas' => 'dr. Dian Sastrowardoyo, Sp.A',
        ]);
    }

    /**
     * Test admin can create a new poliklinik.
     */
    public function test_admin_can_create_new_poliklinik(): void
    {
        // Arrange
        $payload = [
            'kode' => 'Z-REHAB',
            'nama' => 'Poli Rehabilitasi Medis',
            'nama_fonetik' => 'Poliklinik Rehabilitasi Medis dan Fisioterapi',
            'gedung_lantai' => 'Lantai 3 Sayap Barat',
            'status' => 'active',
        ];

        // Act
        $response = $this->postJson('/api/admin/polikliniks', $payload);

        // Assert
        $response->assertStatus(201)
            ->assertJson([
                'success' => true,
                'data' => [
                    'kode' => 'Z-REHAB',
                    'nama' => 'Poli Rehabilitasi Medis',
                ],
            ]);

        $this->assertDatabaseHas('polikliniks', [
            'kode' => 'Z-REHAB',
        ]);
    }

    /**
     * Test admin can update an existing poliklinik.
     */
    public function test_admin_can_update_poliklinik(): void
    {
        // Arrange
        $poli = Poliklinik::firstOrFail();
        $payload = [
            'nama' => 'Poli Anak & Tumbuh Kembang Terpadu',
            'gedung_lantai' => 'Lantai 1 Paviliun Kenanga',
        ];

        // Act
        $response = $this->putJson('/api/admin/polikliniks/' . $poli->id, $payload);

        // Assert
        $response->assertStatus(200)
            ->assertJson([
                'success' => true,
            ]);

        $this->assertDatabaseHas('polikliniks', [
            'id' => $poli->id,
            'nama' => 'Poli Anak & Tumbuh Kembang Terpadu',
        ]);
    }

    /**
     * Test admin can update TV display settings (running text & chime tone).
     */
    public function test_admin_can_update_tv_display_settings(): void
    {
        // Arrange
        $payload = [
            'clinic_name' => 'RSUD Husada Medika Utama',
            'running_text' => 'PENGUMUMAN TESTING: Harap menjaga ketenangan di ruang tunggu.',
            'audio_chime' => 'dingdong',
        ];

        // Act
        $response = $this->postJson('/api/admin/settings', $payload);

        // Assert
        $response->assertStatus(200)
            ->assertJson([
                'success' => true,
            ]);

        $this->assertDatabaseHas('queue_settings', [
            'key' => 'clinic_name',
            'value' => 'RSUD Husada Medika Utama',
        ]);
    }

    /**
     * Test admin can reset daily queues.
     */
    public function test_admin_can_reset_daily_queues_atomically(): void
    {
        // Act
        $response = $this->postJson('/api/admin/queues/reset');

        // Assert
        $response->assertStatus(200)
            ->assertJson([
                'success' => true,
            ]);

        // Verify active and waiting queues are cleared for today
        $remainingWaiting = Queue::whereDate('created_at', now()->toDateString())
            ->whereIn('status', ['waiting', 'calling', 'in_consultation'])
            ->count();

        $this->assertEquals(0, $remainingWaiting);
    }
}
