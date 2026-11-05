import yfinance as yf
import pandas as pd
import numpy as np

def fetch_data():
    df = yf.download('BTC-USD', period='2y', interval='1d')
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    return df.dropna()

def calculate_all(df):
    data = df.copy()
    close = data['Close']
    high = data['High']
    low = data['Low']
    volume = data['Volume']
    
    # CCI 20
    tp = (high + low + close) / 3
    sma_tp = tp.rolling(20).mean()
    md = tp.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    data['CCI'] = (tp - sma_tp) / (0.015 * md)
    
    # BBW
    bb_mid = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    data['BBW'] = (4 * bb_std) / bb_mid
    data['BBW_MA'] = data['BBW'].rolling(20).mean()
    data['Vol_MA20'] = volume.rolling(20).mean()
    
    # ATR 14
    prev_close = close.shift(1)
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    data['ATR'] = tr.rolling(14).mean()
    
    # Supertrend (10, 3)
    hl2 = (high + low) / 2
    upperband = hl2 + (3 * data['ATR'])
    lowerband = hl2 - (3 * data['ATR'])
    supertrend = pd.Series(True, index=data.index)
    for i in range(1, len(data)):
        if close.iloc[i] > upperband.iloc[i-1]:
            supertrend.iloc[i] = True
        elif close.iloc[i] < lowerband.iloc[i-1]:
            supertrend.iloc[i] = False
        else:
            supertrend.iloc[i] = supertrend.iloc[i-1]
    data['Supertrend'] = supertrend
    
    # Original Indicators for Combo
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    data['RSI'] = 100 - (100 / (1 + (avg_gain / avg_loss)))
    data['RSI_MA'] = data['RSI'].rolling(14).mean()
    
    lowest_low = low.rolling(14).min()
    highest_high = high.rolling(14).max()
    data['Stoch_K'] = (100 * (close - lowest_low) / (highest_high - lowest_low)).rolling(3).mean()
    data['Stoch_D'] = data['Stoch_K'].rolling(3).mean()
    
    min_rsi = data['RSI'].rolling(14).min()
    max_rsi = data['RSI'].rolling(14).max()
    stoch_rsi = (data['RSI'] - min_rsi) / (max_rsi - min_rsi)
    data['Stoch_RSI_K'] = (stoch_rsi * 100).rolling(3).mean()
    data['Stoch_RSI_D'] = data['Stoch_RSI_K'].rolling(3).mean()
    
    return data.dropna()

def evaluate(sig, close, name):
    pct = close.pct_change().shift(-1)
    ret = (1 + sig * pct).cumprod()
    peak = ret.cummax()
    dd = ((ret - peak) / peak).min() * 100
    strat_ret = sig * pct
    sharpe = (strat_ret.mean() / strat_ret.std()) * np.sqrt(365) if strat_ret.std() > 0 else 0
    
    in_t = False
    entry = 0
    tr_list = []
    for i in range(len(sig)):
        if not in_t and sig.iloc[i] == 1:
            in_t = True; entry = close.iloc[i]
        elif in_t and sig.iloc[i] == 0:
            in_t = False; tr_list.append((close.iloc[i] - entry)/entry)
    if in_t: tr_list.append((close.iloc[-1] - entry)/entry)
    tr_arr = np.array(tr_list) if len(tr_list)>0 else np.array([0])
    wins = tr_arr[tr_arr > 0]
    losses = tr_arr[tr_arr < 0]
    win_rate = len(wins)/len(tr_arr)*100 if len(tr_arr)>0 else 0
    pf = wins.sum()/abs(losses.sum()) if len(losses)>0 and losses.sum()!=0 else np.nan
    tot_ret = (ret.iloc[-2]-1)*100
    
    return {
        'Strategi': name,
        'Total Return (%)': tot_ret,
        'Max Drawdown (%)': dd,
        'Win Rate (%)': win_rate,
        'Sharpe Ratio': sharpe,
        'Profit Factor': pf,
        'Total Trades': len(tr_arr),
        'equity_curve': ret
    }

def main():
    df = fetch_data()
    data = calculate_all(df)
    close = data['Close']
    high = data['High']
    low = data['Low']
    cci = data['CCI']
    bbw = data['BBW']
    bbw_ma = data['BBW_MA']
    atr = data['ATR']
    supertrend = data['Supertrend']
    
    results = []
    
    # 1. Buy & Hold
    results.append(evaluate(pd.Series(1, index=data.index), close, 'Buy & Hold BTC'))
    
    # 2. Setup Asli Pak Purbaya (4 Osilator + BBW + Vol)
    sig_orig = pd.Series(0, index=data.index)
    p = 0
    for i in range(1, len(data)):
        c1 = (data['RSI'].iloc[i] > data['RSI_MA'].iloc[i]) and (data['RSI'].iloc[i] > 40)
        c2 = (data['Stoch_K'].iloc[i] > data['Stoch_D'].iloc[i])
        c3 = (data['Stoch_RSI_K'].iloc[i] > data['Stoch_RSI_D'].iloc[i])
        c4 = (data['CCI'].iloc[i] > -50)
        osc_score = int(c1) + int(c2) + int(c3) + int(c4)
        vol_filter = data['Volume'].iloc[i] >= data['Vol_MA20'].iloc[i] * 0.9
        bbw_filter = data['BBW'].iloc[i] >= data['BBW_MA'].iloc[i] * 0.8
        if p == 0 and osc_score >= 3 and vol_filter and bbw_filter: p = 1
        elif p == 1 and (osc_score <= 1 or (data['RSI'].iloc[i] < data['RSI_MA'].iloc[i] and data['Stoch_K'].iloc[i] < data['Stoch_D'].iloc[i])): p = 0
        sig_orig.iloc[i] = p
    results.append(evaluate(sig_orig, close, 'Setup Asli Pak Purbaya'))
    
    # 3. Setup Ideal 1: CCI + BBW Volatility Filter
    sig_ideal1 = pd.Series(0, index=data.index)
    p = 0
    for i in range(1, len(data)):
        if p == 0 and cci.iloc[i-1] <= -100 and cci.iloc[i] > -100 and bbw.iloc[i] > bbw_ma.iloc[i] * 0.7: p = 1
        elif p == 1 and cci.iloc[i] < 0: p = 0
        sig_ideal1.iloc[i] = p
    results.append(evaluate(sig_ideal1, close, 'Setup Ideal 1 (CCI + BBW Filter)'))
    
    # 4. Setup Ideal 2: CCI + BBW + ATR Trailing Stop Exit
    sig_ideal2 = pd.Series(0, index=data.index)
    p = 0
    highest_t = 0
    for i in range(1, len(data)):
        if p == 0:
            if cci.iloc[i-1] <= -100 and cci.iloc[i] > -100 and bbw.iloc[i] > bbw_ma.iloc[i] * 0.7:
                p = 1
                highest_t = high.iloc[i]
                sig_ideal2.iloc[i] = 1
        else:
            highest_t = max(highest_t, high.iloc[i])
            stop_price = highest_t - (2.0 * atr.iloc[i])
            if low.iloc[i] <= stop_price or cci.iloc[i] < -50:
                p = 0
                sig_ideal2.iloc[i] = 0
            else:
                sig_ideal2.iloc[i] = 1
    results.append(evaluate(sig_ideal2, close, 'Setup Ideal 2 (CCI + BBW + ATR Stop)'))
    
    res_df = pd.DataFrame([{k: v for k, v in r.items() if k != 'equity_curve'} for r in results]).set_index('Strategi')
    print("\n================== REKAPITULASI HASIL PENGUJIAN SETUP IDEAL ==================")
    print(res_df.round(2).to_string())

if __name__ == '__main__':
    main()
