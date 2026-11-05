import json
import os

with open('reksadana-indonesia/data.js', 'r', encoding='utf-8') as f:
    js_data = f.read()

html_content = f"""<!DOCTYPE html>
<html lang="id" class="font-inter">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Analisis Reksa Dana Indonesia | Next-Gen Institutional Scoring</title>
  
  <!-- Inter Font -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          fontFamily: {{ inter: ['Inter', 'sans-serif'] }},
          colors: {{
            border: 'var(--border)',
            input: 'var(--input)',
            ring: 'var(--ring)',
            background: 'var(--background)',
            foreground: 'var(--foreground)',
            primary: {{ DEFAULT: 'var(--primary)', foreground: 'var(--primary-foreground)' }},
            muted: {{ DEFAULT: 'var(--muted)', foreground: 'var(--muted-foreground)' }},
            accent: {{ DEFAULT: 'var(--accent)', foreground: 'var(--accent-foreground)' }},
            card: {{ DEFAULT: 'var(--card)', foreground: 'var(--card-foreground)' }},
          }}
        }}
      }}
    }}
  </script>

  <!-- Lucide & Chart.js -->
  <script src="https://unpkg.com/lucide@latest"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

  <style>
    :root {{
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
    }}
    .dark {{
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
    }}
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
          <div class="flex items-center gap-2">
            <span class="text-base font-bold tracking-tight">Reksa Dana Indonesia Analytics</span>
            <span class="rounded-md border border-emerald-200 bg-emerald-100/50 px-1.5 py-0.5 text-[11px] font-semibold text-emerald-800 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300">Model Baru (Peer-Group)</span>
          </div>
          <p class="text-xs text-muted-foreground">146 Reksa Dana Terdaftar OJK & Bibit · Analisis Risiko & Return Riil</p>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <div class="relative hidden sm:block w-64">
          <i data-lucide="search" class="absolute start-3 top-2.5 size-4 text-muted-foreground"></i>
          <input 
            type="text" 
            id="searchInput" 
            placeholder="Cari nama produk atau Manajer Investasi..." 
            class="h-9 w-full rounded-md border border-input bg-transparent pe-10 ps-9 text-sm shadow-xs placeholder:text-muted-foreground focus:border-ring focus:outline-none focus:ring-[3px] focus:ring-ring/40 dark:bg-input/20"
          >
          <kbd class="pointer-events-none absolute end-2.5 top-2 inline-flex h-5 items-center rounded border border-border bg-muted px-1.5 font-mono text-[10px] text-muted-foreground">⌘K</kbd>
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
    
    <!-- Title and Filter Navigation -->
    <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <div>
        <h1 class="text-2xl font-bold tracking-tight">Evaluasi Kinerja Reksa Dana Pasar Indonesia</h1>
        <p class="text-sm text-muted-foreground">Penerapan model evaluasi teroptimasi: <b>Anti-Bias Kategori</b>, <b>Max Drawdown</b>, dan <b>Calmar Ratio</b></p>
      </div>

      <!-- Segmented Category Pills -->
      <div class="flex flex-wrap items-center gap-1.5" id="categoryTabs">
        <button class="cat-pill active rounded-lg border border-transparent bg-primary px-3 py-1.5 text-xs font-semibold text-primary-foreground shadow-xs transition-all" data-cat="ALL">
          Semua (146)
        </button>
        <button class="cat-pill rounded-lg border border-border bg-card px-3 py-1.5 text-xs font-semibold text-muted-foreground hover:bg-accent transition-all" data-cat="Pasar Uang">
          💵 Pasar Uang (36)
        </button>
        <button class="cat-pill rounded-lg border border-border bg-card px-3 py-1.5 text-xs font-semibold text-muted-foreground hover:bg-accent transition-all" data-cat="Obligasi">
          📑 Obligasi (46)
        </button>
        <button class="cat-pill rounded-lg border border-border bg-card px-3 py-1.5 text-xs font-semibold text-muted-foreground hover:bg-accent transition-all" data-cat="Saham">
          📈 Saham (46)
        </button>
        <button class="cat-pill rounded-lg border border-border bg-card px-3 py-1.5 text-xs font-semibold text-muted-foreground hover:bg-accent transition-all" data-cat="Campuran">
          ⚖️ Campuran (11)
        </button>
      </div>
    </div>

    <!-- KPI Grid -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      
      <div class="rounded-xl border border-border bg-card p-5 text-card-foreground shadow-xs">
        <div class="flex items-center justify-between pb-2">
          <span class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Total Dana Kelolaan (AUM)</span>
          <div class="flex size-7 items-center justify-center rounded-md bg-blue-500/10 text-blue-600 dark:text-blue-400">
            <i data-lucide="landmark" class="size-4"></i>
          </div>
        </div>
        <div class="text-2xl font-bold tracking-tight" id="kpiAum">Rp 0 Triliun</div>
        <p class="text-xs text-muted-foreground mt-1">Total aset dari <b id="kpiCount">146</b> reksa dana aktif</p>
      </div>

      <div class="rounded-xl border border-border bg-card p-5 text-card-foreground shadow-xs">
        <div class="flex items-center justify-between pb-2">
          <span class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Rata-rata Return 3 Tahun</span>
          <div class="flex size-7 items-center justify-center rounded-md bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
            <i data-lucide="trending-up" class="size-4"></i>
          </div>
        </div>
        <div class="text-2xl font-bold tracking-tight text-emerald-600 dark:text-emerald-400" id="kpiRet3">0.0%</div>
        <p class="text-xs text-muted-foreground mt-1">CAGR 3Y di kategori terpilih</p>
      </div>

      <div class="rounded-xl border border-border bg-card p-5 text-card-foreground shadow-xs">
        <div class="flex items-center justify-between pb-2">
          <span class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Rata-rata Max Drawdown</span>
          <div class="flex size-7 items-center justify-center rounded-md bg-rose-500/10 text-rose-600 dark:text-rose-400">
            <i data-lucide="shield-alert" class="size-4"></i>
          </div>
        </div>
        <div class="text-2xl font-bold tracking-tight text-rose-600 dark:text-rose-400" id="kpiMdd">0.0%</div>
        <p class="text-xs text-muted-foreground mt-1">Kedalaman koreksi terburuk 3 tahun</p>
      </div>

      <div class="rounded-xl border border-border bg-card p-5 text-card-foreground shadow-xs">
        <div class="flex items-center justify-between pb-2">
          <span class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Rata-rata Expense Ratio</span>
          <div class="flex size-7 items-center justify-center rounded-md bg-purple-500/10 text-purple-600 dark:text-purple-400">
            <i data-lucide="percent" class="size-4"></i>
          </div>
        </div>
        <div class="text-2xl font-bold tracking-tight text-foreground" id="kpiExp">0.0%</div>
        <p class="text-xs text-muted-foreground mt-1">Biaya tahunan pengelolaan investasi</p>
      </div>

    </div>

    <!-- Charts Grid -->
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

    <!-- Comparison Callout: Model Lama vs Model Baru -->
    <div class="rounded-xl border border-amber-300/40 bg-amber-50/50 dark:border-amber-500/20 dark:bg-amber-500/5 p-5 text-sm">
      <div class="flex items-start gap-3">
        <i data-lucide="lightbulb" class="size-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5"></i>
        <div>
          <h4 class="font-semibold text-amber-900 dark:text-amber-200">Perbedaan Kunci: Mengapa Model yang Disempurnakan Jauh Lebih Adil?</h4>
          <p class="text-xs text-amber-800/90 dark:text-amber-300/80 mt-1 leading-relaxed">
            Pada <b>Model Evaluasi Konvensional</b>, reksa dana pasar uang seperti <i>Majoris Pasar Uang Syariah</i> dan <i>Trimegah Kas Syariah</i> terdepak nilainya karena return 5%-nya kalah telak oleh reksa dana saham luar negeri yang naik 30%. Padahal, untuk reksa dana pasar uang, return 5% dengan <b>Drawdown 0.00%</b> adalah performa sempurna! 
            <br>Dengan <b>Model Baru (Peer-Group Segmentation)</b>, setiap reksa dana dinilai adil di habitat kelas asetnya masing-masing.
          </p>
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
          <p class="text-xs text-muted-foreground">Peringkat dihitung berdasarkan model skor multi-kriteria terbobot per kategori</p>
        </div>

        <div class="flex items-center gap-2">
          <select id="sortSelect" class="h-8 rounded-md border border-input bg-transparent px-2 text-xs font-medium focus:outline-none dark:bg-input/20">
            <option value="rank_cat">Urutkan: Rank Kategori (Terbaik)</option>
            <option value="score_desc">Skor Enhanced Tertinggi</option>
            <option value="ret3_desc">Return 3Y Tertinggi</option>
            <option value="mdd_asc">Max Drawdown Terendah (Paling Aman)</option>
            <option value="calmar_desc">Calmar Ratio Tertinggi</option>
            <option value="aum_desc">AUM Terbesar</option>
            <option value="exp_asc">Expense Ratio Terendah</option>
          </select>
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
              <th class="h-10 px-4 text-end font-semibold">Skor Model Baru</th>
            </tr>
          </thead>
          <tbody id="tableBody" class="divide-y divide-border">
          </tbody>
        </table>
      </div>

    </div>

  </main>

  <footer class="border-t border-border mt-12 py-6 text-center text-xs text-muted-foreground">
    <p>Pengujian Model Kuantitatif Reksa Dana Indonesia · Data Historis Bibit & Otoritas Jasa Keuangan (OJK)</p>
  </footer>

  <!-- Embedded Indonesian Data -->
  <script>
{js_data}
  </script>

  <script>
    const data = window.INDONESIA_REKSADANA_DATA || [];
    let currentCat = 'ALL';
    let searchQuery = '';
    let sortMode = 'rank_cat';
    let charts = {{}};

    // Theme toggle
    const themeBtn = document.getElementById('themeToggle');
    themeBtn.addEventListener('click', () => {{
      document.documentElement.classList.toggle('dark');
      updateCharts();
    }});

    function getFiltered() {{
      return data.filter(d => {{
        const matchesCat = currentCat === 'ALL' || d.type === currentCat;
        const q = searchQuery.toLowerCase();
        const matchesSearch = !q || 
          d.name.toLowerCase().includes(q) || 
          (d.manager && d.manager.toLowerCase().includes(q));
        return matchesCat && matchesSearch;
      }}).sort((a, b) => {{
        switch(sortMode) {{
          case 'rank_cat': return a.category_rank - b.category_rank;
          case 'score_desc': return b.enhanced_score - a.enhanced_score;
          case 'ret3_desc': return b.returns_3yr - a.returns_3yr;
          case 'mdd_asc': return a.max_drawdown_3yr - b.max_drawdown_3yr;
          case 'calmar_desc': return b.calmar_ratio_3yr - a.calmar_ratio_3yr;
          case 'aum_desc': return b.aum_miliar - a.aum_miliar;
          case 'exp_asc': return a.expense_ratio - b.expense_ratio;
          default: return a.category_rank - b.category_rank;
        }}
      }});
    }}

    function renderKPIs(list) {{
      const totalAum = list.reduce((a, b) => a + (b.aum_miliar || 0), 0) / 1000; // in Triliun
      document.getElementById('kpiAum').textContent = `Rp ${{totalAum.toFixed(2)}} T`;
      document.getElementById('kpiCount').textContent = list.length;

      const avgRet = list.length ? (list.reduce((a, b) => a + (b.returns_3yr || 0), 0) / list.length) : 0;
      document.getElementById('kpiRet3').textContent = `${{avgRet >= 0 ? '+' : ''}}${{avgRet.toFixed(2)}}%`;

      const avgMdd = list.length ? (list.reduce((a, b) => a + (b.max_drawdown_3yr || 0), 0) / list.length) : 0;
      document.getElementById('kpiMdd').textContent = `-${{avgMdd.toFixed(2)}}%`;

      const avgExp = list.length ? (list.reduce((a, b) => a + (b.expense_ratio || 0), 0) / list.length) : 0;
      document.getElementById('kpiExp').textContent = `${{avgExp.toFixed(2)}}%`;
    }}

    function renderTable(list) {{
      const tbody = document.getElementById('tableBody');
      document.getElementById('tableBadgeCount').textContent = `${{list.length}} Produk`;

      tbody.innerHTML = list.map(d => {{
        return `
          <tr class="hover:bg-muted/40 transition-colors">
            <td class="px-4 py-3 whitespace-nowrap">
              <span class="inline-flex size-6 items-center justify-center rounded-md font-bold text-xs ${{d.category_rank <= 3 ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400' : 'bg-muted text-muted-foreground'}}">
                #${{d.category_rank}}
              </span>
            </td>
            <td class="px-4 py-3">
              <div class="font-medium text-foreground flex items-center gap-1.5">
                ${{d.name}}
                ${{d.sharia ? '<span class="rounded bg-emerald-500/10 text-emerald-600 px-1 text-[10px] font-semibold">Syariah</span>' : ''}}
              </div>
              <div class="text-xs text-muted-foreground">${{d.manager}}</div>
            </td>
            <td class="px-4 py-3 whitespace-nowrap">
              <span class="rounded-md border border-border bg-muted/60 px-2 py-0.5 text-xs font-medium">
                ${{d.type}}
              </span>
            </td>
            <td class="px-4 py-3 text-end font-mono text-xs whitespace-nowrap font-medium">
              Rp ${{d.aum_miliar >= 1000 ? (d.aum_miliar/1000).toFixed(2) + ' T' : d.aum_miliar.toFixed(0) + ' M'}}
            </td>
            <td class="px-4 py-3 text-end font-mono text-xs whitespace-nowrap font-bold ${{d.returns_3yr >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-500'}}">
              ${{d.returns_3yr >= 0 ? '+' : ''}}${{d.returns_3yr.toFixed(2)}}%
            </td>
            <td class="px-4 py-3 text-end font-mono text-xs whitespace-nowrap font-medium text-rose-500">
              -${{d.max_drawdown_3yr.toFixed(2)}}%
            </td>
            <td class="px-4 py-3 text-end font-mono text-xs whitespace-nowrap font-medium">
              ${{d.calmar_ratio_3yr.toFixed(2)}}
            </td>
            <td class="px-4 py-3 text-end font-mono text-xs whitespace-nowrap">
              ${{d.expense_ratio.toFixed(2)}}%
            </td>
            <td class="px-4 py-3 text-end font-mono text-xs font-bold text-primary dark:text-primary-foreground whitespace-nowrap">
              ${{d.enhanced_score.toFixed(3)}}
            </td>
          </tr>
        `;
      }}).join('');
    }}

    function updateCharts() {{
      const list = getFiltered();
      const isDark = document.documentElement.classList.contains('dark');
      const textCol = isDark ? '#94a3b8' : '#64748b';
      const gridCol = isDark ? 'rgba(255,255,255,0.08)' : '#f1f5f9';

      // 1. Scatter Chart: Drawdown vs Return
      const scatterPoints = list.map(d => ({{
        x: d.max_drawdown_3yr,
        y: d.returns_3yr,
        name: d.name,
        type: d.type
      }}));

      const ctxScatter = document.getElementById('scatterRiskChart').getContext('2d');
      if (charts.scatter) charts.scatter.destroy();
      charts.scatter = new Chart(ctxScatter, {{
        type: 'scatter',
        data: {{
          datasets: [{{
            label: 'Reksa Dana',
            data: scatterPoints,
            backgroundColor: isDark ? '#38bdf8' : '#0284c7',
            pointRadius: 5
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{
            legend: {{ display: false }},
            tooltip: {{
              callbacks: {{
                label: (ctx) => `${{ctx.raw.name}} (${{ctx.raw.type}}): MDD -${{ctx.raw.x}}%, Return +${{ctx.raw.y}}%`
              }}
            }}
          }},
          scales: {{
            x: {{
              title: {{ display: true, text: 'Max Drawdown 3 Tahun (%)', color: textCol }},
              grid: {{ color: gridCol }},
              ticks: {{ color: textCol }}
            }},
            y: {{
              title: {{ display: true, text: 'Return 3 Tahun CAGR (%)', color: textCol }},
              grid: {{ color: gridCol }},
              ticks: {{ color: textCol }}
            }}
          }}
        }}
      }});

      // 2. Bar Chart: Manajer Investasi AUM
      const mgrMap = {{}};
      list.forEach(d => {{
        const m = d.manager.replace('PT ', '').replace(', PT', '').replace(' Indonesia', '');
        mgrMap[m] = (mgrMap[m] || 0) + (d.aum_miliar || 0);
      }});
      const sortedMgr = Object.entries(mgrMap).sort((a,b) => b[1] - a[1]).slice(0, 6);

      const ctxMgr = document.getElementById('managerAumChart').getContext('2d');
      if (charts.mgr) charts.mgr.destroy();
      charts.mgr = new Chart(ctxMgr, {{
        type: 'bar',
        data: {{
          labels: sortedMgr.map(m => m[0]),
          datasets: [{{
            label: 'AUM (Miliar Rp)',
            data: sortedMgr.map(m => m[1]),
            backgroundColor: '#10b981',
            borderRadius: 6
          }}]
        }},
        options: {{
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ display: false }} }},
          scales: {{
            x: {{ grid: {{ color: gridCol }}, ticks: {{ color: textCol }} }},
            y: {{ grid: {{ display: false }}, ticks: {{ color: textCol, font: {{ size: 10 }} }} }}
          }}
        }}
      }});
    }}

    function refresh() {{
      const list = getFiltered();
      renderKPIs(list);
      renderTable(list);
      updateCharts();
      lucide.createIcons();
    }}

    // Category Tabs
    document.querySelectorAll('.cat-pill').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.cat-pill').forEach(b => {{
          b.classList.remove('active', 'bg-primary', 'text-primary-foreground', 'border-transparent');
          b.classList.add('bg-card', 'text-muted-foreground', 'border-border');
        }});
        btn.classList.add('active', 'bg-primary', 'text-primary-foreground', 'border-transparent');
        btn.classList.remove('bg-card', 'text-muted-foreground', 'border-border');
        currentCat = btn.dataset.cat;
        refresh();
      }});
    }});

    // Search & Sort
    document.getElementById('searchInput').addEventListener('input', (e) => {{
      searchQuery = e.target.value.trim();
      refresh();
    }});
    document.getElementById('sortSelect').addEventListener('change', (e) => {{
      sortMode = e.target.value;
      refresh();
    }});

    document.addEventListener('DOMContentLoaded', () => {{
      refresh();
    }});
  </script>
</body>
</html>
"""

with open('reksadana-indonesia/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("reksadana-indonesia/index.html generated successfully!")
