'use client';

import React, { useEffect, useState, Suspense } from 'react';
import Link from 'next/link';
import {
  Building2,
  Stethoscope,
  Tv,
  Ticket,
  Plus,
  Edit2,
  Trash2,
  Settings,
  Users,
  CheckCircle2,
  Clock,
  AlertCircle,
  RefreshCw,
  Activity,
  Layers,
  Sparkles,
  Sliders,
  RotateCcw,
  ShieldCheck,
  DoorOpen,
  Volume2,
  X,
  Save,
  ArrowRight,
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

type TabType = 'overview' | 'counters' | 'polikliniks' | 'queues' | 'settings';

function AdminContent() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [stats, setStats] = useState<any>(null);
  const [counters, setCounters] = useState<any[]>([]);
  const [polikliniks, setPolikliniks] = useState<any[]>([]);
  const [queues, setQueues] = useState<any[]>([]);
  const [settings, setSettings] = useState<any>({
    clinic_name: '',
    running_text: '',
    audio_chime: 'bell',
  });

  // Modal States
  const [counterModalOpen, setCounterModalOpen] = useState<boolean>(false);
  const [editingCounter, setEditingCounter] = useState<any | null>(null);
  const [counterForm, setCounterForm] = useState({
    poliklinik_id: 1,
    nomor_bilik: '',
    nama_petugas: '',
    gelar_petugas: '',
    status: 'active',
  });

  const [poliModalOpen, setPoliModalOpen] = useState<boolean>(false);
  const [editingPoli, setEditingPoli] = useState<any | null>(null);
  const [poliForm, setPoliForm] = useState({
    kode: '',
    nama: '',
    nama_fonetik: '',
    gedung_lantai: '',
    status: 'active',
  });

  const [savingAction, setSavingAction] = useState<boolean>(false);

  // Fetch all initial data
  const loadAllData = async () => {
    setIsLoading(true);
    try {
      const [statsData, countersData, polisData, queuesData, settingsData] = await Promise.all([
        apiClient.getAdminStats(),
        apiClient.getAdminCounters(),
        apiClient.getAdminPolikliniks(),
        apiClient.getAdminQueues(),
        apiClient.getAdminSettings(),
      ]);

      setStats(statsData);
      setCounters(countersData || []);
      setPolikliniks(polisData || []);
      setQueues(queuesData || []);
      if (settingsData) {
        setSettings({
          clinic_name: settingsData.clinic_name || '',
          running_text: settingsData.running_text || '',
          audio_chime: settingsData.audio_chime || 'bell',
        });
      }
    } catch (err) {
      console.error('Error loading admin data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  // --- COUNTER CRUD HANDLERS ---
  const handleOpenAddCounter = () => {
    setEditingCounter(null);
    setCounterForm({
      poliklinik_id: polikliniks[0]?.id || 1,
      nomor_bilik: `Ruangan ${counters.length + 1}`,
      nama_petugas: '',
      gelar_petugas: 'Dokter Spesialis',
      status: 'active',
    });
    setCounterModalOpen(true);
  };

  const handleOpenEditCounter = (counter: any) => {
    setEditingCounter(counter);
    setCounterForm({
      poliklinik_id: counter.poliklinik_id,
      nomor_bilik: counter.nomor_bilik,
      nama_petugas: counter.nama_petugas,
      gelar_petugas: counter.gelar_petugas || '',
      status: counter.status || 'active',
    });
    setCounterModalOpen(true);
  };

  const handleSaveCounter = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingAction(true);
    try {
      if (editingCounter) {
        await apiClient.updateCounter(editingCounter.id, counterForm);
      } else {
        await apiClient.createCounter(counterForm);
      }
      setCounterModalOpen(false);
      await loadAllData();
    } catch (err: any) {
      alert(err.message || 'Gagal menyimpan ruangan');
    } finally {
      setSavingAction(false);
    }
  };

  const handleDeleteCounter = async (id: number, name: string) => {
    if (!confirm(`Hapus ruangan ${name}? Data antrean terkait ruangan ini mungkin terpengaruh.`)) return;
    try {
      await apiClient.deleteCounter(id);
      await loadAllData();
    } catch (err: any) {
      alert(err.message || 'Gagal menghapus ruangan');
    }
  };

  const handleToggleCounterStatus = async (counter: any) => {
    const nextStatus = counter.status === 'active' ? 'inactive' : 'active';
    try {
      await apiClient.updateCounter(counter.id, { status: nextStatus });
      await loadAllData();
    } catch (err: any) {
      alert(err.message || 'Gagal mengubah status');
    }
  };

  // --- POLIKLINIK CRUD HANDLERS ---
  const handleOpenAddPoli = () => {
    setEditingPoli(null);
    setPoliForm({
      kode: '',
      nama: '',
      nama_fonetik: '',
      gedung_lantai: 'Lantai 1',
      status: 'active',
    });
    setPoliModalOpen(true);
  };

  const handleOpenEditPoli = (poli: any) => {
    setEditingPoli(poli);
    setPoliForm({
      kode: poli.kode,
      nama: poli.nama,
      nama_fonetik: poli.nama_fonetik || '',
      gedung_lantai: poli.gedung_lantai,
      status: poli.status || 'active',
    });
    setPoliModalOpen(true);
  };

  const handleSavePoli = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingAction(true);
    try {
      if (editingPoli) {
        await apiClient.updatePoliklinik(editingPoli.id, poliForm);
      } else {
        await apiClient.createPoliklinik(poliForm);
      }
      setPoliModalOpen(false);
      await loadAllData();
    } catch (err: any) {
      alert(err.message || 'Gagal menyimpan poliklinik');
    } finally {
      setSavingAction(false);
    }
  };

  const handleDeletePoli = async (id: number, name: string) => {
    if (!confirm(`Hapus poliklinik ${name}? Semua ruangan dan antrean di poli ini akan dihapus.`)) return;
    try {
      await apiClient.deletePoliklinik(id);
      await loadAllData();
    } catch (err: any) {
      alert(err.message || 'Gagal menghapus poliklinik');
    }
  };

  // --- SETTINGS HANDLER ---
  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingAction(true);
    try {
      await apiClient.updateAdminSettings(settings);
      alert('Pengaturan sistem berhasil disimpan.');
      await loadAllData();
    } catch (err: any) {
      alert(err.message || 'Gagal menyimpan pengaturan');
    } finally {
      setSavingAction(false);
    }
  };

  // --- RESET QUEUES HANDLER ---
  const handleResetQueues = async () => {
    if (!confirm('PERINGATAN: Apakah Anda yakin ingin mengosongkan/mereset seluruh antrean hari ini? Tindakan ini tidak dapat dibatalkan.')) return;
    try {
      await apiClient.resetAdminQueues();
      alert('Antrean hari ini berhasil direset.');
      await loadAllData();
    } catch (err: any) {
      alert(err.message || 'Gagal mereset antrean');
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex font-sans select-none">
      {/* SISI KIRI: Admin Navigation Sidebar */}
      <aside className="w-64 lg:w-72 bg-card border-r border-border flex flex-col justify-between shrink-0 h-screen sticky top-0 p-4 shadow-2xs z-20">
        <div className="flex flex-col gap-4 overflow-y-auto">
          {/* Logo & Header */}
          <div className="flex items-center gap-3 px-2 py-1">
            <div className="w-9 h-9 rounded-lg bg-zinc-900 flex items-center justify-center text-white shrink-0">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-foreground tracking-tight leading-tight">
                Dashboard Admin
              </h1>
              <p className="text-[11px] font-medium text-muted-foreground">
                Husada Medika Center
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="border-t border-border/60 pt-3 flex flex-col gap-1">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/80 px-2 block mb-1">
              Menu Manajemen
            </span>

            <button
              onClick={() => setActiveTab('overview')}
              className={`w-full text-left px-3.5 py-2 rounded-lg font-medium text-xs flex items-center gap-2.5 transition-all cursor-pointer ${
                activeTab === 'overview' ? 'bg-primary text-primary-foreground shadow-2xs font-medium'
                  : 'text-foreground/90 hover:bg-muted'
              }`}
            >
              <Activity className="w-4 h-4" />
              <span>Ringkasan & KPI</span>
            </button>

            <button
              onClick={() => setActiveTab('counters')}
              className={`w-full text-left px-3.5 py-2 rounded-lg font-medium text-xs flex items-center justify-between transition-all cursor-pointer ${
                activeTab === 'counters' ? 'bg-primary text-primary-foreground shadow-2xs font-medium'
                  : 'text-foreground/90 hover:bg-muted'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <DoorOpen className="w-4 h-4" />
                <span>Kelola Ruangan</span>
              </div>
              <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded font-semibold ${
                activeTab === 'counters' ? 'bg-card/20 text-white' : 'bg-muted text-muted-foreground'
              }`}>
                {counters.length}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('polikliniks')}
              className={`w-full text-left px-3.5 py-2 rounded-lg font-medium text-xs flex items-center justify-between transition-all cursor-pointer ${
                activeTab === 'polikliniks' ? 'bg-primary text-primary-foreground shadow-2xs font-medium'
                  : 'text-foreground/90 hover:bg-muted'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Building2 className="w-4 h-4" />
                <span>Kelola Poliklinik</span>
              </div>
              <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded font-semibold ${
                activeTab === 'polikliniks' ? 'bg-card/20 text-white' : 'bg-muted text-muted-foreground'
              }`}>
                {polikliniks.length}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('queues')}
              className={`w-full text-left px-3.5 py-2 rounded-lg font-medium text-xs flex items-center justify-between transition-all cursor-pointer ${
                activeTab === 'queues' ? 'bg-primary text-primary-foreground shadow-2xs font-medium'
                  : 'text-foreground/90 hover:bg-muted'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Users className="w-4 h-4" />
                <span>Monitoring Antrean</span>
              </div>
              <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded font-semibold ${
                activeTab === 'queues' ? 'bg-card/20 text-white' : 'bg-muted text-muted-foreground'
              }`}>
                {queues.length}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('settings')}
              className={`w-full text-left px-3.5 py-2 rounded-lg font-medium text-xs flex items-center gap-2.5 transition-all cursor-pointer ${
                activeTab === 'settings' ? 'bg-primary text-primary-foreground shadow-2xs font-medium'
                  : 'text-foreground/90 hover:bg-muted'
              }`}
            >
              <Settings className="w-4 h-4" />
              <span>Pengaturan Display TV</span>
            </button>
          </div>
        </div>

        {/* Quick Links */}
        <div className="border-t border-border/60 pt-3 flex flex-col gap-1">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/80 px-2 block mb-0.5">
            Tautan Operasional
          </span>
          <Link
            href="/"
            target="_blank"
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium text-foreground/90 hover:bg-muted transition-colors"
          >
            <Tv className="w-3.5 h-3.5 text-muted-foreground/80" />
            Buka Layar TV Display ↗
          </Link>
          <Link
            href="/console"
            target="_blank"
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium text-foreground/90 hover:bg-muted transition-colors"
          >
            <Stethoscope className="w-3.5 h-3.5 text-muted-foreground/80" />
            Buka Konsol Dokter ↗
          </Link>
          <Link
            href="/kiosk"
            target="_blank"
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium text-foreground/90 hover:bg-muted transition-colors"
          >
            <Ticket className="w-3.5 h-3.5 text-muted-foreground/80" />
            Buka Kiosk Pasien ↗
          </Link>
        </div>
      </aside>

      {/* SISI KANAN: Admin Main Workspace */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto">
        {/* Top Header Bar */}
        <header className="px-6 lg:px-8 py-3.5 bg-card border-b border-border flex items-center justify-between sticky top-0 z-10 shadow-2xs">
          <div>
            <h2 className="text-base lg:text-lg font-bold text-foreground flex items-center gap-2">
              {activeTab === 'overview' && 'Ringkasan & Metrik Operasional'}
              {activeTab === 'counters' && 'Manajemen Ruangan & Dokter Jaga'}
              {activeTab === 'polikliniks' && 'Manajemen Poliklinik & Lokasi'}
              {activeTab === 'queues' && 'Monitoring Antrean Pasien Realtime'}
              {activeTab === 'settings' && 'Konfigurasi Sistem & Pengumuman TV'}
            </h2>
            <p className="text-xs text-muted-foreground font-medium">
              Kelola master data faskes, penambahan ruangan dokter, dan alur antrean terintegrasi
            </p>
          </div>

          <div className="flex items-center gap-2">
            {activeTab === 'counters' && (
              <button
                onClick={handleOpenAddCounter}
                className="px-3 py-1.5 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground shadow-2xs text-white font-semibold text-xs flex items-center gap-1.5 shadow-2xs transition-colors cursor-pointer"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Tambah Ruangan</span>
              </button>
            )}

            {activeTab === 'polikliniks' && (
              <button
                onClick={handleOpenAddPoli}
                className="px-3 py-1.5 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground shadow-2xs text-white font-semibold text-xs flex items-center gap-1.5 shadow-2xs transition-colors cursor-pointer"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Tambah Poliklinik</span>
              </button>
            )}

            {activeTab === 'queues' && (
              <button
                onClick={handleResetQueues}
                className="px-3 py-1.5 rounded-lg bg-card hover:bg-rose-50 text-rose-700 border border-border hover:border-rose-200 font-semibold text-xs flex items-center gap-1.5 transition-colors cursor-pointer"
              >
                <RotateCcw className="w-3.5 h-3.5 text-rose-500" />
                <span>Reset Antrean Hari Ini</span>
              </button>
            )}

            <button
              onClick={loadAllData}
              className="p-1.5 rounded-lg bg-card hover:bg-muted text-muted-foreground border border-border cursor-pointer transition-colors"
              title="Refresh Data"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>
        </header>

        {/* Content Body */}
        <main className="p-6 lg:p-8 flex flex-col gap-6">
          {/* TAB 1: OVERVIEW */}
          {activeTab === 'overview' && (
            <div className="flex flex-col gap-5">
              {/* KPI Cards Grid */}
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
                <div className="p-4 rounded-xl bg-card border border-border shadow-2xs flex flex-col justify-between">
                  <span className="text-[11px] font-medium text-muted-foreground uppercase">Total Ruangan</span>
                  <div className="text-2xl font-bold text-foreground font-mono mt-1">
                    {stats?.total_rooms || counters.length}
                  </div>
                  <span className="text-[10px] font-medium text-green-700 mt-2">
                    {stats?.active_rooms || 0} Ruangan Aktif
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-card border border-border shadow-2xs flex flex-col justify-between">
                  <span className="text-[11px] font-medium text-muted-foreground uppercase">Poliklinik</span>
                  <div className="text-2xl font-bold text-foreground font-mono mt-1">
                    {stats?.total_polikliniks || polikliniks.length}
                  </div>
                  <span className="text-[10px] font-medium text-green-700 mt-2">
                    {stats?.active_polikliniks || 0} Poli Aktif
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-card border border-border shadow-2xs flex flex-col justify-between">
                  <span className="text-[11px] font-medium text-muted-foreground uppercase">Antrean Hari Ini</span>
                  <div className="text-2xl font-bold text-foreground font-mono mt-1">
                    {stats?.total_queues_today || 0}
                  </div>
                  <span className="text-[10px] font-medium text-muted-foreground/80 mt-2">
                    Total Terdaftar
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-card border border-border shadow-2xs flex flex-col justify-between">
                  <span className="text-[11px] font-medium text-muted-foreground uppercase">Menunggu</span>
                  <div className="text-2xl font-bold text-amber-700 font-mono mt-1">
                    {stats?.waiting_today || 0}
                  </div>
                  <span className="text-[10px] font-medium text-amber-700 mt-2">
                    Belum Dipanggil
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-card border border-border shadow-2xs flex flex-col justify-between">
                  <span className="text-[11px] font-medium text-muted-foreground uppercase">Sedang Diperiksa</span>
                  <div className="text-2xl font-bold text-green-700 font-mono mt-1">
                    {stats?.in_consultation_today || 0}
                  </div>
                  <span className="text-[10px] font-medium text-green-700 mt-2">
                    Di Dalam Ruangan
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-card border border-border shadow-2xs flex flex-col justify-between">
                  <span className="text-[11px] font-medium text-muted-foreground uppercase">Selesai Hari Ini</span>
                  <div className="text-2xl font-bold text-foreground font-mono mt-1">
                    {stats?.completed_today || 0}
                  </div>
                  <span className="text-[10px] font-medium text-muted-foreground mt-2">
                    Pemeriksaan Tuntas
                  </span>
                </div>
              </div>

              {/* Quick Summary Panels */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                {/* Ruangan Overview Card */}
                <div className="rounded-xl bg-card border border-border p-5 shadow-2xs">
                  <div className="flex items-center justify-between pb-3 border-b border-border/60 mb-3">
                    <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
                      <DoorOpen className="w-4 h-4 text-muted-foreground" />
                      Daftar Ruangan Terdaftar ({counters.length})
                    </h3>
                    <button
                      onClick={() => setActiveTab('counters')}
                      className="text-xs font-semibold text-muted-foreground hover:text-foreground"
                    >
                      Kelola Semua →
                    </button>
                  </div>

                  <div className="divide-y divide-zinc-100">
                    {counters.slice(0, 5).map((c) => (
                      <div key={c.id} className="py-2.5 flex items-center justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-mono font-semibold text-xs px-2 py-0.5 rounded bg-muted text-foreground/90 border border-border">
                              {c.nomor_bilik}
                            </span>
                            <span className="font-semibold text-sm text-foreground">{c.nama_petugas}</span>
                          </div>
                          <p className="text-xs text-muted-foreground font-medium mt-0.5">
                            {c.poliklinik?.nama} &bull; {c.gelar_petugas}
                          </p>
                        </div>
                        <span className={`text-[10px] px-2 py-0.5 rounded font-semibold uppercase ${
                          c.status === 'active' ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-muted text-muted-foreground border border-border'
                        }`}>
                          {c.status === 'active' ? 'Aktif' : 'Nonaktif'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Poliklinik Overview Card */}
                <div className="rounded-xl bg-card border border-border p-5 shadow-2xs">
                  <div className="flex items-center justify-between pb-3 border-b border-border/60 mb-3">
                    <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
                      <Building2 className="w-4 h-4 text-muted-foreground" />
                      Daftar Poliklinik ({polikliniks.length})
                    </h3>
                    <button
                      onClick={() => setActiveTab('polikliniks')}
                      className="text-xs font-semibold text-muted-foreground hover:text-foreground"
                    >
                      Kelola Semua →
                    </button>
                  </div>

                  <div className="divide-y divide-zinc-100">
                    {polikliniks.map((p) => (
                      <div key={p.id} className="py-2.5 flex items-center justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-mono font-semibold text-xs px-2 py-0.5 rounded bg-muted text-foreground/90 border border-border">
                              {p.kode}
                            </span>
                            <span className="font-semibold text-sm text-foreground">{p.nama}</span>
                          </div>
                          <p className="text-xs text-muted-foreground font-medium mt-0.5">
                            {p.gedung_lantai}
                          </p>
                        </div>
                        <span className="text-xs font-mono font-semibold text-muted-foreground">
                          {p.counters?.length || 0} Ruangan
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: KELOLA RUANGAN DOKTER (COUNTERS) */}
          {activeTab === 'counters' && (
            <div className="rounded-xl bg-card border border-border p-6 shadow-2xs flex flex-col gap-4">
              <div className="flex items-center justify-between pb-3 border-b border-border/60">
                <div>
                  <h3 className="text-base font-bold text-foreground">Daftar Ruangan Pemeriksaan</h3>
                  <p className="text-xs text-muted-foreground font-medium">
                    Menambah, mengubah dokter penanggung jawab, serta mengaktifkan atau menonaktifkan ruangan
                  </p>
                </div>
                <button
                  onClick={handleOpenAddCounter}
                  className="px-3 py-1.5 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground shadow-2xs text-white font-semibold text-xs flex items-center gap-1.5 shadow-2xs transition-colors cursor-pointer"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Tambah Ruangan</span>
                </button>
              </div>

              {/* Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-border/60 text-muted-foreground/80 uppercase font-medium text-[11px]">
                      <th className="py-2.5 px-3">No. Ruangan</th>
                      <th className="py-2.5 px-3">Poliklinik</th>
                      <th className="py-2.5 px-3">Dokter Penanggung Jawab</th>
                      <th className="py-2.5 px-3">Spesialisasi / Gelar</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3 text-right">Aksi</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-100">
                    {counters.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="py-8 text-center text-muted-foreground/80 font-medium italic text-xs">
                          Belum ada ruangan yang ditambahkan.
                        </td>
                      </tr>
                    ) : (
                      counters.map((c) => (
                        <tr key={c.id} className="hover:bg-background transition-colors">
                          <td className="py-3 px-3 font-mono font-bold text-foreground text-sm">
                            <span className="px-2 py-0.5 rounded bg-muted border border-border text-foreground">
                              {c.nomor_bilik}
                            </span>
                          </td>
                          <td className="py-3 px-3 font-semibold text-foreground text-xs lg:text-sm">
                            {c.poliklinik?.nama || '-'}
                            <span className="text-[10px] font-mono font-medium text-muted-foreground/80 block">
                              {c.poliklinik?.kode}
                            </span>
                          </td>
                          <td className="py-3 px-3 font-bold text-foreground text-sm">
                            {c.nama_petugas}
                          </td>
                          <td className="py-3 px-3 text-muted-foreground font-medium text-xs">
                            {c.gelar_petugas || '-'}
                          </td>
                          <td className="py-3 px-3">
                            <button
                              onClick={() => handleToggleCounterStatus(c)}
                              className={`px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase cursor-pointer transition-colors border ${
                                c.status === 'active'
                                  ? 'bg-green-50 text-green-700 border-green-200 hover:bg-green-100'
                                  : 'bg-muted text-muted-foreground border-border hover:bg-zinc-200'
                              }`}
                            >
                              {c.status === 'active' ? '● Aktif' : '○ Nonaktif'}
                            </button>
                          </td>
                          <td className="py-3 px-3 text-right">
                            <div className="flex items-center justify-end gap-1.5">
                              <button
                                onClick={() => handleOpenEditCounter(c)}
                                className="p-1.5 rounded-md bg-card hover:bg-muted text-muted-foreground border border-border cursor-pointer"
                                title="Edit Ruangan"
                              >
                                <Edit2 className="w-3.5 h-3.5" />
                              </button>
                              <button
                                onClick={() => handleDeleteCounter(c.id, c.nomor_bilik)}
                                className="p-1.5 rounded-md bg-card hover:bg-rose-50 text-rose-600 border border-border hover:border-rose-200 cursor-pointer"
                                title="Hapus Ruangan"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 3: KELOLA POLIKLINIK */}
          {activeTab === 'polikliniks' && (
            <div className="rounded-xl bg-card border border-border p-6 shadow-2xs flex flex-col gap-4">
              <div className="flex items-center justify-between pb-3 border-b border-border/60">
                <div>
                  <h3 className="text-base font-bold text-foreground">Daftar Master Poliklinik</h3>
                  <p className="text-xs text-muted-foreground font-medium">
                    Menambah, mengubah nama poli, nama fonetik audio panggilan, dan lokasi lantai
                  </p>
                </div>
                <button
                  onClick={handleOpenAddPoli}
                  className="px-3 py-1.5 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground shadow-2xs text-white font-semibold text-xs flex items-center gap-1.5 shadow-2xs transition-colors cursor-pointer"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Tambah Poliklinik</span>
                </button>
              </div>

              {/* Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-border/60 text-muted-foreground/80 uppercase font-medium text-[11px]">
                      <th className="py-2.5 px-3">Kode</th>
                      <th className="py-2.5 px-3">Nama Poliklinik</th>
                      <th className="py-2.5 px-3">Pengucapan Audio Fonetik</th>
                      <th className="py-2.5 px-3">Gedung / Lantai</th>
                      <th className="py-2.5 px-3">Ruangan Terkait</th>
                      <th className="py-2.5 px-3 text-right">Aksi</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-100">
                    {polikliniks.map((p) => (
                      <tr key={p.id} className="hover:bg-background transition-colors">
                        <td className="py-3 px-3 font-mono font-bold text-foreground text-sm">
                          <span className="px-2 py-0.5 rounded bg-muted border border-border text-foreground">
                            {p.kode}
                          </span>
                        </td>
                        <td className="py-3 px-3 font-bold text-foreground text-sm">
                          {p.nama}
                        </td>
                        <td className="py-3 px-3 text-muted-foreground font-medium text-xs italic">
                          &ldquo;{p.nama_fonetik || p.nama}&rdquo;
                        </td>
                        <td className="py-3 px-3 text-muted-foreground font-medium text-xs">
                          {p.gedung_lantai}
                        </td>
                        <td className="py-3 px-3">
                          <span className="font-mono text-xs px-2 py-0.5 rounded bg-muted text-foreground/90">
                            {p.counters?.length || 0} Bilik
                          </span>
                        </td>
                        <td className="py-3 px-3 text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              onClick={() => handleOpenEditPoli(p)}
                              className="p-1.5 rounded-md bg-card hover:bg-muted text-muted-foreground border border-border cursor-pointer"
                              title="Edit Poli"
                            >
                              <Edit2 className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleDeletePoli(p.id, p.nama)}
                              className="p-1.5 rounded-md bg-card hover:bg-rose-50 text-rose-600 border border-border hover:border-rose-200 cursor-pointer"
                              title="Hapus Poli"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: MONITORING ANTREAN PASIEN */}
          {activeTab === 'queues' && (
            <div className="rounded-xl bg-card border border-border p-6 shadow-2xs flex flex-col gap-4">
              <div className="flex items-center justify-between pb-3 border-b border-border/60">
                <div>
                  <h3 className="text-base font-bold text-foreground">Monitoring Seluruh Antrean Pasien Hari Ini</h3>
                  <p className="text-xs text-muted-foreground font-medium">
                    Memantau status nomor antrean di semua poliklinik secara realtime
                  </p>
                </div>
                <button
                  onClick={handleResetQueues}
                  className="px-3 py-1.5 rounded-lg bg-card hover:bg-rose-50 text-rose-700 border border-border hover:border-rose-200 font-semibold text-xs flex items-center gap-1.5 transition-colors cursor-pointer"
                >
                  <RotateCcw className="w-3.5 h-3.5 text-rose-500" />
                  <span>Reset Antrean Harian</span>
                </button>
              </div>

              {/* Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-border/60 text-muted-foreground/80 uppercase font-medium text-[11px]">
                      <th className="py-2.5 px-3">No. Antrean</th>
                      <th className="py-2.5 px-3">Poliklinik Tujuan</th>
                      <th className="py-2.5 px-3">Nama Pasien</th>
                      <th className="py-2.5 px-3">Kategori</th>
                      <th className="py-2.5 px-3">Ruangan Dilayani</th>
                      <th className="py-2.5 px-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-100">
                    {queues.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="py-8 text-center text-muted-foreground/80 font-medium italic text-xs">
                          Belum ada antrean yang terdaftar hari ini.
                        </td>
                      </tr>
                    ) : (
                      queues.map((q) => (
                        <tr key={q.id} className="hover:bg-background transition-colors">
                          <td className="py-3 px-3 font-mono font-bold text-foreground text-sm">
                            <span className="px-2 py-0.5 rounded bg-muted border border-border text-foreground">
                              {q.nomor_antrean}
                            </span>
                          </td>
                          <td className="py-3 px-3 font-semibold text-foreground text-xs lg:text-sm">
                            {q.poliklinik?.nama}
                          </td>
                          <td className="py-3 px-3 font-bold text-foreground text-sm">
                            {q.nama_pasien}
                          </td>
                          <td className="py-3 px-3">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase border ${
                              q.jenis_pasien === 'prioritas'
                                ? 'bg-amber-50 text-amber-800 border-amber-200'
                                : q.jenis_pasien === 'bpjs'
                                ? 'bg-muted text-foreground/90 border-border'
                                : 'bg-card text-foreground/90 border-border'
                            }`}>
                              {q.jenis_pasien}
                            </span>
                          </td>
                          <td className="py-3 px-3 text-xs text-muted-foreground">
                            {q.counter?.nomor_bilik || 'Menunggu Petugas'}
                          </td>
                          <td className="py-3 px-3">
                            <span className={`px-2 py-0.5 rounded-md text-[10px] font-semibold uppercase border ${
                              q.status === 'in_consultation'
                                ? 'bg-green-50 text-green-700 border-green-200'
                                : q.status === 'calling'
                                ? 'bg-amber-50 text-amber-800 border-amber-200'
                                : q.status === 'completed'
                                ? 'bg-muted text-muted-foreground border-border'
                                : 'bg-background text-muted-foreground border-border'
                            }`}>
                              {q.status === 'in_consultation'
                                ? 'Sedang Diperiksa'
                                : q.status === 'calling'
                                ? 'Sedang Dipanggil'
                                : q.status === 'completed'
                                ? 'Selesai'
                                : 'Menunggu'}
                            </span>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 5: PENGATURAN DISPLAY TV */}
          {activeTab === 'settings' && (
            <div className="max-w-3xl rounded-xl bg-card border border-border p-6 lg:p-8 shadow-2xs">
              <div className="pb-4 border-b border-border/60 mb-6">
                <h3 className="text-base font-bold text-foreground">Konfigurasi Sistem & Teks Berjalan TV</h3>
                <p className="text-xs text-muted-foreground font-medium">
                  Ubah nama instansi klinik, teks berjalan (*running text*) di monitor display TV, serta nada pembuka pengumuman
                </p>
              </div>

              <form onSubmit={handleSaveSettings} className="flex flex-col gap-5">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-foreground/90 mb-1.5">
                    Nama Faskes / Rumah Sakit
                  </label>
                  <input
                    type="text"
                    value={settings.clinic_name}
                    onChange={(e) => setSettings({ ...settings, clinic_name: e.target.value })}
                    className="w-full px-3.5 py-2 rounded-lg border border-border text-sm font-semibold text-foreground focus:outline-none focus:border-zinc-900"
                    placeholder="Contoh: Poliklinik Terpadu Husada Medika"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-foreground/90 mb-1.5">
                    Teks Berjalan (*Running Text Monitor TV*)
                  </label>
                  <textarea
                    rows={4}
                    value={settings.running_text}
                    onChange={(e) => setSettings({ ...settings, running_text: e.target.value })}
                    className="w-full px-3.5 py-2 rounded-lg border border-border text-sm font-medium text-foreground focus:outline-none focus:border-zinc-900 leading-relaxed"
                    placeholder="Tuliskan pesan pengumuman untuk pasien di ruang tunggu..."
                    required
                  />
                  <p className="text-[11px] text-muted-foreground/80 font-medium mt-1">
                    Teks ini akan otomatis bergulir (*marquee*) di footer layar display TV ruang tunggu.
                  </p>
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-foreground/90 mb-1.5">
                    Tipe Nada Pembuka Panggilan (*Chime Tone*)
                  </label>
                  <select
                    value={settings.audio_chime}
                    onChange={(e) => setSettings({ ...settings, audio_chime: e.target.value })}
                    className="w-full px-3.5 py-2 rounded-lg border border-border text-sm font-semibold text-foreground focus:outline-none focus:border-zinc-900 bg-card cursor-pointer"
                  >
                    <option value="bell">Standard Bell (Ting-Tung Dua Nada Hangat)</option>
                    <option value="dingdong">Urgent Dingdong (Nada Resonansi Tegas)</option>
                  </select>
                </div>

                <div className="pt-4 border-t border-border/60 flex justify-end">
                  <button
                    type="submit"
                    disabled={savingAction}
                    className="px-5 py-2 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground shadow-2xs text-white font-semibold text-xs flex items-center gap-1.5 shadow-2xs cursor-pointer transition-colors"
                  >
                    <Save className="w-3.5 h-3.5" />
                    <span>{savingAction ? 'Menyimpan...' : 'Simpan Perubahan'}</span>
                  </button>
                </div>
              </form>
            </div>
          )}
        </main>
      </div>

      {/* MODAL 1: TAMBAH / EDIT RUANGAN */}
      {counterModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-card rounded-xl border border-border p-6 shadow-2xl animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between pb-3 border-b border-border/60 mb-4">
              <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
                <DoorOpen className="w-4 h-4 text-muted-foreground" />
                {editingCounter ? 'Edit Ruangan' : 'Tambah Ruangan Baru'}
              </h3>
              <button
                onClick={() => setCounterModalOpen(false)}
                className="p-1 rounded-md text-muted-foreground/80 hover:text-muted-foreground hover:bg-muted cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveCounter} className="flex flex-col gap-3.5">
              <div>
                <label className="block text-xs font-semibold text-foreground/90 mb-1">Poliklinik</label>
                <select
                  value={counterForm.poliklinik_id}
                  onChange={(e) => setCounterForm({ ...counterForm, poliklinik_id: Number(e.target.value) })}
                  className="w-full px-3 py-2 rounded-lg border border-border text-xs font-semibold text-foreground focus:outline-none focus:border-zinc-900"
                  required
                >
                  {polikliniks.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.nama} ({p.kode})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-foreground/90 mb-1">Nomor / Nama Ruangan</label>
                <input
                  type="text"
                  value={counterForm.nomor_bilik}
                  onChange={(e) => setCounterForm({ ...counterForm, nomor_bilik: e.target.value })}
                  placeholder="Contoh: Ruangan 6 atau Bilik 2"
                  className="w-full px-3 py-2 rounded-lg border border-border text-xs font-semibold text-foreground focus:outline-none focus:border-zinc-900"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-foreground/90 mb-1">Nama Dokter Penanggung Jawab</label>
                <input
                  type="text"
                  value={counterForm.nama_petugas}
                  onChange={(e) => setCounterForm({ ...counterForm, nama_petugas: e.target.value })}
                  placeholder="Contoh: dr. Anisa Putri"
                  className="w-full px-3 py-2 rounded-lg border border-border text-xs font-semibold text-foreground focus:outline-none focus:border-zinc-900"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-foreground/90 mb-1">Gelar / Spesialisasi Dokter</label>
                <input
                  type="text"
                  value={counterForm.gelar_petugas}
                  onChange={(e) => setCounterForm({ ...counterForm, gelar_petugas: e.target.value })}
                  placeholder="Contoh: Spesialis Kulit & Kelamin (Sp.KK)"
                  className="w-full px-3 py-2 rounded-lg border border-border text-xs font-semibold text-foreground focus:outline-none focus:border-zinc-900"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-foreground/90 mb-1">Status Operasional Ruangan</label>
                <select
                  value={counterForm.status}
                  onChange={(e) => setCounterForm({ ...counterForm, status: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-border text-xs font-semibold text-foreground focus:outline-none focus:border-zinc-900"
                >
                  <option value="active">Aktif Melayani</option>
                  <option value="inactive">Nonaktif / Tutup</option>
                </select>
              </div>

              <div className="pt-3 border-t border-border/60 flex justify-end gap-2 mt-2">
                <button
                  type="button"
                  onClick={() => setCounterModalOpen(false)}
                  className="px-3 py-1.5 rounded-lg border border-border text-xs font-medium text-muted-foreground hover:bg-background cursor-pointer"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  disabled={savingAction}
                  className="px-4 py-1.5 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground shadow-2xs text-white text-xs font-semibold shadow-2xs cursor-pointer"
                >
                  {savingAction ? 'Menyimpan...' : 'Simpan Ruangan'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: TAMBAH / EDIT POLIKLINIK */}
      {poliModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-card rounded-xl border border-border p-6 shadow-2xl animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between pb-3 border-b border-border/60 mb-4">
              <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
                <Building2 className="w-4 h-4 text-muted-foreground" />
                {editingPoli ? 'Edit Poliklinik' : 'Tambah Poliklinik Baru'}
              </h3>
              <button
                onClick={() => setPoliModalOpen(false)}
                className="p-1 rounded-md text-muted-foreground/80 hover:text-muted-foreground hover:bg-muted cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSavePoli} className="flex flex-col gap-3.5">
              <div>
                <label className="block text-xs font-semibold text-foreground/90 mb-1">Kode Poliklinik</label>
                <input
                  type="text"
                  value={poliForm.kode}
                  onChange={(e) => setPoliForm({ ...poliForm, kode: e.target.value.toUpperCase() })}
                  placeholder="Contoh: F-THT"
                  className="w-full px-3 py-2 rounded-lg border border-border text-xs font-semibold font-mono text-foreground focus:outline-none focus:border-zinc-900"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-foreground/90 mb-1">Nama Poliklinik</label>
                <input
                  type="text"
                  value={poliForm.nama}
                  onChange={(e) => setPoliForm({ ...poliForm, nama: e.target.value })}
                  placeholder="Contoh: Poli Spesialis THT"
                  className="w-full px-3 py-2 rounded-lg border border-border text-xs font-semibold text-foreground focus:outline-none focus:border-zinc-900"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-foreground/90 mb-1">Pengucapan Audio Suara Fonetik</label>
                <input
                  type="text"
                  value={poliForm.nama_fonetik}
                  onChange={(e) => setPoliForm({ ...poliForm, nama_fonetik: e.target.value })}
                  placeholder="Contoh: Poliklinik Telinga Hidung dan Tenggorokan"
                  className="w-full px-3 py-2 rounded-lg border border-border text-xs font-medium text-foreground focus:outline-none focus:border-zinc-900"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-foreground/90 mb-1">Gedung / Lokasi Lantai</label>
                <input
                  type="text"
                  value={poliForm.gedung_lantai}
                  onChange={(e) => setPoliForm({ ...poliForm, gedung_lantai: e.target.value })}
                  placeholder="Contoh: Lantai 2 - Sayap Utara"
                  className="w-full px-3 py-2 rounded-lg border border-border text-xs font-semibold text-foreground focus:outline-none focus:border-zinc-900"
                  required
                />
              </div>

              <div className="pt-3 border-t border-border/60 flex justify-end gap-2 mt-2">
                <button
                  type="button"
                  onClick={() => setPoliModalOpen(false)}
                  className="px-3 py-1.5 rounded-lg border border-border text-xs font-medium text-muted-foreground hover:bg-background cursor-pointer"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  disabled={savingAction}
                  className="px-4 py-1.5 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground shadow-2xs text-white text-xs font-semibold shadow-2xs cursor-pointer"
                >
                  {savingAction ? 'Menyimpan...' : 'Simpan Poliklinik'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default function AdminPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center font-bold">Memuat Dashboard Admin...</div>}>
      <AdminContent />
    </Suspense>
  );
}
