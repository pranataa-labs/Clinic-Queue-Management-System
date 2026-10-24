// API Client connecting Next.js 16 to Laravel 13 backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';

export interface PoliklinikItem {
  id: number;
  kode: string;
  nama: string;
  gedung_lantai: string;
  current_queue: {
    id?: number;
    nomor_antrean: string;
    nama_pasien?: string;
    nomor_bilik: string;
    nama_petugas: string;
    status: 'calling' | 'in_consultation' | string;
  } | null;
  next_queue?: {
    id: number;
    nomor_antrean: string;
    nama_pasien: string;
    jenis_pasien: string;
    status: 'waiting';
  } | null;
  waiting_count: number;
  total_today: number;
}

export interface RecentCallItem {
  id: number;
  nomor_antrean: string;
  poliklinik: string;
  bilik: string;
  waktu: string;
}

export interface ActiveCallItem {
  call_log_id: number;
  queue_id?: number;
  status?: 'waiting' | 'calling' | 'in_consultation' | 'completed' | 'skipped' | string;
  nomor_antrean: string;
  poliklinik: string;
  poliklinik_fonetik: string;
  bilik: string;
  nama_petugas: string;
  teks_panggilan: string;
  gemini_metadata: {
    call_script: string;
    phonetic_spelling: string;
    chime_tone: string;
    display_headline: string;
    repeat_count: number;
    generator_type?: string;
  } | null;
  called_at: string;
}

export interface DisplayStateResponse {
  active_call: ActiveCallItem | null;
  polikliniks: PoliklinikItem[];
  recent_calls: RecentCallItem[];
  server_time: string;
}

export interface QueueItem {
  id: number;
  poliklinik_id: number;
  counter_id: number | null;
  nomor_antrean: string;
  nomor_urut: number;
  nama_pasien: string;
  jenis_pasien: 'umum' | 'bpjs' | 'prioritas';
  status: 'waiting' | 'calling' | 'in_consultation' | 'skipped' | 'completed';
  call_count: number;
  catatan_khusus: string | null;
  waktu_daftar: string;
  counter?: {
    id: number;
    nomor_bilik: string;
    nama_petugas: string;
  };
}

export const apiClient = {
  async getDisplayState(): Promise<DisplayStateResponse> {
    const res = await fetch(`${API_BASE_URL}/display-state`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Gagal mengambil data display');
    const json = await res.json();
    return json.data;
  },

  async getPolikliniks() {
    const res = await fetch(`${API_BASE_URL}/master/polikliniks`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Gagal mengambil daftar poliklinik');
    const json = await res.json();
    return json.data;
  },

  async getCounters() {
    const res = await fetch(`${API_BASE_URL}/master/counters`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Gagal mengambil daftar counter');
    const json = await res.json();
    return json.data;
  },

  async getClinicQueues(poliId: number) {
    const res = await fetch(`${API_BASE_URL}/queues/poli/${poliId}`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Gagal mengambil data antrean poli');
    const json = await res.json();
    return json.data;
  },

  async callNext(counterId: number) {
    const res = await fetch(`${API_BASE_URL}/queues/call-next`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ counter_id: counterId }),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.message || 'Panggilan gagal');
    return json.data;
  },

  async recall(queueId: number, counterId: number) {
    const res = await fetch(`${API_BASE_URL}/queues/recall`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ queue_id: queueId, counter_id: counterId }),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.message || 'Panggilan ulang gagal');
    return json.data;
  },

  async startConsultation(queueId: number) {
    const res = await fetch(`${API_BASE_URL}/queues/start-consultation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ queue_id: queueId }),
    });
    const json = await res.json();
    return json.data;
  },

  async skip(queueId: number) {
    const res = await fetch(`${API_BASE_URL}/queues/skip`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ queue_id: queueId }),
    });
    const json = await res.json();
    return json.data;
  },

  async complete(queueId: number) {
    const res = await fetch(`${API_BASE_URL}/queues/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ queue_id: queueId }),
    });
    const json = await res.json();
    return json.data;
  },

  async toggleBreak(counterId: number, status: 'active' | 'break') {
    const res = await fetch(`${API_BASE_URL}/queues/toggle-break`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ counter_id: counterId, status }),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.message || 'Gagal mengubah status istirahat');
    return json.data;
  },

  async takeTicket(payload: {
    poliklinik_id: number;
    nama_pasien: string;
    jenis_pasien: 'umum' | 'bpjs' | 'prioritas';
    catatan_khusus?: string;
  }) {
    const res = await fetch(`${API_BASE_URL}/queues/take-ticket`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.message || 'Gagal mendaftar antrean');
    return json.data;
  },

  // WebRTC Signaling
  async sendOffer(
    channel: string,
    offer: RTCSessionDescriptionInit,
    metadata?: { doctor_name?: string; room_name?: string; clinic_name?: string }
  ) {
    await fetch(`${API_BASE_URL}/webrtc/offer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        channel,
        sdp: offer.sdp,
        type: offer.type,
        doctor_name: metadata?.doctor_name,
        room_name: metadata?.room_name,
        clinic_name: metadata?.clinic_name,
      }),
    });
  },

  async getOffer(channel: string) {
    const res = await fetch(`${API_BASE_URL}/webrtc/offer/${channel}`);
    const json = await res.json();
    return json.data;
  },

  async sendAnswer(channel: string, answer: RTCSessionDescriptionInit) {
    await fetch(`${API_BASE_URL}/webrtc/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ channel, sdp: answer.sdp, type: answer.type }),
    });
  },

  async getAnswer(channel: string) {
    const res = await fetch(`${API_BASE_URL}/webrtc/answer/${channel}`);
    const json = await res.json();
    return json.data;
  },

  async sendIceCandidate(channel: string, sender: 'operator' | 'display', candidate: RTCIceCandidate) {
    await fetch(`${API_BASE_URL}/webrtc/ice`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ channel, sender, candidate: candidate.toJSON() }),
    });
  },

  async getIceCandidates(channel: string, sender: 'operator' | 'display') {
    const res = await fetch(`${API_BASE_URL}/webrtc/ice/${channel}/${sender}`);
    const json = await res.json();
    return json.data || [];
  },

  async resetWebRtc(channel: string) {
    await fetch(`${API_BASE_URL}/webrtc/reset/${channel}`, { method: 'POST' });
  },

  // --- Admin API Methods ---
  async getAdminStats() {
    const res = await fetch(`${API_BASE_URL}/admin/stats`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Gagal memuat statistik admin');
    const json = await res.json();
    return json.data;
  },

  async getAdminCounters() {
    const res = await fetch(`${API_BASE_URL}/admin/counters`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Gagal memuat daftar ruangan admin');
    const json = await res.json();
    return json.data;
  },

  async createCounter(data: { poliklinik_id: number; nomor_bilik: string; nama_petugas: string; gelar_petugas?: string; status?: string }) {
    const res = await fetch(`${API_BASE_URL}/admin/counters`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.message || 'Gagal menambahkan ruangan');
    return json.data;
  },

  async updateCounter(id: number, data: Partial<{ poliklinik_id: number; nomor_bilik: string; nama_petugas: string; gelar_petugas?: string; status?: string }>) {
    const res = await fetch(`${API_BASE_URL}/admin/counters/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.message || 'Gagal memperbarui ruangan');
    return json.data;
  },

  async deleteCounter(id: number) {
    const res = await fetch(`${API_BASE_URL}/admin/counters/${id}`, {
      method: 'DELETE',
      headers: { Accept: 'application/json' },
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.message || 'Gagal menghapus ruangan');
    return json;
  },

  async getAdminPolikliniks() {
    const res = await fetch(`${API_BASE_URL}/admin/polikliniks`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Gagal memuat daftar poliklinik');
    const json = await res.json();
    return json.data;
  },

  async createPoliklinik(data: { kode: string; nama: string; nama_fonetik?: string; gedung_lantai: string; status?: string }) {
    const res = await fetch(`${API_BASE_URL}/admin/polikliniks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.message || 'Gagal menambahkan poliklinik');
    return json.data;
  },

  async updatePoliklinik(id: number, data: Partial<{ kode: string; nama: string; nama_fonetik?: string; gedung_lantai: string; status?: string }>) {
    const res = await fetch(`${API_BASE_URL}/admin/polikliniks/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.message || 'Gagal memperbarui poliklinik');
    return json.data;
  },

  async deletePoliklinik(id: number) {
    const res = await fetch(`${API_BASE_URL}/admin/polikliniks/${id}`, {
      method: 'DELETE',
      headers: { Accept: 'application/json' },
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.message || 'Gagal menghapus poliklinik');
    return json;
  },

  async getAdminSettings() {
    const res = await fetch(`${API_BASE_URL}/admin/settings`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Gagal memuat pengaturan sistem');
    const json = await res.json();
    return json.data;
  },

  async updateAdminSettings(data: { clinic_name?: string; running_text?: string; audio_chime?: string }) {
    const res = await fetch(`${API_BASE_URL}/admin/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.message || 'Gagal memperbarui pengaturan');
    return json.data;
  },

  async getAdminQueues() {
    const res = await fetch(`${API_BASE_URL}/admin/queues`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Gagal memuat antrean');
    const json = await res.json();
    return json.data;
  },

  async resetAdminQueues() {
    const res = await fetch(`${API_BASE_URL}/admin/queues/reset`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.message || 'Gagal mereset antrean');
    return json;
  },
};
