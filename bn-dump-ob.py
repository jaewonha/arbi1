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

from util.log import *
import json
import signal
import sys

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

key = None
cb_cnt = 0
def cb_book(msg):
    global cb_cnt
    cb_cnt += 1
    if cb_cnt%3 != 0:
        return
    
    del msg['stream']
    del msg['data']['lastUpdateId']
    #{'stream': 'btcusdt@depth5@100ms', 'data': {'lastUpdateId': 15792298707, 
    # 'bids': [['49382.12000000', '0.26907000'], ['49379.65000000', '0.33396000'], ['49377.28000000', '0.04569000'], ['49377.18000000', '0.06400000'], ['49375.40000000', '0.00829000']], 
    # 'asks': [['49384.37000000', '0.00700000'], ['49384.38000000', '0.01999000'], ['49385.41000000', '0.09458000'], ['49385.42000000', '0.04000000'], ['49386.28000000', '0.23000000']]
    # }}
    msg['date'] = str(time.mktime(datetime.now().timetuple()))

    log(json.dumps(msg))

twm = None
def launchStream():
    global twm
    twm = getBinanceSocket()
    twm.start()
    #twm.start_kline_socket(callback=cb_kline, symbol=config['symbol'], interval=KLINE_INTERVAL_3MINUTE)
    #twm.start_multiplex_socket(callback=cb_book, streams=['btcusdt@bookTicker'])
    twm.start_multiplex_socket(callback=cb_book, streams=['btcusdt@depth5@100ms'])
    #twm.start_depth_socket(callback=cb_depth, symbol=symbol)
    while True:
        input('Ctrl+C to flush and end')

#main
dateStr = datetime.today().strftime("%Y%m%d_%H%M%S")
log_open('./bn-dump/bn-ob-'+dateStr+'.txt')

def signal_handler(sig, frame):
    global twm
    print('You pressed Ctrl+C!')
    print('>> stop thread')
    twm.stop()
    twm.join()
    print('>> log close')
    log_close()
    print('>> end')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

launchStream()

