import pandas as pd
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

from graph.MatpilotUtil import ZoomPan

from util.log import *
import json
import signal
import sys


##note
#socket 빼와서 짜야 queue 에러 안남 https://github.com/sammchardy/python-binance/issues/1016
#그냥 all ticker 가져와서, fut 관련만 돌면서 체크하는게 나을듯..?
#map 구축하기...

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

def cb_fut_ticker(msg):
    '''
    “u”:400900217, // order book updateId 
    “s”:”BNBUSDT”, // symbol 
    “b”:”25.35190000”, // best bid price 
    “B”:”31.21000000”, // best bid qty 
    “a”:”25.36520000”, // best ask price 
    “A”:”40.66000000” // best ask qty
    '''
    if 'data' in msg:
        data = msg['data']
        time = data['u']
        symbol = data['s']
        if 'USDT' in symbol:
            avgPrice = (float(data['b']) + float(data['a']))/2
            #print(f"{symbol}:{avgPrice}")
    else:
        print(msg)

twm = None
def launchStream():
    global twm
    twm = getBinanceSocket()
    twm.start()
    twm.start_all_ticker_futures_socket(callback=cb_fut_ticker)
    while True:
        input('Ctrl+C to flush and end')

#main
dateStr = datetime.today().strftime("%Y%m%d_%H%M%S")

#log_open('./bn-dump/bn-ob-'+dateStr+'.txt')
#fpTrade = open('./bn-dump/bn-trade-'+dateStr+'.txt', 'w')
def signal_handler(sig, frame):
    global twm
    print('You pressed Ctrl+C!')
    print('>> stop thread')
    twm.stop()
    twm.join()
    #print('>> log close')
    #log_close()
    #fpTrade.close()
    print('>> end')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

launchStream()

