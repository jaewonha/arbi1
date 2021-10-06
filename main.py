import pyupbit
from pyupbit import WebSocketManager
from upbit.client import Upbit

from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from requests.exceptions import ConnectionError, ReadTimeout

import json
import pprint

import datetime
import time

import signal
import sys

from conv.krw2usd import krw_per_usd
from arbi.arbi import *

#init
#UB - tradable
access = "p2uhQ8xdqxhEvslccOPkwzreXiuTWysaNTcYigWq"
secret = "k55DdoFw2sPRSYGMzB4IzwNna7ywPHYj1562QykN"
upbit = pyupbit.Upbit(access, secret)
upbit2 = Upbit(access, secret)

#BN - tadable
api_key = 'xc88zHqhZjLhTlYLlHRy2k30tKVVEV3oZq2GodtGP8gQloThM2R1KfMMED4goG3c'
sec_key = 'xzZ8D5qiSXCIJgirSSbD9fLqVFkjcDIHgms17j1u1SwdklCEClSSjqbRk83ZRmO1'
binance = Client(api_key, sec_key)

#config
# status = 'UB'
# OUT_TH = 2.0
# IN_TH = 3.5
status = 'BN'
#status = 'UB' #resume 00:00 10/15
OUT_TH = 1.0
IN_TH = 2.0
IN_TRF_R = 0.85
maxUSD = 50
#maxUSD = 1000
asset = "EOS" #target asset to trade arbi
print(f"config: assets={asset}, OUT_TH={OUT_TH}, IN_TH={IN_TH}")
ORDER_TEST = False
ARBI_SEQ_TEST = False

#init status
lastMin = None

date = datetime.now().strftime("%Y%m%d_%H%M%S")
f = open(f"kimp{date}.txt", "a")

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    print('closing file')
    f.close()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def get_asset_total(binance, upbit, krwPerUsd):
   bn_usd = round(bn_get_spot_balance(binance, 'USDT'), 2)
   ub_usd = round(ub_get_spot_balance(upbit, 'KRW')/krwPerUsd, 2)
   total_usd = bn_usd + ub_usd
   return [bn_usd, ub_usd, total_usd]

def log(msg, f):
    print(msg)
    print(msg, f)

def print_arbi_stat(before, after, th, f):
    ratio = round(after[2]/before[2],4)
    k_gain = ratio*100 -1.0 - th
    msg = f"[total_asset]ub/bn: [{before[0]} + {before[1]} = {before[2]}] -> ({after[0]} + {after[1]} = {after[2]}), ratio={ratio}, th={th}, k_gain={k_gain}"
    log(msg, f)

if ORDER_TEST:
    print('test order')
else:
    msg = input('execute real order? type "go" to do that >> ')
    if msg == 'go':
        print('go real trading')
    else:
        print('not go')
        exit(0)

cnt = 0
delay = 2
while True:
    now = datetime.now()
    print(now)
    if now.minute != lastMin:
        krwPerUsd = float(krw_per_usd()) #fixme: error handling for float version fail
        lastMin = now.minute
        print(f"update krwPerUsd:{krwPerUsd} at min:{lastMin}")

    ub_pair = "KRW-" + asset
    bn_pair = asset + "USDT"
    #print(f"asset:{asset}")

    '''
    #test
    asset_before = get_asset_total(binance, upbit, krwPerUsd)
    asset_after  = get_asset_total(binance, upbit, krwPerUsd)
    print_arbi_stat(asset_before, asset_after, +IN_TH, f)
    print_arbi_stat(asset_before, asset_after, -OUT_TH, f)
    exit(0)
    '''

    #get price
    IN = 0
    OUT = 1
    ub_p_krw = [0,0]
    ub_p_usd = [0,0]
    bn_p_usd = [0,0]
    bn_p_krw = [0,0]
    kimp = [0,0]

    if True: #strict
        try:
            bn_p_usd[IN], _  = bn_spot_1st_ask(binance, bn_pair) #market 
            ub_p_krw[IN], _  = ub_spot_1st_bid(ub_pair)          #market
            ub_p_krw[OUT], _ = ub_spot_1st_ask(ub_pair)          #market
            bn_p_usd[OUT], _ = bn_spot_1st_bid(binance, bn_pair) #market 
        except ReadTimeout as rt:
            print('[read_market_price] read time out.. retry')
            time.sleep(delay)
        except Exception as e:
            print('[read_market_price] error.. retry:' + e)
            time.sleep(delay)
    else: #use native api
        ub_p_krw[IN] = ub_p_krw[OUT] = pyupbit.get_current_price(ub_pair)
        bn_p_usd[IN] = bn_p_usd[OUT] = binance.get_symbol_ticker(symbol=bn_pair)["price"]
    
    #conv currency
    ub_p_usd[IN]  = round(ub_p_krw[IN] / krwPerUsd, 4)
    bn_p_krw[IN]  = round(bn_p_usd[IN] * krwPerUsd, 4)
    ub_p_usd[OUT] = round(ub_p_krw[OUT] / krwPerUsd, 4)
    bn_p_krw[OUT] = round(bn_p_usd[OUT] * krwPerUsd, 4)

    #print
    #print(f"[UB]KRW={ub_p_krw}, USD={ub_p_usd}")
    #print(f"[BN]KRW={bn_p_krw}, USD={bn_p_usd}")
    kimp[IN]  = round( (ub_p_usd[IN]/bn_p_usd[IN]-1)*100,2)
    kimp[OUT] = round( (ub_p_usd[OUT]/bn_p_usd[OUT]-1)*100,2)
    print(f"KIMP[IN] :{kimp[IN] }% (UB={ub_p_usd[IN] }, BN={bn_p_usd[IN] })")
    print(f"KIMP[OUT]:{kimp[OUT]}% (UB={ub_p_usd[OUT]}, BN={bn_p_usd[OUT]}), KIMPDiff:{round(kimp[IN]-kimp[OUT], 2)}%")
    
    if status == 'BN' and (kimp[IN]>(IN_TH*IN_TRF_R) or ARBI_SEQ_TEST):
        log(f"time to get-in(BN->UB)! kimp={kimp[IN]} (UB={ub_p_usd[IN]}, BN={bn_p_usd[IN]}) @{now}", file=f)
        asset_before = get_asset_total(binance, upbit, krwPerUsd)
        if arbi_in_bn_to_ub(binance, upbit, upbit2, asset, maxUSD, krwPerUsd, IN_TH, ORDER_TEST):
            cnt = cnt + 1
            status = 'UB'
            asset_after = get_asset_total(binance, upbit, krwPerUsd)
            print_arbi_stat(asset_before, asset_after, +IN_TH, f)

    elif status == 'UB' and (kimp[OUT]<OUT_TH or ARBI_SEQ_TEST):
        log(f"time to flight(UB->BN)! kimp={kimp[OUT]} (UB={ub_p_usd[OUT]}, BN={bn_p_usd[OUT]}) @{now}", file=f)
        asset_before = get_asset_total(binance, upbit, krwPerUsd)
        if arbi_out_ub_to_bn(binance, upbit, upbit2, asset, maxUSD*krwPerUsd, krwPerUsd, ORDER_TEST):
            cnt = cnt + 1
            status = 'BN'
            asset_after = get_asset_total(binance, upbit, krwPerUsd)
            print_arbi_stat(asset_before, asset_after, -OUT_TH, f)
    
    if cnt > 5:
        exit(0)
    time.sleep(delay)


