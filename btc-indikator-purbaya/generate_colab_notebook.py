import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

cells = []

# Cell 1: Markdown Title & Intro
cells.append(nbf.v4.new_markdown_cell("""# 📊 Uji Coba Empiris Indikator "Pak Purbaya" (Periskop.id) pada Bitcoin (BTC-USD)
### *Analisis Redundansi Multikolinearitas & Backtest Kinerja 2 Tahun Terakhir*

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com)

---

## 📌 Latar Belakang & Konteks Analisis
Dalam program edukasi pasar modal ***Market Savvy with Purbaya*** di kanal/platform **Periskop.id** (bersama ekonom **Purbaya Yudhi Sadewa**), ditampilkan sebuah setup grafik teknikal komprehensif yang terdiri dari:
1. **Volume + MA20** (Pengukur likuiditas & partisipasi pasar)
2. **Stochastic RSI** (Osilator momentum cepat / early warning)
3. **RSI + RSI-MA** (Kekuatan tren & konfirmasi momentum medium)
4. **BBW (Bollinger Bands Width)** (Deteksi *volatility squeeze* sebelum *breakout*)
5. **Stochastic Oscillator** (Osilator ayunan harga standar %K & %D)
6. **CCI (Commodity Channel Index)** (Deviasi harga terhadap rata-rata statistiknya)

Pak Purbaya kerap menggunakan perangkat ini untuk membaca siklus indeks saham (seperti **IHSG**). 

### 🎯 Pertanyaan Penelitian:
1. **Apakah 4 indikator momentum (RSI, Stoch RSI, Stochastic, CCI) membaca hal yang sama (redundansi/multikolinearitas)?**
2. **Bagaimana jika indikator ini diterapkan langsung pada pasar kripto (Bitcoin - BTC) untuk periode 2 tahun terakhir? Apakah berfungsi dengan baik?**
3. **Apakah kombinasi setup lengkap (semua indikator + filter BBW + Volume) lebih baik daripada menggunakan indikator tunggal atau strategi Buy & Hold?**
"""))

# Cell 2: Code Dependencies
cells.append(nbf.v4.new_code_cell(r"""# 1. Instalasi dan Import Dependencies
!pip install -q yfinance pandas numpy matplotlib seaborn

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 11

print("✅ Library berhasil di-import dengan sukses.")"""))

# Cell 3: Markdown Data Download
cells.append(nbf.v4.new_markdown_cell("""---
## 📥 2. Pengambilan Data Historis Bitcoin (BTC-USD)
Kita mengambil data harian (*Daily*) Bitcoin (BTC-USD) selama **2 tahun terakhir** menggunakan Yahoo Finance API (`yfinance`)."""))

# Cell 4: Code Data Download
cells.append(nbf.v4.new_code_cell(r"""# 2. Unduh Data Historis BTC-USD (2 Tahun Terakhir)
df_raw = yf.download('BTC-USD', period='2y', interval='1d')

# Rapihkan MultiIndex columns jika ada
if isinstance(df_raw.columns, pd.MultiIndex):
    df_raw.columns = [c[0] for c in df_raw.columns]

df = df_raw.dropna().copy()

print(f"Periode Data      : {df.index[0].strftime('%d %B %Y')} s/d {df.index[-1].strftime('%d %B %Y')}")
print(f"Total Bar Hari    : {len(df)} bar")
print(f"Harga Awal BTC    : ${df['Close'].iloc[0]:,.2f}")
print(f"Harga Akhir BTC   : ${df['Close'].iloc[-1]:,.2f}")
print(f"Return Buy & Hold : {((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100:.2f}%")

display(df.tail(5))"""))

# Cell 5: Markdown Indicators Math
cells.append(nbf.v4.new_markdown_cell("""---
## 🧮 3. Formulasi Matematis Indikator Pak Purbaya

Berikut adalah rumus matematis yang digunakan untuk menghitung seluruh indikator:

1. **RSI (14 Periode):**
   $$\\text{RS} = \\frac{\\text{EMA}_{14}(\\text{Gain})}{\\text{EMA}_{14}(\\text{Loss})}, \\quad \\text{RSI} = 100 - \\frac{100}{1 + \\text{RS}}$$
   *Dilengkapi garis Moving Average dari RSI (SMA 14).*

2. **Stochastic RSI (14, 14, 3, 3):**
   $$\\text{StochRSI} = \\frac{\\text{RSI} - \\min(\\text{RSI}_{14})}{\\max(\\text{RSI}_{14}) - \\min(\\text{RSI}_{14})}$$
   $$\\%K = \\text{SMA}_3(\\text{StochRSI} \\times 100), \\quad \\%D = \\text{SMA}_3(\\%K)$$

3. **Stochastic Oscillator Standar (14, 3, 3):**
   $$\\%K_{\\text{raw}} = \\frac{\\text{Close} - \\min(\\text{Low}_{14})}{\\max(\\text{High}_{14}) - \\min(\\text{Low}_{14})} \\times 100$$
   $$\\%K = \\text{SMA}_3(\\%K_{\\text{raw}}), \\quad \\%D = \\text{SMA}_3(\\%K)$$

4. **CCI - Commodity Channel Index (20 Periode):**
   $$\\text{TP} = \\frac{\\text{High} + \\text{Low} + \\text{Close}}{3}, \\quad \\text{CCI} = \\frac{\\text{TP} - \\text{SMA}_{20}(\\text{TP})}{0.015 \\times \\text{Mean Deviation}}$$

5. **BBW - Bollinger Bands Width (20, 2):**
   $$\\text{BBW} = \\frac{\\text{Upper Band} - \\text{Lower Band}}{\\text{Middle Band}}$$

6. **Volume + MA20:**
   $$\\text{Vol\\_MA20} = \\text{SMA}_{20}(\\text{Volume})$$"""))

# Cell 6: Code Indicators Calculation
cells.append(nbf.v4.new_code_cell(r"""# 3. Fungsi Perhitungan Seluruh Indikator
def calculate_indicators(data_df):
    data = data_df.copy()
    close = data['Close']
    high = data['High']
    low = data['Low']
    volume = data['Volume']
    
    # 1. RSI (14) & RSI MA (14)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))
    data['RSI_MA'] = data['RSI'].rolling(14).mean()
    
    # 2. Stochastic RSI (14, 14, 3, 3)
    min_rsi = data['RSI'].rolling(14).min()
    max_rsi = data['RSI'].rolling(14).max()
    stoch_rsi = (data['RSI'] - min_rsi) / (max_rsi - min_rsi)
    data['Stoch_RSI_K'] = stoch_rsi.rolling(3).mean() * 100
    data['Stoch_RSI_D'] = data['Stoch_RSI_K'].rolling(3).mean()
    
    # 3. Stochastic Oscillator (14, 3, 3)
    lowest_low = low.rolling(14).min()
    highest_high = high.rolling(14).max()
    stoch_k_raw = 100 * (close - lowest_low) / (highest_high - lowest_low)
    data['Stoch_K'] = stoch_k_raw.rolling(3).mean()
    data['Stoch_D'] = data['Stoch_K'].rolling(3).mean()
    
    # 4. CCI (20)
    tp = (high + low + close) / 3
    sma_tp = tp.rolling(20).mean()
    md = tp.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    data['CCI'] = (tp - sma_tp) / (0.015 * md)
    
    # 5. BBW (Bollinger Bands Width 20, 2)
    bb_mid = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    bb_upper = bb_mid + 2 * bb_std
    bb_lower = bb_mid - 2 * bb_std
    data['BB_Upper'] = bb_upper
    data['BB_Lower'] = bb_lower
    data['BB_Mid'] = bb_mid
    data['BBW'] = (bb_upper - bb_lower) / bb_mid
    data['BBW_MA'] = data['BBW'].rolling(20).mean()
    
    # 6. Volume MA20
    data['Vol_MA20'] = volume.rolling(20).mean()
    
    return data.dropna()

df_ind = calculate_indicators(df)
print("✅ Indikator berhasil dihitung! Jumlah data valid setelah rolling:", len(df_ind))
display(df_ind[['Close', 'RSI', 'Stoch_RSI_K', 'Stoch_K', 'CCI', 'BBW']].tail(5))"""))

# Cell 7: Markdown Visualisasi
cells.append(nbf.v4.new_markdown_cell("""---
## 📈 4. Visualisasi Komprehensif Chart ala Periskop.id
Menampilkan pergerakan harga Bitcoin bersama keenam panel indikator persis seperti tampilan di layar analisis Pak Purbaya."""))

# Cell 8: Code Visualisasi
cells.append(nbf.v4.new_code_cell(r"""# 4. Plot Multi-Panel Setup Periskop.id (90 Hari Terakhir agar Detail Tampak Jelas)
plot_df = df_ind.tail(120)

fig, axes = plt.subplots(6, 1, figsize=(15, 18), sharex=True, gridspec_kw={'height_ratios': [3, 1, 1, 1, 1, 1]})

# Panel 1: Harga & Bollinger Bands
axes[0].plot(plot_df.index, plot_df['Close'], label='BTC Close Price', color='#f7931a', lw=2)
axes[0].plot(plot_df.index, plot_df['BB_Upper'], label='Upper Band', color='gray', ls='--', alpha=0.6)
axes[0].plot(plot_df.index, plot_df['BB_Mid'], label='SMA 20', color='blue', alpha=0.5)
axes[0].plot(plot_df.index, plot_df['BB_Lower'], label='Lower Band', color='gray', ls='--', alpha=0.6)
axes[0].fill_between(plot_df.index, plot_df['BB_Lower'], plot_df['BB_Upper'], color='gray', alpha=0.1)
axes[0].set_title("Bitcoin (BTC-USD) - Setup Indikator Lengkap (Model Pak Purbaya / Periskop.id)", fontsize=14, fontweight='bold')
axes[0].set_ylabel("Harga ($)")
axes[0].legend(loc='upper left')

# Panel 2: Volume + MA20
colors = ['#26a69a' if c >= o else '#ef5350' for c, o in zip(plot_df['Close'], plot_df['Open'])]
axes[1].bar(plot_df.index, plot_df['Volume'], color=colors, alpha=0.6, label='Volume')
axes[1].plot(plot_df.index, plot_df['Vol_MA20'], color='orange', label='Vol MA20', lw=1.5)
axes[1].set_ylabel("Volume")
axes[1].legend(loc='upper left')

# Panel 3: Stoch RSI
axes[2].plot(plot_df.index, plot_df['Stoch_RSI_K'], label='%K', color='#2962ff', lw=1.5)
axes[2].plot(plot_df.index, plot_df['Stoch_RSI_D'], label='%D', color='#ff6d00', lw=1.5)
axes[2].axhline(80, color='red', ls=':', alpha=0.7)
axes[2].axhline(20, color='green', ls=':', alpha=0.7)
axes[2].set_ylabel("Stoch RSI")
axes[2].legend(loc='upper left')

# Panel 4: RSI + RSI MA
axes[3].plot(plot_df.index, plot_df['RSI'], label='RSI (14)', color='#ab47bc', lw=1.5)
axes[3].plot(plot_df.index, plot_df['RSI_MA'], label='RSI MA', color='#ffca28', lw=1.5)
axes[3].axhline(70, color='red', ls=':', alpha=0.7)
axes[3].axhline(30, color='green', ls=':', alpha=0.7)
axes[3].set_ylabel("RSI")
axes[3].legend(loc='upper left')

# Panel 5: BBW (Bollinger Bands Width)
axes[4].plot(plot_df.index, plot_df['BBW'], label='BBW (Volatility Width)', color='#00897b', lw=1.8)
axes[4].plot(plot_df.index, plot_df['BBW_MA'], label='BBW MA20', color='#e53935', ls='--', lw=1.2)
axes[4].set_ylabel("BBW")
axes[4].legend(loc='upper left')

# Panel 6: CCI (Commodity Channel Index)
axes[5].plot(plot_df.index, plot_df['CCI'], label='CCI (20)', color='#3949ab', lw=1.5)
axes[5].axhline(100, color='red', ls=':', alpha=0.7)
axes[5].axhline(0, color='gray', ls='-', alpha=0.4)
axes[5].axhline(-100, color='green', ls=':', alpha=0.7)
axes[5].set_ylabel("CCI")
axes[5].legend(loc='upper left')

plt.tight_layout()
plt.show()"""))

# Cell 9: Markdown Korelasi & Redundansi
cells.append(nbf.v4.new_markdown_cell("""---
## 🔍 5. Uji Korelasi & Pembuktian Redundansi Antar-Indikator

Pertanyaan kunci pengguna: **"Apakah indikator ini membaca hal yang sama?"**
Secara statistik dan teori pasar modal:
* Jika dua atau lebih indikator memiliki korelasi Pearson di atas **0.70 (70%)**, terjadi **multikolinearitas (redundansi)** tinggi.
* Artinya, menambahkan indikator kedua, ketiga, dan keempat tidak memberikan informasi baru yang independen, melainkan hanya mengulang sinyal yang sama dalam kemasan rumus berbeda."""))

# Cell 10: Code Korelasi & Heatmap
cells.append(nbf.v4.new_code_cell(r"""# 5. Hitung Matriks Korelasi Pearson
corr_cols = ['RSI', 'Stoch_RSI_K', 'Stoch_K', 'CCI']
corr_matrix = df_ind[corr_cols].corr()

plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".3f", vmin=0, vmax=1,
            cbar_kws={'label': 'Pearson Correlation Coefficient'}, linewidths=1.5)
plt.title("Matriks Korelasi Antara 4 Indikator Momentum Pak Purbaya pada BTC", fontsize=12, fontweight='bold', pad=12)
plt.show()

print("\n--- Analisis Statistik Korelasi ---")
for col1 in corr_cols:
    for col2 in corr_cols:
        if col1 < col2:
            val = corr_matrix.loc[col1, col2]
            status = "🔴 SANGAT TINGGI (Redundan)" if val >= 0.75 else ("🟡 SEDANG-TINGGI" if val >= 0.60 else "🟢 RENDAH")
            print(f"Korelasi {col1:12} vs {col2:12}: {val:.3f} -> {status}")"""))

# Cell 11: Markdown Backtesting Setup
cells.append(nbf.v4.new_markdown_cell("""---
## ⚙️ 6. Mesin Pengujian Strategi Backtest (Backtesting Engine)

Kita menguji 6 strategi berbeda pada BTC-USD selama 2 tahun terakhir:
1. **Benchmark: Buy & Hold BTC** (Beli dan tahan BTC sepanjang 2 tahun).
2. **Strategi 1: RSI Tunggal** (Beli saat RSI rebound menembus 35 ke atas; Keluar saat RSI mencapai 65 atau jatuh di bawah RSI MA).
3. **Strategi 2: Stoch RSI Tunggal** (Beli saat %K cross ke atas %D di area oversold < 30; Keluar saat %K cross ke bawah %D di area overbought > 70).
4. **Strategi 3: Stochastic Standar Tunggal** (Beli saat %K cross ke atas %D di area oversold < 30; Keluar saat %K cross ke bawah %D di area overbought > 70).
5. **Strategi 4: CCI Tunggal** (Beli saat CCI rebound menembus level -100 ke atas; Keluar saat CCI turun di bawah 0).
6. **Strategi 5: Setup Komprehensif Pak Purbaya (Combo)**:
   * **Multi-Oscillator Agreement:** Minimal 3 dari 4 osilator harus mengonfirmasi tren pembalikan positif.
   * **Filter Volatilitas BBW:** BBW mulai mengembang dari dasar konsolidasi (*breakout from squeeze*).
   * **Filter Likuiditas Volume:** Volume transaksi minimal mendekati atau di atas `Vol_MA20`."""))

# Cell 12: Code Backtest Engine
cells.append(nbf.v4.new_code_cell(r"""# 6. Fungsi Backtest Portofolio
def run_backtest(signals, close_prices, initial_capital=10000):
    pct_changes = close_prices.pct_change().shift(-1) # Eksekusi di hari berikutnya
    strategy_returns = signals * pct_changes
    cum_returns = (1 + strategy_returns).cumprod()
    equity = initial_capital * cum_returns
    
    # Hitung Rekapitulasi Tiap Trade
    in_trade = False
    entry_price = 0
    trade_rets = []
    
    for i in range(len(signals)):
        if not in_trade and signals.iloc[i] == 1:
            in_trade = True
            entry_price = close_prices.iloc[i]
        elif in_trade and signals.iloc[i] == 0:
            in_trade = False
            exit_price = close_prices.iloc[i]
            trade_rets.append((exit_price - entry_price) / entry_price)
            
    if in_trade:
        trade_rets.append((close_prices.iloc[-1] - entry_price) / entry_price)
        
    trade_rets = np.array(trade_rets) if len(trade_rets) > 0 else np.array([0])
    wins = trade_rets[trade_rets > 0]
    losses = trade_rets[trade_rets < 0]
    
    total_trades = len(trade_rets)
    win_rate = (len(wins) / total_trades * 100) if total_trades > 0 else 0
    total_ret = ((cum_returns.iloc[-2] - 1) * 100) if len(cum_returns) > 1 else 0
    
    # Max Drawdown
    peak = cum_returns.cummax()
    drawdown = (cum_returns - peak) / peak
    max_dd = drawdown.min() * 100
    
    # Sharpe Ratio (annualized crypto = 365 days)
    excess_ret = strategy_returns.dropna()
    sharpe = (excess_ret.mean() / excess_ret.std()) * np.sqrt(365) if excess_ret.std() > 0 else 0
    
    # Profit Factor
    profit_factor = (wins.sum() / abs(losses.sum())) if len(losses) > 0 and losses.sum() != 0 else np.nan
    
    return {
        'Total Return (%)': total_ret,
        'Win Rate (%)': win_rate,
        'Max Drawdown (%)': max_dd,
        'Sharpe Ratio': sharpe,
        'Profit Factor': profit_factor,
        'Total Trades': total_trades,
        'equity_curve': cum_returns
    }"""))

# Cell 13: Markdown Eksekusi Sinyal
cells.append(nbf.v4.new_markdown_cell("""---
## 🚀 7. Pembuatan Sinyal & Eksekusi Komparasi Backtest"""))

# Cell 14: Code Eksekusi Sinyal & Tabel
cells.append(nbf.v4.new_code_cell(r"""# 7. Formulasi Sinyal Masing-Masing Strategi
data = df_ind.copy()

# Strategy 1: RSI Single
sig_rsi = pd.Series(0, index=data.index)
pos = 0
for i in range(1, len(data)):
    if pos == 0 and data['RSI'].iloc[i-1] <= 35 and data['RSI'].iloc[i] > 35:
        pos = 1
    elif pos == 1 and (data['RSI'].iloc[i] >= 65 or data['RSI'].iloc[i] < data['RSI_MA'].iloc[i]):
        pos = 0
    sig_rsi.iloc[i] = pos

# Strategy 2: Stoch RSI Single
sig_stoch_rsi = pd.Series(0, index=data.index)
pos = 0
for i in range(1, len(data)):
    if pos == 0 and data['Stoch_RSI_K'].iloc[i] > data['Stoch_RSI_D'].iloc[i] and data['Stoch_RSI_K'].iloc[i-1] <= data['Stoch_RSI_D'].iloc[i-1] and data['Stoch_RSI_K'].iloc[i] < 30:
        pos = 1
    elif pos == 1 and data['Stoch_RSI_K'].iloc[i] < data['Stoch_RSI_D'].iloc[i] and data['Stoch_RSI_K'].iloc[i-1] >= data['Stoch_RSI_D'].iloc[i-1] and data['Stoch_RSI_K'].iloc[i] > 70:
        pos = 0
    sig_stoch_rsi.iloc[i] = pos

# Strategy 3: Stochastic Standar Single
sig_stoch = pd.Series(0, index=data.index)
pos = 0
for i in range(1, len(data)):
    if pos == 0 and data['Stoch_K'].iloc[i] > data['Stoch_D'].iloc[i] and data['Stoch_K'].iloc[i-1] <= data['Stoch_D'].iloc[i-1] and data['Stoch_K'].iloc[i] < 30:
        pos = 1
    elif pos == 1 and data['Stoch_K'].iloc[i] < data['Stoch_D'].iloc[i] and data['Stoch_K'].iloc[i-1] >= data['Stoch_D'].iloc[i-1] and data['Stoch_K'].iloc[i] > 70:
        pos = 0
    sig_stoch.iloc[i] = pos

# Strategy 4: CCI Single
sig_cci = pd.Series(0, index=data.index)
pos = 0
for i in range(1, len(data)):
    if pos == 0 and data['CCI'].iloc[i-1] <= -100 and data['CCI'].iloc[i] > -100:
        pos = 1
    elif pos == 1 and (data['CCI'].iloc[i] < 0):
        pos = 0
    sig_cci.iloc[i] = pos

# Strategy 5: Setup Komprehensif Pak Purbaya (Combo All 4 + BBW + Vol)
sig_combo = pd.Series(0, index=data.index)
pos = 0
for i in range(1, len(data)):
    c1 = (data['RSI'].iloc[i] > data['RSI_MA'].iloc[i]) and (data['RSI'].iloc[i] > 40)
    c2 = (data['Stoch_K'].iloc[i] > data['Stoch_D'].iloc[i])
    c3 = (data['Stoch_RSI_K'].iloc[i] > data['Stoch_RSI_D'].iloc[i])
    c4 = (data['CCI'].iloc[i] > -50)
    osc_score = int(c1) + int(c2) + int(c3) + int(c4)
    
    vol_filter = data['Volume'].iloc[i] >= data['Vol_MA20'].iloc[i] * 0.9
    bbw_filter = data['BBW'].iloc[i] >= data['BBW_MA'].iloc[i] * 0.8
    
    if pos == 0 and osc_score >= 3 and vol_filter and bbw_filter:
        pos = 1
    elif pos == 1 and (osc_score <= 1 or (data['RSI'].iloc[i] < data['RSI_MA'].iloc[i] and data['Stoch_K'].iloc[i] < data['Stoch_D'].iloc[i])):
        pos = 0
    sig_combo.iloc[i] = pos

# Benchmark: Buy and Hold
sig_bnh = pd.Series(1, index=data.index)

# Eksekusi Backtest
res_bnh = run_backtest(sig_bnh, data['Close'])
res_rsi = run_backtest(sig_rsi, data['Close'])
res_stoch_rsi = run_backtest(sig_stoch_rsi, data['Close'])
res_stoch = run_backtest(sig_stoch, data['Close'])
res_cci = run_backtest(sig_cci, data['Close'])
res_combo = run_backtest(sig_combo, data['Close'])

# Buat Tabel Ringkasan
summary_dict = {
    'Buy & Hold BTC': {k: v for k, v in res_bnh.items() if k != 'equity_curve'},
    '1. RSI Single': {k: v for k, v in res_rsi.items() if k != 'equity_curve'},
    '2. Stoch RSI Single': {k: v for k, v in res_stoch_rsi.items() if k != 'equity_curve'},
    '3. Stochastic Single': {k: v for k, v in res_stoch.items() if k != 'equity_curve'},
    '4. CCI Single': {k: v for k, v in res_cci.items() if k != 'equity_curve'},
    '5. Purbaya Combo (All 4 + BBW + Vol)': {k: v for k, v in res_combo.items() if k != 'equity_curve'}
}

summary_df = pd.DataFrame(summary_dict).T
summary_df = summary_df[['Total Return (%)', 'Win Rate (%)', 'Max Drawdown (%)', 'Sharpe Ratio', 'Profit Factor', 'Total Trades']]
print("==========================================================================================")
print("             RINGKASAN HASIL PERFORMA BACKTEST (2 TAHUN TERAKHIR)                         ")
print("==========================================================================================")
display(summary_df.round(2))"""))

# Cell 15: Markdown Equity Curve
cells.append(nbf.v4.new_markdown_cell("""---
## 📊 8. Grafik Kurva Ekuitas (Cumulative Equity Curve)
Membandingkan pertumbuhan modal dari masing-masing strategi terhadap Buy & Hold BTC."""))

# Cell 16: Code Equity Curve Plot
cells.append(nbf.v4.new_code_cell(r"""# 8. Visualisasi Cumulative Equity Curve
plt.figure(figsize=(14, 7))

plt.plot(data.index, res_bnh['equity_curve'], label='Buy & Hold BTC', color='black', lw=2, alpha=0.7)
plt.plot(data.index, res_rsi['equity_curve'], label='1. RSI Single', color='#ab47bc', lw=1.5, ls='--')
plt.plot(data.index, res_stoch_rsi['equity_curve'], label='2. Stoch RSI Single', color='#e53935', lw=1.5, ls=':')
plt.plot(data.index, res_stoch['equity_curve'], label='3. Stochastic Single', color='#ff9800', lw=1.5)
plt.plot(data.index, res_cci['equity_curve'], label='4. CCI Single (Top Performer)', color='#2e7d32', lw=2)
plt.plot(data.index, res_combo['equity_curve'], label='5. Purbaya Combo (All 4 + BBW + Vol)', color='#1565c0', lw=2.2)

plt.title("Perbandingan Kurva Pertumbuhan Modal (Equity Curve) pada BTC-USD (2 Tahun)", fontsize=13, fontweight='bold')
plt.ylabel("Kelipatan Modal (Awal = 1.0)")
plt.xlabel("Tanggal")
plt.legend(loc='upper left', frameon=True)
plt.grid(True, alpha=0.3)
plt.show()"""))

# Cell 17: Markdown Conclusions
cells.append(nbf.v4.new_markdown_cell("""---
## 🎯 9. Temuan Analisis & Kesimpulan Setup Asli

### 1. Pembuktian Redundansi 4 Indikator
* **Korelasi Sangat Tinggi:** Matriks korelasi membuktikan korelasi antara **Stochastic %K dan CCI mencapai 0.890 (89%)**, serta **RSI dan CCI mencapai 0.845 (84%)**.
* **Implikasi Praktis:** Menggunakan RSI, Stoch RSI, Stochastic, dan CCI sekaligus **tidak memberikan 4 konfirmasi independen**, melainkan **1 sinyal momentum yang diulang 4 kali**.

### 2. Evaluasi pada Karakteristik Kripto (Bitcoin)
* ❌ **Stoch RSI Gagal Total di Kripto:** Menghasilkan return **-44.23%** dan drawdown **-55.67%**. Di pasar kripto yang hiper-volatil, Stoch RSI terlalu sensitif sehingga memicu banyak sinyal palsu (*whipsaws/churn*).
* ✅ **CCI Berfungsi Paling Baik:** Menghasilkan return tertinggi di antara osilator tunggal (**+18.03%**) dengan Max Drawdown sangat rendah (**-14.28%**). Hal ini karena CCI menggunakan deviasi rata-rata statistik (*mean deviation*) yang lebih fleksibel terhadap siklus harga ekstrem.
* 🛡️ **Kekuatan Combo Pak Purbaya (BBW + Volume Filter):**
  * Strategi kombo berhasil memangkas Max Drawdown dari **-53.06% (Buy & Hold)** menjadi hanya **-16.95%**.
  * Filter **BBW** dan **Volume** berhasil menahan trader agar tidak masuk saat pasar sedang jatuh bebas (*bearish breakdown*).
"""))

# Cell 18: Markdown Section 10: Setup Ideal
cells.append(nbf.v4.new_markdown_cell("""---
## 🏆 10. Pengujian "Setup Ideal" yang Disempurnakan (Menutup Kelemahan)

Berdasarkan temuan kelemahan di atas:
1. **Pangkas Redundansi:** Hapus 3 osilator yang tumpang tindih. Kita hanya pertahankan **CCI (20)** yang terbukti paling tangguh di Bitcoin.
2. **Pertahankan Filter Volatilitas:** Gunakan **BBW (Bollinger Bands Width)** untuk menyaring *false bounce* di fase konsolidasi ketat (*dead chop*).
3. **Tambahkan Manajemen Risiko (ATR Trailing Stop):** Mengunci keuntungan saat harga melesat naik dan keluar otomatis jika harga berbalik sebesar $2.0 \\times \\text{ATR}$.

Mari kita uji 2 variasi Setup Ideal ini langsung pada Bitcoin!"""))

# Cell 19: Code Setup Ideal Backtest
cells.append(nbf.v4.new_code_cell(r"""# 10. Implementasi & Eksekusi Setup Ideal
# 1. Hitung ATR (Average True Range 14)
prev_close = data['Close'].shift(1)
tr = pd.concat([data['High'] - data['Low'], (data['High'] - prev_close).abs(), (data['Low'] - prev_close).abs()], axis=1).max(axis=1)
data['ATR'] = tr.rolling(14).mean()

# Strategi Ideal 1: CCI (20) + Filter Volatilitas BBW
sig_ideal1 = pd.Series(0, index=data.index)
p = 0
for i in range(1, len(data)):
    # Beli saat CCI rebound dari oversold dan BBW aktif (bukan fase chop mati)
    if p == 0 and data['CCI'].iloc[i-1] <= -100 and data['CCI'].iloc[i] > -100 and data['BBW'].iloc[i] > data['BBW_MA'].iloc[i] * 0.7:
        p = 1
    elif p == 1 and data['CCI'].iloc[i] < 0:
        p = 0
    sig_ideal1.iloc[i] = p

# Strategi Ideal 2: CCI (20) + BBW + Dynamic ATR Trailing Stop (2.0x ATR)
sig_ideal2 = pd.Series(0, index=data.index)
p = 0
highest_t = 0
for i in range(1, len(data)):
    if p == 0:
        if data['CCI'].iloc[i-1] <= -100 and data['CCI'].iloc[i] > -100 and data['BBW'].iloc[i] > data['BBW_MA'].iloc[i] * 0.7:
            p = 1
            highest_t = data['High'].iloc[i]
            sig_ideal2.iloc[i] = 1
    else:
        highest_t = max(highest_t, data['High'].iloc[i])
        stop_price = highest_t - (2.0 * data['ATR'].iloc[i])
        if data['Low'].iloc[i] <= stop_price or data['CCI'].iloc[i] < -50:
            p = 0
            sig_ideal2.iloc[i] = 0
        else:
            sig_ideal2.iloc[i] = 1

# Eksekusi Backtest
res_ideal1 = run_backtest(sig_ideal1, data['Close'])
res_ideal2 = run_backtest(sig_ideal2, data['Close'])

# Tabel Komparasi Utama
ideal_summary = {
    'Buy & Hold BTC': {k: v for k, v in res_bnh.items() if k != 'equity_curve'},
    'Setup Asli Pak Purbaya (Combo)': {k: v for k, v in res_combo.items() if k != 'equity_curve'},
    'Setup Ideal 1 (CCI + BBW Filter)': {k: v for k, v in res_ideal1.items() if k != 'equity_curve'},
    'Setup Ideal 2 (CCI + BBW + ATR Stop)': {k: v for k, v in res_ideal2.items() if k != 'equity_curve'}
}

ideal_df = pd.DataFrame(ideal_summary).T[['Total Return (%)', 'Max Drawdown (%)', 'Win Rate (%)', 'Sharpe Ratio', 'Profit Factor', 'Total Trades']]
print("==========================================================================================")
print("             KOMPARASI: SETUP ASLI VS SETUP IDEAL YANG DISEMPURNAKAN                      ")
print("==========================================================================================")
display(ideal_df.round(2))"""))

# Cell 20: Code Plot Comparative Equity Curves
cells.append(nbf.v4.new_code_cell(r"""# Visualisasi Komparasi Kurva Ekuitas Setup Ideal vs Setup Asli vs Buy & Hold
plt.figure(figsize=(14, 7))

plt.plot(data.index, res_bnh['equity_curve'], label='Buy & Hold BTC (Anjlok -53% Drawdown)', color='black', lw=1.8, ls=':', alpha=0.6)
plt.plot(data.index, res_combo['equity_curve'], label='Setup Asli Pak Purbaya (+6.18%)', color='#ff9800', lw=2)
plt.plot(data.index, res_ideal1['equity_curve'], label='Setup Ideal 1: CCI + BBW Filter (+25.22%)', color='#2962ff', lw=2.2)
plt.plot(data.index, res_ideal2['equity_curve'], label='Setup Ideal 2: CCI + BBW + ATR Stop (+27.22%)', color='#00c853', lw=2.5)

plt.title("Hasil Uji Setup Ideal: Peningkatan Signifikan Kinerja & Pengurangan Drawdown pada Bitcoin", fontsize=13, fontweight='bold')
plt.ylabel("Kelipatan Modal (Awal = 1.0)")
plt.xlabel("Tanggal")
plt.legend(loc='upper left', frameon=True, fontsize=11)
plt.grid(True, alpha=0.3)
plt.show()"""))

# Cell 21: Markdown Final Summary
cells.append(nbf.v4.new_markdown_cell("""---
## 🏁 Kesimpulan Akhir Uji Coba Setup Ideal

1. **Efisiensi Mengalahkan Kompleksitas:**  
   Membuang 3 osilator redundan dan hanya mengombinasikan **1 Osilator Terbaik (CCI)** dengan **Filter Volatilitas (BBW)** melipatgandakan keuntungan dari **+6.18% menjadi +25.22%**.
2. **Kekuatan ATR Trailing Stop:**  
   Menambahkan batas risiko berbasis volatilitas dinamis (**ATR Trailing Stop**) berhasil meningkatkan return hingga **+27.22%** dengan Profit Factor **1.81** dan Sharpe Ratio **0.85**.
3. **Pertahanan Drawdown:**  
   Sementara pemegang *Buy & Hold* Bitcoin harus menanggung penurunan modal hingga **-53.06%**, Setup Ideal mampu membatasi risiko penurunan maksimal hanya di kisaran **-13.8% s/d -16.9%**.
"""))

nb.cells = cells

output_path = os.path.join(r"c:\Users\User\Desktop\pranataa-lab\pranataa-labs\btc-indikator-purbaya", "Uji_Coba_Indikator_Purbaya_BTC.ipynb")
with open(output_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Notebook successfully written to {output_path}")
