<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Queue extends Model
{
    use HasFactory;

    protected $fillable = [
        'poliklinik_id',
        'counter_id',
        'nomor_antrean',
        'nomor_urut',
        'nama_pasien',
        'jenis_pasien',
        'status',
        'call_count',
        'catatan_khusus',
        'waktu_daftar',
        'waktu_dipanggil',
        'waktu_selesai',
    ];

    protected $casts = [
        'waktu_daftar' => 'datetime',
        'waktu_dipanggil' => 'datetime',
        'waktu_selesai' => 'datetime',
        'nomor_urut' => 'integer',
        'call_count' => 'integer',
    ];

    public function poliklinik(): BelongsTo
    {
        return $this->belongsTo(Poliklinik::class);
    }

    public function counter(): BelongsTo
    {
        return $this->belongsTo(Counter::class);
    }

    public function callLogs(): HasMany
    {
        return $this->hasMany(QueueCallLog::class);
    }
}
