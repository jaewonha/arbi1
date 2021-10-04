import pyupbit
from pyupbit import WebSocketManager
from upbit.client import Upbit

from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from requests.exceptions import ConnectionError

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
OUT_TH = 2.0
IN_TH = 2.5
maxUSD = 50
asset = "EOS" #target asset to trade arbi
print(f"config: assets={asset}, OUT_TH={OUT_TH}, IN_TH={IN_TH}")
ORDER_TEST = False
ARBI_SEQ_TEST = True

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
while True:
    now = datetime.now()
    print(now)
    if now.minute != lastMin:
        usd_conv = float(krw_per_usd()) #fixme: error handling for float version fail
        lastMin = now.minute
        print(f"update usd_conv:{usd_conv} at min:{lastMin}")

    ub_pair = "KRW-" + asset
    bn_pair = asset + "USDT"
    #print(f"asset:{asset}")

    ub_p_krw = pyupbit.get_current_price(ub_pair)
    ub_p_usd = round(ub_p_krw / usd_conv, 4)
    #print(f"[UB]KRW={ub_p_krw}, USD={ub_p_usd}")

    btc_price = binance.get_symbol_ticker(symbol=bn_pair)
    bn_p_usd = float(btc_price["price"])
    bn_p_krw = round(bn_p_usd * usd_conv, 4)
    #print(f"[BN]KRW={bn_p_krw}, USD={bn_p_usd}")

    kimp = round( (ub_p_usd/bn_p_usd -1)*100,2)
    print(f"KIMP:{kimp}% (UB={ub_p_usd}, BN={bn_p_usd})")
    
    if status == 'BN' and (kimp>IN_TH or ARBI_SEQ_TEST):
        msg = f"time to get-in(BN->UB)! kimp={kimp} (UB={ub_p_usd}, BN={bn_p_usd}) @{now}"
        print(msg)
        f.write(msg+'\n')
        if True:# arbi_in_bn_to_ub(binance, upbit, upbit2, asset, maxUSD, usd_conv, ORDER_TEST):
            cnt = cnt + 1
            status = 'UB'

    elif status == 'UB' and (kimp<OUT_TH or ARBI_SEQ_TEST):
        msg = f"time to flight(UB->BN)! kimp={kimp} (UB={ub_p_usd}, BN={bn_p_usd}) @{now}"
        print(msg)
        f.write(msg+'\n')
        if arbi_out_ub_to_bn(binance, upbit, upbit2, asset, maxUSD*usd_conv, usd_conv, ORDER_TEST):
            cnt = cnt + 1
            status = 'BN'
    
    if cnt > 1:
        exit(0)
    time.sleep(1)


