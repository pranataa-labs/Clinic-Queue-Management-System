'use client';

import React, { useEffect, useState, useRef, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  Stethoscope,
  Mic,
  MicOff,
  UserCheck,
  SkipForward,
  Play,
  RotateCcw,
  CheckCircle2,
  Users,
  Sparkles,
  History,
  Clock,
  RefreshCw,
  Lock,
  LogOut,
  MapPin,
  ArrowRight,
  ShieldCheck,
  AlertCircle,
  Coffee,
} from 'lucide-react';
import { apiClient, QueueItem, RecentCallItem } from '@/lib/api-client';
import { audioEngine } from '@/lib/audio-engine';
import { WebRtcIntercom } from '@/lib/webrtc-intercom';

function ConsoleContent() {
  const searchParams = useSearchParams();
  const counterParam = searchParams.get('counter') || searchParams.get('room');

  const [counters, setCounters] = useState<any[]>([]);
  const [activeDoctor, setActiveDoctor] = useState<any | null>(null);
  const [isInitializing, setIsInitializing] = useState<boolean>(true);

  const [waitingList, setWaitingList] = useState<QueueItem[]>([]);
  const [currentQueue, setCurrentQueue] = useState<QueueItem | null>(null);
  const [recentCompleted, setRecentCompleted] = useState<QueueItem[]>([]);
  const [recentCalls, setRecentCalls] = useState<RecentCallItem[]>([]);
  const [loadingAction, setLoadingAction] = useState<boolean>(false);
  const [lastAnnouncement, setLastAnnouncement] = useState<string>('');

  // WebRTC Intercom state & Safety Countdown
  const [isBroadcasting, setIsBroadcasting] = useState<boolean>(false);
  const [intercomStatus, setIntercomStatus] = useState<string>('Siap');
  const [micCountdown, setMicCountdown] = useState<number>(30);
  const [isOnBreak, setIsOnBreak] = useState<boolean>(false);
  const intercomRef = useRef<WebRtcIntercom | null>(null);
  const micTimerRef = useRef<NodeJS.Timeout | null>(null);

  // 1. Load All Counters & Resolve Doctor Session
  useEffect(() => {
    const initMaster = async () => {
      try {
        const countersData = await apiClient.getCounters();
        setCounters(countersData || []);

        const savedCounterId = localStorage.getItem('husada_active_doctor_counter_id');
        const targetId = counterParam ? Number(counterParam) : savedCounterId ? Number(savedCounterId) : null;

        if (targetId && countersData?.length > 0) {
          const matched = countersData.find((c: any) => c.id === targetId);
          if (matched) {
            setActiveDoctor(matched);
            setIsOnBreak(matched.status === 'break');
            localStorage.setItem('husada_active_doctor_counter_id', String(matched.id));
          }
        }
      } catch (err) {
        console.error('Error fetching counters:', err);
      } finally {
        setIsInitializing(false);
      }
    };
    initMaster();
  }, [counterParam]);

  // Handle Doctor Room Selection
  const handleSelectDoctor = (counter: any) => {
    setActiveDoctor(counter);
    setIsOnBreak(counter.status === 'break');
    localStorage.setItem('husada_active_doctor_counter_id', String(counter.id));
  };

  // Handle Doctor Logout / Session Exit
  const handleLogoutDoctor = () => {
    if (confirm(`Apakah Anda ingin keluar dari sesi ${activeDoctor?.nama_petugas} (${activeDoctor?.nomor_bilik})?`)) {
      stopIntercom();
      localStorage.removeItem('husada_active_doctor_counter_id');
      setActiveDoctor(null);
      setCurrentQueue(null);
      setWaitingList([]);
    }
  };

  // Toggle Break / Ishoma Mode
  const handleToggleBreak = async () => {
    if (!activeDoctor) return;
    const newStatus = isOnBreak ? 'active' : 'break';
    setLoadingAction(true);
    try {
      if (isBroadcasting) stopIntercom();
      await apiClient.toggleBreak(activeDoctor.id, newStatus);
      setIsOnBreak(newStatus === 'break');
      setActiveDoctor((prev: any) => (prev ? { ...prev, status: newStatus } : null));
      await loadQueues();
    } catch (err: any) {
      alert(err.message || 'Gagal mengubah status istirahat');
    } finally {
      setLoadingAction(false);
    }
  };

  // 2. Poll Queues for Active Doctor's Room Only
  const loadQueues = async () => {
    if (!activeDoctor) return;
    try {
      const data = await apiClient.getClinicQueues(activeDoctor.poliklinik_id);
      setWaitingList(data.waiting || []);
      setRecentCompleted(data.recent_completed || []);

      const active = (data.calling_or_active || []).find(
        (q: QueueItem) => q.counter_id === activeDoctor.id || !q.counter_id
      );
      setCurrentQueue(active || null);

      const displayData = await apiClient.getDisplayState();
      setRecentCalls(displayData.recent_calls || []);
    } catch (err) {
      console.warn('Gagal refresh antrean:', err);
    }
  };

  useEffect(() => {
    if (!activeDoctor) return;
    loadQueues();
    const interval = setInterval(loadQueues, 1500);
    return () => clearInterval(interval);
  }, [activeDoctor]);

  // Stop Intercom Helper
  const stopIntercom = (reason?: string) => {
    if (micTimerRef.current) {
      clearInterval(micTimerRef.current);
      micTimerRef.current = null;
    }
    if (intercomRef.current) {
      intercomRef.current.stopBroadcasting();
      intercomRef.current = null;
    }
    setIsBroadcasting(false);
    setIntercomStatus(reason || 'Mati');
  };

  // Start Intercom with Anti-Lupa 30s Countdown & Metadata
  const startIntercom = async () => {
    if (!activeDoctor) return;
    audioEngine.cancelAll();

    try {
      const intercom = new WebRtcIntercom();
      intercomRef.current = intercom;
      setIsBroadcasting(true);
      setIntercomStatus('Menghubungkan...');
      setMicCountdown(30);

      const roomName = activeDoctor.nomor_bilik?.replace('Bilik', 'Ruangan') || `Ruangan ${activeDoctor.id}`;
      const poliName = activeDoctor.poliklinik?.nama || 'Poliklinik';

      await intercom.startBroadcasting(
        {
          doctor_name: activeDoctor.nama_petugas,
          room_name: roomName,
          clinic_name: poliName,
        },
        (status) => {
          setIntercomStatus(status);
        }
      );

      if (micTimerRef.current) clearInterval(micTimerRef.current);
      micTimerRef.current = setInterval(() => {
        setMicCountdown((prev) => {
          if (prev <= 1) {
            stopIntercom('Otomatis dimatikan (30s) - Privasi terjaga');
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } catch {
      stopIntercom('Gagal membuka mikrofon');
    }
  };

  // Toggle Intercom
  const toggleIntercom = async () => {
    if (isBroadcasting) {
      stopIntercom('Dimatikan oleh dokter');
    } else {
      await startIntercom();
    }
  };

  // Call Next
  const handleCallNext = async () => {
    if (!activeDoctor) return;
    setLoadingAction(true);
    try {
      if (isBroadcasting) {
        stopIntercom('Dimatikan otomatis untuk memutar pengumuman');
        await new Promise((r) => setTimeout(r, 350));
      }

      await audioEngine.unlockAudio();
      const res = await apiClient.callNext(activeDoctor.id);
      if (res?.queue) {
        setCurrentQueue(res.queue);
      }
      setLastAnnouncement(res.announcement?.call_script || '');
      audioEngine.enqueueAnnouncement({
        text: res.announcement?.call_script,
        chimeType: res.announcement?.chime_tone,
        repeatCount: 1,
      });
      await loadQueues();
    } catch (err: any) {
      alert(err.message || 'Gagal memanggil antrean');
    } finally {
      setLoadingAction(false);
    }
  };

  // Recall
  const handleRecall = async () => {
    if (!currentQueue || !activeDoctor) return;
    setLoadingAction(true);
    try {
      if (isBroadcasting) {
        stopIntercom('Dimatikan otomatis untuk memutar pengumuman');
        await new Promise((r) => setTimeout(r, 350));
      }

      await audioEngine.unlockAudio();
      const res = await apiClient.recall(currentQueue.id, activeDoctor.id);
      if (res?.queue) {
        setCurrentQueue(res.queue);
      }
      setLastAnnouncement(res.announcement?.call_script || '');
      audioEngine.enqueueAnnouncement({
        text: res.announcement?.call_script,
        chimeType: res.announcement?.chime_tone,
        repeatCount: 1,
      });
      await loadQueues();
    } catch (err: any) {
      alert(err.message || 'Gagal memanggil ulang');
    } finally {
      setLoadingAction(false);
    }
  };

  // Start Consultation
  const handleStartConsultation = async () => {
    if (!currentQueue) return;
    if (isBroadcasting) {
      stopIntercom('Dimatikan saat konsultasi dimulai');
    }

    setLoadingAction(true);
    try {
      setCurrentQueue((prev) => (prev ? { ...prev, status: 'in_consultation' } : null));
      await apiClient.startConsultation(currentQueue.id);
      await loadQueues();
    } catch (err: any) {
      alert(err.message || 'Gagal memulai pemeriksaan');
      await loadQueues();
    } finally {
      setLoadingAction(false);
    }
  };

  // Skip
  const handleSkip = async () => {
    if (!currentQueue) return;
    if (!confirm('Apakah pasien benar-benar tidak hadir dan ingin dilewati?')) return;
    if (isBroadcasting) stopIntercom();

    setLoadingAction(true);
    try {
      setCurrentQueue(null);
      await apiClient.skip(currentQueue.id);
      await loadQueues();
    } catch (err: any) {
      alert(err.message);
      await loadQueues();
    } finally {
      setLoadingAction(false);
    }
  };

  // Complete
  const handleComplete = async () => {
    if (!currentQueue) return;
    if (isBroadcasting) stopIntercom();

    setLoadingAction(true);
    try {
      setCurrentQueue(null);
      await apiClient.complete(currentQueue.id);
      await loadQueues();
    } catch (err: any) {
      alert(err.message);
      await loadQueues();
    } finally {
      setLoadingAction(false);
    }
  };

  // LOADING STATE
  if (isInitializing) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6 text-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-zinc-900 flex items-center justify-center text-white shadow-xs animate-pulse">
            <Stethoscope className="w-5 h-5" />
          </div>
          <span className="font-semibold text-foreground/90 text-sm">Menyiapkan Konsol Dokter...</span>
        </div>
      </div>
    );
  }

  // SCREEN 1: DOCTOR LOGIN / ROOM ASSIGNMENT GATE
  if (!activeDoctor) {
    return (
      <div className="min-h-screen bg-background text-foreground flex flex-col font-sans select-none">
        {/* Top Simple Bar */}
        <header className="px-6 lg:px-8 py-3.5 bg-card border-b border-border flex items-center justify-between shadow-2xs">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-zinc-900 flex items-center justify-center text-white shrink-0">
              <Stethoscope className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-base font-bold text-foreground leading-tight">Konsol Dokter Husada Medika</h1>
              <p className="text-xs text-muted-foreground font-medium">Pemilihan Ruangan & Autentikasi Tugas</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs px-2.5 py-1 rounded-md bg-muted border border-border text-muted-foreground font-medium flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-muted-foreground" />
              Sesi Tenaga Medis
            </span>
          </div>
        </header>

        {/* Doctor Selection Grid */}
        <main className="flex-1 max-w-5xl mx-auto w-full p-6 lg:p-10 flex flex-col justify-center">
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-muted text-foreground/90 border border-border text-xs font-semibold mb-3">
              <ShieldCheck className="w-3.5 h-3.5 text-muted-foreground" />
              Akses Terisolasi Per Ruangan
            </div>
            <h2 className="text-2xl lg:text-3xl font-bold text-foreground tracking-tight">
              Pilih Profil Dokter & Ruangan Anda
            </h2>
            <p className="text-sm text-muted-foreground mt-1 max-w-md mx-auto font-medium">
              Setiap dokter hanya dapat mengakses, melihat antrean, dan memanggil pasien di ruangannya sendiri.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {counters.map((c: any) => {
              const roomName = c.nomor_bilik?.replace('Bilik', 'Ruangan') || `Ruangan ${c.id}`;
              const poliName = c.poliklinik?.nama || 'Poliklinik';
              const poliCode = c.poliklinik?.kode || '-';
              const floor = c.poliklinik?.gedung_lantai || 'Lantai 1';

              return (
                <div
                  key={c.id}
                  onClick={() => handleSelectDoctor(c)}
                  className="bg-card rounded-xl border border-border hover:border-zinc-400 p-5 shadow-xs hover:shadow-sm transition-all cursor-pointer flex flex-col justify-between group"
                >
                  <div>
                    <div className="flex items-center justify-between pb-3 border-b border-border/60">
                      <span className="text-xs font-bold text-foreground bg-muted border border-border px-2.5 py-0.5 rounded-md">
                        {roomName}
                      </span>
                      <span className="text-[11px] font-mono font-medium text-muted-foreground">
                        {poliCode}
                      </span>
                    </div>

                    <div className="pt-3.5 flex flex-col gap-0.5">
                      <h3 className="text-base font-bold text-foreground group-hover:text-foreground/90 transition-colors">
                        {c.nama_petugas}
                      </h3>
                      <p className="text-xs font-medium text-muted-foreground">
                        {c.gelar_petugas || 'Dokter Spesialis'}
                      </p>
                      <p className="text-xs font-semibold text-foreground/90 mt-1">
                        {poliName}
                      </p>
                      <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground/80 mt-2">
                        <MapPin className="w-3.5 h-3.5" />
                        <span>{floor}</span>
                      </div>
                    </div>
                  </div>

                  <div className="pt-4 mt-4 border-t border-border/60">
                    <div className="w-full py-2 px-3 rounded-lg bg-primary group-hover:bg-primary/90 text-primary-foreground shadow-2xs font-semibold text-xs flex items-center justify-center gap-1.5 transition-all shadow-xs">
                      <span>Masuk ke {roomName}</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </main>
      </div>
    );
  }

  // SCREEN 2: ACTIVE DOCTOR DEDICATED CONSOLE
  const roomDisplayName = activeDoctor.nomor_bilik?.replace('Bilik', 'Ruangan') || `Ruangan ${activeDoctor.id}`;
  const poliDisplayName = activeDoctor.poliklinik?.nama || 'Poliklinik';

  return (
    <div className="min-h-screen bg-background text-foreground flex font-sans select-none">
      {/* SISI KIRI: Dedicated Doctor Sidebar */}
      <aside className="w-64 lg:w-72 bg-card border-r border-border flex flex-col justify-between shrink-0 h-screen sticky top-0 p-4 shadow-2xs z-20">
        <div className="flex flex-col gap-4 overflow-y-auto">
          {/* Logo & Brand Header */}
          <div className="flex items-center gap-3 px-2 py-1">
            <div className="w-9 h-9 rounded-lg bg-zinc-900 flex items-center justify-center text-white shrink-0">
              <Stethoscope className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-foreground tracking-tight leading-tight">
                Konsol Dokter
              </h1>
              <p className="text-[11px] font-medium text-muted-foreground">
                Husada Medika
              </p>
            </div>
          </div>

          {/* Dedicated Doctor Profile Card (Locked Room) */}
          <div className="border border-border rounded-xl p-3.5 bg-background/70 flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] px-2 py-0.5 rounded-md font-semibold bg-green-50 text-green-700 border border-green-200 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-green-600 animate-pulse" />
                Sedang Bertugas
              </span>
              <span className="text-[10px] px-1.5 py-0.5 rounded font-mono font-medium bg-card text-muted-foreground border border-border">
                {activeDoctor.poliklinik?.kode}
              </span>
            </div>

            <div>
              <h2 className="text-sm font-bold text-foreground leading-tight">
                {activeDoctor.nama_petugas}
              </h2>
              <p className="text-[11px] font-medium text-muted-foreground">
                {activeDoctor.gelar_petugas}
              </p>
            </div>

            <div className="pt-2 border-t border-border/60 flex flex-col gap-1 text-[11px]">
              <div className="flex items-center justify-between font-semibold">
                <span className="text-muted-foreground">Ruangan:</span>
                <span className="text-foreground font-bold">{roomDisplayName}</span>
              </div>
              <div className="flex items-center justify-between font-medium">
                <span className="text-muted-foreground">Poli:</span>
                <span className="text-foreground/90 truncate max-w-[130px]">{poliDisplayName}</span>
              </div>
            </div>

            {/* Lock isolation badge */}
            <div className="mt-1 p-2 rounded-lg bg-card border border-border flex items-center gap-2 text-[10px] font-medium text-muted-foreground">
              <Lock className="w-3.5 h-3.5 shrink-0 text-muted-foreground/80" />
              <span>Akses Khusus {roomDisplayName}</span>
            </div>
          </div>

          {/* Shift Queue Statistics */}
          <div className="grid grid-cols-2 gap-2">
            <div className="p-2.5 rounded-lg bg-card border border-border text-center">
              <span className="text-[10px] font-medium text-muted-foreground uppercase block">Menunggu</span>
              <span className="text-lg font-bold text-foreground font-mono">{waitingList.length}</span>
            </div>
            <div className="p-2.5 rounded-lg bg-card border border-border text-center">
              <span className="text-[10px] font-medium text-muted-foreground uppercase block">Selesai</span>
              <span className="text-lg font-bold text-green-700 font-mono">{recentCompleted.length}</span>
            </div>
          </div>

          {/* Exit / Switch Doctor Button */}
          <button
            onClick={handleLogoutDoctor}
            className="w-full py-2 px-3 rounded-lg border border-border hover:border-zinc-300 bg-card hover:bg-background text-muted-foreground text-xs font-medium transition-all flex items-center justify-center gap-1.5 cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
            Keluar / Ganti Dokter
          </button>
        </div>

        {/* Dedicated System Footer */}
        <div className="border-t border-border pt-3 flex flex-col gap-1 text-[11px] text-muted-foreground/80">
          <div className="flex items-center justify-between font-medium">
            <span>Sistem Konsol Dokter</span>
            <span className="font-mono text-muted-foreground">v1.0</span>
          </div>
          <p className="text-[10px] text-muted-foreground/80">Husada Medika Center</p>
        </div>
      </aside>

      {/* SISI KANAN: Dedicated Console Workspace */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto">
        {/* Sleek Top Header */}
        <header className="px-6 lg:px-8 py-3.5 bg-card border-b border-border flex items-center justify-between sticky top-0 z-10 shadow-2xs">
          <div>
            <h2 className="text-base lg:text-lg font-bold text-foreground flex items-center gap-2">
              <span>{roomDisplayName}</span>
              <span className="text-zinc-300">&bull;</span>
              <span className="text-muted-foreground font-semibold">{poliDisplayName}</span>
            </h2>
            <p className="text-xs text-muted-foreground font-medium">
              Dokter Jaga: <strong className="text-foreground font-semibold">{activeDoctor.nama_petugas}</strong> ({activeDoctor.gelar_petugas})
            </p>
          </div>

          <div className="flex items-center gap-2">
            {/* Jeda Istirahat / Ishoma Toggle */}
            <button
              onClick={handleToggleBreak}
              disabled={loadingAction}
              className={`px-3 py-1.5 rounded-lg font-semibold text-xs flex items-center gap-1.5 transition-all cursor-pointer border ${
                isOnBreak
                  ? 'bg-amber-600 hover:bg-amber-700 text-white border-amber-600 shadow-xs'
                  : 'bg-card hover:bg-amber-50 text-amber-900 border-amber-300'
              }`}
            >
              <Coffee className="w-3.5 h-3.5" />
              <span>{isOnBreak ? 'Mode Istirahat Aktif' : 'Jeda Istirahat / Ishoma'}</span>
            </button>

            {/* Interactive Intercom Button */}
            <button
              onClick={toggleIntercom}
              className={`px-3 py-1.5 rounded-lg font-medium text-xs flex items-center gap-1.5 transition-all cursor-pointer border ${
                isBroadcasting
                  ? 'bg-rose-600 hover:bg-rose-700 text-white border-rose-600 animate-pulse'
                  : 'bg-card hover:bg-background text-foreground/90 border-border'
              }`}
            >
              {isBroadcasting ? (
                <>
                  <MicOff className="w-3.5 h-3.5" />
                  <span>Mic Aktif ({micCountdown}s) - Klik Matikan</span>
                </>
              ) : (
                <>
                  <Mic className="w-3.5 h-3.5 text-muted-foreground" />
                  <span>Bicara di Speaker TV (Mic)</span>
                </>
              )}
            </button>

            {/* Refresh Button */}
            <button
              onClick={loadQueues}
              className="p-1.5 rounded-lg bg-card hover:bg-muted text-muted-foreground border border-border cursor-pointer transition-colors"
              title="Refresh Antrean"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>
        </header>

        {/* Content Area */}
        <main className="p-6 lg:p-8 flex flex-col gap-5">
          {/* BANNER MODE ISTIRAHAT */}
          {isOnBreak && (
            <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 flex flex-col md:flex-row items-center justify-between gap-3 shadow-xs">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-amber-600 text-white flex items-center justify-center font-bold shrink-0 shadow-xs">
                  <Coffee className="w-4 h-4" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold uppercase text-amber-900 tracking-wider">
                      RUANGAN SEDANG DALAM MODE JEDA / ISTIRAHAT & SHOLAT (ISHOMA)
                    </span>
                  </div>
                  <p className="text-xs text-amber-800 font-medium mt-0.5">
                    Layar display TV ruang tunggu menampilkan informasi jeda ini. Panggilan antrean dihentikan sementara.
                  </p>
                </div>
              </div>

              <button
                onClick={handleToggleBreak}
                className="px-3.5 py-1.5 rounded-lg bg-green-600 hover:bg-green-700 text-white text-xs font-bold flex items-center gap-1.5 shadow-xs cursor-pointer shrink-0 transition-colors"
              >
                <span>Lanjutkan Pelayanan Dokter</span>
              </button>
            </div>
          )}

          {/* BANNER MIKROFON AKTIF */}
          {isBroadcasting && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 flex flex-col md:flex-row items-center justify-between gap-3 shadow-xs">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-rose-600 text-white flex items-center justify-center font-bold shrink-0">
                  <Mic className="w-4 h-4 animate-pulse" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-rose-600 animate-ping" />
                    <span className="text-xs font-bold uppercase text-rose-900 tracking-wider">
                      SIARAN MIKROFON LANGSUNG AKTIF DI SPEAKER TV
                    </span>
                    <span className="font-mono font-bold text-xs px-2 py-0.5 rounded bg-rose-600 text-white">
                      Auto-Off: {micCountdown}s
                    </span>
                  </div>
                  <p className="text-xs text-rose-700 font-medium mt-0.5">
                    Suara Anda saat ini terdengar di seluruh ruang tunggu. Panggilan otomatis dijeda untuk menghindari tabrakan audio.
                  </p>
                </div>
              </div>

              <button
                onClick={() => stopIntercom('Dimatikan oleh dokter')}
                className="px-3.5 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold flex items-center gap-1.5 shadow-xs cursor-pointer shrink-0 transition-colors"
              >
                <MicOff className="w-3.5 h-3.5" />
                <span>Matikan Mic Sekarang</span>
              </button>
            </div>
          )}

          {/* Grid Utama (5/12 & 7/12) */}
          <div className="grid grid-cols-12 gap-5 lg:gap-6">
            {/* Left Column (5/12): Current Patient & Controls */}
            <div className="col-span-12 lg:col-span-5 flex flex-col gap-5">
              {/* Active Patient Card */}
              <div className="rounded-xl bg-card border border-border p-6 flex flex-col justify-between shadow-2xs">
                <div className="flex items-center justify-between pb-3 border-b border-border/60">
                  <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-zinc-400" />
                    Pasien di Ruangan
                  </span>
                  <span
                    className={`text-xs px-2.5 py-0.5 rounded-md font-semibold border ${
                      currentQueue?.status === 'in_consultation'
                        ? 'bg-green-50 text-green-700 border-green-200'
                        : currentQueue?.status === 'calling'
                        ? 'bg-amber-50 text-amber-800 border-amber-200'
                        : 'bg-muted text-muted-foreground border-border'
                    }`}
                  >
                    {currentQueue?.status === 'in_consultation'
                      ? 'Sedang Diperiksa'
                      : currentQueue?.status === 'calling'
                      ? 'Sedang Dipanggil'
                      : 'Ruangan Kosong'}
                  </span>
                </div>

                {/* Patient Info */}
                <div className="py-6 text-center">
                  <div className="text-6xl lg:text-7xl font-black text-foreground tracking-tight font-mono">
                    {currentQueue?.nomor_antrean || '---'}
                  </div>
                  <div className="text-xl font-extrabold text-foreground mt-2">
                    {currentQueue?.nama_pasien || 'Belum Ada Pasien'}
                  </div>
                  {currentQueue && (
                    <div className="mt-2.5 flex items-center justify-center gap-2">
                      <span className="text-xs px-2 py-0.5 rounded bg-muted border border-border text-foreground/90 font-semibold uppercase">
                        Kategori: {currentQueue.jenis_pasien}
                      </span>
                      <span className="text-xs px-2 py-0.5 rounded bg-background border border-border text-muted-foreground font-medium">
                        Panggilan Ke-{currentQueue.call_count}
                      </span>
                    </div>
                  )}
                  {currentQueue?.catatan_khusus && (
                    <div className="mt-3 p-2.5 rounded-lg bg-amber-50/70 border border-amber-200 text-amber-900 text-xs font-medium">
                      <strong>Catatan Khusus:</strong> {currentQueue.catatan_khusus}
                    </div>
                  )}

                  {/* ANTISIPASI: Pasien Belum Datang Saat Dipanggil */}
                  {currentQueue?.status === 'calling' && (
                    <div className="mt-4 p-3 rounded-lg bg-amber-50/60 border border-amber-200 flex items-center justify-between text-left">
                      <div>
                        <div className="text-xs font-bold text-amber-900 flex items-center gap-1.5">
                          <AlertCircle className="w-3.5 h-3.5 text-amber-700" />
                          Pasien belum masuk ruangan?
                        </div>
                        <p className="text-[11px] text-amber-800 font-medium mt-0.5">
                          Gunakan pengeras suara TV untuk memanggil secara manual.
                        </p>
                      </div>
                      <button
                        onClick={toggleIntercom}
                        className="px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-700 text-white font-semibold text-xs flex items-center gap-1 shadow-xs cursor-pointer shrink-0 transition-colors"
                      >
                        <Mic className="w-3.5 h-3.5" />
                        <span>Panggil via Mic</span>
                      </button>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="grid grid-cols-2 gap-2 pt-3 border-t border-border/60">
                  <button
                    onClick={handleCallNext}
                    disabled={loadingAction || waitingList.length === 0 || isOnBreak}
                    className={`col-span-2 py-2.5 px-4 rounded-lg font-semibold text-xs flex items-center justify-center gap-2 shadow-xs transition-all cursor-pointer ${
                      isOnBreak
                        ? 'bg-zinc-200 text-muted-foreground cursor-not-allowed border border-zinc-300'
                        : 'bg-primary hover:bg-primary/90 disabled:opacity-40 text-primary-foreground shadow-2xs'
                    }`}
                  >
                    <Play className="w-3.5 h-3.5 fill-current" />
                    <span>
                      {isOnBreak
                        ? 'Pelayanan Sedang Dijeda (Istirahat / Ishoma)'
                        : isBroadcasting
                        ? 'Matikan Mic & Panggil Berikutnya'
                        : 'Panggil Antrean Berikutnya (Next)'}
                    </span>
                  </button>

                  <button
                    onClick={handleRecall}
                    disabled={loadingAction || !currentQueue}
                    className="py-2 px-3 rounded-lg bg-card hover:bg-background disabled:opacity-40 text-foreground font-medium text-xs flex items-center justify-center gap-1.5 border border-border transition-all cursor-pointer"
                  >
                    <RotateCcw className="w-3.5 h-3.5 text-muted-foreground" />
                    <span>Panggil Ulang (Recall)</span>
                  </button>

                  <button
                    onClick={handleStartConsultation}
                    disabled={loadingAction || !currentQueue || currentQueue.status === 'in_consultation'}
                    className={`py-2 px-3 rounded-lg font-medium text-xs flex items-center justify-center gap-1.5 border transition-all cursor-pointer ${
                      currentQueue?.status === 'in_consultation'
                        ? 'bg-green-50 text-green-800 border-green-300'
                        : 'bg-card hover:bg-background text-foreground border-border'
                    }`}
                  >
                    <UserCheck className="w-3.5 h-3.5" />
                    <span>{currentQueue?.status === 'in_consultation' ? '✓ Sedang Diperiksa' : 'Mulai Diperiksa'}</span>
                  </button>

                  <button
                    onClick={handleSkip}
                    disabled={loadingAction || !currentQueue}
                    className="py-2 px-3 rounded-lg bg-card hover:bg-rose-50 disabled:opacity-40 text-rose-700 font-medium text-xs flex items-center justify-center gap-1.5 border border-border hover:border-rose-200 transition-all cursor-pointer"
                  >
                    <SkipForward className="w-3.5 h-3.5 text-rose-500" />
                    <span>Lewati (Skip)</span>
                  </button>

                  <button
                    onClick={handleComplete}
                    disabled={loadingAction || !currentQueue}
                    className="py-2 px-3 rounded-lg bg-card hover:bg-background disabled:opacity-40 text-foreground font-medium text-xs flex items-center justify-center gap-1.5 border border-border transition-all cursor-pointer"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5 text-muted-foreground" />
                    <span>Selesai Konsultasi</span>
                  </button>
                </div>
              </div>

              {/* Announcement Preview */}
              {lastAnnouncement && (
                <div className="p-3.5 rounded-xl bg-card border border-border text-xs shadow-2xs">
                  <div className="flex items-center gap-1.5 text-foreground/90 font-semibold mb-1">
                    <Sparkles className="w-3.5 h-3.5 text-muted-foreground/80" />
                    Skrip Panggilan Suara Terakhir:
                  </div>
                  <p className="text-muted-foreground italic leading-relaxed">
                    &ldquo;{lastAnnouncement}&rdquo;
                  </p>
                </div>
              )}
            </div>

            {/* Right Column (7/12): Queue Table & Log */}
            <div className="col-span-12 lg:col-span-7 flex flex-col gap-5">
              {/* Waiting Table Card */}
              <div className="rounded-xl bg-card border border-border p-6 flex flex-col shadow-2xs">
                <div className="flex items-center justify-between pb-3 border-b border-border/60">
                  <div>
                    <h3 className="text-base font-bold text-foreground flex items-center gap-2">
                      <Users className="w-4 h-4 text-muted-foreground" />
                      Daftar Antrean Menunggu ({waitingList.length})
                    </h3>
                    <p className="text-xs text-muted-foreground font-medium">
                      Antrean khusus {poliDisplayName}
                    </p>
                  </div>
                </div>

                {/* Table */}
                <div className="overflow-x-auto mt-2">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-border/60 text-muted-foreground/80 uppercase font-medium text-[11px]">
                        <th className="py-2.5 px-3">No. Antrean</th>
                        <th className="py-2.5 px-3">Nama Pasien</th>
                        <th className="py-2.5 px-3">Kategori</th>
                        <th className="py-2.5 px-3">Catatan</th>
                        <th className="py-2.5 px-3 text-right">Aksi</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-100">
                      {waitingList.length === 0 ? (
                        <tr>
                          <td colSpan={5} className="py-6 text-center text-muted-foreground/80 font-medium italic text-xs">
                            Tidak ada pasien yang sedang menunggu antrean di poli ini.
                          </td>
                        </tr>
                      ) : (
                        waitingList.map((q) => (
                          <tr key={q.id} className="hover:bg-background transition-colors">
                            <td className="py-3 px-3 font-mono font-bold text-foreground text-sm">
                              {q.nomor_antrean}
                            </td>
                            <td className="py-3 px-3 font-semibold text-foreground text-xs lg:text-sm">
                              {q.nama_pasien}
                            </td>
                            <td className="py-3 px-3">
                              <span
                                className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase border ${
                                  q.jenis_pasien === 'prioritas'
                                    ? 'bg-amber-50 text-amber-800 border-amber-200'
                                    : q.jenis_pasien === 'bpjs'
                                    ? 'bg-muted text-foreground/90 border-border'
                                    : 'bg-card text-foreground/90 border-border'
                                }`}
                              >
                                {q.jenis_pasien}
                              </span>
                            </td>
                            <td className="py-3 px-3 text-muted-foreground font-medium text-xs max-w-[150px] truncate">
                              {q.catatan_khusus || '-'}
                            </td>
                            <td className="py-3 px-3 text-right">
                              <button
                                onClick={async () => {
                                  try {
                                    if (isBroadcasting) stopIntercom();
                                    await apiClient.recall(q.id, activeDoctor.id);
                                    await loadQueues();
                                  } catch (err: any) {
                                    alert(err.message);
                                  }
                                }}
                                className="px-2.5 py-1 rounded-md bg-green-600 hover:bg-green-700 text-white text-[11px] font-medium shadow-2xs cursor-pointer"
                              >
                                Panggil
                              </button>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>

                {/* Completed Patients Bar */}
                <div className="pt-3 border-t border-border/60 mt-4">
                  <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wide block mb-1.5">
                    Pasien Selesai Hari Ini:
                  </span>
                  <div className="flex flex-wrap gap-1.5 text-xs">
                    {recentCompleted.length === 0 ? (
                      <span className="text-muted-foreground/80 text-xs italic">Belum ada pasien selesai.</span>
                    ) : (
                      recentCompleted.map((cq) => (
                        <span
                          key={cq.id}
                          className="px-2 py-0.5 rounded-md bg-muted text-foreground/90 border border-border font-mono font-medium text-[11px]"
                        >
                          ✓ {cq.nomor_antrean} ({cq.nama_pasien})
                        </span>
                      ))
                    )}
                  </div>
                </div>
              </div>

              {/* Operational Log */}
              <div className="rounded-xl bg-card border border-border p-6 shadow-2xs">
                <div className="flex items-center justify-between pb-2.5 border-b border-border/60 mb-3">
                  <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
                    <History className="w-4 h-4 text-muted-foreground" />
                    Riwayat Panggilan Terakhir (Log Suara Klinik)
                  </h3>
                  <span className="text-[11px] font-medium text-muted-foreground bg-muted px-2 py-0.5 rounded border border-border">
                    Log Operasional
                  </span>
                </div>

                <div className="divide-y divide-zinc-100">
                  {recentCalls.length === 0 ? (
                    <div className="py-4 text-center text-muted-foreground/80 font-medium italic text-xs">
                      Belum ada log panggilan audio tercatat hari ini.
                    </div>
                  ) : (
                    recentCalls.map((rc) => (
                      <div key={rc.id} className="py-2 flex items-center justify-between">
                        <div className="flex items-center gap-2.5">
                          <span className="text-xs font-bold font-mono px-2 py-0.5 bg-muted border border-border text-foreground rounded">
                            {rc.nomor_antrean}
                          </span>
                          <div>
                            <div className="font-semibold text-foreground text-xs">
                              {rc.poliklinik}
                            </div>
                            <div className="text-[10px] text-muted-foreground/80">
                              {rc.bilik?.replace('Bilik', 'Ruangan')}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-1 text-[11px] font-mono text-muted-foreground bg-background px-2 py-0.5 rounded border border-border">
                          <Clock className="w-3 h-3 text-muted-foreground/80" />
                          {rc.waktu}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default function ConsolePage() {
  return (
    <Suspense fallback={<div className="p-8 text-center font-bold">Memuat Konsol Ruangan Dokter...</div>}>
      <ConsoleContent />
    </Suspense>
  );
}
