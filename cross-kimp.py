#import pyupbit
from requests.exceptions import ConnectionError, ReadTimeout
import json
import pprint
from datetime import datetime
import time
import signal
import sys
import numpy as np

from classes import *
from util.log import *
from arbi import *
from main import *

ex = Exchanges()

lastMin = None
delay = 1

#bn_tickers = ex.binance.get_all_tickers()

bn_fut_asset = []
bn_fut_tickers = ex.binance.futures_ticker()
for bn_fut_ticker in bn_fut_tickers:
    symbol = bn_fut_ticker['symbol']
    if 'USDT' in symbol:
        bn_fut_asset.append(symbol[0:-4])

ub_asset = []
ub_tickers = pyupbit.get_tickers()
for ub_ticker in ub_tickers:
    if 'KRW-' in ub_ticker:
        ub_asset.append(ub_ticker[4:])

assets = np.intersect1d(bn_fut_asset, ub_asset)
#assets = ['EOS']
print(assets)
skip_asset = ['HBAR', 'BTC', 'BCH'] #how to check disabled coins?
while True:
    now = datetime.now()
    if now.minute != lastMin:
        ex.updateCurrency()
        lastMin = now.minute
        print(f"update krwPerUsd:{ex.krwPerUsd} at min:{lastMin}")
        log_flush()
    
    max_in = 0; max_in_asset = None;
    min_out = 999; min_out_asset = None;
    for asset in assets:
        if asset in skip_asset: continue
        ub_p_krw, bn_p_usd, bn_f_usd, kimp = calc_kimp(ex, asset, CHECK_BACKWARD = False)
        print(f"{asset}: IN={kimp[IN]}, OUT={kimp[OUT]}")
        if kimp[IN]  > max_in  : max_in  = kimp[IN] ; max_in_asset  = asset
        if kimp[OUT] < min_out : min_out = kimp[OUT]; min_out_asset = asset
        #print(f"KIMP[IN] :{kimp[IN]}% (UB={toUsd(ex, ub_p_krw[IN])}, BN={bn_p_usd[IN] })")
        #print(f"KIMP[OUT]:{kimp[OUT]}% (UB={toUsd(ex, ub_p_krw[OUT])}, BN={bn_p_usd[OUT]}), KIMPDiff:{round(kimp[IN]-kimp[OUT], 2)}%")
    print(f"max_in: {max_in_asset}={max_in}, min_out: {min_out_asset}={min_out}, diff={max_in-min_out}")
    time.sleep(delay)

assets = ['ADA' 'ANKR' 'ATOM' 'AXS' 'BAT' 'BCH' 'BTC' 'BTT' 'CHZ' 'CVC' 'DOGE'
 'DOT' 'ENJ' 'EOS' 'ETC' 'ETH' 'HBAR' 'ICX' 'IOST' 'IOTA' 'KAVA' 'KNC'
 'LINK' 'LTC' 'MANA' 'MTL' 'NEO' 'OMG' 'ONT' 'QTUM' 'SAND' 'SC' 'SRM'
 'STMX' 'STORJ' 'SXP' 'THETA' 'TRX' 'VET' 'WAVES' 'XEM' 'XLM' 'XRP' 'XTZ'
 'ZIL' 'ZRX']