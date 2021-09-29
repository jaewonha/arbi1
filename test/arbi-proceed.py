import asyncio
import json
import pandas as pd
import numpy as np
import json
import math

from datetime import datetime, date, timedelta
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.exceptions import BinanceAPIException, BinanceOrderException
#from binance import Client, AsyncClient, DepthCacheManager, BinanceSocketManager

api_key = 'xc88zHqhZjLhTlYLlHRy2k30tKVVEV3oZq2GodtGP8gQloThM2R1KfMMED4goG3c'
api_secret = 'xzZ8D5qiSXCIJgirSSbD9fLqVFkjcDIHgms17j1u1SwdklCEClSSjqbRk83ZRmO1'
client = Client(api_key, api_secret)

ORDER_TEST = True

if ORDER_TEST:
    print('test order')
else:
    msg = input('execute real order? type "go" to do that >> ')
    if msg == 'go':
        print('go real trading')
    else:
        print('not go')
        exit(0)

print('### spot balance ###')
balance = client.get_asset_balance(asset='EOS')
assert balance['asset'] == 'EOS'
s_q = math.floor(float(balance['free'])*10)/10
print(f"eos: q={s_q}")

print('### futures balance ###')
acc = client.futures_account()
f_eos = acc['positions'][67]
assert f_eos['symbol'] == 'EOSUSDT'
f_p = float(f_eos['entryPrice'])
f_q = float(f_eos['positionAmt'])
assert f_q < 0 #short

print(f"f_eos: p={f_p}, q={f_q}")


try:
    print('### spot sell ###')
    depth = client.get_order_book(symbol='EOSUSDT')
    #print(depth)
    t_p = round(float(depth['bids'][0][0]), 4)
    av_q = float(depth['bids'][0][1])

    print(f"spot sell: p={t_p} * q={s_q}(av:{av_q}) = ${t_p*s_q} ")

    #amount = 15.0
    #t_q = round(amount/t_p, 1)

    #print(f"target: t_p={t_p}, av_q={av_q} => t_q={t_q} & total$={t_q*t_p}")

    if ORDER_TEST:
        spot_order = client.create_test_order(
            symbol='EOSUSDT',
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_LIMIT,
            timeInForce='GTC',
            price=t_p,
            quantity=s_q)
    else:    
        #exit(0)
        spot_order = client.create_order(
            symbol='EOSUSDT',
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_LIMIT,
            timeInForce='GTC',
            price=t_p,
            quantity=s_q)
    print(spot_order)


    print('### futures long ###')
    depth = client.futures_order_book(symbol='EOSUSDT')
    #print(depth)
    t_p = round(float(depth['asks'][0][0]), 4)
    av_q = float(depth['asks'][0][1])
    
    # amount = 15.0
    # t_q = round(amount/t_p, 1)

    print(f"target: t_p={t_p} * f_q={-f_q}(av:{av_q}) = ${-t_p*f_q}")

    if ORDER_TEST:
        fut_order = client.create_test_order(
            symbol='EOSUSDT',
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_LIMIT,
            timeInForce='GTC',
            price=t_p,
            quantity=-f_q)
    else:    
        #exit(0)
        fut_order = client.futures_create_order(
            symbol='EOSUSDT',
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_LIMIT,
            timeInForce='GTC',
            price=t_p,
            quantity=-f_q)
    print(fut_order)

    # client.futures_create_order(
    #     symbol='EOSUSDT',
    #     type='LIMIT',
    #     timeInForce='GTC',  # Can be changed - see link to API doc below
    #     price=30000,  # The price at which you wish to buy/sell, float
    #     side='BUY',  # Direction ('BUY' / 'SELL'), string
    #     quantity=0.001  # Number of coins you wish to buy / sell, float
    # )


except BinanceAPIException as e:
    # error handling goes here
    print(e)
except BinanceOrderException as e:
    # error handling goes here
    print(e)

finally:
    pass


