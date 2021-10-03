import asyncio
import json
import pandas as pd
import numpy as np
import json
import math

from exchange import *

ub_eos_addr = 'eosupbitsusr'
ub_eos_memo = '5772f423-5c5a-4361-9678-2e070338fec1'

bn_eos_addr = 'binancecleos'
bn_eos_memo = '109642124'


def arbi_in_bn_to_ub(binance, upbit, upbit2, asset, maxUSD, krwPerUSD, TEST= True):
    balUSDT = bn_get_spot_balance(binance, 'USDT')
    fee = 0.1

    #1. check spot balance is enough
    if balUSDT < maxUSD:
        print(f"insufficient USDT balance {balUSDT} < {maxUSD}")
        return False

    ### 2. Hedge & Buy ####
    #2a. Spot Buy
    bn_pair = bn_usdt_pair(asset)
    #t_p, av_q = bn_spot_1st_ask(binance, bn_pair) #market
    t_p, av_q = bn_spot_1st_bid(binance, bn_pair) #wait
    #t_q = round(maxUSD/t_p, 1) #spot 4, future 1...
    t_q = math.floor(maxUSD/t_p*10)/10
    # order = bn_spot_trade(binance, bn_pair, TRADE_BUY, t_p, t_q, TEST)
    #print(f"spot buy:{order}")

    # bn_wait_order(binance, bn_pair, order['orderId'])
    
    # #2b. Futures Short
    f_t_p, f_av_q = bn_fut_1st_bid(binance, bn_pair)
    # order = bn_fut_trade(binance, bn_pair, TRADE_SELL, f_t_p, t_q-fee, TEST)

    # bn_wait_fut_order(binance, bn_pair, order['orderId'])
    
    

    #### 3. swap exchange ####
    #3a. withdraw
    # withdraw_id = bn_withdraw(binance, asset, ub_eos_addr, ub_eos_memo, t_q)
    withdraw_id = '50114af2397b44afb0893fc3c60ae4dd'
    print(f"withdraw_id:{withdraw_id}")

    #3b. wait finished - BN
    txid = bn_wait_withdraw(binance, withdraw_id)
    print(f"txid:{txid}")

    #3c. wait deposit - UB
    ub_wait_deposit(upbit2, txid)

    #check balance
    print(ub_get_spot_balance(upbit, asset))

    #### 4. Sell & UnHedge ####
    #4a. Spot Sell
    ub_pair = ub_krw_pair(asset)
    t_p, av_q = ub_spot_1st_bid(ub_pair)
    ub_spot_trade(upbit, ub_pair, TRADE_SELL, t_p, t_q-fee, krwPerUSD, TEST)

    #4b. Futures Long
    f_t_p, f_av_q = bn_fut_1st_ask(binance, bn_pair)
    bn_fut_trade(binance, bn_pair, TRADE_BUY, f_t_p, t_q-fee, TEST)

    return True
    
def arbi_out_ub_to_bn(binance, upbit, upbit2, asset, maxKRW, krwPerUSD, TEST=True):

    balKRW = ub_get_spot_balance(upbit, 'KRW')
    #binance future account balance check!!
    bn_pair = bn_usdt_pair(asset)
    #binance.futures_change_leverage(bn_pair, leverage=1)

    #1. check spot balance is enough
    if balKRW < maxKRW:
        print(f"insufficient KRW balance {balKRW} < {maxKRW}")
        return False

    ### 2. Hedge & Buy ####
    #2a. Spot Buy
    ub_pair = ub_krw_pair(asset)
    t_p, av_q = ub_spot_1st_ask(ub_pair) #market
    #t_p, av_q = ub_spot_1st_bid(ub_pair) #wait
    # t_p = 5730 #fixed
    t_q = math.floor(maxKRW/t_p*10)/10
    order = ub_spot_trade(upbit, ub_pair, TRADE_BUY, t_p, t_q, krwPerUSD, TEST)
    print(f"spot buy:{order}")
    
    ub_wait_order(upbit, order['uuid'])

    #2b. Futures Short
    f_t_p, f_av_q = bn_fut_1st_bid(binance, bn_pair)
    bn_fut_trade(binance, bn_pair, TRADE_SELL, f_t_p, t_q, TEST)
    
    #t_q = 20.9

    #### 3. swap exchange ####
    #3a. withdraw
    withdraw_uuid = ub_withdraw(upbit2, asset, t_q, bn_eos_addr, bn_eos_memo)
    print(f"withdraw_uuid:{withdraw_uuid}")

    #3b. wait finished - UB
    txid = ub_wait_withdraw(upbit2, withdraw_uuid)
    print(f"txid:{txid}")

    #3c. wait deposit - BN
    bn_wait_deposit(binance, asset, txid)

    #check balance
    print(bn_get_spot_balance(binance, asset))

    #### 4. Sell & UnHedge ####
    #4a. Spot Sell
    bn_pair = bn_usdt_pair(asset)
    t_p, av_q = bn_spot_1st_bid(binance, bn_pair) #market
    bn_spot_trade(binance, bn_pair, TRADE_SELL, t_p, t_q, TEST)

    #4b. Futures Long
    f_t_p, f_av_q = bn_fut_1st_ask(binance, bn_pair)
    bn_fut_trade(binance, bn_pair, TRADE_BUY, f_t_p, t_q, TEST)

    #def bn_wait_order(binance, orderId):
    return True

