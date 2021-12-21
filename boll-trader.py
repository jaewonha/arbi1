import time
import json
from binance import Client, ThreadedWebsocketManager
from binance.enums import *

import time
from datetime import datetime, date, timedelta
import numpy as np
import pandas as pd
from util.time import *

import mplfinance as mpf
from graph.MatpilotUtil import ZoomPan

#import mplcursors #pip install mplcursors

f = open('.key.ini','r')
keyJson = json.load(f)

testnet = False
if testnet:
    api_key = keyJson['binance-testnet']['apiKey']
    sec_key = keyJson['binance-testnet']['secKey']
else:
    api_key = keyJson['binance']['apiKey']
    sec_key = keyJson['binance']['secKey']

binance = Client(api_key, sec_key)

config = {
    "asset":"BTC",
    "interval":"3m",
    "prev": 20
}
config['symbol'] = config['asset'] + "USDT"

df = Key = None
figZoom = figPan = None #prevent garbage collection
bol_upper = bol_lower = None

def main():
    downloadPrev(config)
    initGraph(config)
    applyStrategy(config)
    #launchStream(config)

def applyStrategy(config):
    pass

def downloadPrev(config, useCached:bool = True):
    global df
    if useCached:
        df = pd.read_csv('boll-tradef-df.csv', index_col=0, parse_dates=True)         
    else:
        days = 24.0/24.0
        yesterday = date.today() - timedelta(days)
        from_ts = time.mktime(yesterday.timetuple())

        klines = binance.get_historical_klines(config['symbol'], Client.KLINE_INTERVAL_1MINUTE, str(from_ts))
        klines2 = np.delete(klines, range(6,12), axis=1) #remove unnecessary column
        for i in range(0, len(klines2)):
            klines2[i][0] = utc_to_str(klines2[i][0], True) #utc to date string
            
        df = pd.DataFrame(klines2, columns=['ts','open','high','low','close','volume']) \
                .rename(columns = {'ts': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume':'Volume'}) \
                .set_index('Date')
        df.index = pd.DatetimeIndex(df.index)
        df = df.astype({"Open":float, "High":float, "Low":float, "Close":float, "Volume":float})
        df.to_csv('boll-tradef-df.csv')
    
    
    print(df)

# <- signal
#https://medium.datadriveninvestor.com/how-to-implement-bollinger-bands-in-python-1106b90da8d1
#https://pythonforfinance.net/2017/07/31/bollinger-band-trading-strategy-backtest-in-python/
#https://tradewithpython.com/generating-buy-sell-signals-using-python
def initGraph(config):
    global df, figZoom, figPan
    global bol_upper, bol_lower
    #generate processed data
    ma5  = df["Close"].rolling(5).mean().values
    ma10 = df["Close"].rolling(10).mean().values
    ma20 = df["Close"].rolling(20).mean().values
    ma40 = df["Close"].rolling(40).mean().values
    ma60 = df["Close"].rolling(60).mean().values
    ma120 = df["Close"].rolling(120).mean().values
    std20 = df["Close"].rolling(20).std()
    bol_upper = ma20 + 2*std20
    bol_lower = ma20 - 2*std20
    buySignal  = df[df['Close'] <= bol_lower]['Close'].to_frame('buySignal')
    sellSignal = df[df['Close'] >= bol_upper]['Close'].to_frame('sellSignal')
    buySignal2  = pd.concat([df['Close'],buySignal], axis=1)['buySignal']
    sellSignal2 = pd.concat([df['Close'],sellSignal], axis=1)['sellSignal']
    #construct addplot
    ma_df = pd.DataFrame(dict(Opma5=ma5,Opma10=ma10,Opma20=ma20,Opma40=ma40,Opma60=ma60,Opma120=ma120),index=df.index)
    boll_df = pd.DataFrame(dict(MA20=ma20, BollUpper=bol_upper,BollLower=bol_lower),index=df.index)
    ap = [
        #mpf.make_addplot(ma_df, type='line', width= 0.5, alpha = 1.0),
        mpf.make_addplot(boll_df, type='line', width= 0.5, alpha = 1.0),
        mpf.make_addplot(buySignal2, type='scatter', marker='^', markersize=10, color='g'),
        mpf.make_addplot(sellSignal2,type='scatter', marker='v', markersize=10, color='r'),
    ]
    #candle coloring
    mc = mpf.make_marketcolors(
            up='tab:red',down='tab:green',
            edge='lime',
            wick={'up':'red','down':'green'},
            volume='tab:blue',
        )
    s  = mpf.make_mpf_style(marketcolors=mc)

    fig, axes = mpf.plot(df,returnfig=True,figsize=(11,8), \
        volume=True, ylabel_lower='Volume', \
        type='candle',title=config['symbol'], show_nontrading=True, style=s, addplot=ap)
        
    ax = axes[0]
    #ax.fill_between(df.index.get_level_values(0), bol_upper, bol_lower, color='lightgrey')

    zp = ZoomPan()
    figZoom = zp.zoom_factory(ax, base_scale = 1.5)
    figPan = zp.pan_factory(ax)

    def on_press(event):
        global key
        print('press', event.key)
        key = event.key

    fig.canvas.mpl_connect('key_press_event', on_press)

    #mplcursors.cursor(hover=True)
    mpf.show()


def launchStream(config):
    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=sec_key)
    # start is required to initialise its internal loop
    twm.start()

    twm.start_kline_socket(callback=cb_kline, symbol=config['symbol'], interval=KLINE_INTERVAL_3MINUTE)

    #twm.start_multiplex_socket(callback=cb_book, streams=['btcusdt@bookTicker'])
    twm.start_multiplex_socket(callback=cb_book, streams=['btcusdt@depth5@100ms'])

    #twm.start_depth_socket(callback=cb_depth, symbol=symbol)
    
    twm.join()


## callbacks

def cb_kline(msg):
    print(f'[kline]{msg}')

    #check buy condition
    #update graph

#def cb_depth(msg):
    #print(f'[depth]{msg}')
    #check buy condition
    #update graph

def cb_book(msg):
    print(f'[book]{msg}')


if __name__ == "__main__":
    main()

'''
import asyncio

from binance import AsyncClient, DepthCacheManager


async def main():
    client = await AsyncClient.create()
    dcm = DepthCacheManager(client, 'BNBBTC')

    async with dcm as dcm_socket:
        while True:
            depth_cache = await dcm_socket.recv()
            print("symbol {}".format(depth_cache.symbol))
            print("top 5 bids")
            print(depth_cache.get_bids()[:5])
            print("top 5 asks")
            print(depth_cache.get_asks()[:5])
            print("last update time {}".format(depth_cache.update_time))

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
'''
