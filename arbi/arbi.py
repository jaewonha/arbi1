import asyncio
import json
import pandas as pd
import numpy as np
import json
import math

from ..exchange import *

def arbi_in_bn_to_ub(binance, upbit, asset, maxUSD, krwPerUSD, TEST= True):
    balUSDT = get_spot_balance('USDT')

    #1. check spot balance is enough
    if balUSDT < maxUSD:
        print(f"insufficient USDT balance {balUSDT} < {maxAmt}")
        return False

    ##2. Hedge & Buy
    #2a. Spot Buy
    bn_pair = bn_usdt_pair(asset)
    t_p, av_q = bn_get_1st_ask(binance, bn_pair)
    t_q = round(maxUSD/t_p, 4)
    order = bn_spot_buy(binance, bn_pair, TRADE_BUY, t_p, t_q, TEST)
    print(f"spot buy:{order}")

    #2b. Futures Short
    f_t_p, f_av_q = bn_fut_1st_bid(binance, bn_pair)
    bn_fut_trade(binance, bn_pair, TRADE_SELL, f_t_p, t_q, TEST)

    #3a. Withdrawal
    ub_eos_addr = 'eosupbitsusr'
    ub_eos_memo = '5772f423-5c5a-4361-9678-2e070338fec1'

    #bn_deposite_addr = client.get_deposit_address(coin=asset)

    withdraw = binance.withdraw(
        coin=asset,
        address=ub_address,
        addressMemo=ub_eos_memo, #or TAG
        amount=t_q)

    #3b. wait finished
    while True:
        withdraw_result = client.get_withdraw_history(withdraw_id['id'])
        if withdraw_result['status'] == 6:
            break

    #3c. wait deposit


    #except BinanceAPIException as e:
        #print(e)

    ##4. Sell & UnHedge
    #4a. Spot Sell
    ub_pair = ub_krw_pair(asset)
    t_p, av_q = ub_spot_1st_bid(upbit, ub_pair)
    ub_spot_trade(upbit, ub_pair, TRADE_SELL, t_p, t_q, TEST)

    #4b. Futures Long
    f_t_p, f_av_q = bn_fut_1st_ask(binance, bn_pair)
    bn_fut_trade(binance, bn_pair, TRADE_BUY, f_t_p, t_q, TEST)

    
def arbi_out_ub_to_bn(binance, upbit, asset, maxUSD, krwPerUSD, TEST=True):
    pass




# print(f"f_eos: p={f_p}, q={f_q}")


# try:
    

#     print(f"spot sell: p={t_p} * q={s_q}(av:{av_q}) = ${t_p*s_q} ")

#     #amount = 15.0
#     #t_q = round(amount/t_p, 1)

#     #print(f"target: t_p={t_p}, av_q={av_q} => t_q={t_q} & total$={t_q*t_p}")

#     if ORDER_TEST:
#         spot_order = client.create_test_order(
#             symbol='EOSUSDT',
#             side=Client.SIDE_SELL,
#             type=Client.ORDER_TYPE_LIMIT,
#             timeInForce='GTC',
#             price=t_p,
#             quantity=s_q)
#     else:    
#         #exit(0)
#         spot_order = client.create_order(
#             symbol='EOSUSDT',
#             side=Client.SIDE_SELL,
#             type=Client.ORDER_TYPE_LIMIT,
#             timeInForce='GTC',
#             price=t_p,
#             quantity=s_q)
#     print(spot_order)


#     print('### futures long ###')
#     depth = client.futures_order_book(symbol='EOSUSDT')
#     #print(depth)
#     t_p = round(float(depth['asks'][0][0]), 4)
#     av_q = float(depth['asks'][0][1])
    
#     # amount = 15.0
#     # t_q = round(amount/t_p, 1)

#     print(f"target: t_p={t_p} * f_q={-f_q}(av:{av_q}) = ${-t_p*f_q}")

#     if ORDER_TEST:
#         fut_order = client.create_test_order(
#             symbol='EOSUSDT',
#             side=Client.SIDE_BUY,
#             type=Client.ORDER_TYPE_LIMIT,
#             timeInForce='GTC',
#             price=t_p,
#             quantity=-f_q)
#     else:    
#         #exit(0)
#         fut_order = client.futures_create_order(
#             symbol='EOSUSDT',
#             side=Client.SIDE_BUY,
#             type=Client.ORDER_TYPE_LIMIT,
#             timeInForce='GTC',
#             price=t_p,
#             quantity=-f_q)
#     print(fut_order)

#     # client.futures_create_order(
#     #     symbol='EOSUSDT',
#     #     type='LIMIT',
#     #     timeInForce='GTC',  # Can be changed - see link to API doc below
#     #     price=30000,  # The price at which you wish to buy/sell, float
#     #     side='BUY',  # Direction ('BUY' / 'SELL'), string
#     #     quantity=0.001  # Number of coins you wish to buy / sell, float
#     # )

# except BinanceAPIException as e:
#     # error handling goes here
#     print(e)
# except BinanceOrderException as e:
#     # error handling goes here
#     print(e)

# finally:
#     pass


