import urllib.request
import json
import pandas as pd
import numpy as np
import io
import os
import sys
from concurrent.futures import ThreadPoolExecutor

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def fetch_indonesian_mutual_funds():
    print("📥 Mengunduh master katalog reksa dana Indonesia dari Bibit / OJK registry...")
    url = 'https://raw.githubusercontent.com/risan/reksadana-id/main/data/bibit/funds.csv'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    content = urllib.request.urlopen(req, timeout=15).read()
    df_master = pd.read_csv(io.BytesIO(content))
    
    tradeable = df_master[df_master['tradeable'] == 1].copy()
    print(f"Ditemukan {len(tradeable)} reksa dana aktif & tradeable di pasar Indonesia.")
    
    def fetch_fund_detail(sym):
        try:
            f_url = f'https://raw.githubusercontent.com/risan/reksadana-id/main/data/bibit/funds/{sym}.json'
            r = urllib.request.Request(f_url, headers={'User-Agent': 'Mozilla/5.0'})
            data = json.loads(urllib.request.urlopen(r, timeout=10).read().decode('utf-8'))
            return data
        except Exception:
            return None

    symbols = tradeable['symbol'].tolist()
    print("⏳ Mengambil rincian metrik finansial (CAGR, Max Drawdown, AUM, Expense Ratio) secara paralel...")
    with ThreadPoolExecutor(max_workers=20) as executor:
        fund_details = list(executor.map(fetch_fund_detail, symbols))
        
    records = []
    for d in fund_details:
        if not d:
            continue
        cagr = d.get('cagr') or {}
        mdd = d.get('maxdrawdown') or {}
        aum_obj = d.get('aum') or {}
        exp_obj = d.get('expenseratio') or {}
        mgr_obj = d.get('investment_manager') or {}
        
        # Parse metrics
        ret_1y = (cagr.get('1y') or 0.0) * 100
        ret_3y = (cagr.get('3y') or 0.0) * 100
        ret_5y = (cagr.get('5y') or 0.0) * 100
        
        mdd_1y = abs(mdd.get('1y') or 0.0) * 100
        mdd_3y = abs(mdd.get('3y') or 0.0) * 100
        mdd_5y = abs(mdd.get('5y') or 0.0) * 100
        
        aum_val = aum_obj.get('value') or 0.0
        aum_miliar = aum_val / 1e9 # Konversi ke Miliar Rupiah
        
        expense_ratio = (exp_obj.get('percentage') or 0.0) * 100
        # Default expense ratio fallback if missing based on category typical values
        if expense_ratio <= 0:
            if d.get('type') == 'Pasar Uang': expense_ratio = 0.85
            elif d.get('type') == 'Obligasi': expense_ratio = 1.45
            else: expense_ratio = 2.25
            
        # Calmar Ratio (Return 3Y / MDD 3Y)
        calmar_3y = (ret_3y / mdd_3y) if mdd_3y > 0 else (ret_3y / 1.0)
        
        records.append({
            'symbol': d.get('symbol'),
            'name': d.get('name'),
            'type': d.get('type'),
            'manager': mgr_obj.get('name') or 'N/A',
            'sharia': bool(d.get('sharia')),
            'aum_miliar': round(aum_miliar, 2),
            'expense_ratio': round(expense_ratio, 2),
            'returns_1yr': round(ret_1y, 2),
            'returns_3yr': round(ret_3y, 2),
            'returns_5yr': round(ret_5y, 2),
            'max_drawdown_3yr': round(mdd_3y, 2),
            'calmar_ratio_3yr': round(calmar_3y, 2),
            'min_buy': d.get('minbuy') or 10000
        })
        
    df = pd.DataFrame(records)
    print(f"✅ Berhasil menyusun {len(df)} reksa dana Indonesia dengan data lengkap.\n")
    return df

def apply_original_model(df):
    """
    Model Evaluasi Konvensional (Baseline Global):
    - Normalisasi MinMaxScaler lintas semua kategori (tanpa segmentasi).
    - Bobot statis: Expense 20%, Ret1Y 15%, Ret3Y 15%, Ret5Y 15%, dll.
    """
    df_calc = df.copy()
    
    # MinMaxScaler global
    def minmax(series, invert=False):
        s_min, s_max = series.min(), series.max()
        if s_max == s_min:
            res = pd.Series(0.5, index=series.index)
        else:
            res = (series - s_min) / (s_max - s_min)
        return (1.0 - res) if invert else res
        
    df_calc['norm_exp'] = minmax(df_calc['expense_ratio'], invert=True)
    df_calc['norm_r1'] = minmax(df_calc['returns_1yr'])
    df_calc['norm_r3'] = minmax(df_calc['returns_3yr'])
    df_calc['norm_r5'] = minmax(df_calc['returns_5yr'])
    df_calc['norm_calmar'] = minmax(df_calc['calmar_ratio_3yr'])
    
    # Model Baseline weighted sum
    df_calc['original_score'] = (
        df_calc['norm_exp'] * 0.25 +
        df_calc['norm_r1'] * 0.25 +
        df_calc['norm_r3'] * 0.25 +
        df_calc['norm_r5'] * 0.15 +
        df_calc['norm_calmar'] * 0.10
    )
    df_calc['original_rank'] = df_calc['original_score'].rank(ascending=False).astype(int)
    return df_calc

def apply_enhanced_institutional_model(df):
    """
    Model Baru yang Disempurnakan (Next-Gen Institutional Model):
    1. Segmentasi Intra-Category (Peer-Group Normalization).
    2. Percentile Ranking (Tahan Outlier Ekstrem).
    3. Metrik Risiko Riil (Max Drawdown & Calmar Ratio).
    4. Bobot Dinamis Berdasarkan Karakteristik Kelas Aset.
    5. Likuiditas & Kapasitas Penalti (AUM Filter).
    """
    results = []
    
    # Bobot Spesifik Kelas Aset
    category_weights = {
        'Pasar Uang': {
            'drawdown': 0.35,   # Keamanan modal & DD terendah nomor 1
            'expense': 0.25,    # Efisiensi biaya pengelolaan
            'aum': 0.20,        # Likuiditas instan
            'return': 0.20      # Yield stabil
        },
        'Obligasi': {
            'calmar': 0.30,     # Return per unit drawdown
            'return_3y': 0.25,  # Akumulasi kupon & capital gain
            'drawdown': 0.20,   # Kontrol fluktuasi yield
            'expense': 0.15,    # Efisiensi biaya
            'aum': 0.10         # Skala likuiditas
        },
        'Saham': {
            'return_3y': 0.30,  # Alpha & pertumbuhan
            'calmar': 0.25,     # Ketahanan saat bursa crash
            'drawdown': 0.20,   # Drawdown recovery
            'expense': 0.15,    # Biaya
            'aum': 0.10         # Kapasitas manajer investasi
        },
        'Campuran': {
            'calmar': 0.30,
            'return_3y': 0.25,
            'drawdown': 0.25,
            'expense': 0.10,
            'aum': 0.10
        }
    }
    
    # Segmentasi dan kalkulasi per tipe reksa dana
    for cat_name, group in df.groupby('type'):
        g = group.copy()
        if len(g) < 2:
            g['enhanced_score'] = 1.0
            g['category_rank'] = 1
            results.append(g)
            continue
            
        # 1. Percentile Ranking (Rank PCT: 0.0 s/d 1.0)
        p_ret3y = g['returns_3yr'].rank(pct=True)
        p_ret1y = g['returns_1yr'].rank(pct=True)
        p_drawdown = g['max_drawdown_3yr'].rank(pct=True, ascending=False) # Makin kecil makin bagus
        p_calmar = g['calmar_ratio_3yr'].rank(pct=True)
        p_expense = g['expense_ratio'].rank(pct=True, ascending=False)   # Makin hemat makin bagus
        p_aum = g['aum_miliar'].rank(pct=True)
        
        # 2. Penalti AUM terlalu kecil (< Rp 25 Miliar berisiko likuidasi OJK)
        aum_penalty = np.where(g['aum_miliar'] < 25.0, 0.70, 1.0)
        
        # 3. Terapkan bobot spesifik kategori
        w = category_weights.get(cat_name, category_weights['Saham'])
        
        if cat_name == 'Pasar Uang':
            raw_score = (
                p_drawdown * w['drawdown'] +
                p_expense * w['expense'] +
                p_aum * w['aum'] +
                p_ret1y * w['return']
            )
        elif cat_name == 'Obligasi':
            raw_score = (
                p_calmar * w['calmar'] +
                p_ret3y * w['return_3y'] +
                p_drawdown * w['drawdown'] +
                p_expense * w['expense'] +
                p_aum * w['aum']
            )
        else: # Saham & Campuran
            raw_score = (
                p_ret3y * w['return_3y'] +
                p_calmar * w['calmar'] +
                p_drawdown * w['drawdown'] +
                p_expense * w['expense'] +
                p_aum * w['aum']
            )
            
        g['enhanced_score'] = raw_score * aum_penalty
        g['category_rank'] = g['enhanced_score'].rank(ascending=False).astype(int)
        results.append(g)
        
    df_final = pd.concat(results, axis=0)
    df_final['overall_rank'] = df_final['enhanced_score'].rank(ascending=False).astype(int)
    return df_final

def main():
    df_raw = fetch_indonesian_mutual_funds()
    
    # 1. Jalankan Model Evaluasi Konvensional (Baseline Global)
    df_orig = apply_original_model(df_raw)
    
    # 2. Jalankan Model Baru yang Disempurnakan
    df_enhanced = apply_enhanced_institutional_model(df_orig)
    
    # Simpan Dataset
    out_csv = os.path.join(DATA_DIR, 'reksadana_indonesia_scored.csv')
    df_enhanced.to_csv(out_csv, index=False)
    
    out_xlsx = os.path.join(DATA_DIR, 'reksadana_indonesia_scored.xlsx')
    with pd.ExcelWriter(out_xlsx, engine='openpyxl') as writer:
        df_enhanced.to_excel(writer, sheet_name='Semua Reksa Dana', index=False)
        for cat in ['Saham', 'Obligasi', 'Pasar Uang', 'Campuran']:
            cat_df = df_enhanced[df_enhanced['type'] == cat].sort_values('category_rank')
            cat_df.to_excel(writer, sheet_name=cat, index=False)
            
    print("=" * 90)
    print("      HASIL KOMPARASI EMPIRIS: MODEL ASLI VS MODEL YANG DISEMPURNAKAN               ")
    print("=" * 90)
    
    print("\n🔴 TOP 5 MENURUT MODEL ASLI (Baseline Global - Mengalami Bias Kategori):")
    top_orig = df_enhanced.sort_values('original_rank').head(5)
    print(top_orig[['original_rank', 'name', 'type', 'manager', 'returns_3yr', 'max_drawdown_3yr', 'original_score']].to_string(index=False))
    
    print("\n🟢 TOP 3 REKSA DANA PER KATEGORI (Model yang Disempurnakan / Peer-Group Segmentation):")
    for cat in ['Pasar Uang', 'Obligasi', 'Saham', 'Campuran']:
        print(f"\n📂 Kategori: {cat}")
        cat_top = df_enhanced[df_enhanced['type'] == cat].sort_values('category_rank').head(3)
        cols = ['category_rank', 'name', 'manager', 'returns_3yr', 'max_drawdown_3yr', 'calmar_ratio_3yr', 'expense_ratio', 'aum_miliar', 'enhanced_score']
        print(cat_top[cols].to_string(index=False))
        
    print("\n" + "=" * 90)
    print(f"📁 Berkas tersimpan di:")
    print(f" - CSV: {out_csv}")
    print(f" - Excel: {out_xlsx}")

if __name__ == '__main__':
    main()
