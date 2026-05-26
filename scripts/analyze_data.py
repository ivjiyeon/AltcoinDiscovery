import json
import sys
import pandas as pd
import ta
from scipy.signal import find_peaks

def _find_peaks_troughs(prices, order=5):
    # Find peaks
    peaks, _ = find_peaks(prices, order=order)
    # Find troughs (inverted peaks)
    troughs, _ = find_peaks(-prices, order=order)
    return peaks, troughs

def _detect_pattern_breakout(df, entry_price, breakout_threshold_percent=0.01):
    # Check if the last close price broke above/below a certain level
    # with increased volume.
    last_close = df['close'].iloc[-1]
    last_volume = df['volume'].iloc[-1]
    prev_volume = df['volume'].iloc[-2]

    if breakout_threshold_percent > 0: # Bullish breakout
        if last_close > entry_price * (1 + breakout_threshold_percent) and last_volume > prev_volume * 1.2:
            return True
    elif breakout_threshold_percent < 0: # Bearish breakout
        if last_close < entry_price * (1 + breakout_threshold_percent) and last_volume > prev_volume * 1.2:
            return True
    return False

def find_head_and_shoulders(df):
    # Advanced Inverse Head and Shoulders (bullish) pattern detection.
    # An Inverse Head and Shoulders is a bullish reversal pattern.
    # We look for three troughs with the middle one (head) being the lowest,
    # and two peaks (shoulders) at roughly similar levels.
    # A breakout above the neckline confirms the pattern.

    if len(df) < 60: # Need sufficient data for a robust pattern
        return False

    prices = df['close'].values
    peaks, troughs = _find_peaks_troughs(prices, order=5) # Adjust order based on desired sensitivity

    # Filter for recent troughs and peaks
    recent_troughs = [t for t in troughs if t > len(df) - 60]
    recent_peaks = [p for p in peaks if p > len(df) - 60]

    if len(recent_troughs) < 3 or len(recent_peaks) < 2:
        return False

    # Look for Left Shoulder, Head, Right Shoulder (troughs)
    # and two intermediate peaks
    # This is a simplified search and assumes a clear sequence.
    # A more robust solution would iterate through combinations.
    
    # Try to find a Head (lowest trough)
    head_idx = -1
    for i in recent_troughs:
        if head_idx == -1 or prices[i] < prices[head_idx]:
            head_idx = i
            
    if head_idx == -1: return False
            
    # Find potential left shoulder (trough before head) and right shoulder (trough after head)
    left_shoulder_candidates = [t for t in recent_troughs if t < head_idx and t > head_idx - 30]
    right_shoulder_candidates = [t for t in recent_troughs if t > head_idx and t < head_idx + 30]

    if not left_shoulder_candidates or not right_shoulder_candidates:
        return False

    # Take the closest troughs as shoulders for simplicity
    ls_idx = max(left_shoulder_candidates)
    rs_idx = min(right_shoulder_candidates)
    
    # Validate shoulder and head relationships
    # Head should be the lowest
    if not (prices[ls_idx] > prices[head_idx] < prices[rs_idx]):
        return False
        
    # Shoulders should be at roughly similar levels
    if abs(prices[ls_idx] - prices[rs_idx]) / prices[ls_idx] > 0.05: # 5% tolerance
        return False

    # Find the peaks (neckline points) between LS-Head and Head-RS
    peak1_candidates = [p for p in recent_peaks if ls_idx < p < head_idx]
    peak2_candidates = [p for p in recent_peaks if head_idx < p < rs_idx]

    if not peak1_candidates or not peak2_candidates:
        return False

    peak1_idx = max(peak1_candidates)
    peak2_idx = min(peak2_candidates)

    # Neckline: average of the two peaks
    neckline_price = (prices[peak1_idx] + prices[peak2_idx]) / 2

    # Check for breakout above neckline
    # Also ensure the breakout happens recently and with increased volume
    if df['close'].iloc[-1] > neckline_price and _detect_pattern_breakout(df, neckline_price):
        return True

    return False

def find_double_bottom_top(df, pattern_type='bottom'):
    # Advanced Double Bottom/Top pattern detection.
    # A Double Bottom is a bullish reversal pattern.
    # A Double Top is a bearish reversal pattern.

    if len(df) < 60: # Need sufficient data for a robust pattern
        return False

    prices = df['close'].values
    peaks, troughs = _find_peaks_troughs(prices, order=5)

    # Filter for recent troughs and peaks
    recent_troughs = [t for t in troughs if t > len(df) - 60]
    recent_peaks = [p for p in peaks if p > len(df) - 60]

    if pattern_type == 'bottom':
        if len(recent_troughs) < 2 or len(recent_peaks) < 1:
            return False

        # Look for two recent troughs (B1, B2) and an intermediate peak
        # Iterate through combinations to find valid patterns
        for i in range(len(recent_troughs) - 1):
            b1_idx = recent_troughs[i]
            for j in range(i + 1, len(recent_troughs)):
                b2_idx = recent_troughs[j]

                if b2_idx - b1_idx < 10: # Ensure sufficient separation between bottoms
                    continue

                # Check if bottoms are at similar price levels
                if abs(prices[b1_idx] - prices[b2_idx]) / prices[b1_idx] > 0.03: # 3% tolerance
                    continue

                # Find intermediate peak
                intermediate_peaks_between = [p for p in recent_peaks if b1_idx < p < b2_idx]
                if not intermediate_peaks_between:
                    continue
                
                intermediate_peak_idx = intermediate_peaks_between[0] # Take the first for simplicity
                # Ensure intermediate peak is significantly higher than bottoms
                if prices[intermediate_peak_idx] < prices[b1_idx] * 1.05: # At least 5% higher
                    continue

                # Neckline is the intermediate peak price
                neckline_price = prices[intermediate_peak_idx]

                # Check for breakout above neckline
                if df['close'].iloc[-1] > neckline_price and _detect_pattern_breakout(df, neckline_price):
                    return True

    elif pattern_type == 'top': # Double Top
        if len(recent_peaks) < 2 or len(recent_troughs) < 1:
            return False

        # Look for two recent peaks (T1, T2) and an intermediate trough
        for i in range(len(recent_peaks) - 1):
            t1_idx = recent_peaks[i]
            for j in range(i + 1, len(recent_peaks)):
                t2_idx = recent_peaks[j]

                if t2_idx - t1_idx < 10: # Ensure sufficient separation
                    continue

                # Check if tops are at similar price levels
                if abs(prices[t1_idx] - prices[t2_idx]) / prices[t1_idx] > 0.03: # 3% tolerance
                    continue

                # Find intermediate trough
                intermediate_troughs_between = [t for t in recent_troughs if t1_idx < t < t2_idx]
                if not intermediate_troughs_between:
                    continue

                intermediate_trough_idx = intermediate_troughs_between[0]
                # Ensure intermediate trough is significantly lower than tops
                if prices[intermediate_trough_idx] > prices[t1_idx] * 0.95: # At least 5% lower
                    continue

                # Neckline is the intermediate trough price
                neckline_price = prices[intermediate_trough_idx]

                # Check for breakout below neckline
                if df['close'].iloc[-1] < neckline_price and _detect_pattern_breakout(df, neckline_price, breakout_threshold_percent=-0.01): # Negative for breakdown
                    return True

    return False

def analyze_accumulation(df):
    # Advanced Volume Accumulation detection using CMF and VPT.
    # Chaikin Money Flow (CMF) measures the amount of Money Flow Volume over a specific period.
    # Volume Price Trend (VPT) is a momentum indicator that relates volume changes to price changes.
    if len(df) < 30: # Need sufficient data for CMF and VPT
        return False

    # CMF analysis: Look for positive CMF indicating buying pressure
    # and/or a rising trend in CMF.
    recent_cmf = df['cmf'].iloc[-10:]
    cmf_threshold = 0.1 # A common threshold for CMF

    cmf_condition = False
    if recent_cmf.iloc[-1] > cmf_threshold and recent_cmf.iloc[-1] > recent_cmf.iloc[-5]: # Current CMF is positive and rising
        cmf_condition = True

    # VPT analysis: Look for a rising VPT, indicating accumulation alongside price increases.
    recent_vpt = df['vpt'].iloc[-10:]
    vpt_condition = False
    if len(recent_vpt) > 1 and recent_vpt.iloc[-1] > recent_vpt.iloc[-5]: # VPT is trending upwards
        vpt_condition = True

    # Combine conditions: at least one volume indicator should be bullish, 
    # and price should not be significantly declining.
    price_condition = df['close'].iloc[-1] > df['close'].iloc[-10] * 0.98 # Price moved up at least 2% or stayed flat over 10 periods

    if (cmf_condition or vpt_condition) and price_condition:
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
        
        # Advanced Volume Indicators
        df['vpt'] = ta.volume.VolumePriceTrend(close=df['close'], volume=df['volume'], fillna=True).volume_price_trend()
        df['cmf'] = ta.volume.ChaikinMoneyFlowIndicator(high=df['high'], low=df['low'], close=df['close'], volume=df['volume'], window=20, fillna=True).chaikin_money_flow()

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
