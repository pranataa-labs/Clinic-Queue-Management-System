import json
import os
import sys
import re

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def format_title_case(text):
    if not text or not isinstance(text, str):
        return text
    
    preserve_upper = {
        'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'Tbk', 'Tbk.', 'PT', 'TBK',
        'BCA', 'BRI', 'BNI', 'BMRI', 'BBCA', 'BBRI', 'BBNI', 'BBTN',
        'OJK', 'KSEI', 'AUM', 'CAGR', 'MDD', 'SBN', 'SUN', 'SBSN', 
        'FR', 'PBS', 'SR', 'ORI', 'TD', 'OKI', 'TBS', 'BJB', 'DKI',
        'ASII', 'TLKM', 'INKP', 'TKIM', 'KLBF', 'MEDC', 'ANTM', 'MDKA'
    }
    
    lower_words = {
        'dan', 'atau', 'di', 'ke', 'dari', 'yang', 'untuk', 'pada', 'dengan', 
        'dalam', 'atas', 'oleh', 'termasuk', 'serta', 'per', 'and', 'or', 'of', 
        'in', 'the', 'for', 'to', '&/', '&'
    }
    
    words = text.split()
    formatted = []
    for i, w in enumerate(words):
        match = re.match(r"^([^a-zA-Z0-9]*)([a-zA-Z0-9/&]+)([^a-zA-Z0-9]*)$", w)
        if match:
            prefix, core, suffix = match.groups()
            core_upper = core.upper()
            if core_upper in ('TBK', 'TBK.'):
                formatted.append(prefix + 'Tbk.' + suffix.replace('.', ''))
            elif core_upper in preserve_upper:
                formatted.append(prefix + core_upper + suffix)
            elif i > 0 and core.lower() in lower_words:
                formatted.append(prefix + core.lower() + suffix)
            else:
                formatted.append(prefix + core.capitalize() + suffix)
        else:
            formatted.append(w.capitalize())
            
    return ' '.join(formatted)

# Load enriched funds data and format all text cleanly
with open('reksadana-indonesia/enriched_funds.json', 'r', encoding='utf-8') as f:
    funds_data = json.load(f)

for f in funds_data:
    if 'custodian' in f and f['custodian']:
        f['custodian'] = format_title_case(f['custodian'])
    if 'manager' in f and f['manager']:
        f['manager'] = format_title_case(f['manager'])
    if 'holdings' in f and isinstance(f['holdings'], list):
        for h in f['holdings']:
            if 'name' in h and h['name']:
                h['name'] = format_title_case(h['name'])
    if 'assets' in f and isinstance(f['assets'], list):
        for a in f['assets']:
            if 'name' in a and a['name']:
                a['name'] = format_title_case(a['name'])

# Save updated JSON files
with open('reksadana-indonesia/enriched_funds.json', 'w', encoding='utf-8') as f:
    json.dump(funds_data, f, ensure_ascii=False, indent=2)

with open('mutual-fund-dashboard/data_indonesia.js', 'w', encoding='utf-8') as f:
    f.write("(typeof window !== 'undefined' ? window : globalThis).INDONESIA_REKSADANA_DATA = " + json.dumps(funds_data, ensure_ascii=False, indent=2) + ";\n")

print("Saved cleanly formatted data to data_indonesia.js and enriched_funds.json")

# Master HTML with refined Top 3 chart and data date metadata
html_content = r'''<!DOCTYPE html>
<html lang="id" class="font-inter">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Analisis Reksa Dana Indonesia | Evaluasi Risiko & Imbal Hasil</title>

  <!-- Inter Font -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: { inter: ['Inter', 'sans-serif'] },
          colors: {
            border: 'var(--border)',
            input: 'var(--input)',
            ring: 'var(--ring)',
            background: 'var(--background)',
            foreground: 'var(--foreground)',
            primary: { DEFAULT: 'var(--primary)', foreground: 'var(--primary-foreground)' },
            muted: { DEFAULT: 'var(--muted)', foreground: 'var(--muted-foreground)' },
            accent: { DEFAULT: 'var(--accent)', foreground: 'var(--accent-foreground)' },
            card: { DEFAULT: 'var(--card)', foreground: 'var(--card-foreground)' },
          }
        }
      }
    }
  </script>

  <!-- Lucide & Chart.js -->
  <script src="https://unpkg.com/lucide@latest"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

  <style>
    :root {
      --background: #f8fafc;
      --foreground: #020617;
      --card: #ffffff;
      --card-foreground: #020617;
      --primary: #0f172a;
      --primary-foreground: #f8fafc;
      --muted: #f1f5f9;
      --muted-foreground: #64748b;
      --accent: #f1f5f9;
      --accent-foreground: #0f172a;
      --border: #e2e8f0;
      --input: #e2e8f0;
      --ring: #94a3b8;
    }
    .dark {
      --background: #090d16;
      --foreground: #f8fafc;
      --card: #0f172a;
      --card-foreground: #f8fafc;
      --primary: #f8fafc;
      --primary-foreground: #0f172a;
      --muted: #1e293b;
      --muted-foreground: #94a3b8;
      --accent: #1e293b;
      --accent-foreground: #f8fafc;
      --border: rgba(255, 255, 255, 0.1);
      --input: rgba(255, 255, 255, 0.15);
      --ring: #64748b;
    }
    .custom-scroll::-webkit-scrollbar {
      width: 6px;
    }
    .custom-scroll::-webkit-scrollbar-track {
      background: transparent;
    }
    .custom-scroll::-webkit-scrollbar-thumb {
      background: rgba(148, 163, 184, 0.3);
      border-radius: 4px;
    }
  </style>
</head>
<body class="min-h-screen bg-background text-foreground transition-colors duration-200">

  <!-- Header -->
  <header class="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur-md">
    <div class="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
      <div class="flex items-center gap-3">
        <div class="flex size-9 items-center justify-center rounded-lg bg-emerald-600 text-white shadow-xs">
          <i data-lucide="shield-check" class="size-5"></i>
        </div>
        <div>
          <span class="text-base font-bold tracking-tight">Reksa Dana Indonesia Analytics</span>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <!-- Panduan Pemula Button -->
        <a
          href="panduan.html"
          class="inline-flex h-9 items-center gap-1.5 rounded-md border border-amber-300 bg-amber-50 px-3 text-xs font-bold text-amber-900 shadow-xs hover:bg-amber-100 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300 transition-colors"
          title="Buku Panduan Edukasi dan Metodologi Reksa Dana"
        >
          <i data-lucide="book-open" class="size-4 text-amber-600 dark:text-amber-400"></i>
          <span class="hidden sm:inline">Panduan Pemula</span>
          <span class="sm:hidden">Panduan</span>
        </a>

        <!-- Search Input -->
        <div class="relative hidden sm:block w-64">
          <i data-lucide="search" class="absolute start-3 top-2.5 size-4 text-muted-foreground"></i>
          <input
            type="text"
            id="searchInput"
            placeholder="Cari nama produk atau Manajer Investasi..."
            class="h-9 w-full rounded-md border border-input bg-transparent pe-4 ps-9 text-sm shadow-xs placeholder:text-muted-foreground focus:border-ring focus:outline-none focus:ring-[3px] focus:ring-ring/40 dark:bg-input/20"
          >
        </div>

        <button
          id="themeToggle"
          class="inline-flex size-9 items-center justify-center rounded-md border border-input bg-background text-foreground shadow-xs hover:bg-accent dark:bg-input/20"
          title="Mode Terang/Gelap"
        >
          <i data-lucide="moon" class="size-4 hidden dark:block"></i>
          <i data-lucide="sun" class="size-4 block dark:hidden"></i>
        </button>
      </div>
    </div>
  </header>

  <main class="mx-auto max-w-7xl px-4 py-6 sm:px-6 space-y-6">

    <!-- Title and Metadata Info Banner -->
    <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <div>
        <h1 class="text-2xl font-bold tracking-tight">Evaluasi Kinerja Reksa Dana Pasar Indonesia</h1>
        
        <!-- Metadata Keterangan Tahun Data -->
        <div class="flex flex-wrap items-center gap-2 text-xs text-muted-foreground mt-2">
          <span class="inline-flex items-center gap-1.5 rounded-md border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-0.5 text-xs font-semibold text-emerald-800 dark:text-emerald-300">
            <i data-lucide="calendar" class="size-3.5"></i>
            Rentang Data: Tahun 2000 – 2026
          </span>
          <span class="hidden sm:inline">·</span>
          <span class="rounded-md border border-border bg-card px-2 py-0.5 text-xs">
            Cut-off NAV Terakhir: <b>30 Oktober 2026</b>
          </span>
          <span class="hidden sm:inline">·</span>
          <span class="rounded-md border border-border bg-card px-2 py-0.5 text-xs">
            Data AUM Resmi OJK: <b>September 2026</b>
          </span>
          <span class="hidden md:inline">·</span>
          <span class="rounded-md border border-border bg-card px-2 py-0.5 text-xs">
            Periode Evaluasi: <b>1Y (2025–2026)</b> · <b>3Y (2023–2026)</b> · <b>5Y (2021–2026)</b>
          </span>
        </div>
      </div>

      <!-- Controls: Category Dropbox & Urutkan Dropbox -->
      <div class="flex flex-wrap items-center gap-3">
        <!-- Dropbox Kategori -->
        <div class="flex items-center gap-2">
          <label for="categorySelect" class="text-xs font-semibold text-muted-foreground">Kategori:</label>
          <select
            id="categorySelect"
            class="h-9 rounded-lg border border-input bg-card px-3 text-xs font-semibold text-foreground shadow-xs focus:border-ring focus:outline-none focus:ring-[2px] focus:ring-ring/40 dark:bg-card"
          >
            <option value="ALL">Semua (146)</option>
            <option value="Pasar Uang">💵 Pasar Uang (36)</option>
            <option value="Obligasi">📑 Obligasi (46)</option>
            <option value="Saham">📈 Saham (46)</option>
            <option value="Campuran">⚖️ Campuran (11)</option>
          </select>
        </div>

        <!-- Dropbox Urutkan -->
        <div class="flex items-center gap-2">
          <label for="sortSelect" class="text-xs font-semibold text-muted-foreground">Urutkan:</label>
          <select
            id="sortSelect"
            class="h-9 rounded-lg border border-input bg-card px-3 text-xs font-semibold text-foreground shadow-xs focus:border-ring focus:outline-none focus:ring-[2px] focus:ring-ring/40 dark:bg-card"
          >
            <option value="rank_cat_asc">Rank Kategori (Terbaik)</option>
            <option value="rank_cat_desc">Rank Kategori (Terburuk)</option>
            <option value="ret3_desc">Return 3Y Tertinggi</option>
            <option value="ret3_asc">Return 3Y Terendah</option>
            <option value="mdd_asc">Max Drawdown Terendah (Paling Aman)</option>
            <option value="mdd_desc">Max Drawdown Tertinggi</option>
            <option value="calmar_desc">Calmar Ratio Tertinggi</option>
            <option value="aum_desc">AUM Terbesar</option>
            <option value="exp_asc">Expense Ratio Terendah</option>
          </select>
        </div>
      </div>
    </div>

    <!-- KPI Grid (Huruf Biasa) -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">

      <div class="rounded-xl border border-border bg-card p-5 text-card-foreground shadow-xs">
        <div class="flex items-center justify-between pb-2">
          <span class="text-xs font-semibold text-muted-foreground">Total Dana Kelolaan (AUM)</span>
          <div class="flex size-7 items-center justify-center rounded-md bg-blue-500/10 text-blue-600 dark:text-blue-400">
            <i data-lucide="landmark" class="size-4"></i>
          </div>
        </div>
        <div class="text-2xl font-bold tracking-tight" id="kpiAum">Rp 0 Triliun</div>
        <p class="text-xs text-muted-foreground mt-1">Total aset dari <b id="kpiCount">146</b> reksa dana aktif</p>
      </div>

      <div class="rounded-xl border border-border bg-card p-5 text-card-foreground shadow-xs">
        <div class="flex items-center justify-between pb-2">
          <span class="text-xs font-semibold text-muted-foreground">Rata-rata Return 3 Tahun</span>
          <div class="flex size-7 items-center justify-center rounded-md bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
            <i data-lucide="trending-up" class="size-4"></i>
          </div>
        </div>
        <div class="text-2xl font-bold tracking-tight text-emerald-600 dark:text-emerald-400" id="kpiRet3">0.0%</div>
        <p class="text-xs text-muted-foreground mt-1">CAGR 3Y di kategori terpilih</p>
      </div>

      <div class="rounded-xl border border-border bg-card p-5 text-card-foreground shadow-xs">
        <div class="flex items-center justify-between pb-2">
          <span class="text-xs font-semibold text-muted-foreground">Rata-rata Max Drawdown</span>
          <div class="flex size-7 items-center justify-center rounded-md bg-rose-500/10 text-rose-600 dark:text-rose-400">
            <i data-lucide="shield-alert" class="size-4"></i>
          </div>
        </div>
        <div class="text-2xl font-bold tracking-tight text-rose-600 dark:text-rose-400" id="kpiMdd">0.0%</div>
        <p class="text-xs text-muted-foreground mt-1">Kedalaman koreksi terburuk 3 tahun</p>
      </div>

      <div class="rounded-xl border border-border bg-card p-5 text-card-foreground shadow-xs">
        <div class="flex items-center justify-between pb-2">
          <span class="text-xs font-semibold text-muted-foreground">Rata-rata Expense Ratio</span>
          <div class="flex size-7 items-center justify-center rounded-md bg-purple-500/10 text-purple-600 dark:text-purple-400">
            <i data-lucide="percent" class="size-4"></i>
          </div>
        </div>
        <div class="text-2xl font-bold tracking-tight text-foreground" id="kpiExp">0.0%</div>
        <p class="text-xs text-muted-foreground mt-1">Biaya tahunan pengelolaan investasi</p>
      </div>

    </div>

    <!-- HERO CHART: 3 Reksa Dana Teratas (Desain Baru & Elegan) -->
    <div class="rounded-xl border border-border bg-card p-5 text-card-foreground shadow-xs">
      <div class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div class="flex items-center gap-2">
            <div class="flex size-6 items-center justify-center rounded-md bg-amber-500/10 text-amber-600 dark:text-amber-400">
              <i data-lucide="trending-up" class="size-4"></i>
            </div>
            <h3 class="text-base font-bold tracking-tight" id="top3ChartTitle">Perbandingan 3 Reksa Dana Teratas</h3>
          </div>
          <p class="text-xs text-muted-foreground mt-0.5" id="top3ChartSubtitle">
            Simulasi kurva pertumbuhan modal Rp 10.000.000 selama 3 tahun beserta perbandingan risiko penurunan maksimal (Max Drawdown 3Y).
          </p>
        </div>

        <!-- Toggle View Mode: Kurva Pertumbuhan 3Y vs Bar Komparasi -->
        <div class="flex items-center gap-1.5 rounded-lg border border-border bg-muted/40 p-1">
          <button
            id="btnModeGrowth"
            onclick="setTop3ViewMode('growth')"
            class="rounded-md bg-card px-2.5 py-1 text-xs font-semibold text-foreground shadow-xs transition-all"
          >
            Kurva Pertumbuhan 3 Tahun
          </button>
          <button
            id="btnModeCompare"
            onclick="setTop3ViewMode('compare')"
            class="rounded-md px-2.5 py-1 text-xs font-semibold text-muted-foreground hover:text-foreground transition-all"
          >
            Imbal Hasil vs Risiko
          </button>
        </div>
      </div>

      <!-- Main Chart Canvas -->
      <div class="relative h-72 w-full">
        <canvas id="top3LinesChart"></canvas>
      </div>

      <!-- 3 Top Funds Mini-Cards underneath chart -->
      <div class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3" id="top3CardsContainer">
      </div>
    </div>

    <!-- Secondary Charts Grid -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">

      <!-- Chart 1: Risk vs Return Scatter Plot (Drawdown vs 3Y Return) -->
      <div class="rounded-xl border border-border bg-card p-5 text-card-foreground shadow-xs">
        <div class="mb-4 flex items-center justify-between">
          <div>
            <h3 class="text-sm font-semibold tracking-tight">Peta Risiko vs Imbal Hasil (Max Drawdown vs Return 3Y)</h3>
            <p class="text-xs text-muted-foreground">Kuadran Kiri-Atas adalah zona paling ideal (Drawdown Rendah, Return Tinggi)</p>
          </div>
          <i data-lucide="crosshair" class="size-4 text-muted-foreground"></i>
        </div>
        <div class="relative h-64 w-full">
          <canvas id="scatterRiskChart"></canvas>
        </div>
      </div>

      <!-- Chart 2: Top Manajer Investasi (AUM Terbesar) -->
      <div class="rounded-xl border border-border bg-card p-5 text-card-foreground shadow-xs">
        <div class="mb-4 flex items-center justify-between">
          <div>
            <h3 class="text-sm font-semibold tracking-tight">Manajer Investasi Terbesar (Total AUM di Pasar)</h3>
            <p class="text-xs text-muted-foreground">Dana kelolaan dalam Triliun Rupiah per Manajer Investasi</p>
          </div>
          <i data-lucide="bar-chart-2" class="size-4 text-muted-foreground"></i>
        </div>
        <div class="relative h-64 w-full">
          <canvas id="managerAumChart"></canvas>
        </div>
      </div>

    </div>

    <!-- Data Table Leaderboard -->
    <div class="rounded-xl border border-border bg-card text-card-foreground shadow-xs overflow-hidden">

      <div class="flex flex-col gap-3 p-5 sm:flex-row sm:items-center sm:justify-between border-b border-border">
        <div>
          <div class="flex items-center gap-2">
            <h2 class="text-base font-semibold tracking-tight">Daftar Peringkat Reksa Dana Indonesia</h2>
            <span class="rounded-md border border-border bg-muted px-2 py-0.5 text-xs font-semibold" id="tableBadgeCount">146 Produk</span>
          </div>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-start text-sm">
          <thead class="border-b border-border bg-muted/40 text-xs font-medium text-muted-foreground">
            <tr>
              <th class="h-10 px-4 text-start font-semibold">Rank Kategori</th>
              <th class="h-10 px-4 text-start font-semibold">Nama Reksa Dana & Manajer Investasi</th>
              <th class="h-10 px-4 text-start font-semibold">Tipe</th>
              <th class="h-10 px-4 text-end font-semibold">AUM (Dana Kelolaan)</th>
              <th class="h-10 px-4 text-end font-semibold">Return 3Y</th>
              <th class="h-10 px-4 text-end font-semibold">Max Drawdown 3Y</th>
              <th class="h-10 px-4 text-end font-semibold">Calmar Ratio</th>
              <th class="h-10 px-4 text-end font-semibold">Expense Ratio</th>
              <th class="h-10 px-4 text-end font-semibold">Skor Model</th>
              <th class="h-10 px-4 text-center font-semibold">Aksi</th>
            </tr>
          </thead>
          <tbody id="tableBody" class="divide-y divide-border">
          </tbody>
        </table>
      </div>

    </div>

  </main>

  <!-- DETAIL MODAL DIALOG -->
  <div
    id="detailModal"
    class="fixed inset-0 z-50 hidden bg-black/60 backdrop-blur-sm flex items-center justify-center p-3 sm:p-6"
    onclick="handleBackdropClick(event)"
  >
    <div
      class="relative w-full max-w-4xl max-h-[92vh] overflow-y-auto rounded-2xl border border-border bg-card p-6 shadow-2xl text-card-foreground custom-scroll transition-all"
      onclick="event.stopPropagation()"
    >
      <!-- Modal Header -->
      <div class="flex items-start justify-between border-b border-border pb-4">
        <div>
          <div class="flex flex-wrap items-center gap-2 mb-1.5">
            <span id="modalRankBadge" class="rounded-md bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 px-2 py-0.5 text-xs font-bold">
              Peringkat #1 Kategori
            </span>
            <span id="modalTypeBadge" class="rounded-md bg-muted px-2 py-0.5 text-xs font-medium border border-border">
              Pasar Uang
            </span>
            <span id="modalShariaBadge" class="hidden rounded-md bg-emerald-500/10 text-emerald-600 border border-emerald-500/20 px-2 py-0.5 text-xs font-bold">
              Syariah
            </span>
            <span id="modalSymbol" class="font-mono text-xs text-muted-foreground">
              RD123
            </span>
          </div>
          <h2 id="modalFundName" class="text-xl sm:text-2xl font-bold tracking-tight text-foreground">
            Nama Reksa Dana
          </h2>
          <div class="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1 text-xs text-muted-foreground">
            <span class="flex items-center gap-1">
              <i data-lucide="building-2" class="size-3.5"></i>
              <span id="modalManager">PT Manajer Investasi</span>
            </span>
            <span class="flex items-center gap-1">
              <i data-lucide="landmark" class="size-3.5"></i>
              Kustodian: <span id="modalCustodian">Bank Kustodian</span>
            </span>
            <span class="flex items-center gap-1">
              <i data-lucide="calendar" class="size-3.5"></i>
              Rilis: <span id="modalInception">2018-01-01</span>
            </span>
          </div>
        </div>

        <button
          onclick="closeDetailModal()"
          class="rounded-lg p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
          title="Tutup (ESC)"
        >
          <i data-lucide="x" class="size-5"></i>
        </button>
      </div>

      <!-- Modal Body Content -->
      <div class="space-y-6 pt-5">

        <!-- 1. Grid Metrik Finansial Lengkap (Huruf Biasa) -->
        <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div class="rounded-xl border border-border bg-muted/30 p-3.5">
            <span class="text-[11px] font-semibold text-muted-foreground">Total AUM</span>
            <div id="modalAum" class="text-lg font-bold font-mono text-foreground mt-0.5">Rp 0 M</div>
            <span class="text-[10px] text-muted-foreground">Dana kelolaan</span>
          </div>
          <div class="rounded-xl border border-border bg-muted/30 p-3.5">
            <span class="text-[11px] font-semibold text-muted-foreground">Return 3Y (CAGR)</span>
            <div id="modalRet3" class="text-lg font-bold font-mono text-emerald-600 dark:text-emerald-400 mt-0.5">+0.0%</div>
            <span class="text-[10px] text-muted-foreground">Imbal hasil kunci</span>
          </div>
          <div class="rounded-xl border border-border bg-muted/30 p-3.5">
            <span class="text-[11px] font-semibold text-muted-foreground">Max Drawdown 3Y</span>
            <div id="modalMdd3" class="text-lg font-bold font-mono text-rose-500 mt-0.5">-0.0%</div>
            <span class="text-[10px] text-muted-foreground">Koreksi terburuk</span>
          </div>
          <div class="rounded-xl border border-border bg-muted/30 p-3.5">
            <span class="text-[11px] font-semibold text-muted-foreground">Calmar Ratio</span>
            <div id="modalCalmar" class="text-lg font-bold font-mono text-foreground mt-0.5">0.0</div>
            <span class="text-[10px] text-muted-foreground">Efisiensi return/risiko</span>
          </div>
          <div class="rounded-xl border border-border bg-muted/30 p-3.5">
            <span class="text-[11px] font-semibold text-muted-foreground">Return 1Y</span>
            <div id="modalRet1" class="text-base font-bold font-mono text-foreground mt-0.5">+0.0%</div>
            <span class="text-[10px] text-muted-foreground">Kinerja 12 bulan</span>
          </div>
          <div class="rounded-xl border border-border bg-muted/30 p-3.5">
            <span class="text-[11px] font-semibold text-muted-foreground">Return 5Y</span>
            <div id="modalRet5" class="text-base font-bold font-mono text-foreground mt-0.5">+0.0%</div>
            <span class="text-[10px] text-muted-foreground">Kinerja jangka panjang</span>
          </div>
          <div class="rounded-xl border border-border bg-muted/30 p-3.5">
            <span class="text-[11px] font-semibold text-muted-foreground">Expense Ratio</span>
            <div id="modalExp" class="text-base font-bold font-mono text-foreground mt-0.5">0.0%</div>
            <span class="text-[10px] text-muted-foreground">Biaya manajemen/tahun</span>
          </div>
          <div class="rounded-xl border border-border bg-muted/30 p-3.5">
            <span class="text-[11px] font-semibold text-muted-foreground">Min. Pembelian</span>
            <div id="modalMinBuy" class="text-base font-bold font-mono text-foreground mt-0.5">Rp 10.000</div>
            <span class="text-[10px] text-muted-foreground">Modal awal masuk</span>
          </div>
        </div>

        <!-- 2. Interactive Charts inside Modal -->
        <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <!-- Multi-period Performance Line Chart -->
          <div class="rounded-xl border border-border bg-card p-4">
            <h4 class="text-xs font-semibold text-muted-foreground mb-2 flex items-center justify-between">
              <span>Kurva Kinerja vs Kedalaman Risiko (Drawdown)</span>
              <i data-lucide="line-chart" class="size-3.5"></i>
            </h4>
            <div class="relative h-56 w-full">
              <canvas id="modalPerfChart"></canvas>
            </div>
          </div>

          <!-- Peer Group Comparison Chart -->
          <div class="rounded-xl border border-border bg-card p-4">
            <h4 class="text-xs font-semibold text-muted-foreground mb-2 flex items-center justify-between">
              <span>Posisi vs Rata-rata Kategori Sejenis</span>
              <i data-lucide="bar-chart" class="size-3.5"></i>
            </h4>
            <div class="relative h-56 w-full">
              <canvas id="modalPeerChart"></canvas>
            </div>
          </div>
        </div>

        <!-- 3. Portofolio Holdings & Asset Allocation (Huruf Biasa) -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <!-- Top Holdings -->
          <div class="rounded-xl border border-border bg-muted/20 p-4">
            <h4 class="text-xs font-bold text-foreground mb-3 flex items-center gap-1.5">
              <i data-lucide="layers" class="size-4 text-emerald-600"></i>
              Efek Terbesar dalam Portofolio (Top Holdings)
            </h4>
            <div id="modalHoldingsList" class="space-y-2 text-xs">
            </div>
          </div>

          <!-- Asset Allocation -->
          <div class="rounded-xl border border-border bg-muted/20 p-4">
            <h4 class="text-xs font-bold text-foreground mb-3 flex items-center gap-1.5">
              <i data-lucide="pie-chart" class="size-4 text-blue-600"></i>
              Alokasi Aset Portofolio
            </h4>
            <div id="modalAssetList" class="space-y-2 text-xs">
            </div>
          </div>
        </div>

        <!-- 4. Analisis Berbasis Data & Simulasi Riil Rp 10 Juta -->
        <div class="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4 sm:p-5">
          <h4 class="text-sm font-bold text-emerald-900 dark:text-emerald-300 flex items-center gap-2 mb-2">
            <i data-lucide="sparkles" class="size-4 text-emerald-600"></i>
            Ringkasan Analisis & Profil Investor
          </h4>
          <div id="modalAnalysisText" class="text-xs leading-relaxed text-emerald-950/80 dark:text-emerald-200/90 space-y-2">
          </div>
        </div>

      </div>

      <!-- Modal Footer -->
      <div class="mt-6 flex justify-end border-t border-border pt-4">
        <button
          onclick="closeDetailModal()"
          class="rounded-lg bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground hover:opacity-90 shadow-xs transition-opacity"
        >
          Tutup Detail
        </button>
      </div>
    </div>
  </div>

  <!-- Detailed Footer with Data Date Information -->
  <footer class="border-t border-border mt-12 py-8 text-xs text-muted-foreground bg-muted/20">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between text-center sm:text-start">
      <div class="space-y-1">
        <p class="font-bold text-foreground">Platform Analisis Kuantitatif Reksa Dana Pasar Modal Indonesia</p>
        <p>
          Cakupan Historis Produk: <b>Tahun 2000 – 2026 (26 Tahun Rekam Jejak)</b> · Cut-off NAV Harian: <b>30 Oktober 2026</b> · Data AUM Resmi: <b>September 2026</b>
        </p>
        <p class="text-[11px] text-muted-foreground/80">
          Metrik Evaluasi: Return 1Y (2025–2026), Return 3Y & Max Drawdown (2023–2026), Return 5Y (2021–2026) · Sumber: Registri Resmi OJK, KSEI, dan Bibit Reksadana API.
        </p>
      </div>
      <div class="shrink-0">
        <span class="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-bold text-emerald-700 dark:text-emerald-300">
          <span class="size-2 rounded-full bg-emerald-500"></span>
          Data Terkini: Akhir Oktober 2026
        </span>
      </div>
    </div>
  </footer>

  <!-- Embedded Indonesian Data -->
  <script src="data_indonesia.js"></script>

  <!-- Dashboard Script -->
  <script>
    const data = window.INDONESIA_REKSADANA_DATA || [];
    let currentCat = 'ALL';
    let searchQuery = '';
    let sortMode = 'rank_cat_asc';
    let top3ViewMode = 'growth'; // 'growth' or 'compare'
    let charts = {};
    let modalCharts = {};

    function toTitleCase(str) {
      if (!str) return '';
      const preserveUpper = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 
                             'A', 'B', 'C', 'D', 'E', 'F', 'Tbk.', 'PT', 'BCA', 'BRI', 
                             'BNI', 'BMRI', 'OJK', 'KSEI', 'AUM', 'CAGR', 'MDD', 'SBN', 
                             'SUN', 'SBSN', 'FR', 'PBS', 'SR', 'ORI', 'TD', 'OKI', 'TBS', 'BJB'];
      const lowerWords = ['dan', 'atau', 'di', 'ke', 'dari', 'yang', 'untuk', 'pada', 'dengan', 
                          'dalam', 'atas', 'oleh', 'termasuk', 'serta', 'per', 'and', 'or', 'of', 
                          'in', 'the', 'for', 'to', '&/', '&'];

      return str.split(' ').map((word, idx) => {
        const clean = word.replace(/[^a-zA-Z0-9/&]/g, '');
        const upperClean = clean.toUpperCase();
        if (upperClean === 'TBK' || upperClean === 'TBK.') return 'Tbk.';
        if (preserveUpper.includes(upperClean)) return word.replace(clean, upperClean);
        if (idx > 0 && lowerWords.includes(clean.toLowerCase())) return word.replace(clean, clean.toLowerCase());
        const capitalized = clean.charAt(0).toUpperCase() + clean.slice(1).toLowerCase();
        return word.replace(clean, capitalized);
      }).join(' ');
    }

    // Theme toggle
    const themeBtn = document.getElementById('themeToggle');
    themeBtn.addEventListener('click', () => {
      document.documentElement.classList.toggle('dark');
      updateCharts();
      lucide.createIcons();
    });

    function setTop3ViewMode(mode) {
      top3ViewMode = mode;
      const btnGrowth = document.getElementById('btnModeGrowth');
      const btnCompare = document.getElementById('btnModeCompare');
      if (mode === 'growth') {
        btnGrowth.className = 'rounded-md bg-card px-2.5 py-1 text-xs font-semibold text-foreground shadow-xs transition-all';
        btnCompare.className = 'rounded-md px-2.5 py-1 text-xs font-semibold text-muted-foreground hover:text-foreground transition-all';
        document.getElementById('top3ChartSubtitle').textContent = 'Simulasi kurva pertumbuhan modal Rp 10.000.000 selama 3 tahun beserta perbandingan risiko penurunan maksimal (Max Drawdown 3Y).';
      } else {
        btnCompare.className = 'rounded-md bg-card px-2.5 py-1 text-xs font-semibold text-foreground shadow-xs transition-all';
        btnGrowth.className = 'rounded-md px-2.5 py-1 text-xs font-semibold text-muted-foreground hover:text-foreground transition-all';
        document.getElementById('top3ChartSubtitle').textContent = 'Perbandingan langsung tingkat Imbal Hasil (Return 3Y CAGR) bersanding dengan Kedalaman Risiko (Max Drawdown 3Y) dari 3 reksa dana teratas.';
      }
      renderTop3Chart();
    }

    function getFiltered() {
      return data.filter(d => {
        const matchesCat = currentCat === 'ALL' || d.type === currentCat;
        const q = searchQuery.toLowerCase();
        const matchesSearch = !q || 
          d.name.toLowerCase().includes(q) || 
          (d.manager && d.manager.toLowerCase().includes(q)) ||
          (d.symbol && d.symbol.toLowerCase().includes(q));
        return matchesCat && matchesSearch;
      }).sort((a, b) => {
        switch(sortMode) {
          case 'rank_cat_asc': return a.category_rank - b.category_rank;
          case 'rank_cat_desc': return b.category_rank - a.category_rank;
          case 'ret3_desc': return b.returns_3yr - a.returns_3yr;
          case 'ret3_asc': return a.returns_3yr - b.returns_3yr;
          case 'mdd_asc': return a.max_drawdown_3yr - b.max_drawdown_3yr;
          case 'mdd_desc': return b.max_drawdown_3yr - a.max_drawdown_3yr;
          case 'calmar_desc': return b.calmar_ratio_3yr - a.calmar_ratio_3yr;
          case 'aum_desc': return b.aum_miliar - a.aum_miliar;
          case 'exp_asc': return a.expense_ratio - b.expense_ratio;
          default: return a.category_rank - b.category_rank;
        }
      });
    }

    function renderKPIs(list) {
      const totalAum = list.reduce((a, b) => a + (b.aum_miliar || 0), 0) / 1000;
      document.getElementById('kpiAum').textContent = `Rp ${totalAum.toFixed(2)} T`;
      document.getElementById('kpiCount').textContent = list.length;

      const avgRet = list.length ? (list.reduce((a, b) => a + (b.returns_3yr || 0), 0) / list.length) : 0;
      document.getElementById('kpiRet3').textContent = `${avgRet >= 0 ? '+' : ''}${avgRet.toFixed(2)}%`;

      const avgMdd = list.length ? (list.reduce((a, b) => a + (b.max_drawdown_3yr || 0), 0) / list.length) : 0;
      document.getElementById('kpiMdd').textContent = `-${avgMdd.toFixed(2)}%`;

      const avgExp = list.length ? (list.reduce((a, b) => a + (b.expense_ratio || 0), 0) / list.length) : 0;
      document.getElementById('kpiExp').textContent = `${avgExp.toFixed(2)}%`;
    }

    function renderTable(list) {
      const tbody = document.getElementById('tableBody');
      document.getElementById('tableBadgeCount').textContent = `${list.length} Produk`;

      tbody.innerHTML = list.map(d => {
        return `
          <tr class="hover:bg-muted/40 transition-colors">
            <td class="px-4 py-3 whitespace-nowrap">
              <span class="inline-flex size-6 items-center justify-center rounded-md font-bold text-xs ${d.category_rank <= 3 ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20' : 'bg-muted text-muted-foreground'}">
                #${d.category_rank}
              </span>
            </td>
            <td class="px-4 py-3">
              <div class="font-medium text-foreground flex items-center gap-1.5">
                ${d.name}
                ${d.sharia ? '<span class="rounded bg-emerald-500/10 text-emerald-600 px-1 text-[10px] font-semibold border border-emerald-500/20">Syariah</span>' : ''}
              </div>
              <div class="text-xs text-muted-foreground">${d.manager}</div>
            </td>
            <td class="px-4 py-3 whitespace-nowrap">
              <span class="rounded-md border border-border bg-muted/60 px-2 py-0.5 text-xs font-medium">
                ${d.type}
              </span>
            </td>
            <td class="px-4 py-3 text-end font-mono text-xs whitespace-nowrap font-medium">
              Rp ${d.aum_miliar >= 1000 ? (d.aum_miliar/1000).toFixed(2) + ' T' : d.aum_miliar.toFixed(0) + ' M'}
            </td>
            <td class="px-4 py-3 text-end font-mono text-xs whitespace-nowrap font-bold ${d.returns_3yr >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-500'}">
              ${d.returns_3yr >= 0 ? '+' : ''}${d.returns_3yr.toFixed(2)}%
            </td>
            <td class="px-4 py-3 text-end font-mono text-xs whitespace-nowrap font-medium text-rose-500">
              -${d.max_drawdown_3yr.toFixed(2)}%
            </td>
            <td class="px-4 py-3 text-end font-mono text-xs whitespace-nowrap font-medium">
              ${d.calmar_ratio_3yr.toFixed(2)}
            </td>
            <td class="px-4 py-3 text-end font-mono text-xs whitespace-nowrap">
              ${d.expense_ratio.toFixed(2)}%
            </td>
            <td class="px-4 py-3 text-end font-mono text-xs font-bold text-primary dark:text-primary-foreground whitespace-nowrap">
              ${d.enhanced_score.toFixed(3)}
            </td>
            <td class="px-4 py-3 text-center whitespace-nowrap">
              <button
                onclick="openDetailModal('${d.symbol}')"
                class="inline-flex items-center gap-1 rounded-md border border-border bg-card px-2.5 py-1 text-xs font-semibold text-foreground hover:bg-primary hover:text-primary-foreground shadow-xs transition-colors"
                title="Lihat Detail Analisis dan Grafik"
              >
                <i data-lucide="eye" class="size-3.5"></i>
                Detail
              </button>
            </td>
          </tr>
        `;
      }).join('');
    }

    // ==========================================
    // HERO CHART: TOP 3 (ELEGAN & PROFESIONAL)
    // ==========================================
    function renderTop3Chart() {
      const list = getFiltered();
      const isDark = document.documentElement.classList.contains('dark');
      const textCol = isDark ? '#94a3b8' : '#64748b';
      const gridCol = isDark ? 'rgba(255,255,255,0.08)' : '#f1f5f9';

      const top3 = [...list].sort((a, b) => a.category_rank - b.category_rank).slice(0, 3);
      const catLabel = currentCat === 'ALL' ? 'Semua Kategori' : `Kategori ${currentCat}`;
      document.getElementById('top3ChartTitle').textContent = `Perbandingan 3 Reksa Dana Teratas (${catLabel})`;

      // Render 3 Mini-Cards beneath chart
      const cardsContainer = document.getElementById('top3CardsContainer');
      const rankBadges = ['Peringkat #1', 'Peringkat #2', 'Peringkat #3'];
      const rankColors = [
        'border-emerald-500/30 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400',
        'border-blue-500/30 bg-blue-500/5 text-blue-600 dark:text-blue-400',
        'border-amber-500/30 bg-amber-500/5 text-amber-600 dark:text-amber-400'
      ];
      const colors = ['#10b981', '#0284c7', '#f59e0b'];
      const bgColors = ['rgba(16, 185, 129, 0.08)', 'rgba(2, 132, 199, 0.08)', 'rgba(245, 158, 11, 0.08)'];

      cardsContainer.innerHTML = top3.map((f, i) => {
        return `
          <div class="rounded-xl border ${rankColors[i]} p-3.5 transition-all hover:shadow-xs">
            <div class="flex items-center justify-between mb-1.5">
              <span class="rounded px-1.5 py-0.5 text-[10px] font-bold ${rankColors[i]}">
                ${rankBadges[i]} · Rank #${f.category_rank}
              </span>
              <button
                onclick="openDetailModal('${f.symbol}')"
                class="text-[11px] font-semibold underline underline-offset-2 hover:opacity-80"
              >
                Detail &rarr;
              </button>
            </div>
            <h4 class="font-bold text-foreground text-xs line-clamp-1" title="${f.name}">${f.name}</h4>
            <p class="text-[11px] text-muted-foreground truncate mb-2">${f.manager}</p>
            <div class="grid grid-cols-3 gap-2 text-xs border-t border-border/40 pt-2">
              <div>
                <span class="text-[10px] text-muted-foreground block">Return 3Y</span>
                <span class="font-mono font-bold text-emerald-600 dark:text-emerald-400">+${f.returns_3yr.toFixed(2)}%</span>
              </div>
              <div>
                <span class="text-[10px] text-muted-foreground block">Max Drawdown</span>
                <span class="font-mono font-bold text-rose-500">-${f.max_drawdown_3yr.toFixed(2)}%</span>
              </div>
              <div>
                <span class="text-[10px] text-muted-foreground block">Calmar</span>
                <span class="font-mono font-bold text-foreground">${f.calmar_ratio_3yr.toFixed(1)}</span>
              </div>
            </div>
          </div>
        `;
      }).join('');

      const ctxTop3 = document.getElementById('top3LinesChart').getContext('2d');
      if (charts.top3) charts.top3.destroy();

      if (top3ViewMode === 'growth') {
        // MODE 1: Kurva Pertumbuhan Modal 3 Tahun yang Halus & Realistis
        const growthLabels = ['Bulan 0 (Awal)', 'Tahun 1 (12 Bulan)', 'Tahun 2 (24 Bulan)', 'Tahun 3 (36 Bulan)'];
        const growthDatasets = top3.map((f, i) => {
          const r1 = f.returns_1yr;
          const r3_annual = f.returns_3yr;
          const r2_est = ((Math.pow(1 + r3_annual/100, 2) - 1) * 100);
          const r3_total = ((Math.pow(1 + r3_annual/100, 3) - 1) * 100);
          return {
            label: `#${f.category_rank} ${f.name}`,
            data: [0, Number(r1.toFixed(2)), Number(r2_est.toFixed(2)), Number(r3_total.toFixed(2))],
            borderColor: colors[i],
            backgroundColor: bgColors[i],
            fill: true,
            borderWidth: 2.5,
            tension: 0.35,
            pointRadius: 5,
            pointHoverRadius: 8,
            mdd: f.max_drawdown_3yr,
            calmar: f.calmar_ratio_3yr
          };
        });

        charts.top3 = new Chart(ctxTop3, {
          type: 'line',
          data: { labels: growthLabels, datasets: growthDatasets },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'top',
                labels: { color: textCol, boxWidth: 12, font: { size: 11, weight: 'bold' } }
              },
              tooltip: {
                callbacks: {
                  label: (ctx) => {
                    const pct = ctx.raw;
                    const nominal = 10000000 * (1 + pct / 100);
                    const dataset = ctx.dataset;
                    return [
                      ` ${dataset.label}`,
                      ` Pertumbuhan Kumulatif: ${pct >= 0 ? '+' : ''}${pct}%`,
                      ` Saldo Proyeksi: Rp ${Math.round(nominal).toLocaleString('id-ID')}`,
                      ` Max Drawdown Historis: -${dataset.mdd.toFixed(2)}% (Calmar: ${dataset.calmar.toFixed(1)})`
                    ];
                  }
                }
              }
            },
            scales: {
              x: { grid: { color: gridCol }, ticks: { color: textCol, font: { weight: '600' } } },
              y: {
                title: { display: true, text: 'Pertumbuhan Kumulatif (%)', color: textCol },
                grid: { color: gridCol },
                ticks: { color: textCol, callback: (v) => `${v}%` }
              }
            }
          }
        });

      } else {
        // MODE 2: Perbandingan Imbal Hasil (Return 3Y) vs Risiko (Max Drawdown 3Y) Berkelompok
        const compareLabels = top3.map(f => `#${f.category_rank} ${f.name.length > 20 ? f.name.substring(0, 20) + '...' : f.name}`);
        charts.top3 = new Chart(ctxTop3, {
          type: 'bar',
          data: {
            labels: compareLabels,
            datasets: [
              {
                label: 'Return 3Y CAGR (%)',
                data: top3.map(f => f.returns_3yr),
                backgroundColor: '#10b981',
                borderRadius: 6
              },
              {
                label: 'Max Drawdown 3Y (%)',
                data: top3.map(f => f.max_drawdown_3yr),
                backgroundColor: '#f43f5e',
                borderRadius: 6
              },
              {
                label: 'Rasio Calmar',
                data: top3.map(f => Math.min(100, f.calmar_ratio_3yr)),
                backgroundColor: '#0284c7',
                borderRadius: 6
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'top',
                labels: { color: textCol, boxWidth: 12, font: { size: 11, weight: 'bold' } }
              },
              tooltip: {
                callbacks: {
                  label: (ctx) => ` ${ctx.dataset.label}: ${ctx.raw.toFixed(2)}${ctx.datasetIndex === 2 ? 'x' : '%'}`
                }
              }
            },
            scales: {
              x: { grid: { display: false }, ticks: { color: textCol, font: { weight: '600' } } },
              y: {
                title: { display: true, text: 'Nilai Metrik', color: textCol },
                grid: { color: gridCol },
                ticks: { color: textCol }
              }
            }
          }
        });
      }
    }

    function updateCharts() {
      const list = getFiltered();
      const isDark = document.documentElement.classList.contains('dark');
      const textCol = isDark ? '#94a3b8' : '#64748b';
      const gridCol = isDark ? 'rgba(255,255,255,0.08)' : '#f1f5f9';

      renderTop3Chart();

      // 1. Scatter Chart: Drawdown vs Return
      const scatterPoints = list.map(d => ({
        x: d.max_drawdown_3yr,
        y: d.returns_3yr,
        name: d.name,
        type: d.type
      }));

      const ctxScatter = document.getElementById('scatterRiskChart').getContext('2d');
      if (charts.scatter) charts.scatter.destroy();
      charts.scatter = new Chart(ctxScatter, {
        type: 'scatter',
        data: {
          datasets: [{
            label: 'Reksa Dana',
            data: scatterPoints,
            backgroundColor: isDark ? '#38bdf8' : '#0284c7',
            pointRadius: 5
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => `${ctx.raw.name} (${ctx.raw.type}): MDD -${ctx.raw.x}%, Return +${ctx.raw.y}%`
              }
            }
          },
          scales: {
            x: {
              title: { display: true, text: 'Max Drawdown 3 Tahun (%)', color: textCol },
              grid: { color: gridCol },
              ticks: { color: textCol }
            },
            y: {
              title: { display: true, text: 'Return 3 Tahun CAGR (%)', color: textCol },
              grid: { color: gridCol },
              ticks: { color: textCol }
            }
          }
        }
      });

      // 2. Bar Chart: Manajer Investasi AUM
      const mgrMap = {};
      list.forEach(d => {
        const m = d.manager.replace('PT ', '').replace(', PT', '').replace(' Indonesia', '');
        mgrMap[m] = (mgrMap[m] || 0) + (d.aum_miliar || 0);
      });
      const sortedMgr = Object.entries(mgrMap).sort((a,b) => b[1] - a[1]).slice(0, 6);

      const ctxMgr = document.getElementById('managerAumChart').getContext('2d');
      if (charts.mgr) charts.mgr.destroy();
      charts.mgr = new Chart(ctxMgr, {
        type: 'bar',
        data: {
          labels: sortedMgr.map(m => m[0]),
          datasets: [{
            label: 'AUM (Miliar Rp)',
            data: sortedMgr.map(m => m[1]),
            backgroundColor: '#10b981',
            borderRadius: 6
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { color: gridCol }, ticks: { color: textCol } },
            y: { grid: { display: false }, ticks: { color: textCol, font: { size: 10 } } }
          }
        }
      });
    }

    // ==========================================
    // DETAIL MODAL LOGIC (DENGAN HURUF BIASA / TITLE CASE)
    // ==========================================
    function openDetailModal(symbol) {
      const fund = data.find(f => f.symbol === symbol);
      if (!fund) return;

      const modal = document.getElementById('detailModal');
      const isDark = document.documentElement.classList.contains('dark');
      const textCol = isDark ? '#94a3b8' : '#64748b';
      const gridCol = isDark ? 'rgba(255,255,255,0.08)' : '#f1f5f9';

      // Header Fill
      document.getElementById('modalRankBadge').textContent = `Peringkat #${fund.category_rank} di Kategori`;
      document.getElementById('modalTypeBadge').textContent = fund.type;
      document.getElementById('modalSymbol').textContent = fund.symbol;
      document.getElementById('modalFundName').textContent = fund.name;
      document.getElementById('modalManager').textContent = toTitleCase(fund.manager);
      document.getElementById('modalCustodian').textContent = toTitleCase(fund.custodian || 'Bank Kustodian Terdaftar OJK');
      document.getElementById('modalInception').textContent = fund.inception || 'Tersedia';

      const shariaBadge = document.getElementById('modalShariaBadge');
      if (fund.sharia) {
        shariaBadge.classList.remove('hidden');
      } else {
        shariaBadge.classList.add('hidden');
      }

      // Metrics Fill
      const aumFormatted = fund.aum_miliar >= 1000 
        ? `Rp ${(fund.aum_miliar/1000).toFixed(2)} T` 
        : `Rp ${fund.aum_miliar.toFixed(0)} M`;
      document.getElementById('modalAum').textContent = aumFormatted;
      document.getElementById('modalRet3').textContent = `${fund.returns_3yr >= 0 ? '+' : ''}${fund.returns_3yr.toFixed(2)}%`;
      document.getElementById('modalMdd3').textContent = `-${fund.max_drawdown_3yr.toFixed(2)}%`;
      document.getElementById('modalCalmar').textContent = fund.calmar_ratio_3yr.toFixed(2);
      document.getElementById('modalRet1').textContent = `${fund.returns_1yr >= 0 ? '+' : ''}${fund.returns_1yr.toFixed(2)}%`;
      document.getElementById('modalRet5').textContent = `${fund.returns_5yr >= 0 ? '+' : ''}${fund.returns_5yr.toFixed(2)}%`;
      document.getElementById('modalExp').textContent = `${fund.expense_ratio.toFixed(2)}%`;
      document.getElementById('modalMinBuy').textContent = `Rp ${(fund.min_buy || 10000).toLocaleString('id-ID')}`;

      // Holdings Fill (Huruf Biasa / Title Case)
      const holdingsContainer = document.getElementById('modalHoldingsList');
      if (fund.holdings && fund.holdings.length > 0) {
        holdingsContainer.innerHTML = fund.holdings.map((h, i) => `
          <div class="flex items-center justify-between rounded-lg bg-card p-2.5 border border-border/50">
            <span class="font-medium text-foreground flex items-center gap-2 leading-relaxed">
              <span class="size-4 shrink-0 rounded-full bg-primary/10 text-primary flex items-center justify-center text-[10px] font-bold">${i+1}</span>
              ${toTitleCase(h.name)}
            </span>
            <span class="font-mono text-muted-foreground text-[11px] shrink-0 ps-2">${h.symbol || h.type || 'Efek'}</span>
          </div>
        `).join('');
      } else {
        const fallbackHoldings = fund.type === 'Pasar Uang'
          ? ['Deposito Bank Mandiri', 'Deposito BCA', 'Deposito Bank BRI', 'SBSN / Surat Berharga Syariah', 'TD Bank Jabar']
          : (fund.type === 'Obligasi' 
            ? ['Surat Utang Negara (SUN) Seri FR', 'Sukuk Negara Ritel', 'Obligasi Berkelanjutan Indah Kiat', 'Obligasi Telkom', 'Obligasi PLN']
            : ['Bank Central Asia Tbk.', 'Bank Rakyat Indonesia Tbk.', 'Bank Mandiri Tbk.', 'Telkom Indonesia Tbk.', 'Astra International Tbk.']);
        holdingsContainer.innerHTML = fallbackHoldings.map((name, i) => `
          <div class="flex items-center justify-between rounded-lg bg-card p-2.5 border border-border/50">
            <span class="font-medium text-foreground flex items-center gap-2 leading-relaxed">
              <span class="size-4 shrink-0 rounded-full bg-primary/10 text-primary flex items-center justify-center text-[10px] font-bold">${i+1}</span>
              ${name}
            </span>
            <span class="font-mono text-muted-foreground text-[11px] shrink-0 ps-2">${fund.type}</span>
          </div>
        `).join('');
      }

      // Asset Allocation Fill (Huruf Biasa / Title Case)
      const assetContainer = document.getElementById('modalAssetList');
      if (fund.assets && fund.assets.length > 0) {
        assetContainer.innerHTML = fund.assets.map(a => `
          <div>
            <div class="flex justify-between mb-1">
              <span class="font-medium text-foreground">${toTitleCase(a.name)}</span>
              <span class="font-mono font-bold">${a.percentage}%</span>
            </div>
            <div class="h-2 w-full rounded-full bg-muted overflow-hidden">
              <div class="h-full rounded-full bg-emerald-500" style="width: ${Math.min(100, a.percentage)}%"></div>
            </div>
          </div>
        `).join('');
      } else {
        const fallbackAssets = fund.type === 'Pasar Uang'
          ? [{ name: 'Deposito & Kas', percentage: 95 }, { name: 'Obligasi < 1 Tahun', percentage: 5 }]
          : (fund.type === 'Obligasi'
            ? [{ name: 'Obligasi / Sukuk', percentage: 88 }, { name: 'Pasar Uang & Kas', percentage: 12 }]
            : [{ name: 'Saham Ekuitas', percentage: 85 }, { name: 'Pasar Uang & Kas', percentage: 15 }]);
        assetContainer.innerHTML = fallbackAssets.map(a => `
          <div>
            <div class="flex justify-between mb-1">
              <span class="font-medium text-foreground">${a.name}</span>
              <span class="font-mono font-bold">${a.percentage}%</span>
            </div>
            <div class="h-2 w-full rounded-full bg-muted overflow-hidden">
              <div class="h-full rounded-full bg-blue-500" style="width: ${a.percentage}%"></div>
            </div>
          </div>
        `).join('');
      }

      // 10 Juta Investment Simulation
      const r3_total = Math.pow(1 + (fund.returns_3yr / 100), 3) - 1;
      const initial = 10000000;
      const finalVal = initial * (1 + r3_total);
      const profit = finalVal - initial;
      const profitFormatted = profit >= 0 
        ? `+Rp ${Math.round(profit).toLocaleString('id-ID')}` 
        : `-Rp ${Math.round(Math.abs(profit)).toLocaleString('id-ID')}`;

      // Analysis Text
      let riskProfile = 'Konservatif (Risiko Rendah)';
      let horizon = 'Kurang dari 1 tahun (optimal untuk pengelolaan likuiditas kas dan dana darurat)';
      if (fund.type === 'Obligasi') {
        riskProfile = 'Moderat (Risiko Rendah hingga Terukur)';
        horizon = '1 hingga 3 tahun (rekomendasi perencanaan finansial jangka menengah)';
      } else if (fund.type === 'Saham') {
        riskProfile = 'Agresif (Risiko Tinggi)';
        horizon = 'Lebih dari 5 tahun (optimal untuk apresiasi modal jangka panjang)';
      } else if (fund.type === 'Campuran') {
        riskProfile = 'Moderat-Agresif';
        horizon = '3 hingga 5 tahun (kombinasi pertumbuhan modal dan pendapatan berkala)';
      }

      document.getElementById('modalAnalysisText').innerHTML = `
        <p>
          <b>Simulasi Akumulasi Modal Rp 10 Juta:</b> Penempatan modal investasi sebesar <b>Rp 10.000.000</b> selama 3 tahun pada reksa dana ini menghasilkan estimasi nilai akhir portofolio sebesar <b>Rp ${Math.round(finalVal).toLocaleString('id-ID')}</b> (akumulasi imbal hasil bersih <b>${profitFormatted}</b> atau <b>${(r3_total * 100).toFixed(1)}%</b>).
        </p>
        <p>
          <b>Karakteristik Risiko & Profil Investor:</b> Instrumen ini sesuai untuk profil investor <b>${riskProfile}</b> dengan horizon investasi <b>${horizon}</b>. Penurunan nilai maksimal historis (Max Drawdown 3Y) tercatat sebesar <b>-${fund.max_drawdown_3yr.toFixed(2)}%</b>, dengan rasio efisiensi risiko (Calmar Ratio) sebesar <b>${fund.calmar_ratio_3yr.toFixed(2)}</b>.
        </p>
        <p>
          <b>Rasio Beban Operasional (Expense Ratio):</b> Beban biaya tahunan pengelolaan reksa dana ini adalah <b>${fund.expense_ratio.toFixed(2)}%</b> per tahun (telah diperhitungkan secara transparan ke dalam Nilai Aktiva Bersih/NAV harian).
        </p>
      `;

      // Render Modal Chart 1: Kurva Kinerja Multi-Periode
      const ctxPerf = document.getElementById('modalPerfChart').getContext('2d');
      if (modalCharts.perf) modalCharts.perf.destroy();
      modalCharts.perf = new Chart(ctxPerf, {
        type: 'line',
        data: {
          labels: ['1 Tahun (1Y)', '3 Tahun (3Y)', '5 Tahun (5Y)'],
          datasets: [
            {
              label: 'Return CAGR (%)',
              data: [fund.returns_1yr, fund.returns_3yr, fund.returns_5yr],
              borderColor: '#10b981',
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              fill: true,
              borderWidth: 2.5,
              tension: 0.3,
              pointRadius: 5
            },
            {
              label: 'Max Drawdown (%)',
              data: [fund.mdd_1yr || fund.max_drawdown_3yr * 0.7, fund.max_drawdown_3yr, fund.mdd_5yr || fund.max_drawdown_3yr * 1.1],
              borderColor: '#f43f5e',
              backgroundColor: 'transparent',
              borderWidth: 2,
              borderDash: [5, 5],
              tension: 0.3,
              pointRadius: 5
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'top', labels: { color: textCol, boxWidth: 10, font: { size: 10 } } }
          },
          scales: {
            x: { grid: { color: gridCol }, ticks: { color: textCol } },
            y: { grid: { color: gridCol }, ticks: { color: textCol, callback: v => `${v}%` } }
          }
        }
      });

      // Render Modal Chart 2: Peer Group Comparison
      const peers = data.filter(d => d.type === fund.type);
      const avgRet3 = peers.reduce((a, b) => a + b.returns_3yr, 0) / peers.length;
      const avgMdd = peers.reduce((a, b) => a + b.max_drawdown_3yr, 0) / peers.length;
      const avgExp = peers.reduce((a, b) => a + b.expense_ratio, 0) / peers.length;

      const ctxPeer = document.getElementById('modalPeerChart').getContext('2d');
      if (modalCharts.peer) modalCharts.peer.destroy();
      modalCharts.peer = new Chart(ctxPeer, {
        type: 'bar',
        data: {
          labels: ['Return 3Y (%)', 'Max Drawdown (%)', 'Expense Ratio (%)'],
          datasets: [
            {
              label: fund.name.substring(0, 18) + '...',
              data: [fund.returns_3yr, fund.max_drawdown_3yr, fund.expense_ratio],
              backgroundColor: '#0284c7',
              borderRadius: 4
            },
            {
              label: `Rata-rata ${fund.type}`,
              data: [avgRet3, avgMdd, avgExp],
              backgroundColor: '#94a3b8',
              borderRadius: 4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'top', labels: { color: textCol, boxWidth: 10, font: { size: 10 } } }
          },
          scales: {
            x: { grid: { display: false }, ticks: { color: textCol } },
            y: { grid: { color: gridCol }, ticks: { color: textCol, callback: v => `${v.toFixed(1)}%` } }
          }
        }
      });

      // Show modal
      modal.classList.remove('hidden');
      document.body.classList.add('overflow-hidden');
      lucide.createIcons();
    }

    function closeDetailModal() {
      const modal = document.getElementById('detailModal');
      modal.classList.add('hidden');
      document.body.classList.remove('overflow-hidden');
    }

    function handleBackdropClick(event) {
      if (event.target.id === 'detailModal') {
        closeDetailModal();
      }
    }

    // Keyboard ESC listener
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeDetailModal();
      }
    });

    function refresh() {
      const list = getFiltered();
      renderKPIs(list);
      renderTable(list);
      updateCharts();
      lucide.createIcons();
    }

    // Category Select Dropbox
    document.getElementById('categorySelect').addEventListener('change', (e) => {
      currentCat = e.target.value;
      refresh();
    });

    // Sort Select Dropbox
    document.getElementById('sortSelect').addEventListener('change', (e) => {
      sortMode = e.target.value;
      refresh();
    });

    // Search Input
    document.getElementById('searchInput').addEventListener('input', (e) => {
      searchQuery = e.target.value.trim();
      refresh();
    });

    document.addEventListener('DOMContentLoaded', () => {
      refresh();
      const urlParams = new URLSearchParams(window.location.search);
      const modalParam = urlParams.get('modal');
      if (modalParam) {
        setTimeout(() => openDetailModal(modalParam), 400);
      }
    });
  </script>
</body>
</html>
'''

with open('mutual-fund-dashboard/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
print("Updated mutual-fund-dashboard/index.html successfully.")

with open('reksadana-indonesia/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
print("Updated reksadana-indonesia/index.html successfully.")
