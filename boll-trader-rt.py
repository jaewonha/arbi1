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

binance = getBinance(False)
df = None

## Class to simulate getting more data from API:
class RealTimeAPI():
    def __init__(self):
        self.data_pointer = 0
        #self.df = pd.read_csv('SP500_NOV2019_IDay.csv',index_col=0,parse_dates=True)
        #self.df = self.df.iloc[0:120,:]
        days = 2.0/24.0
        min = config['interval'] + 'm'
        fname = 'boll-tradef-df_'+str(days)+'d'+'-'+min+'.csv'
        useCached = False
        if useCached:
            df = pd.read_csv(fname, index_col=0, parse_dates=True)         
        else:
            yesterday = (datetime.now() - timedelta(9.0/24.0)) - timedelta(days) #kst-9h
            #yesterday = date.today() - timedelta(days)
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
        self.data_pointer += self.df_len
        return self.df.iloc[r1:self.data_pointer,:]

def init():
    global df
    #data
    rtapi = RealTimeAPI()
    df = rtapi.initial_fetch()

    ma20 = df["Close"].rolling(20).mean().values     
    std20 = df["Close"].rolling(20).std()
    bol_upper = ma20 + 2*std20
    bol_lower = ma20 - 2*std20   
    boll_df = pd.DataFrame(dict(MA20=ma20, BollUpper=bol_upper,BollLower=bol_lower),index=df.index)
    
    #graph
    ap = [
        mpf.make_addplot(boll_df, type='line', width= 0.5, alpha = 1.0),
        #mpf.make_addplot(buySignal2, type='scatter', marker='^', markersize=25, color='g'),
        #mpf.make_addplot(sellSignal2,type='scatter', marker='v', markersize=25, color='r'),
    ]
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

def update(nxt):
    global ax, fig, df
    if nxt is not None:
        df = df.append(nxt)

    ma20 = df["Close"].rolling(20).mean().values     
    std20 = df["Close"].rolling(20).std()
    bol_upper = ma20 + 2*std20
    bol_lower = ma20 - 2*std20   
    boll_df = pd.DataFrame(dict(MA20=ma20, BollUpper=bol_upper,BollLower=bol_lower),index=df.index)
    ap = [
        mpf.make_addplot(boll_df, ax=ax, type='line', width= 0.5, alpha = 1.0),
        #mpf.make_addplot(buySignal2, type='scatter', marker='^', markersize=25, color='g'),
        #mpf.make_addplot(sellSignal2,type='scatter', marker='v', markersize=25, color='r'),
    ]
    #print(f"len:{len(rtapi.df)}")
    #cur_xlim = ax.get_xlim()
    #cur_ylim = ax.get_ylim()
    ax.clear()
    #ax.set_xlim(cur_xlim)
    #ax.set_ylim(cur_ylim)
    mpf.plot(df, ax=ax, type='candle', addplot=ap)

    fig.canvas.draw()
    #fig.canvas.flush_events()

rtapi, fig, ax, figZoom, figPan = init()

'''
import threading
 
def sum(rtapi):
    for i in range(1,100):
        time.sleep(0.25)
        if key == 'q': break
        print(f'draw:{i}')
        nxt = rtapi.fetch_next()
        update(nxt)

t = threading.Thread(target=sum, args=(rtapi))
t.start()
'''


TM_NONE = 10
TM_BUY = 11
TM_SELL = 12
tradeMode = TM_NONE
cb_cnt = 0
def cb_book(msg):
    global cb_cnt
    cb_cnt += 1
    if cb_cnt%3 is not 0:
        return
    
    print(f'[book]{msg}')
    #{'stream': 'btcusdt@depth5@100ms', 'data': {'lastUpdateId': 15792298707, 
    # 'bids': [['49382.12000000', '0.26907000'], ['49379.65000000', '0.33396000'], ['49377.28000000', '0.04569000'], ['49377.18000000', '0.06400000'], ['49375.40000000', '0.00829000']], 
    # 'asks': [['49384.37000000', '0.00700000'], ['49384.38000000', '0.01999000'], ['49385.41000000', '0.09458000'], ['49385.42000000', '0.04000000'], ['49386.28000000', '0.23000000']]
    # }}
    #msg['stream']
    #msg['data']['lastUpdateId']
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
    print('updatePrice')
    global ax, fig
    #update graph
    lastRow = df.iloc[-1]
    lastDate = lastRow.name

    period = timedelta(minutes=int(config['interval']))
    nxt = lastRow.copy()
    if (date-lastDate) > period:
        nxt.name = lastDate + period
        nxt['Open'] = nxt['High'] = nxt['Low'] = nxt['Close'] = price
    else:
        nxt['Close'] = price
        if price > nxt['High']: nxt['High'] = price
        if price < nxt['Low']: nxt['Low'] = price
        df.drop(df.tail(1).index,inplace=True)
        #nxt = None
    
    update(nxt)
    #trade decision

    #### run!
    pass


def launchStream(config):
    twm = getBinanceSocket()
    twm.start()
    #twm.start_kline_socket(callback=cb_kline, symbol=config['symbol'], interval=KLINE_INTERVAL_3MINUTE)
    #twm.start_multiplex_socket(callback=cb_book, streams=['btcusdt@bookTicker'])
    twm.start_multiplex_socket(callback=cb_book, streams=['btcusdt@depth5@100ms'])
    #twm.start_depth_socket(callback=cb_depth, symbol=symbol)
    print('show')
    mpf.show()
    print('join')
    twm.join()
    
launchStream(config)

#mpf.show() #inside launchStream