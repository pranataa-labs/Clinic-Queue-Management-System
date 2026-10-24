'use client';

import React, { useEffect, useState, useRef } from 'react';
import {
  Volume2,
  VolumeX,
  Clock,
  Building2,
  Stethoscope,
  Activity,
  CheckCircle2,
  AlertCircle,
  Mic,
  Coffee,
} from 'lucide-react';
import { apiClient, DisplayStateResponse, PoliklinikItem } from '@/lib/api-client';
import { audioEngine } from '@/lib/audio-engine';
import { WebRtcIntercom } from '@/lib/webrtc-intercom';

export default function DisplayPage() {
  const [data, setData] = useState<DisplayStateResponse | null>(null);
  const [audioEnabled, setAudioEnabled] = useState<boolean>(false);
  const [isCallingVisual, setIsCallingVisual] = useState<boolean>(false);
  const [currentTime, setCurrentTime] = useState<string>('');
  const [activeRoomIndex, setActiveRoomIndex] = useState<number>(0);
  const [isLockedOnCall, setIsLockedOnCall] = useState<boolean>(false);
  const lastProcessedCallId = useRef<number | null>(null);

  // WebRTC Live Intercom State & Receiver
  const intercomRef = useRef<WebRtcIntercom | null>(null);
  const [intercomActive, setIntercomActive] = useState<{
    isActive: boolean;
    doctor_name?: string;
    room_name?: string;
    clinic_name?: string;
  } | null>(null);

  useEffect(() => {
    const intercom = new WebRtcIntercom();
    intercomRef.current = intercom;

    intercom.startListening((isActive, metadata) => {
      if (isActive) {
        audioEngine.cancelAll();
        setIsCallingVisual(false);
        setIntercomActive({
          isActive: true,
          doctor_name: metadata?.doctor_name,
          room_name: metadata?.room_name,
          clinic_name: metadata?.clinic_name,
        });
      } else {
        setIntercomActive(null);
      }
    });

    return () => {
      intercom.stopListening();
    };
  }, []);

  // Realtime Clock
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const datePart = now.toLocaleDateString('id-ID', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric',
      });
      const timePart = now.toLocaleTimeString('id-ID', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
      setCurrentTime(`${datePart}, ${timePart} WIB`);
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  // Poll Display State every 1.5 seconds
  useEffect(() => {
    const fetchData = async () => {
      try {
        const state = await apiClient.getDisplayState();
        setData(state);

        if (state.active_call && state.active_call.call_log_id !== lastProcessedCallId.current) {
          lastProcessedCallId.current = state.active_call.call_log_id;

          const calledIndex = state.polikliniks.findIndex(
            (p) => p.nama === state.active_call?.poliklinik || p.kode === state.active_call?.poliklinik
          );
          if (calledIndex !== -1) {
            setActiveRoomIndex(calledIndex);
          }

          setIsLockedOnCall(true);
          setIsCallingVisual(true);
          setTimeout(() => {
            setIsCallingVisual(false);
            setIsLockedOnCall(false);
          }, 8000);

          const callText =
            state.active_call.gemini_metadata?.call_script || state.active_call.teks_panggilan;
          const chimeType =
            state.active_call.gemini_metadata?.chime_tone || 'standard_bell';
          const repeatCount = state.active_call.gemini_metadata?.repeat_count || 1;

          if (audioEnabled && !intercomActive?.isActive) {
            audioEngine.enqueueAnnouncement({
              text: callText,
              chimeType,
              repeatCount,
              onStart: () => setIsCallingVisual(true),
              onEnd: () => setIsCallingVisual(false),
            });
          }
        }
      } catch (err) {
        console.warn('Gagal memuat status antrean:', err);
      }
    };

    fetchData();
    const pollTimer = setInterval(fetchData, 1500);
    return () => clearInterval(pollTimer);
  }, [audioEnabled, intercomActive]);

  const clinics: PoliklinikItem[] = data?.polikliniks || [];

  // Automatic Room Rotation
  useEffect(() => {
    if (isLockedOnCall || clinics.length === 0) return;

    const rotationTimer = setInterval(() => {
      setActiveRoomIndex((prev) => (prev + 1) % clinics.length);
    }, 5000);

    return () => clearInterval(rotationTimer);
  }, [isLockedOnCall, clinics.length]);

  const handleUnlockAudio = async () => {
    const success = await audioEngine.unlockAudio();
    if (success) {
      setAudioEnabled(true);
      audioEngine.playChime('standard_bell');
    }
  };

  const currentPoli = clinics[activeRoomIndex] || clinics[0];
  const currentQueue = currentPoli?.current_queue;
  const isExamining = currentQueue?.status === 'in_consultation';
  const isCalling = currentQueue?.status === 'calling';

  return (
    <div className="h-screen max-h-screen overflow-hidden bg-background text-foreground flex flex-col justify-between select-none relative font-sans">
      {/* Live Intercom Banner */}
      {intercomActive?.isActive && (
        <div className="absolute top-3 left-6 right-6 z-50 bg-zinc-900 text-white rounded-xl p-4 shadow-xl border border-zinc-700 flex items-center justify-between">
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-lg bg-rose-600 text-white flex items-center justify-center shrink-0 shadow-xs">
              <Mic className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
                <span className="text-[11px] font-semibold uppercase tracking-wider text-rose-300">
                  Siaran Langsung Mikrofon Dokter
                </span>
              </div>
              <div className="text-base lg:text-lg font-bold text-white mt-0.5">
                {intercomActive.doctor_name || 'Dokter Jaga'} &bull; {intercomActive.room_name || 'Ruangan Dokter'} ({intercomActive.clinic_name || 'Poliklinik'})
              </div>
            </div>
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-zinc-800 border border-zinc-700 text-zinc-300 font-medium text-xs">
            Suara Tersiar di Pengeras Suara
          </div>
        </div>
      )}

      {/* 1. Header Bar - Crisp White with Hairline Zinc Border */}
      <header className="px-6 py-3 bg-card border-b border-border shadow-2xs flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-green-600 flex items-center justify-center text-white shrink-0 shadow-xs">
            <Building2 className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg lg:text-xl font-bold tracking-tight text-foreground leading-tight">
              Poliklinik Terpadu Husada Medika
            </h1>
            <p className="text-xs text-muted-foreground font-medium flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-muted-foreground/80" />
              {currentTime || 'Memuat waktu...'}
            </p>
          </div>
        </div>

        {/* Header Actions */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={handleUnlockAudio}
            className={`px-3 py-1.5 rounded-lg border text-xs font-semibold flex items-center gap-2 transition-all cursor-pointer ${
              audioEnabled
                ? 'bg-green-50 border-green-200 text-green-700 hover:bg-green-100'
                : 'bg-zinc-900 border-zinc-900 text-white hover:bg-zinc-800 shadow-xs'
            }`}
          >
            {audioEnabled ? (
              <>
                <Volume2 className="w-3.5 h-3.5 text-green-600" />
                <span>Audio Aktif</span>
              </>
            ) : (
              <>
                <VolumeX className="w-3.5 h-3.5 text-zinc-300" />
                <span>Aktifkan Audio</span>
              </>
            )}
          </button>
        </div>
      </header>

      {/* 2. Main Desktop Grid */}
      <main className="flex-1 min-h-0 p-4 lg:p-6 grid grid-cols-12 gap-5 lg:gap-6 items-stretch overflow-hidden">
        {/* Left Column (7/12): HERO CARD */}
        <section className="col-span-12 lg:col-span-7 flex flex-col h-full min-h-0">
          <div className="flex-1 min-h-0 rounded-2xl bg-card border border-border p-6 lg:p-8 flex flex-col justify-between shadow-xs relative overflow-hidden">
            {/* Top Row: Status Badge & 5 Room Selector Tabs */}
            <div className="flex items-center justify-between pb-3 border-b border-border/60 shrink-0">
              {/* Status Badge */}
              <div>
                {(currentPoli as any)?.counter_status === 'break' ? (
                  <span className="px-3 py-1 rounded-md bg-amber-50 text-amber-900 border border-amber-300 font-bold text-xs flex items-center gap-1.5 animate-pulse">
                    <Coffee className="w-3.5 h-3.5 text-amber-700" />
                    Sedang Istirahat & Sholat (Ishoma)
                  </span>
                ) : isExamining ? (
                  <span className="px-3 py-1 rounded-md bg-green-50 text-green-700 border border-green-200 font-semibold text-xs flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-green-600" />
                    Sedang Diperiksa di Ruangan
                  </span>
                ) : isCalling ? (
                  <span className="px-3 py-1 rounded-md bg-amber-50 text-amber-800 border border-amber-200 font-semibold text-xs flex items-center gap-1.5">
                    <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                    Panggilan Aktif Menuju Ruangan
                  </span>
                ) : (
                  <span className="px-3 py-1 rounded-md bg-muted text-muted-foreground border border-border font-medium text-xs">
                    Menunggu Panggilan Dokter
                  </span>
                )}
              </div>

              {/* Room 1 to 5 Quick Tabs */}
              <div className="flex items-center gap-1 bg-muted p-1 rounded-lg border border-border/80">
                {clinics.map((p, idx) => (
                  <button
                    key={p.id}
                    onClick={() => {
                      setActiveRoomIndex(idx);
                      setIsLockedOnCall(true);
                      setTimeout(() => setIsLockedOnCall(false), 7000);
                    }}
                    className={`px-2.5 py-1 rounded-md text-xs font-semibold transition-all cursor-pointer ${
                      activeRoomIndex === idx
                        ? 'bg-primary text-primary-foreground shadow-2xs'
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    Ruangan {idx + 1}
                  </button>
                ))}
              </div>
            </div>

            {/* Giant Number & Poliklinik Destination */}
            <div className="my-auto text-center flex flex-col items-center justify-center py-4">
              <span className="text-xs font-bold tracking-widest text-muted-foreground uppercase mb-1">
                NOMOR ANTREAN
              </span>

              {/* Giant Crisp Number */}
              <div className="text-7xl sm:text-8xl md:text-9xl font-black tracking-tight text-foreground font-mono leading-none my-2">
                {currentQueue?.nomor_antrean || '---'}
              </div>

              {/* Destination Poliklinik */}
              <div className="mt-3 flex flex-col items-center">
                <span className="text-xs font-bold tracking-wider text-muted-foreground uppercase">
                  SILAKAN MENUJU KE
                </span>
                <div className="text-3xl sm:text-4xl lg:text-5xl font-black text-foreground mt-1 tracking-tight">
                  {currentPoli?.nama || 'Poliklinik'}
                </div>
              </div>
            </div>

            {/* Fixed Bottom Bar: Ruangan di Pojok Kiri & Nama Dokter di Pojok Kanan */}
            <div className="w-full flex items-center justify-between pt-3 pb-1 border-t border-border/60 shrink-0">
              <span className="px-3 py-1 bg-muted rounded-md border border-border text-foreground font-extrabold text-sm lg:text-base">
                Ruangan {activeRoomIndex + 1}
              </span>

              <div className="flex items-center gap-2 text-foreground/90 font-bold text-sm lg:text-base">
                <Stethoscope className="w-4 h-4 text-green-600 shrink-0" />
                <span>{currentQueue?.nama_petugas || 'Dokter Jaga'}</span>
              </div>
            </div>

            {/* Bottom Rotator Progress */}
            <div className="pt-2 border-t border-border/60 flex items-center justify-between text-xs text-muted-foreground font-semibold shrink-0">
              <span>Rotasi antrean otomatis untuk seluruh poliklinik</span>
              <span className="font-mono text-foreground/90 bg-muted px-2 py-0.5 rounded border border-border font-bold">
                Ruangan {activeRoomIndex + 1} dari {clinics.length || 5}
              </span>
            </div>
          </div>
        </section>

        {/* Right Column (5/12): 5 RUANGAN POLIKLINIK LIST */}
        <section className="col-span-12 lg:col-span-5 flex flex-col h-full min-h-0">
          <div className="flex items-center justify-between pb-2 border-b border-border shrink-0 mb-2.5">
            <h2 className="text-base font-bold text-foreground flex items-center gap-2">
              <Activity className="w-4 h-4 text-green-600" />
              <span>Daftar Antrean Ruangan</span>
            </h2>
            <span className="text-xs font-medium text-muted-foreground bg-muted px-2.5 py-0.5 rounded-md border border-border">
              {clinics.length} Ruangan Aktif
            </span>
          </div>

          {/* 5 Distinct Rooms */}
          <div className="flex-1 min-h-0 flex flex-col justify-between gap-2 overflow-hidden">
            {clinics.map((poli, idx) => {
              const current = poli.current_queue;
              const nextQ = poli.next_queue;
              const isSelected = activeRoomIndex === idx;

              return (
                <div
                  key={poli.id}
                  onClick={() => {
                    setActiveRoomIndex(idx);
                    setIsLockedOnCall(true);
                    setTimeout(() => setIsLockedOnCall(false), 7000);
                  }}
                  className={`px-4 py-2.5 rounded-xl border transition-all flex items-center justify-between shadow-2xs flex-1 min-h-0 overflow-hidden cursor-pointer ${
                    isSelected
                      ? 'bg-card border-2 border-primary shadow-xs'
                      : 'bg-card border-border hover:border-zinc-300'
                  }`}
                >
                  {/* Left Side */}
                  <div className="flex-1 pr-3 min-w-0 flex flex-col justify-between h-full">
                    {/* Top Row: Status Sedang Diperiksa / Istirahat */}
                    <div className="flex items-center gap-2">
                      {(poli as any)?.counter_status === 'break' ? (
                        <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-900 border border-amber-200 font-bold text-[10px] uppercase tracking-wider flex items-center gap-1 shrink-0">
                          <Coffee className="w-3 h-3 text-amber-700" />
                          Istirahat (Ishoma)
                        </span>
                      ) : current ? (
                        <>
                          <span className="px-2 py-0.5 rounded bg-green-50 text-green-700 border border-green-200 font-semibold text-[10px] uppercase tracking-wider flex items-center gap-1 shrink-0">
                            <CheckCircle2 className="w-3 h-3 text-green-600" />
                            Sedang Diperiksa
                          </span>
                          <span className="font-mono font-bold text-foreground text-base leading-none">
                            {current.nomor_antrean}
                          </span>
                        </>
                      ) : (
                        <span className="px-2 py-0.5 rounded bg-muted text-muted-foreground font-medium text-[10px] uppercase tracking-wider border border-border">
                          Ruangan Kosong
                        </span>
                      )}
                    </div>

                    {/* Bottom Row: Ruangan & Nama Poli */}
                    <div className="flex items-center gap-2 min-w-0 mt-1">
                      <span className="text-[11px] font-mono px-1.5 py-0.5 rounded bg-muted text-foreground font-bold border border-border shrink-0">
                        Ruangan {idx + 1}
                      </span>
                      <h3 className="font-extrabold text-foreground text-sm truncate">
                        {poli.nama}
                      </h3>
                    </div>
                  </div>

                  {/* Right Side: Antrean Berikutnya */}
                  <div className="text-right pl-3 border-l border-border/60 min-w-[130px] shrink-0 flex flex-col items-end justify-between h-full">
                    <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-900 border border-amber-200 font-bold text-[10px] uppercase tracking-wider flex items-center gap-1">
                      <Clock className="w-3 h-3 text-amber-700" />
                      Berikutnya
                    </span>

                    <div className="text-2xl font-black text-foreground font-mono tracking-tight leading-none mt-1">
                      {nextQ?.nomor_antrean || '---'}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </main>

      {/* 3. Bottom Running Text Ticker */}
      <footer className="h-10 bg-zinc-900 text-zinc-100 flex items-center overflow-hidden px-6 border-t border-zinc-800 shrink-0 z-10">
        <div className="bg-green-600 text-white px-2.5 py-0.5 rounded text-xs font-bold mr-4 whitespace-nowrap uppercase tracking-wider shrink-0 shadow-xs">
          PENGUMUMAN
        </div>
        <div className="flex-1 overflow-hidden relative">
          <div className="animate-marquee font-medium text-zinc-100 text-xs lg:text-sm">
            Selamat datang di Poliklinik Terpadu Husada Medika, harap memperhatikan nomor antrean pada layar display dan menyiapkan berkas BPJS serta kartu identitas Anda — Bagi pasien prioritas lansia, ibu hamil, dan balita, silakan menghubungi petugas jika memerlukan bantuan kursi roda — Budayakan tertib antre demi kenyamanan dan kelancaran pelayanan bersama.
          </div>
        </div>
      </footer>
    </div>
  );
}
