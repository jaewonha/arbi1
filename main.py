import pyupbit
from pyupbit import WebSocketManager

from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager

import json
import pprint

import datetime
import time

import signal
import sys

from conv.krw2usd import krw_per_usd

#init
#UB - tradable
access = "p2uhQ8xdqxhEvslccOPkwzreXiuTWysaNTcYigWq"
secret = "k55DdoFw2sPRSYGMzB4IzwNna7ywPHYj1562QykN"
upbit = pyupbit.Upbit(access, secret)

#BN - tadable
api_key = 'xc88zHqhZjLhTlYLlHRy2k30tKVVEV3oZq2GodtGP8gQloThM2R1KfMMED4goG3c'
sec_key = 'xzZ8D5qiSXCIJgirSSbD9fLqVFkjcDIHgms17j1u1SwdklCEClSSjqbRk83ZRmO1'
binance = Client(api_key, sec_key)

#config
status = 'BN'
OUT_TH = 2.7
IN_TH = 3.7
asset = "EOS" #target asset to trade arbi
print(f"config: assets={asset}, OUT_TH={OUT_TH}, IN_TH={IN_TH}")
ORDER_TEST = True

#init status
lastMin = None

date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
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

while True:
    now = datetime.datetime.now()
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
    
    if status == 'BN' and kimp>IN_TH:
        msg = f"time to get-in(BN->UB)! kimp={kimp} (UB={ub_p_usd}, BN={bn_p_usd}) @{now}"
        print(msg)
        f.write(msg+'\n')
        if arbi_in_bn_to_ub(binance, upbit, 1000, ORDER_TEST):
            status = 'UB'

    if status == 'UB' and kimp<OUT_TH:
        msg = f"time to flight(UB->BN)! kimp={kimp} (UB={ub_p_usd}, BN={bn_p_usd}) @{now}"
        print(msg)
        f.write(msg+'\n')
        if arbi_out_ub_to_bn(upbit, binance, 1000, ORDER_TEST):
            status = 'BN'
    
    time.sleep(1)


