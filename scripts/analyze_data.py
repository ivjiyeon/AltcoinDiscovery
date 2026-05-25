import json
import sys
import pandas as pd

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

        # Simple analysis: check for a significant price increase in the last day
        if len(df) > 1: # Ensure there's at least today and yesterday's data
            today_close = df.iloc[-1]['close']
            today_open = df.iloc[-1]['open']
            yesterday_close = df.iloc[-2]['close']

            # Example: If today's close is significantly higher than yesterday's close and today's open
            if today_close > yesterday_close * 1.05 and today_close > today_open * 1.05: # 5% increase
                # More sophisticated analysis would go here (e.g., volume spikes, indicator analysis)
                potential_percent = ((today_close - yesterday_close) / yesterday_close) * 100
                estimated_target_price = today_close * 1.30 # Example target: 30% above current

                shooting_coins.append({
                    'coin': coin,
                    'current_price': today_close,
                    'potential_percent': potential_percent,
                    'estimated_target_price': estimated_target_price
                })
    return shooting_coins

if __name__ == "__main__":
    # Read OHLCV data from stdin
    raw_data = sys.stdin.read()
    ohlcv_data = json.loads(raw_data)
    
    result = analyze_data(ohlcv_data)
    print(json.dumps(result, indent=2))
