#import pyupbit
from requests.exceptions import ConnectionError, ReadTimeout
import json
from datetime import datetime
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Lock

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

assets_1min = ['NANO', 'EOS', 'ATOM', 'AVA', 'BTS', 'NEM', 'SOL', 'STEEM', 'XLM', 'XRP', 'HBAR', 'WAVES', 'NEO', 'ALGO']

assets_10min = ['ADA', 'ANKR', 'ATOM', 'AXS', 'BAT', 'BTT', 'CHZ', 'CVC', 'DOGEDOT', 
'ENJ', 'EOS', 'HBAR', 'ICX', 'IOST', 'IOTA', 'KAVA', 'KNCLINK', 'MANA', 
'MTL', 'NEO', 'OMG', 'ONT', 'SAND', 'SC', 'SRMSTMX', 'STORJ', 'SXP', 'THETA', 'TRX', 'VET', 
'WAVES', 'XEM', 'XLM', 'XRP', 'XTZZIL', 'ZRX'] #within 10min

assets_30minplus = ['AE', 'BCN', 'QTUM', 'DCR', 'XTZ', 'XMR', 'LTC', 'MXR',
        'LTC', 'LSK', 'ZEC', 'BCD', 'BTG', 'BCHA', 'BSV', 'BTC', 'RVN', 'BCH',
        'ETC', 'ETH',
        #temp
        'MATIC',    #bn suspended
        'DOT',       #ub suspended
        'NEO', #ub address invalid
        
]
#assets = np.intersect1d(assets, assets_10min)

num_assets = len(assets)
print(f"num_assets:{num_assets}")
print(assets)


#ex = []
#for i in range(0, num_assets):
#    ex.append(Exchanges())

#skip_asset = []
skip_asset = assets_30minplus
#skip_asset = ['HBAR', 'BTC', 'BCH'] #how to check disabled coins?
#executor = ThreadPoolExecutor(max_workers=num_assets-len(skip_asset))
executor = ThreadPoolExecutor(max_workers=1)
'''
class ThreadCalcKimpParam:
    def __init__(self, lock, asset, max_in, min_out):
        self.lock = lock
        self.asset = asset
        self.max_in = max_in
        self.min_out = min_out
'''
def thread_calc_kimp(asset):
    if asset in skip_asset: return [0,99]
    ub_p_krw, bn_p_usd, bn_f_usd, kimp = calc_kimp(ex, asset, CHECK_BACKWARD=False)
    return kimp

while True:
    '''
    now = datetime.now()
    if now.minute != lastMin:
        ex.updateCurrency()
        lastMin = now.minute
        print(f"update krwPerUsd:{ex.krwPerUsd} at min:{lastMin}")
        log_flush()
    '''

    futRetArr = []
    for i in range(0,len(assets)):
        futRetArr.append(executor.submit(thread_calc_kimp, assets[i]))
    
    max_in  = 0.0   ;   max_in_asset = None
    min_out = 999.0 ;   min_out_asset = None
    for i in range(0,len(assets)):
        futRet = futRetArr[i]
        asset = assets[i]
        kimp = futRet.result()
        if asset=='EOS': print(f"{asset}: IN={kimp[IN]}, OUT={kimp[OUT]}")
        if kimp[IN]  > max_in  : max_in  = kimp[IN] ; max_in_asset  = asset
        if kimp[OUT] < min_out : min_out = kimp[OUT]; min_out_asset = asset
        '''
        if asset in skip_asset: continue
        ub_p_krw, bn_p_usd, bn_f_usd, kimp = calc_kimp(ex, asset, CHECK_BACKWARD = False)
        print(f"{asset}: IN={kimp[IN]}, OUT={kimp[OUT]}")
        if kimp[IN]  > max_in  : max_in  = kimp[IN] ; max_in_asset  = asset
        if kimp[OUT] < min_out : min_out = kimp[OUT]; min_out_asset = asset
        #print(f"KIMP[IN] :{kimp[IN]}% (UB={toUsd(ex, ub_p_krw[IN])}, BN={bn_p_usd[IN] })")
        #print(f"KIMP[OUT]:{kimp[OUT]}% (UB={toUsd(ex, ub_p_krw[OUT])}, BN={bn_p_usd[OUT]}), KIMPDiff:{round(kimp[IN]-kimp[OUT], 2)}%")
        '''

    print(f"max_in: {max_in_asset}={max_in}, min_out: {min_out_asset}={min_out}, diff={max_in-min_out}")
    time.sleep(1)

exit(0)
assets = ['ADA','ANKR','ATOM','AXS','BAT','BCH','BTC','BTT','CHZ','CVC','DOGE',
 'DOT','ENJ','EOS','ETC','ETH','HBAR','ICX','IOST','IOTA','KAVA','KNC',
 'LINK','LTC','MANA','MTL','NEO','OMG','ONT','QTUM','SAND','SC','SRM',
 'STMX','STORJ','SXP','THETA','TRX','VET','WAVES','XEM','XLM','XRP','XTZ'
 'ZIL','ZRX']

 
 #https://m.blog.naver.com/tjdalse103/222432774991 tx spped
coin_withdraw_time = {
    'min1': {
        'NANO', 'EOS', 'ATOM', 'AVA', 'BTS', 'NEM', 'SOL', 'STEEM', 'XLM', 'XRP', 'HBAR', 'WAVES', 'NEO', 'ALGO'
    },
    'min5': {
        'DGB', 'IOTA', 'BTT', 'TRX'
    },
    'min10': {
        'DOGE', 'DASH', 'ICX', 'ICN', 'ONT', 'ADA'
    },
    'min30': {
        'AE', 'BCN', 'QTUM', 'DCR', 'XTZ', 'XMR', 'LTC', 'MXR'
    },
    'hours': {
        'LTC', 'LSK', 'ZEC', 'BCD', 'BTG', 'BCHA', 'BSV', 'BTC', 'RVN', 'BCH'
    },
    'exclude': {
        'ETC', 'ETH'
    }
}

assets_trimmed = ['ADA', 'ANKR', 'ATOM', 'AXS', 'BAT', 'BTT', 'CHZ', 'CVC', 'DOGEDOT', 
'ENJ', 'EOS', 'ETC', 'ETH', 'HBAR', 'ICX', 'IOST', 'IOTA', 'KAVA', 'KNCLINK', 'MANA', 
'MTL', 'NEO', 'OMG', 'ONT', 'SAND', 'SC', 'SRMSTMX', 'STORJ', 'SXP', 'THETA', 'TRX', 'VET', 
'WAVES', 'XEM', 'XLM', 'XRP', 'XTZZIL', 'ZRX']

remove_classes = ['min30', 'hours']
for asset in assets:
    assign = True
    for rc in remove_classes:
        if asset in coin_withdraw_time[rc]:
            assign = False
    if assign:
        assets_trimmed.append(asset)

print(assets_trimmed)
'''
classes = ['min1', 'min5', 'min10', 'min30', 'hours']
for asset in assets: 
    speedType = 'None'

    for c in classes:
        if asset in coin_withdraw_time[c]:
            speedType = c
    
    print(f"{asset}:{speedType}")

sorted(d.items(), key=lambda x: x[1])    
#https://blog.naver.com/PostView.nhn?blogId=healingallvin&logNo=222279889007 tx fee
'''