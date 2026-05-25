import ccxt
import json
import os

def get_binance_ohlcv(symbol, timeframe='1d', limit=30):
    exchange = ccxt.binanceus({
        'apiKey': os.environ.get('BINANCE_API_KEY'),
        'secret': os.environ.get('BINANCE_SECRET_KEY'),
        'enableRateLimit': True,
    })
    try:
        # Fetch OHLCV data
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        # Format data as a list of dictionaries
        formatted_ohlcv = []
        for item in ohlcv:
            formatted_ohlcv.append({
                'open_time': exchange.iso8601(item[0]),
                'open': item[1],
                'high': item[2],
                'low': item[3],
                'close': item[4],
                'volume': item[5],
            })
        return formatted_ohlcv
    except ccxt.NetworkError as e:
        print(f"Network error: {e}")
        return None
    except ccxt.ExchangeError as e:
        print(f"Exchange error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def get_all_binance_ohlcv_data():
    exchange = ccxt.binanceus({
        'enableRateLimit': True,
    })
    markets = exchange.load_markets()
    symbols = [s for s in exchange.symbols if s.endswith('/USDT') and not any(ext in s for ext in ['UP', 'DOWN', 'BULL', 'BEAR'])]

    all_ohlcv_data = {}
    for symbol in symbols:
        # For simplicity and to avoid hitting rate limits too hard, fetch less data for all symbols
        # In a real scenario, you might want to parallelize this or fetch in batches.
        ohlcv_data = get_binance_ohlcv(symbol, limit=30) 
        if ohlcv_data:
            all_ohlcv_data[symbol.replace('/USDT', '')] = ohlcv_data
    return all_ohlcv_data

if __name__ == "__main__":
    data = get_all_binance_ohlcv_data()
    print(json.dumps(data, indent=2))
