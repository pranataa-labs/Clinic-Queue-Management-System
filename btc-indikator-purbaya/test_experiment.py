import yfinance as yf
import pandas as pd
import numpy as np

def fetch_data():
    df = yf.download('BTC-USD', period='2y', interval='1d')
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    df = df.dropna()
    return df

def calculate_indicators(df):
    data = df.copy()
    close = data['Close']
    high = data['High']
    low = data['Low']
    volume = data['Volume']
    
    # 1. RSI (14)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))
    data['RSI_MA'] = data['RSI'].rolling(14).mean()
    
    # 2. Stoch RSI (14, 14, 3, 3)
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
    data['BBW'] = (bb_upper - bb_lower) / bb_mid
    data['BBW_MA'] = data['BBW'].rolling(20).mean()
    
    # 6. Volume MA20
    data['Vol_MA20'] = volume.rolling(20).mean()
    
    return data.dropna()

def backtest_strategy(signals, close_prices):
    """
    signals: Series of 1 (Long) or 0 (Cash/Flat)
    """
    pct_changes = close_prices.pct_change().shift(-1) # return on next bar
    strategy_returns = signals * pct_changes
    cum_returns = (1 + strategy_returns).cumprod()
    
    # Calculate trades
    trade_entries = (signals == 1) & (signals.shift(1).fillna(0) == 0)
    trade_exits = (signals == 0) & (signals.shift(1).fillna(0) == 1)
    
    # Evaluate individual trade returns
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
    
    win_rate = (len(wins) / len(trade_rets) * 100) if len(trade_rets) > 0 else 0
    total_ret = (cum_returns.iloc[-2] - 1) * 100 if len(cum_returns) > 1 else 0
    
    # Max drawdown
    peak = cum_returns.cummax()
    drawdown = (cum_returns - peak) / peak
    max_dd = drawdown.min() * 100
    
    # Sharpe
    daily_rf = 0
    excess_ret = strategy_returns.dropna() - daily_rf
    sharpe = (excess_ret.mean() / excess_ret.std()) * np.sqrt(365) if excess_ret.std() > 0 else 0
    
    return {
        'Total Return (%)': total_ret,
        'Win Rate (%)': win_rate,
        'Max Drawdown (%)': max_dd,
        'Sharpe Ratio': sharpe,
        'Total Trades': len(trade_rets),
        'Profit Factor': (wins.sum() / abs(losses.sum())) if len(losses) > 0 and losses.sum() != 0 else np.nan
    }

def main():
    df = fetch_data()
    print(f"Data range: {df.index[0].date()} to {df.index[-1].date()} ({len(df)} days)")
    data = calculate_indicators(df)
    
    # 1. Correlation Matrix
    corr_cols = ['RSI', 'Stoch_RSI_K', 'Stoch_K', 'CCI']
    corr = data[corr_cols].corr()
    print("\n--- Correlation Matrix (BTC 2 Years) ---")
    print(corr.round(3))
    
    # 2. Formulate Signals
    # Strategy 1: RSI (Buy < 35 cross up, Sell > 65 cross down or < MA)
    sig_rsi = pd.Series(0, index=data.index)
    pos = 0
    for i in range(1, len(data)):
        if pos == 0 and data['RSI'].iloc[i-1] <= 35 and data['RSI'].iloc[i] > 35:
            pos = 1
        elif pos == 1 and (data['RSI'].iloc[i] >= 65 or data['RSI'].iloc[i] < data['RSI_MA'].iloc[i]):
            pos = 0
        sig_rsi.iloc[i] = pos
        
    # Strategy 2: Stoch RSI (Buy %K cross %D < 25, Sell %K cross %D > 75)
    sig_stoch_rsi = pd.Series(0, index=data.index)
    pos = 0
    for i in range(1, len(data)):
        if pos == 0 and data['Stoch_RSI_K'].iloc[i] > data['Stoch_RSI_D'].iloc[i] and data['Stoch_RSI_K'].iloc[i-1] <= data['Stoch_RSI_D'].iloc[i-1] and data['Stoch_RSI_K'].iloc[i] < 30:
            pos = 1
        elif pos == 1 and data['Stoch_RSI_K'].iloc[i] < data['Stoch_RSI_D'].iloc[i] and data['Stoch_RSI_K'].iloc[i-1] >= data['Stoch_RSI_D'].iloc[i-1] and data['Stoch_RSI_K'].iloc[i] > 70:
            pos = 0
        sig_stoch_rsi.iloc[i] = pos
        
    # Strategy 3: Stoch Oscillator (Buy %K cross %D < 25, Sell %K cross %D > 75)
    sig_stoch = pd.Series(0, index=data.index)
    pos = 0
    for i in range(1, len(data)):
        if pos == 0 and data['Stoch_K'].iloc[i] > data['Stoch_D'].iloc[i] and data['Stoch_K'].iloc[i-1] <= data['Stoch_D'].iloc[i-1] and data['Stoch_K'].iloc[i] < 30:
            pos = 1
        elif pos == 1 and data['Stoch_K'].iloc[i] < data['Stoch_D'].iloc[i] and data['Stoch_K'].iloc[i-1] >= data['Stoch_D'].iloc[i-1] and data['Stoch_K'].iloc[i] > 70:
            pos = 0
        sig_stoch.iloc[i] = pos
        
    # Strategy 4: CCI (Buy CCI cross > -100, Sell CCI cross < 100 or < 0)
    sig_cci = pd.Series(0, index=data.index)
    pos = 0
    for i in range(1, len(data)):
        if pos == 0 and data['CCI'].iloc[i-1] <= -100 and data['CCI'].iloc[i] > -100:
            pos = 1
        elif pos == 1 and (data['CCI'].iloc[i] < 0):
            pos = 0
        sig_cci.iloc[i] = pos
        
    # Strategy 5: Setup Komprehensif (Pak Purbaya Combo + BBW Squeeze/Expansion + Volume)
    # Buy: Minimal 2 osilator crossing up dari area oversold + Volume > Vol_MA20 + BBW mulai ekspansi
    sig_combo = pd.Series(0, index=data.index)
    pos = 0
    for i in range(1, len(data)):
        # Kondisi osilator
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
    
    results = {
        'Buy & Hold BTC': backtest_strategy(sig_bnh, data['Close']),
        '1. RSI Single': backtest_strategy(sig_rsi, data['Close']),
        '2. Stoch RSI Single': backtest_strategy(sig_stoch_rsi, data['Close']),
        '3. Stochastic Single': backtest_strategy(sig_stoch, data['Close']),
        '4. CCI Single': backtest_strategy(sig_cci, data['Close']),
        '5. Purbaya Combo (All 4 + BBW + Vol)': backtest_strategy(sig_combo, data['Close']),
    }
    
    res_df = pd.DataFrame(results).T
    print("\n--- Backtest Performance Comparison (2 Years) ---")
    print(res_df.to_string())

if __name__ == '__main__':
    main()
