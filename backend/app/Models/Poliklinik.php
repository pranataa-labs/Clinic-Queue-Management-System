<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Poliklinik extends Model
{
    use HasFactory;

    protected $fillable = [
        'kode',
        'nama',
        'nama_fonetik',
        'gedung_lantai',
        'status',
    ];

    public function counters(): HasMany
    {
        return $this->hasMany(Counter::class);
    }

    public function queues(): HasMany
    {
        return $this->hasMany(Queue::class);
    }

    public function activeQueues(): HasMany
    {
        return $this->hasMany(Queue::class)->whereIn('status', ['waiting', 'calling', 'in_consultation']);
    }
}
