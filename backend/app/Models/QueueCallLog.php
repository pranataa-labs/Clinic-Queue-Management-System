<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class QueueCallLog extends Model
{
    use HasFactory;

    public $timestamps = false;

    protected $fillable = [
        'queue_id',
        'counter_id',
        'teks_panggilan',
        'tipe_panggilan',
        'gemini_metadata',
        'created_at',
    ];

    protected $casts = [
        'gemini_metadata' => 'array',
        'created_at' => 'datetime',
    ];

    public function queue(): BelongsTo
    {
        return $this->belongsTo(Queue::class);
    }

    public function counter(): BelongsTo
    {
        return $this->belongsTo(Counter::class);
    }
}
