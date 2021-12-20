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

def main():
    downloadPrev(config)
    initGraph(config)
    #launchStream(config)

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
    #moving average
    mav5 = df["Close"].rolling(5).mean().values
    mav10 = df["Close"].rolling(10).mean().values
    mav20 = df["Close"].rolling(20).mean().values
    mav40 = df["Close"].rolling(40).mean().values
    mav60 = df["Close"].rolling(60).mean().values
    mav120 = df["Close"].rolling(120).mean().values
    std20 = df["Close"].rolling(20).std()
    bol_upper = mav20 + 2*std20
    bol_lower = mav20 - 2*std20
    #mavdf = pd.DataFrame(dict(OpMav5=mav5,OpMav10=mav10,OpMav20=mav20,OpMav40=mav40,OpMav60=mav60,OpMav120=mav120),index=df.index)
    #mavdf = pd.DataFrame(dict(BollUpper=bol_upper,BollLower=bol_lower, OpMav5=mav5,OpMav10=mav10,OpMav20=mav20,OpMav40=mav40,OpMav60=mav60,OpMav120=mav120),index=df.index)
    mavdf = pd.DataFrame(dict(OpMav20=mav20, BollUpper=bol_upper,BollLower=bol_lower),index=df.index)
    ap = mpf.make_addplot(mavdf,type='line', width= 0.5, alpha = 1.0)
    #candle coloring
    mc = mpf.make_marketcolors(
                            up='tab:blue',down='tab:red',
                            edge='lime',
                            wick={'up':'blue','down':'red'},
                            volume='tab:green',
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
