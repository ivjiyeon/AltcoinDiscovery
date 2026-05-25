import os
from binance.um_futures import UMFutures
import pandas as pd
import datetime
import json

def get_futures_symbols():
    client = UMFutures()
    exchange_info = client.exchange_info()
    symbols = []
    for s in exchange_info['symbols']:
        if s['contractType'] == 'PERPETUAL' and s['status'] == 'TRADING':
            if s['symbol'] not in ['BTCUSDT', 'ETHUSDT']:
                symbols.append(s['symbol'])
    return symbols

def get_weekly_candlestick_data(symbol, limit=52): # last 52 weeks = 1 year
    client = UMFutures()
    klines = client.klines(symbol=symbol, interval='1w', limit=limit)
    df = pd.DataFrame(klines, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    df = df[['open_time', 'open', 'high', 'low', 'close', 'volume']].astype({
        'open': float, 'high': float, 'low': float, 'close': float, 'volume': float
    })
    return df

if __name__ == "__main__":
    altcoin_symbols = get_futures_symbols()
    all_altcoin_data = {}
    symbols_to_fetch = altcoin_symbols[:50]

    for symbol in symbols_to_fetch:
        try:
            data = get_weekly_candlestick_data(symbol)
            if not data.empty:
                all_altcoin_data[symbol] = data.to_dict(orient='records')
        except Exception as e:
            pass

    print(json.dumps(all_altcoin_data))

