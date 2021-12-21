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
def getBinance(testnet:bool):
    f = open('.key.ini','r')
    keyJson = json.load(f)

    if testnet:
        api_key = keyJson['binance-testnet']['apiKey']
        sec_key = keyJson['binance-testnet']['secKey']
    else:
        api_key = keyJson['binance']['apiKey']
        sec_key = keyJson['binance']['secKey']
    return Client(api_key, sec_key)

binance = getBinance(True)

config = {
    "asset":"BTC",
    "interval":"3m",
    "prev": 20
}
config['symbol'] = config['asset'] + "USDT"


## Class to simulate getting more data from API:
class RealTimeAPI():
    def __init__(self):
        self.data_pointer = 0
        #self.data_frame = pd.read_csv('SP500_NOV2019_IDay.csv',index_col=0,parse_dates=True)
        #self.data_frame = self.data_frame.iloc[0:120,:]
        days = 3
        min = Client.KLINE_INTERVAL_3MINUTE
        fname = 'boll-tradef-df_'+str(days)+'d'+'-'+min+'.csv'
        useCached = True
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
        self.data_frame = df
        self.df_len = len(self.data_frame)

    def fetch_next(self):
        r1 = self.data_pointer
        self.data_pointer += 1
        if self.data_pointer >= self.df_len:
            return None
        return self.data_frame.iloc[r1:self.data_pointer,:] #r1:r1+1

    def initial_fetch(self):
        if self.data_pointer > 0:
            return
        r1 = self.data_pointer
        self.data_pointer += 20#int(0.2*self.df_len)
        return self.data_frame.iloc[r1:self.data_pointer,:]

rtapi = RealTimeAPI()

resample_map ={'Open' :'first',
            'High' :'max'  ,
            'Low'  :'min'  ,
            'Close':'last' }
resample_period = '15T'

df = rtapi.initial_fetch()
rs = df.resample(resample_period).agg(resample_map).dropna()

fig, axes = mpf.plot(rs,returnfig=True,figsize=(11,8),type='candle',title='\n\nGrowing Candle')
ax = axes[0]

def animate(ival):
    global df
    global rs
    nxt = rtapi.fetch_next()
    if nxt is None:
        print('no more data to plot')
        ani.event_source.interval *= 3
        if ani.event_source.interval > 12000:
            exit()
        return
    df = df.append(nxt)
    #rs = df.resample(resample_period).agg(resample_map).dropna()
    rs = df
    cur_xlim = ax.get_xlim()
    cur_ylim = ax.get_ylim()
    ax.clear()
    ax.set_xlim(cur_xlim)
    ax.set_ylim(cur_ylim)
    mpf.plot(rs,ax=ax,type='candle')

#ani = animation.FuncAnimation(fig, animate, interval=250)

zp = ZoomPan()
figZoom = zp.zoom_factory(ax, base_scale = 1.5)
figPan = zp.pan_factory(ax)

key = None
def on_press(event):
    global key
    print('press', event.key)
    key = event.key
        
fig.canvas.mpl_connect('key_press_event', on_press)

import threading
 
def sum(low, high):
    for i in range(1,100):
        time.sleep(0.25)
        if key == 'q': break
        print(f'draw:{i}')
        animate(0)
        fig.canvas.draw()
        #fig.canvas.flush_events()
 
t = threading.Thread(target=sum, args=(1, 100000))
t.start()
 
mpf.show()