# 📊 Uji Coba Empiris Indikator Pak Purbaya vs Setup Ideal pada Bitcoin (BTC-USD)

Eksperimen komputasional dan backtesting strategi teknikal yang diadaptasi dari setup grafik **Pak Purbaya (Purbaya Yudhi Sadewa)** pada platform **Periskop.id**, serta pengujian **Setup Ideal** yang disempurnakan pada aset kripto **Bitcoin (BTC-USD)** selama 2 tahun terakhir (2024–2026).

---

## 📁 Struktur Direktori
```text
btc-indikator-purbaya/
├── Uji_Coba_Indikator_Purbaya_BTC.ipynb   # File Google Colab / Jupyter Notebook siap pakai (Full Pre-rendered)
├── test_ideal_setup.py                  # Script pengujian komparasi Setup Asli vs Setup Ideal
├── test_experiment.py                   # Script eksekusi backtesting indikator tunggal
├── generate_colab_notebook.py           # Script generator notebook
└── README.md                            # Dokumentasi lengkap & interpretasi hasil
```

---

## 🎯 Fokus Pertanyaan Riset
1. **Redundansi Multikolinearitas:** Apakah 4 indikator momentum (RSI, Stoch RSI, Stochastic Oscillator, dan CCI) membaca sinyal yang sama?
2. **Kinerja di Aset Kripto:** Bagaimana performa masing-masing indikator vs strategi kombo vs Buy & Hold pada Bitcoin?
3. **Penyempurnaan Setup Ideal:** Apa yang terjadi jika kelemahan setup asli ditutup (membuang osilator redundan, mempertahankan BBW, dan menambahkan ATR Trailing Stop)?

---

## 📊 Hasil Uji Coba: Setup Asli vs Setup Ideal

| Strategi / Model | Total Return (%) | Max Drawdown (%) | Win Rate (%) | Sharpe Ratio | Profit Factor | Total Trades |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Buy & Hold BTC (Tolok Ukur)** | -18.18% | **-53.06%** | 0.0% | -0.03 | 0.00 | 1 |
| **Setup Asli Pak Purbaya (Combo)** | +6.18% | -16.95% | 42.86% | 0.25 | 1.19 | 35 |
| **Setup Ideal 1 (CCI + BBW Filter)** | **+25.22%** | **-13.82%** | **54.84%** | **0.87** | **1.96** | 31 |
| **Setup Ideal 2 (CCI + BBW + ATR Stop)** | **+27.22%** | **-16.91%** | 48.39% | **0.85** | **1.81** | 31 |

---

## 💡 Temuan Kunci dari Uji Coba Setup Ideal

1. **Memangkas Redundansi Melipatgandakan Keuntungan (+6.18% ➡️ +25.22%):**  
   Dengan membuang 3 osilator yang saling bertabrakan (Stoch RSI, Stoch, RSI) dan hanya mempertahankan **1 Osilator Terbaik (CCI)** yang digabungkan dengan **Filter Volatilitas (BBW)**, performa profit meningkat lebih dari **400%**.
2. **BBW Adalah Komponen Terbaik dari Setup Asli:**  
   BBW berhasil menyaring 7 sinyal palsu saat pasar dalam fase konsolidasi ketat (*dead chop*), sehingga Win Rate naik dari 42.8% menjadi **54.8%**.
3. **Manajemen Risiko ATR Mengunci Reli Besar (+27.22%):**  
   Penambahan **ATR Trailing Stop ($2.0 \times \text{ATR}$)** mengatasi kelemahan "keluar terlalu dini" dan melindungi modal saat pasar tiba-tiba berbalik arah.
4. **Proteksi Drawdown Maksimal:**  
   Ketika pemegang *Buy & Hold* Bitcoin mengalami penurunan modal hingga **-53.06%**, Setup Ideal membatasi kerugian maksimal hanya di kisaran **-13.8% s/d -16.9%**.

---

## 🚀 Cara Menjalankan di Google Colab
1. Buka [Google Colab](https://colab.research.google.com).
2. Pilih tab **Upload** dan unggah file [`Uji_Coba_Indikator_Purbaya_BTC.ipynb`](file:///c:/Users/User/Desktop/pranataa-lab/pranataa-labs/btc-indikator-purbaya/Uji_Coba_Indikator_Purbaya_BTC.ipynb).
3. Klik menu **Runtime** -> **Run all** (`Ctrl + F9`).
