import json
import sys
import pandas as pd
import ta

def find_head_and_shoulders(df):
    # Simplified Inverse Head and Shoulders (bullish) pattern detection.
    # Requires sufficient data points.
    if len(df) < 15: # Need at least 15 candles for a plausible pattern
        return False

    # Look for three troughs (LSH, H, RSH) and two peaks (between LSH-H and H-RSH)
    # This is a very basic heuristic and not a robust financial pattern detection.
    # A more advanced implementation would use peak/trough detection algorithms and neckline validation.

    # For simplicity, let's look for a general shape in recent data
    # This is highly simplified and illustrative.
    recent_closes = df['close'].iloc[-15:].reset_index(drop=True)

    # Example heuristic: a dip, then a deeper dip, then a shallower dip
    # followed by a breakout. This is NOT a precise H&S detection.
    # This part would need significant development for real-world use.
    # For now, let's return False to avoid false positives with this placeholder.
    return False

def find_double_bottom_top(df, pattern_type='bottom'):
    # Simplified Double Bottom (bullish) pattern detection.
    # Requires sufficient data points.
    if len(df) < 20: # Need at least 20 candles for a plausible pattern
        return False

    if pattern_type == 'bottom':
        # Look for two distinct troughs at similar levels, separated by a peak.
        # This is a very basic heuristic and not a robust financial pattern detection.
        # A more advanced implementation would use peak/trough detection algorithms and neckline validation.

        recent_lows = df['low'].iloc[-20:]
        # Find potential first bottom (B1)
        b1_idx = recent_lows.nsmallest(2).index[0] # Smallest low
        # Find potential second bottom (B2)
        b2_idx = recent_lows.nsmallest(2).index[1] # Second smallest low
        
        # Ensure B1 and B2 are somewhat separated in time and price
        if abs(b1_idx - b2_idx) > 3 and abs(recent_lows.loc[b1_idx] - recent_lows.loc[b2_idx]) / recent_lows.loc[b1_idx] < 0.03: # Within 3%
            # Check for an intermediate peak between B1 and B2
            start_idx = min(b1_idx, b2_idx)
            end_idx = max(b1_idx, b2_idx)
            intermediate_peak = df['high'].iloc[start_idx:end_idx].max()
            
            if intermediate_peak > recent_lows.loc[start_idx] * 1.05: # Intermediate peak is at least 5% higher than bottoms
                # Now check for a breakout above the intermediate peak level (neckline)
                if df['close'].iloc[-1] > intermediate_peak:
                    return True
    return False

def analyze_accumulation(df):
    # Simplified Volume Accumulation detection using On-Balance Volume (OBV).
    # OBV is a momentum indicator that relates volume changes to price changes.
    # A rising OBV indicates that volume is flowing into an asset, suggesting accumulation.
    if len(df) < 20: # Need sufficient data for OBV
        return False

    df['obv'] = ta.volume.OnBalanceVolumeIndicator(close=df['close'], volume=df['volume'], fillna=True).on_balance_volume()

    # Check if OBV is trending upwards recently
    # This is a basic check. A more advanced check would look for divergence, etc.
    recent_obv = df['obv'].iloc[-10:]
    if len(recent_obv) > 1 and recent_obv.iloc[-1] > recent_obv.iloc[0]:
        # Check if price is also generally moving upwards or consolidating
        recent_closes = df['close'].iloc[-10:]
        if recent_closes.iloc[-1] > recent_closes.iloc[0] * 0.98: # Price moved up at least 2% or stayed flat
            return True
    return False

def is_shooting_coin(df):
    reasons = []

    if len(df) < 2:  # Need at least two data points for most analysis
        return False, reasons

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    # RSI Check (e.g., oversold and starting to recover, or strong momentum without being overbought)
    if latest['rsi'] < 40 and latest['rsi'] > previous['rsi']: # Coming out of oversold
        reasons.append("RSI showing recovery from oversold")
    elif latest['rsi'] > 60 and latest['rsi'] > previous['rsi'] and latest['rsi'] < 70: # Strong but not overbought
        reasons.append("RSI showing strong momentum")

    # MACD Check (e.g., bullish crossover)
    if latest['macd'] > latest['macd_signal'] and previous['macd'] < previous['macd_signal']:
        reasons.append("MACD bullish crossover")

    # Bollinger Bands Check (e.g., price breaking out above upper band)
    if latest['close'] > latest['bollinger_high'] and previous['close'] < previous['bollinger_high']:
        reasons.append("Price breaking above Bollinger Upper Band")

    # Ichimoku Cloud Check (e.g., Tenkan-sen (conversion) crossing above Kijun-sen (base))
    if latest['ichimoku_conversion'] > latest['ichimoku_base'] and previous['ichimoku_conversion'] < previous['ichimoku_base']:
        reasons.append("Ichimoku Conversion Line bullish crossover")
    
    # Chart Patterns (using placeholder functions)
    if find_head_and_shoulders(df): # Assuming this detects bullish H&S (inverse H&S)
        reasons.append("Inverse Head and Shoulders pattern detected")
    if find_double_bottom_top(df, pattern_type='bottom'):
        reasons.append("Double Bottom pattern detected")

    # Volume Analysis (using placeholder function)
    if analyze_accumulation(df):
        reasons.append("Volume accumulation detected")

    return len(reasons) > 0, reasons

def analyze_data(ohlcv_data):
    shooting_coins = []
    for coin, data in ohlcv_data.items():
        df = pd.DataFrame(data)
        if df.empty: # Skip empty dataframes
            continue
        
        # Ensure numeric types for calculations
        df['open'] = pd.to_numeric(df['open'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        df['close'] = pd.to_numeric(df['close'])
        df['volume'] = pd.to_numeric(df['volume'])

        # Calculate Technical Indicators
        df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=14, fillna=True).rsi()
        df['macd'] = ta.trend.MACD(close=df['close'], window_fast=12, window_slow=26, window_sign=9, fillna=True).macd()
        df['macd_signal'] = ta.trend.MACD(close=df['close'], window_fast=12, window_slow=26, window_sign=9, fillna=True).macd_signal()
        df['bollinger_high'] = ta.volatility.BollingerBands(close=df['close'], window=20, window_dev=2, fillna=True).bollinger_hband()
        df['bollinger_low'] = ta.volatility.BollingerBands(close=df['close'], window=20, window_dev=2, fillna=True).bollinger_lband()
        df['ichimoku_base'] = ta.trend.IchimokuIndicator(high=df['high'], low=df['low'], close=df['close'], window1=9, window2=26, window3=52, fillna=True).ichimoku_base_line()
        df['ichimoku_conversion'] = ta.trend.IchimokuIndicator(high=df['high'], low=df['low'], close=df['close'], window1=9, window2=26, window3=52, fillna=True).ichimoku_conversion_line()
        df['ichimoku_a'] = ta.trend.IchimokuIndicator(high=df['high'], low=df['low'], close=df['close'], window1=9, window2=26, window3=52, fillna=True).ichimoku_a()
        df['ichimoku_b'] = ta.trend.IchimokuIndicator(high=df['high'], low=df['low'], close=df['close'], window1=9, window2=26, window3=52, fillna=True).ichimoku_b()

        # Advanced analysis using indicators and patterns
        is_shooting, reasons = is_shooting_coin(df)
        
        if is_shooting:
            shooting_coins.append({
                'coin': coin,
                'current_price': df.iloc[-1]['close'],
                'reasons': reasons
            })
    return shooting_coins

if __name__ == "__main__":
    # Read OHLCV data from stdin
    raw_data = sys.stdin.read()
    ohlcv_data = json.loads(raw_data)
    
    result = analyze_data(ohlcv_data)
    print(json.dumps(result, indent=2))
