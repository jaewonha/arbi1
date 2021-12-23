import pandas as pd
import mplfinance as mpf
import matplotlib.animation as animation
import time
from graph.MatpilotUtil import ZoomPan

import time
import json
from binance import Client, ThreadedWebsocketManager
from binance.enums import *

import time
from datetime import datetime, date, timedelta
import numpy as np
import pandas as pd
from util.time import *
from util.math import *

import mplfinance as mpf
from graph.MatpilotUtil import ZoomPan

from classes import *
from arbi import *

#common
def getBianceKey(testnet:bool):
    f = open('.key.ini','r')
    keyJson = json.load(f)

    if testnet:
        api_key = keyJson['binance-testnet']['apiKey']
        sec_key = keyJson['binance-testnet']['secKey']
    else:
        api_key = keyJson['binance']['apiKey']
        sec_key = keyJson['binance']['secKey']
    return api_key, sec_key

def getBinance(testnet:bool = False):
    api_key, sec_key = getBianceKey(testnet)
    return Client(api_key, sec_key)

def getBinanceSocket(testnet:bool = False):
    api_key, sec_key = getBianceKey(testnet)
    return ThreadedWebsocketManager(api_key=api_key, api_secret=sec_key)


config = {
    "asset":"BTC",
    "interval":"3", #min
    "prev": 20
}
config['symbol'] = config['asset'] + "USDT"

P = 0
Q = 1
key = None
df = None

ex = Exchanges()
asset = 'BTC'
TEST = True            

backTesting = True
## Class to simulate getting more data from API:
class RealTimeAPI():
    def __init__(self):
        self.data_pointer = 0
        #self.df = pd.read_csv('SP500_NOV2019_IDay.csv',index_col=0,parse_dates=True)
        #self.df = self.df.iloc[0:120,:]
        days = 1 if backTesting else 2.0/24.0
        min = config['interval'] + 'm'
        fname = 'boll-tradef-df_'+str(days)+'d'+'-'+min+'.csv'
        useCached = False
        if useCached:
            df = pd.read_csv(fname, index_col=0, parse_dates=True)         
        else:
            yesterday = (datetime.now() - timedelta(9.0/24.0)) - timedelta(days) #kst-9h
            #yesterday = date.today() - timedelta(days)
            from_ts = time.mktime(yesterday.timetuple())
            #from_ts = 1640076128.0 #1
            from_ts = 1640076245.0 #3
            print(f'from_ts:{from_ts}') 
            klines = ex.binance.get_historical_klines(config['symbol'], min, str(from_ts))
            print(f'klines:{len(klines)}')
            klines2 = np.delete(klines, range(6,12), axis=1) #remove unnecessary column
            for i in range(0, len(klines2)):
                klines2[i][0] = utc_to_str(klines2[i][0], True) #utc to date string
                
            df = pd.DataFrame(klines2, columns=['ts','open','high','low','close','volume']) \
                    .rename(columns = {'ts': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume':'Volume'}) \
                    .set_index('Date')
            df.index = pd.DatetimeIndex(df.index)
            df = df.astype({"Open":float, "High":float, "Low":float, "Close":float, "Volume":float})
            df.to_csv(fname)
        self.df = df
        self.df_len = len(self.df)

    def fetch_next(self):
        r1 = self.data_pointer
        self.data_pointer += 1
        if self.data_pointer >= self.df_len:
            return None
        return self.df.iloc[r1:self.data_pointer,:] #r1:r1+1

    def initial_fetch(self):
        if self.data_pointer > 0:
            return
        r1 = self.data_pointer
        #self.data_pointer += int(0.2*self.df_len)
        #self.data_pointer += 20
        #self.data_pointer += 1
        self.data_pointer += 75 if backTesting else self.df_len
        return self.df.iloc[r1:self.data_pointer,:]

sellSignal2 = buySignal2 = None
def init():
    global df, sellSignal2, buySignal2
    #data
    rtapi = RealTimeAPI()
    df = rtapi.initial_fetch()

    ma20 = df["Close"].rolling(20).mean().values     
    std20 = df["Close"].rolling(20).std()
    bol_upper = ma20 + 2*std20
    bol_lower = ma20 - 2*std20   
    boll_df = pd.DataFrame(dict(MA20=ma20, BollUpper=bol_upper,BollLower=bol_lower),index=df.index)
    sellSignal2 = pd.DataFrame(index=df.index.copy(), columns=["sellSignal"])
    buySignal2  = pd.DataFrame(index=df.index.copy(), columns=["buySignal"])    
    #graph
    ap = [mpf.make_addplot(boll_df, type='line', width= 0.5, alpha = 1.0)]
    
    fig, axes = mpf.plot(df,returnfig=True,figsize=(11,4),type='candle',title='\n\nBTCUSDT', addplot=ap)
    ax = axes[0]

    zp = ZoomPan()
    figZoom = zp.zoom_factory(ax, base_scale = 1.5)
    figPan = zp.pan_factory(ax)

    def on_press(event):
        global key
        print('press', event.key)
        key = event.key

    fig.canvas.mpl_connect('key_press_event', on_press)

    return rtapi, fig, ax, figZoom, figPan

def current_milli_time():
    return round(time.time() * 1000)

STR_NORMAL = 20
STR_UPPER_NEXT = 21
STR_LOWER_NEXT = 21
strMode = STR_NORMAL
sellPrice = buyPrice = None
lastCompleted = None
def update(nxt, dropLast):
    global ax, fig, df, strMode, sellPrice, buyPrice, sellSignal2, buySignal2, lastCompleted
    #ts10 = current_milli_time()
    if nxt is not None:
        df = df.append(nxt)
    #print(nxt)
    ma20 = df["Close"].rolling(20).mean()     
    std20 = df["Close"].rolling(20).std()
    #ts11 = current_milli_time()
    bol_upper = ma20 + 2*std20
    bol_lower = ma20 - 2*std20   
    boll_df = pd.DataFrame(dict(MA20=ma20, BollUpper=bol_upper,BollLower=bol_lower),index=df.index)
    #ts12 = current_milli_time()
    txFee = 0.036/100
    tailRatio = 0.3

    r = nxt
    date = nxt.name
    max = cmax(r['Open'], r['Close'], r['High'])
    min = cmin(r['Open'], r['Close'], r['Low'])
    ma20v = ma20[date]

    #ts13 = current_milli_time()
    bn_order = None
    if date == lastCompleted:
        print("this candle is completed")
    elif strMode == STR_NORMAL:
        if min > ma20v and max > ma20v: #short
            #inpect upper case            
            bolv = bol_upper.loc[date]
            tail = max - bolv
            sellPrice = tail*(1-tailRatio) + bolv

            tradeDecisionPrice = bolv*(1+txFee*2)
            if sellPrice > tradeDecisionPrice:
                #_nxt = sellSignal2.iloc[-1].copy()
                #_nxt.name = date
                #_nxt['sellSignal'] = sellPrice
                #_nxt = pd.DataFrame(index=[date], data=[sellPrice], columns=['sellSignal'])
                #if dropLast: sellSignal2.drop(sellSignal2.tail(1).index,inplace=True)
                #sellSignal2 = sellSignal2.append(_nxt)
                sellSignal2.loc[date] = sellPrice
                print(f'sellSignal:{[date, sellPrice]}')
                ##trade short
                bn_order = bn_fut_trade(ex, asset, TRADE_SELL, floor_2(sellPrice), 1.0, TEST)

                strMode = STR_UPPER_NEXT
        elif min < ma20v and max < ma20v: #long
            pass
    elif strMode == STR_UPPER_NEXT:
        bolv2 = bol_upper.iloc[-1] #if bolv2 is lower than prev, use bolv1?

        r2 = nxt
        min2 = cmin(r2['Open'], r2['Close'], r2['Low'])
        if bolv2 > min2:
            buyPrice = bolv2
            #candlePassed = j-i #length...

            fee = (sellPrice + buyPrice)*txFee
            gainAmount = sellPrice - buyPrice - fee
            gainRatio = gainAmount/sellPrice 
            
            date2 = date
            buySignal2.loc[date2] = buyPrice
            #gain_df.loc[date2]['gain'] = gainRatio
            
            print(f'buySignal:{[date, buyPrice, gainAmount, gainRatio]}')
            ##trade buy
            bn_order = bn_fut_trade(ex, asset, TRADE_BUY, floor_2(buyPrice), 1.0, TEST)

            strMode = STR_NORMAL
            lastCompleted = date2
    elif strMode == STR_LOWER_NEXT:
        pass

    if len(buySignal2) < len(df): buySignal2 = buySignal2.append(pd.DataFrame(index=[date], data=[None], columns=['buySignal']))
    if len(sellSignal2) < len(df): sellSignal2 = sellSignal2.append(pd.DataFrame(index=[date], data=[None], columns=['sellSignal']))

    assert len(buySignal2) == len(df)                 
    assert len(sellSignal2) == len(df)                 

    #ts19 = current_milli_time() #long part - graph pipeline

    ap = [mpf.make_addplot(boll_df, ax=ax, type='line', width= 0.5, alpha = 1.0)]
    if buySignal2['buySignal'].sum() > 0:
        ap.append(mpf.make_addplot(buySignal2, ax=ax, type='scatter', marker='^', markersize=25, color='g'))
    if sellSignal2['sellSignal'].sum() > 0:
        ap.append(mpf.make_addplot(sellSignal2, ax=ax,type='scatter', marker='v', markersize=25, color='r'))
    #print(f"len:{len(rtapi.df)}")
    #cur_xlim = ax.get_xlim()
    #cur_ylim = ax.get_ylim()
    ax.clear()
    #ax.set_xlim(cur_xlim)
    #ax.set_ylim(cur_ylim)
    mpf.plot(df, ax=ax, type='candle', addplot=ap)

    fig.canvas.draw()
    #fig.canvas.flush_events()
    if len(df) > 25:
        df = df.iloc[-25:len(df)]
        boll_df = boll_df.iloc[-25:len(df)]
    if len(buySignal2) > 25:
        buySignal2 = buySignal2.iloc[-25:len(buySignal2)]
    if len(sellSignal2) > 25:
        sellSignal2 = sellSignal2.iloc[-25:len(sellSignal2)]
    
    #ts20 = current_milli_time()

    #print(f'update[{ts20-ts10}]ms')
    #print(f'\t[{ts11-ts10}]ms')
    #print(f'\t[{ts12-ts11}]ms')
    #print(f'\t[{ts13-ts12}]ms')
    #print(f'\t[{ts20-ts19}]ms')
    
    if bn_order: bn_wait_order(ex, bn_order, BN_FUT, TEST)
    #if failed -> prevent next order..? total amount management?
        

rtapi, fig, ax, figZoom, figPan = init()




TM_NONE = 10
TM_BUY = 11
TM_SELL = 12
tradeMode = TM_NONE
cb_cnt = 0
def cb_book(msg):
    global cb_cnt
    cb_cnt += 1
    if cb_cnt%3 != 0:
        return
    
    #print(f'[book]{msg}')
    date = datetime.now()
    ob = msg['data']
    bids = ob['bids']
    asks = ob['asks']

    bids[0][P] = float(bids[0][P])
    asks[0][P] = float(asks[0][P])
    bids[0][Q] = float(bids[0][Q])
    asks[0][Q] = float(asks[0][Q])

    if tradeMode is TM_NONE:
        estPrice = (bids[0][P] + asks[0][P])/2
    else:
        estPrice = asks[0][P] if tradeMode is TM_BUY else bids[0][P]
    
    updatePrice(date, estPrice)

def updatePrice(date, price):
    global ax, fig
    #print(f'updatePrice:[{date}:{price}]')

    #update graph
    lastRow = df.iloc[-1]
    lastDate = lastRow.name

    period = timedelta(minutes=int(config['interval']))
    nxt = lastRow.copy()
    dropLast = False
    if (date-lastDate) > period:
        nxt.name = lastDate + period
        nxt['Open'] = nxt['High'] = nxt['Low'] = nxt['Close'] = price
    else:
        nxt['Close'] = price
        if price > nxt['High']: nxt['High'] = price
        if price < nxt['Low']: nxt['Low'] = price
        df.drop(df.tail(1).index,inplace=True)
        dropLast = True
        #nxt = None
    
    update(nxt, dropLast)
    #trade decision

    #### run!
    pass

import threading
 
def work():
    global rtapi
    while True:
        nxt = rtapi.fetch_next().iloc[0]
        if nxt is None:
            break
        date = nxt.name
        delta = timedelta(seconds=60*int(config['interval'])/5)
        updatePrice(date + delta*1, nxt['Open'])
        updatePrice(date + delta*2, nxt['High'])
        updatePrice(date + delta*3, nxt['Low'])
        updatePrice(date + delta*4, nxt['Close'])

def launchStream(config):
    if backTesting:
        t = threading.Thread(target=work, args=())
        t.start()

        mpf.show()
        t.join()
        pass
    else:
        twm = getBinanceSocket()
        twm.start()
        #twm.start_kline_socket(callback=cb_kline, symbol=config['symbol'], interval=KLINE_INTERVAL_3MINUTE)
        #twm.start_multiplex_socket(callback=cb_book, streams=['btcusdt@bookTicker'])
        twm.start_multiplex_socket(callback=cb_book, streams=['btcusdt@depth5@100ms'])
        #twm.start_depth_socket(callback=cb_depth, symbol=symbol)

        mpf.show()
        twm.join()

launchStream(config)

#mpf.show() #inside launchStream