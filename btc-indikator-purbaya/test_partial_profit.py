import yfinance as yf
import pandas as pd
import numpy as np

def fetch_data():
    df = yf.download('BTC-USD', period='2y', interval='1d')
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    return df.dropna()

def main():
    df = fetch_data()
    close = df['Close']
    high = df['High']
    low = df['Low']
    
    # 1. CCI 20
    tp = (high + low + close) / 3
    sma_tp = tp.rolling(20).mean()
    md = tp.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    cci = (tp - sma_tp) / (0.015 * md)
    
    # 2. BBW
    bb_mid = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    bbw = (4 * bb_std) / bb_mid
    bbw_ma = bbw.rolling(20).mean()
    
    # 3. ATR 14
    prev_close = close.shift(1)
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    
    def simulate_partial(sell_pct=0.5, name=""):
        sig = pd.Series(0.0, index=df.index)
        in_pos = False
        half_closed = False
        highest_h = 0
        
        for i in range(1, len(df)):
            if not in_pos:
                if cci.iloc[i-1] <= -100 and cci.iloc[i] > -100 and bbw.iloc[i] > bbw_ma.iloc[i] * 0.7:
                    in_pos = True
                    half_closed = False
                    highest_h = high.iloc[i]
                    sig.iloc[i] = 1.0
            else:
                highest_h = max(highest_h, high.iloc[i])
                
                # Partial profit taking when CCI reaches overbought (> 100)
                if not half_closed and cci.iloc[i] >= 100:
                    half_closed = True
                
                curr_weight = (1.0 - sell_pct) if half_closed else 1.0
                trailing_sl = highest_h - (2.0 * atr.iloc[i])
                
                if low.iloc[i] <= trailing_sl or cci.iloc[i] < -50:
                    in_pos = False
                    sig.iloc[i] = 0.0
                else:
                    sig.iloc[i] = curr_weight
                    
        pct_changes = close.pct_change().shift(-1)
        ret = (1 + sig * pct_changes).cumprod()
        peak = ret.cummax()
        dd = ((ret - peak) / peak).min() * 100
        strat_ret = sig * pct_changes
        sharpe = (strat_ret.mean() / strat_ret.std()) * np.sqrt(365) if strat_ret.std() > 0 else 0
        tot_ret = (ret.iloc[-2] - 1) * 100
        
        return {
            'Strategi': name,
            'Total Return (%)': tot_ret,
            'Max Drawdown (%)': dd,
            'Sharpe Ratio': sharpe
        }
        
    results = [
        {'Strategi': 'Buy & Hold BTC', 'Total Return (%)': -18.18, 'Max Drawdown (%)': -53.06, 'Sharpe Ratio': -0.03},
        simulate_partial(sell_pct=0.0, name='Full Trail (Tanpa Partial PT / 100% Runner)'),
        simulate_partial(sell_pct=0.3, name='Partial PT 30% di Overbought + 70% Runner'),
        simulate_partial(sell_pct=0.5, name='Partial PT 50% di Overbought + 50% Runner'),
        simulate_partial(sell_pct=0.7, name='Partial PT 70% di Overbought + 30% Runner'),
    ]
    
    res_df = pd.DataFrame(results).set_index('Strategi')
    print("\n================== HASIL UJI PARTIAL PROFIT-TAKING PADA BITCOIN ==================")
    print(res_df.round(2).to_string())

if __name__ == '__main__':
    main()
