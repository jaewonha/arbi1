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

def downloadPrev(config, useCached:bool = False):
    global df
    days = 3
    min = Client.KLINE_INTERVAL_3MINUTE
    fname = 'boll-tradef-df_'+str(days)+'d'+'-'+min+'.csv'
    if useCached:
        df = pd.read_csv(fname, index_col=0, parse_dates=True)         
    else:
        
        yesterday = date.today() - timedelta(days)
        from_ts = time.mktime(yesterday.timetuple())

        klines = binance.get_historical_klines(config['symbol'], min, str(from_ts))
        klines2 = np.delete(klines, range(6,12), axis=1) #remove unnecessary column
        for i in range(0, len(klines2)):
            klines2[i][0] = utc_to_str(klines2[i][0], True) #utc to date string
            
        df = pd.DataFrame(klines2, columns=['ts','open','high','low','close','volume']) \
                .rename(columns = {'ts': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume':'Volume'}) \
                .set_index('Date')
        df.index = pd.DatetimeIndex(df.index)
        df = df.astype({"Open":float, "High":float, "Low":float, "Close":float, "Volume":float})
        df.to_csv(fname)
    
    
    print(df)

def cmax(arg1, arg2, arg3):
    return max(max(arg1, arg2), arg3)

def cmin(arg1, arg2, arg3):
    return min(min(arg1, arg2), arg3)    

# <- signal
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
    #stratedgy
    txFee = 0.036/100
    tailRatio = 0.3

    sellSignal2 = pd.DataFrame(index=df.index.copy(), columns=["sellSignal"])
    buySignal2  = pd.DataFrame(index=df.index.copy(), columns=["buySignal"])    
    gain_df     = pd.DataFrame(index=df.index.copy(), columns=["gain"])    

    for i in range(19, len(df.index)):
        date = df.index[i]
        r = df.loc[date]
        max = cmax(r['Open'], r['Close'], r['High'])
        min = cmin(r['Open'], r['Close'], r['Low'])
    
        ma20v = ma20[i]

        if min > ma20v and max > ma20v:
            #inpect upper case            
            bolv = bol_upper.loc[date]

            tail = max - bolv
            sellPrice = tail*(1-tailRatio) + bolv

            tradeDecisionPrice = bolv*(1+txFee*2)
            if sellPrice > tradeDecisionPrice:
                for j in range(i, len(df.index)):
                    date2 = df.index[j]
                    bolv2 = bol_upper.loc[date2] #if bolv2 is lower than prev, use bolv1?

                    r2 = df.loc[date2]
                    min2 = cmin(r2['Open'], r2['Close'], r2['Low'])
                    if bolv2 > min2:
                        buyPrice = bolv2
                        candlePassed = j-i
                        if candlePassed > 0:
                            print(f"candlePassed:{candlePassed}")
                        break

                fee = (sellPrice + buyPrice)*txFee
                gainRatio = (sellPrice - buyPrice - fee)/sellPrice 
                
                sellSignal2.loc[date] = sellPrice
                buySignal2.loc[date2] = buyPrice
                gain_df.loc[date2]['gain'] = gainRatio
                #sell 
                #sellSignal2
                #gain = sellPrice / bolv - txFee

                '''
                if gain < 0 and i+1 < len(df.index):
                    idx2 = df.index[i+1]
                    r2 = df.loc[idx2]
                    min2 = min(r['Open'], r['Close'], r['Low'])
                    
                    #!issue <- min2를 잡는다는 보장이 없다... 바로 타고 올라갈 수도 있음.. 드물지만.. low candle 처리해줘야..? 예외케이스 따로 확인 필요
                    #바로 빠지지 않으면 거기서 팔아 치워야됨..?
                    buyPrice = bolv if min2 < bolv else min2 
                '''
        elif min < ma20v and max < ma20v:
            #inpect lower case
            #bolv = bol_lower.loc[idx]
            pass
    
    sum = gain_df['gain'].sum()
    print ("gain_df sum(%):", sum*100) 

    #buySignal  = df[df['Close'] <= bol_lower]['Close'].to_frame('buySignal')
    #sellSignal = df[df['Close'] >= bol_upper]['Close'].to_frame('sellSignal')
    #buySignal2  = pd.concat([df['Close'],buySignal], axis=1)['buySignal']
    #sellSignal2 = pd.concat([df['Close'],sellSignal], axis=1)['sellSignal']
    #construct addplot
    ma_df = pd.DataFrame(dict(Opma5=ma5,Opma10=ma10,Opma20=ma20,Opma40=ma40,Opma60=ma60,Opma120=ma120),index=df.index)
    boll_df = pd.DataFrame(dict(MA20=ma20, BollUpper=bol_upper,BollLower=bol_lower),index=df.index)
    ap = [
        #mpf.make_addplot(ma_df, type='line', width= 0.5, alpha = 1.0),
        mpf.make_addplot(boll_df, type='line', width= 0.5, alpha = 1.0),
        mpf.make_addplot(buySignal2, type='scatter', marker='^', markersize=25, color='g'),
        mpf.make_addplot(sellSignal2,type='scatter', marker='v', markersize=25, color='r'),
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
