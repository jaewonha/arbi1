import pprint
import time
import traceback

from exchange import *

import pyupbit
#from pyupbit import WebSocketManager
acc_key = "p2uhQ8xdqxhEvslccOPkwzreXiuTWysaNTcYigWq"          # 본인 값으로 변경
sec_key = "k55DdoFw2sPRSYGMzB4IzwNna7ywPHYj1562QykN"          # 본인 값으로 변경
upbit = pyupbit.Upbit(acc_key, sec_key)

from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
api_key = 'xc88zHqhZjLhTlYLlHRy2k30tKVVEV3oZq2GodtGP8gQloThM2R1KfMMED4goG3c'
sec_key = 'xzZ8D5qiSXCIJgirSSbD9fLqVFkjcDIHgms17j1u1SwdklCEClSSjqbRk83ZRmO1'
binance = Client(api_key, sec_key)

asset = 'EOS'
ub_pair = ub_krw_pair(asset)
bn_pair = bn_usdt_pair(asset)

t_q = 10
TEST = False
UB_TEST = True
BN_TEST = False

if UB_TEST:
    try:
        t_p, av_q = ub_spot_1st_ask(ub_pair) #ask
        order = ub_spot_trade(upbit, ub_pair, TRADE_BUY, t_p, t_q, TEST)

        ub_wait_order(upbit, order, TEST)
        time.sleep(3)

        t_p, av_q = ub_spot_1st_bid(ub_pair) #bid
        order = ub_spot_trade(upbit, ub_pair, TRADE_SELL, t_p, t_q, TEST)

        ub_wait_order(upbit, order, TEST)
        print(order)
    except Exception as e:
        print('error:', e)

if BN_TEST:
    try:
        t_p, av_q = bn_spot_1st_bid(binance, bn_pair) #ask
        order = bn_spot_trade(binance, bn_pair, TRADE_BUY, t_p, t_q, TEST)

        bn_wait_order(binance, bn_pair, order, TEST)
        time.sleep(3)

        t_p, av_q = bn_spot_1st_ask(binance, bn_pair) #bid
        order = bn_spot_trade(binance, bn_pair, TRADE_SELL, t_p, t_q, TEST)

        bn_wait_order(binance, bn_pair, order, TEST)
        print('done')
        print(order)
    except Exception as e:
        traceback.print_exc()