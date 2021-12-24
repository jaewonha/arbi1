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

import threading

'''
1. 시뮬레이션 한번에 돌려보기
2. 100ms 오차 sims가능하려나..? (다음 ob에 적용..?, 아님 window를 넓혀서 적용..?)
 -> 다음 ob까지 persist한 ob에 대해 order
3. tail왔다갔다 하는거 놓치는 거에 대해 중복 적용..? <- 이전보다 위로 간다면..? 리스크 없다면..? 리스크 나오는 케이스 조심하여 확인
4. boll under side 코드 적용
5. 실제 적용
'''
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
#fastTesting = True
#backTestingSrc = 'candle-fetch'
backTestingSrc = 'ob-dump'
useCached = False
narrowWindow = False
useObDump = False
obDumpPath = './bn-dump/bn-ob-20211223_002151-copy.txt'
obDumpFp = None
prevLen = 21
rtLen = 25
forceDraw = True
## Class to simulate getting more data from API:
class BTDataFeeder(): #BackTestingDataFeeder
    def __init__(self):
        global obDumpFp
        self.data_pointer = 0
        #self.df = pd.read_csv('SP500_NOV2019_IDay.csv',index_col=0,parse_dates=True)
        #self.df = self.df.iloc[0:120,:]
        days = 1 if backTesting else 2.0/24.0
        min = config['interval'] + 'm'
        fname = 'boll-tradef-df_'+str(days)+'d'+'-'+min+'.csv'
        
        if useCached:
            df = pd.read_csv(fname, index_col=0, parse_dates=True)         
        else:
            if backTesting and backTestingSrc == 'ob-dump':
                obDumpFp = open(obDumpPath, 'r')
                min1 = int(10/3.0*60)         
                readCnt = 1000 + min1*60*3
                for i in range(1, readCnt):
                    ob = json.loads(obDumpFp.readline())
                ts = ob['date']
                dateTimeobj = datetime.fromtimestamp(float(ts))
                fromTimeObj = dateTimeobj - timedelta(hours=9) - timedelta(minutes=3*20)
                from_ts = time.mktime(fromTimeObj.timetuple())
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
        self.data_pointer += prevLen if backTesting else self.df_len
        return self.df.iloc[r1:self.data_pointer,:]

sellSignal = buySignal = None
def init():
    global df, sellSignal, buySignal
    #data
    btData = BTDataFeeder()
    df = btData.initial_fetch()

    ma20 = df["Close"].rolling(20).mean().values     
    std20 = df["Close"].rolling(20).std()
    bol_upper = ma20 + 2*std20
    bol_lower = ma20 - 2*std20   
    boll_df = pd.DataFrame(dict(MA20=ma20, BollUpper=bol_upper,BollLower=bol_lower),index=df.index)
    sellSignal = pd.DataFrame(index=df.index.copy(), columns=["sellSignal"])
    buySignal  = pd.DataFrame(index=df.index.copy(), columns=["buySignal"])    
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

    return btData, fig, ax, figZoom, figPan

def current_milli_time():
    return round(time.time() * 1000)

STR_NORMAL = 20
STR_UPPER_NEXT = 21
STR_LOWER_NEXT = 21
strMode = STR_NORMAL
sellPrice = buyPrice = None
lastCompleted = None

TS_UPPER = 1
TS_LOWER = -1
TS_NONE = 0
gainSum = 0.0
tradeStart = None
tradeEnd = None
def update(nxt):
    global ax, fig, df, strMode, sellPrice, buyPrice, sellSignal, buySignal, lastCompleted, readCnt
    global tradeStart, tradeEnd, gainSum
    #ts10 = current_milli_time()
    if nxt is None:
        print('nxt is none')
        exit(0)

    df = df.append(nxt)

    if readCnt%100 == 0: print(f"readCnt:{readCnt}")
    #print(nxt)
    ma20 = df["Close"].rolling(20).mean()     
    std20 = df["Close"].rolling(20).std()
    #ts11 = current_milli_time()
    bol_upper = ma20 + 2*std20
    bol_lower = ma20 - 2*std20   
    #ts12 = current_milli_time()
    txFee = 0.036/100
    tailRatio = 0.3

    date = nxt.name    
    ma20v = ma20[date]
    q = 0.0005
    #ts13 = current_milli_time()
    bn_order = None
    tradeCompleted = False
    if date == lastCompleted:
        pass
        #print("this candle is completed")
    elif strMode == STR_NORMAL:
        max = cmax(nxt['Open'], nxt['Close'], nxt['High'])
        min = cmin(nxt['Open'], nxt['Close'], nxt['Low'])
        if min > ma20v and max > ma20v: #short
            #inpect upper case            
            bolv = bol_upper.loc[date]
            tail = max - bolv
            sellPrice = tail*(1-tailRatio) + bolv

            tradeDecisionPrice = bolv*(1+txFee*2)
            if sellPrice > tradeDecisionPrice:
                #_nxt = sellSignal.iloc[-1].copy()
                #_nxt.name = date
                #_nxt['sellSignal'] = sellPrice
                #_nxt = pd.DataFrame(index=[date], data=[sellPrice], columns=['sellSignal'])
                #if dropLast: sellSignal.drop(sellSignal.tail(1).index,inplace=True)
                #sellSignal = sellSignal.append(_nxt)
                sellSignal.loc[date] = sellPrice
                print(f'sellSignal:{[date, sellPrice]}')
                ##trade short
                bn_order = bn_fut_trade(ex, asset, TRADE_SELL, floor_2(sellPrice), q, TEST)
                #tradeCompleted = True
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
            buySignal.loc[date2] = buyPrice
            #gain_df.loc[date2]['gain'] = gainRatio
            
            print(f'buySignal:{[date, buyPrice, gainAmount, gainRatio]}')
            ##trade buy
            bn_order = bn_fut_trade(ex, asset, TRADE_BUY, floor_2(buyPrice), q, TEST)
            print(f"[result]sell:{sellPrice}, buy:{buyPrice}, gain:{floor_4(gainRatio*100)}%")
            tradeCompleted = True
            gainSum += gainRatio
            strMode = STR_NORMAL
            lastCompleted = date2
    elif strMode == STR_LOWER_NEXT:
        pass

    if len(buySignal)  < len(df): buySignal  = buySignal.append (pd.DataFrame(index=[date], data=[None], columns=['buySignal']))
    if len(sellSignal) < len(df): sellSignal = sellSignal.append(pd.DataFrame(index=[date], data=[None], columns=['sellSignal']))

    assert len(buySignal)  == len(df)                 
    assert len(sellSignal) == len(df)                 

    if tradeCompleted:
        if tradeStart is None: tradeStart = date 
        tradeEnd = date
        period = tradeEnd - tradeStart
        print(f"[stat]({cb_cnt})gainSum:{floor_4(gainSum*100)}%, period:{period}, avg:{floor_4(gainSum/period.days*100) if period.days > 0.0 else gainSum}%")
    #ts19 = current_milli_time() #long part - graph pipeline
    if not backTesting or tradeCompleted or forceDraw: #or (backTestingSrc == 'ob-dump' and updateCnt%(2)==0):
        '''
        boll_df = pd.DataFrame(dict(MA20=ma20, BollUpper=bol_upper, BollLower=bol_lower), index=df.index)
        ap = [mpf.make_addplot(boll_df, ax=ax, type='line', width= 0.5, alpha = 1.0)]
        if buySignal['buySignal'].sum() > 0:
            ap.append(mpf.make_addplot(buySignal, ax=ax, type='scatter', marker='^', markersize=25, color='g'))
        if sellSignal['sellSignal'].sum() > 0:
            ap.append(mpf.make_addplot(sellSignal, ax=ax,type='scatter', marker='v', markersize=25, color='r'))
        '''
        #print(f"len:{len(btData.df)}")
        #cur_xlim = ax.get_xlim()
        #cur_ylim = ax.get_ylim()
        ax.clear()
        #ax.set_xlim(cur_xlim)
        #ax.set_ylim(cur_ylim)
        mpf.plot(df, ax=ax, type='candle')#, addplot=ap)

        fig.canvas.draw()
        fig.savefig('./fig/bn-ob-20211223_002151-'+str(readCnt)+'.png', dpi=300)
        #fig.canvas.flush_events()

    if narrowWindow:
        if len(df) > rtLen:
            df = df.iloc[-rtLen:len(df)]
            #boll_df = boll_df.iloc[-rtLen:len(df)]
        if len(buySignal) > rtLen:
            buySignal = buySignal.iloc[-rtLen:len(buySignal)]
        if len(sellSignal) > rtLen:
            sellSignal = sellSignal.iloc[-rtLen:len(sellSignal)]

    #ts20 = current_milli_time()

    #print(f'update[{ts20-ts10}]ms')
    #print(f'\t[{ts11-ts10}]ms')
    #print(f'\t[{ts12-ts11}]ms')
    #print(f'\t[{ts13-ts12}]ms')
    #print(f'\t[{ts20-ts19}]ms')
    
    if bn_order: bn_wait_order(ex, bn_order, BN_FUT, TEST)
    #if failed -> prevent next order..? total amount management?

btData, fig, ax, figZoom, figPan = init()




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
    date = datetime.fromtimestamp(float(msg['date'])) if msg['date'] else datetime.now()
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
    
    update(nxt)
    #trade decision

    #### run!
    pass

readCnt = 0
def BTThread():
    global btData, obDumpFp, readCnt
    if backTestingSrc == 'candle-fetch':
        while True:
            nxt = btData.fetch_next().iloc[0]
            if nxt is None:
                break
            date = nxt.name
            delta = timedelta(seconds=60*int(config['interval'])/5)
            updatePrice(date + delta*1, nxt['Open'])
            updatePrice(date + delta*2, nxt['High'])
            updatePrice(date + delta*3, nxt['Low'])
            updatePrice(date + delta*4, nxt['Close'])
    elif backTestingSrc == 'ob-dump':
        while True:
            line = obDumpFp.readline()
            if len(line) == 0:
                break
            ob = json.loads(line)
            cb_book(ob)
            readCnt += 1

def launchStream():
    if backTesting:
        t = threading.Thread(target=BTThread, args=())
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

launchStream()

#mpf.show() #inside launchStream