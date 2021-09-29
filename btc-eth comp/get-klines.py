import asyncio
import json
import pandas as pd
import numpy as np

from datetime import datetime, date, timedelta
from binance import AsyncClient, DepthCacheManager, BinanceSocketManager

def utc_to_str(utc_ts_bn, div1000=False):
        if div1000:
            ts = int(utc_ts_bn)/1000
        else:
            ts = int(utc_ts_bn)
        #return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%SZ')
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        #return datetime.fromtimestamp(ts).strftime('%Y/%m/%d %H:%M')
        #return datetime.fromtimestamp(ts).strftime('%Y/%m/%d')

def handle_socket_message(msg):
    #print(f"message type: {msg['e']}")
    #print(f"message symbol: {msg['s']}")
    #print(msg)
    #print(f"time: {bn_utc_to_str(msg['E'])}")
    print(utc_to_str(msg['k']['t'], True))
    print(msg['k']['o'])
    print(msg['k']['c'])
    print(msg['k']['h'])
    print(msg['k']['l'])
    print(utc_to_str(msg['k']['T'], True))
    print("\n")
    

# [
#     [
#         1499040000000,      # Open time
#         "0.01634790",       # Open
#         "0.80000000",       # High
#         "0.01575800",       # Low
#         "0.01577100",       # Close
#         "148976.11427815",  # Volume
#         1499644799999,      # Close time
#         "2434.19055334",    # Quote asset volume
#         308,                # Number of trades
#         "1756.87402397",    # Taker buy base asset volume
#         "28.46694368",      # Taker buy quote asset volume
#         "17928899.62484339" # Can be ignored
#     ]
# ]

async def main():
    # initialise the client
    api_key = 'xc88zHqhZjLhTlYLlHRy2k30tKVVEV3oZq2GodtGP8gQloThM2R1KfMMED4goG3c'
    api_secret = 'xzZ8D5qiSXCIJgirSSbD9fLqVFkjcDIHgms17j1u1SwdklCEClSSjqbRk83ZRmO1'
    #client = Client(api_key, api_secret)
    client = await AsyncClient.create()
    
    symbol = 'EOSUSDT'

    days=3
    #days=180
    #yesterday = date.today() - timedelta(365*2-1) #2 years
    yesterday = date.today() - timedelta(days)
    unix_time= yesterday.strftime("%s")
    #print(unix_time)
    from_ts = unix_time

    # fetch 1 minute klines for the last day up until now
    #klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, from_ts)
    klines = []
    async for ohlc in await client.get_historical_klines_generator(symbol, AsyncClient.KLINE_INTERVAL_1MINUTE, from_ts):
    #async for ohlc in await client.get_historical_klines_generator(symbol, AsyncClient.KLINE_INTERVAL_1DAY, from_ts):
    #async for ohlc in await client.get_historical_klines_generator(symbol, AsyncClient.KLINE_INTERVAL_1HOUR, from_ts):
        #print(f"{bn_utc_to_str(str(ohlc[0]))}:[{ohlc[1]},{ohlc[2]},{ohlc[3]},{ohlc[4]}]")
        klines.append( [utc_to_str(str(ohlc[0]), True), ohlc[1], ohlc[2], ohlc[3], ohlc[4]] )
    df = pd.DataFrame(klines, columns=['ts','o','h','l','c']).set_index('ts')
    #print(df)
    df.to_csv('BN-'+symbol+'-'+str(days)+'d.csv')

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
