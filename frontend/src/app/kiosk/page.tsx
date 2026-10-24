'use client';

import React, { useEffect, useState } from 'react';
import {
  Ticket,
  Building2,
  CheckCircle,
  Printer,
  Sparkles,
  ShieldCheck,
  Coffee,
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

export default function KioskPage() {
  const [polikliniks, setPolikliniks] = useState<any[]>([]);
  const [selectedPoliId, setSelectedPoliId] = useState<number>(1);
  const [namaPasien, setNamaPasien] = useState<string>('');
  const [jenisPasien, setJenisPasien] = useState<'umum' | 'bpjs' | 'prioritas'>('umum');
  const [catatan, setCatatan] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [printedTicket, setPrintedTicket] = useState<any | null>(null);

  useEffect(() => {
    const fetchPolis = async () => {
      try {
        const polis = await apiClient.getPolikliniks();
        setPolikliniks(polis || []);
        if (polis && polis.length > 0) {
          setSelectedPoliId(polis[0].id);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchPolis();
  }, []);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!namaPasien.trim()) {
      alert('Silakan masukkan nama pasien');
      return;
    }

    setLoading(true);
    try {
      const ticket = await apiClient.takeTicket({
        poliklinik_id: selectedPoliId,
        nama_pasien: namaPasien,
        jenis_pasien: jenisPasien,
        catatan_khusus: catatan,
      });

      setPrintedTicket(ticket);
      setNamaPasien('');
      setCatatan('');
      setJenisPasien('umum');
    } catch (err: any) {
      alert(err.message || 'Gagal mendaftar antrean');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-900 flex flex-col font-sans select-none">
      {/* Top Header */}
      <header className="px-6 lg:px-8 py-3.5 bg-white border-b border-zinc-200 shadow-2xs flex items-center justify-between">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-zinc-900 flex items-center justify-center text-white shrink-0">
            <Ticket className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg lg:text-xl font-bold text-zinc-900 leading-tight">
              Anjungan Pendaftaran Mandiri (Kiosk)
            </h1>
            <p className="text-xs text-zinc-500 font-medium">
              Ambil tiket antrean poliklinik secara mandiri dan praktis
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-green-50 border border-green-200 text-green-700 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-green-600 animate-pulse" />
            <span>Kiosk Siap Melayani</span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 p-6 lg:p-8 max-w-5xl mx-auto w-full grid grid-cols-1 md:grid-cols-12 gap-6 items-start my-auto">
        {/* Left Form (7/12) */}
        <div className="md:col-span-7 bg-white border border-zinc-200 rounded-xl p-6 lg:p-7 shadow-2xs">
          <h2 className="text-base font-bold text-zinc-900 mb-0.5 flex items-center gap-2">
            <Building2 className="w-5 h-5 text-zinc-600" />
            Pilih Poliklinik & Data Pasien
          </h2>
          <p className="text-xs text-zinc-500 font-medium mb-4">
            Pilih poliklinik tujuan dan masukkan data pasien untuk mencetak nomor antrean.
          </p>

          {/* Jadwal Ishoma Notice */}
          <div className="mb-4 p-3 rounded-lg bg-amber-50/80 border border-amber-200 flex items-center gap-2.5 text-xs text-amber-900">
            <Coffee className="w-4 h-4 text-amber-700 shrink-0" />
            <span>
              <strong>Jadwal Ishoma (Istirahat & Sholat):</strong> Pukul 12:00 – 13:00 WIB. Tiket antrean yang Anda ambil tetap masuk sistem dan dipanggil saat sesi siang dibuka kembali.
            </span>
          </div>

          <form onSubmit={handleRegister} className="space-y-4">
            {/* 1. Pilih Poliklinik */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-700 mb-2">
                1. Pilih Layanan Poliklinik Tujuan
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {polikliniks.map((poli) => (
                  <button
                    key={poli.id}
                    type="button"
                    onClick={() => setSelectedPoliId(poli.id)}
                    className={`p-3.5 rounded-lg border transition-all cursor-pointer text-left flex flex-col justify-between ${
                      selectedPoliId === poli.id
                        ? 'bg-green-600 border-green-600 text-white shadow-xs ring-2 ring-green-600/30'
                        : 'bg-white border-zinc-200 text-zinc-900 hover:border-zinc-300'
                    }`}
                  >
                    <span
                      className={`text-[11px] font-mono font-semibold ${
                        selectedPoliId === poli.id ? 'text-zinc-300' : 'text-zinc-400'
                      }`}
                    >
                      {poli.kode}
                    </span>
                    <span className="font-bold text-sm mt-0.5">{poli.nama}</span>
                    <span
                      className={`text-[11px] font-medium mt-1 ${
                        selectedPoliId === poli.id ? 'text-zinc-200' : 'text-zinc-600'
                      }`}
                    >
                      {poli.gedung_lantai}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* 2. Nama Pasien */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-zinc-800 mb-1.5">
                2. Nama Lengkap Pasien
              </label>
              <input
                type="text"
                required
                value={namaPasien}
                onChange={(e) => setNamaPasien(e.target.value)}
                placeholder="Contoh: Muhammad Aria Sastra"
                className="w-full px-3.5 py-2.5 rounded-lg bg-white border border-zinc-200 text-zinc-950 placeholder-zinc-400 focus:outline-none focus:border-zinc-950 text-sm font-bold"
              />
            </div>

            {/* 3. Kategori Pasien */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-zinc-800 mb-2">
                3. Kategori Pasien / Penjamin
              </label>
              <div className="grid grid-cols-3 gap-2.5">
                {[
                  { id: 'umum', label: 'Umum / Mandiri', icon: ShieldCheck },
                  { id: 'bpjs', label: 'BPJS Kesehatan', icon: CheckCircle },
                  { id: 'prioritas', label: 'Prioritas (Lansia/Bumil)', icon: Sparkles },
                ].map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setJenisPasien(item.id as any)}
                    className={`py-2.5 px-2 rounded-lg border text-xs font-medium flex flex-col items-center justify-center gap-1 transition-all cursor-pointer ${
                      jenisPasien === item.id
                        ? 'bg-zinc-900 border-zinc-900 text-white shadow-2xs'
                        : 'bg-white border-zinc-200 text-zinc-700 hover:border-zinc-300'
                    }`}
                  >
                    <item.icon className="w-3.5 h-3.5" />
                    <span>{item.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* 4. Catatan Khusus */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-700 mb-1.5">
                4. Catatan Khusus / Keluhan (Opsional)
              </label>
              <input
                type="text"
                value={catatan}
                onChange={(e) => setCatatan(e.target.value)}
                placeholder="Misal: Memerlukan kursi roda / kontrol rutin"
                className="w-full px-3.5 py-2 rounded-lg bg-white border border-zinc-200 text-zinc-900 placeholder-zinc-400 focus:outline-none focus:border-zinc-900 text-xs font-medium"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 px-4 rounded-lg bg-green-600 hover:bg-green-700 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-xs transition-all cursor-pointer disabled:opacity-50"
            >
              <Printer className="w-4 h-4" />
              <span>{loading ? 'Mencetak Nomor Tiket...' : 'Ambil Nomor Antrean Sekarang'}</span>
            </button>
          </form>
        </div>

        {/* Right Section: Printed Ticket Preview (5/12) */}
        <div className="md:col-span-5 flex flex-col gap-4">
          <div className="bg-white text-zinc-900 rounded-xl p-6 shadow-2xs border border-zinc-200 flex flex-col items-center text-center">
            <div className="w-12 h-12 rounded-full bg-zinc-100 text-zinc-900 flex items-center justify-center mb-2.5 border border-zinc-200">
              <Printer className="w-6 h-6 text-zinc-800" />
            </div>

            <div className="text-[11px] font-mono font-extrabold tracking-widest uppercase text-zinc-800">
              Husada Medika Integrated Clinic
            </div>
            <div className="text-xs font-bold text-zinc-500">Struk Antrean Pasien</div>

            <div className="my-5 w-full border-t border-b border-dashed border-zinc-300 py-5">
              <div className="text-[11px] font-bold text-zinc-500 uppercase tracking-widest">
                NOMOR ANTREAN ANDA
              </div>
              <div className="text-6xl font-black font-mono text-zinc-950 tracking-tight my-2">
                {printedTicket?.nomor_antrean || '---'}
              </div>
              <div className="text-base font-extrabold text-zinc-950">
                {printedTicket?.poliklinik?.nama || 'Silakan Ambil Tiket'}
              </div>
            </div>

            <div className="w-full text-left text-xs space-y-2 text-zinc-700 font-medium">
              <div className="flex justify-between">
                <span className="text-zinc-400">Nama Pasien:</span>
                <strong className="text-zinc-900 font-semibold">{printedTicket?.nama_pasien || '-'}</strong>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-400">Kategori:</span>
                <span className="uppercase font-semibold text-zinc-900">
                  {printedTicket?.jenis_pasien || '-'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-400">Waktu Ambil:</span>
                <span className="text-zinc-900">
                  {printedTicket?.waktu_daftar
                    ? new Date(printedTicket.waktu_daftar).toLocaleTimeString('id-ID')
                    : '-'}
                </span>
              </div>
            </div>

            <div className="mt-5 text-[11px] text-zinc-400 font-medium italic text-center leading-relaxed">
              Harap menunggu di ruang tunggu poliklinik. Nomor Anda akan dipanggil melalui pengeras suara audio otomatis.
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
