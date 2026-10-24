<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        // 1. Poliklinik Master Table
        Schema::create('polikliniks', function (Blueprint $table) {
            $table->id();
            $table->string('kode', 20)->unique()->comment('Contoh: POLI-UMUM, POLI-GIGI, POLI-ANAK');
            $table->string('nama', 100);
            $table->string('nama_fonetik', 150)->nullable()->comment('Ejaan fonetik untuk TTS, cth: Poliklinik Gigi dan Mulut');
            $table->string('gedung_lantai', 50)->default('Lantai 1');
            $table->enum('status', ['active', 'inactive'])->default('active');
            $table->timestamps();

            $table->index(['status', 'kode'], 'idx_polikliniks_status_kode');
        });

        // 2. Counters / Bilik Pemeriksaan Table
        Schema::create('counters', function (Blueprint $table) {
            $table->id();
            $table->foreignId('poliklinik_id')->constrained('polikliniks')->cascadeOnDelete();
            $table->string('nomor_bilik', 20)->comment('Bilik 1, Ruang 2, Meja 1');
            $table->string('nama_petugas', 100)->nullable();
            $table->string('gelar_petugas', 100)->nullable()->comment('Spesialisasi atau gelar dokter');
            $table->enum('status', ['active', 'break', 'inactive'])->default('active');
            $table->timestamps();

            $table->index(['poliklinik_id', 'status'], 'idx_counters_poli_status');
        });

        // 3. Queues (Antrean) Table
        Schema::create('queues', function (Blueprint $table) {
            $table->id();
            $table->foreignId('poliklinik_id')->constrained('polikliniks')->cascadeOnDelete();
            $table->foreignId('counter_id')->nullable()->constrained('counters')->nullOnDelete();
            $table->string('nomor_antrean', 20)->comment('Contoh: A-001, B-012');
            $table->unsignedInteger('nomor_urut');
            $table->string('nama_pasien', 150);
            $table->enum('jenis_pasien', ['umum', 'bpjs', 'prioritas'])->default('umum');
            $table->enum('status', ['waiting', 'calling', 'in_consultation', 'skipped', 'completed'])->default('waiting');
            $table->unsignedSmallInteger('call_count')->default(0);
            $table->text('catatan_khusus')->nullable()->comment('Instruksi khusus atau peringatan triage');
            $table->timestamp('waktu_daftar')->useCurrent();
            $table->timestamp('waktu_dipanggil')->nullable();
            $table->timestamp('waktu_selesai')->nullable();
            $table->timestamps();

            $table->index(['poliklinik_id', 'status', 'waktu_daftar'], 'idx_queues_lookup');
            $table->index(['status', 'waktu_dipanggil'], 'idx_queues_active_call');
        });

        // 4. Queue Call Logs Table
        Schema::create('queue_call_logs', function (Blueprint $table) {
            $table->id();
            $table->foreignId('queue_id')->constrained('queues')->cascadeOnDelete();
            $table->foreignId('counter_id')->constrained('counters')->cascadeOnDelete();
            $table->text('teks_panggilan')->comment('Skrip teks yang dibacakan oleh TTS/Web Speech API');
            $table->enum('tipe_panggilan', ['auto_tts', 'gemini_phonetic', 'webrtc_intercom'])->default('auto_tts');
            $table->json('gemini_metadata')->nullable()->comment('Structured output payload dari Gemini 2.5 Flash');
            $table->timestamp('created_at')->useCurrent();

            $table->index(['queue_id', 'created_at'], 'idx_call_logs_queue_created');
        });

        // 5. System Settings Table
        Schema::create('queue_settings', function (Blueprint $table) {
            $table->id();
            $table->string('key', 100)->unique();
            $table->text('value')->nullable();
            $table->string('deskripsi', 255)->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('queue_call_logs');
        Schema::dropIfExists('queues');
        Schema::dropIfExists('counters');
        Schema::dropIfExists('polikliniks');
        Schema::dropIfExists('queue_settings');
    }
};
