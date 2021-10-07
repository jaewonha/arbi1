import asyncio
import json
import pandas as pd
import numpy as np
import json
import math

from exchange import *
from util.math import *

ub_eos_addr = 'eosupbitsusr'
ub_eos_memo = '5772f423-5c5a-4361-9678-2e070338fec1'

bn_eos_addr = 'binancecleos'
bn_eos_memo = '109642124'

def check_fee_bnb(binance, maxUSD):
    bnb_q = bn_get_spot_balance(binance, 'BNB') 
    bnb_price = float(binance.get_symbol_ticker(symbol='BNBUSDT')['price'])
    bnb_usdt = bnb_q * bnb_price
    feeUSDT = maxUSD * (0.0010 + 0.0004*2 + 0.03) #spot fee + future fee 2x + pad

    if bnb_usdt < feeUSDT: 
        print(f"insufficient bnbUSDT: {bnb_usdt} < {feeUSDT}")
        return False

    return True
    

def wait_kimp_inTh(binance, bn_pair, ub_pair, krwPerUsd, inTh):
    cnt = 0
    while True:
        bn_p_usd, _  = bn_spot_1st_ask(binance, bn_pair) #market 
        ub_p_krw, _  = ub_spot_1st_bid(ub_pair)          #market
        ub_p_usd  = round(ub_p_krw / krwPerUsd, 4)
        kimp  = round( (ub_p_usd/bn_p_usd-1)*100,2)
        print(f"[wait_kimp_inTh]({cnt}) kimp({kimp}) > inTh({inTh}) ?")
        if kimp > inTh:
            return ub_p_krw, bn_p_usd
        cnt = cnt + 1
        time.sleep(1)
'''
def wait_kimp_outTh(binance, bn_pair, ub_pair, krwPerUsd, outTh):
    cnt = 0
    while True:
        bn_p_usd, _  = bn_spot_1st_bid(binance, bn_pair) #market 
        ub_p_krw, _  = ub_spot_1st_ask(ub_pair)          #market
        ub_p_usd  = round(ub_p_krw / krwPerUsd, 4)
        kimp  = round( (ub_p_usd/bn_p_usd-1)*100,2)
        print(f"[wait_kimp_outTh]({cnt}) kimp({kimp}) < inTh({outTh}) ?")
        if kimp < outTh:
            return ub_p_krw, bn_p_usd
        cnt = cnt + 1
        time.sleep(1)
'''

def wait_bn_future_settle(binance, bn_pair, bn_p_usd):
    max_wait = 10
    permit_diff = 0.004 #asset -> price -> 3ticks
    for i in range(1,max_wait+1):
        f_t_p, f_av_q = bn_fut_1st_bid(binance, bn_pair)
        diff = bn_p_usd - f_t_p #for short, f_t_p higher is okay
        if diff < permit_diff:
            break
        print(f"[wait_bn_future_settle]price wait bn:{bn_p_usd} - f_p:{f_t_p} < diff:{diff}")
        time.sleep(1)
        if i == max_wait:
            print(f"[wait_bn_future_settle]spot-future diff not converge:{diff}. taking risks")
    return f_t_p, f_av_q

def arbi_in_bn_to_ub(binance, upbit, upbit2, asset, bn_p_usd, maxUSD, krwPerUSD, inTh, TEST=True):
    assert check_fee_bnb(binance, maxUSD)

    balUSDT = bn_get_spot_balance(binance, 'USDT')
    fee = 0.1

    #1. check spot balance is enough
    if balUSDT < maxUSD:
        print(f"insufficient USDT balance {balUSDT} < {maxUSD}")
        return False

    # ### 2. Hedge & Buy ####
    # #2a. Spot Buy
    bn_pair = bn_usdt_pair(asset)
    #t_p, av_q = bn_spot_1st_ask(binance, bn_pair) #market <-
    t_q = floor_1(maxUSD/bn_p_usd) #spot 4, future 1 #<-
    t_q_fee = round(t_q-fee, 1)
    bn_order_s = bn_spot_trade(binance, bn_pair, TRADE_BUY, bn_p_usd, t_q, TEST) #<-
    bn_wait_order(binance, bn_order_s, BN_SPOT, TEST) #<-
    
    # #2b. Futures Short
    f_t_p, f_av_q = wait_bn_future_settle(binance, bn_pair, bn_p_usd)

    bn_order_f = bn_fut_trade(binance, bn_pair, TRADE_SELL, f_t_p, t_q_fee, TEST) #<-
    bn_wait_order(binance, bn_order_f, BN_FUT, TEST) #<-

    #### 3. swap exchange ####
    bn_wait_balance(binance, asset, t_q)

    #3a. withdraw
    withdraw_id = bn_withdraw(binance, asset, ub_eos_addr, ub_eos_memo, t_q)
    #withdraw_id = '50114af2397b44afb0893fc3c60ae4dd'
    print(f"withdraw_id:{withdraw_id}")

    ## below prerequiste (txid, t_q <-t_p)
    #3b. wait finished - BN
    txid = bn_wait_withdraw(binance, withdraw_id)
    #txid = 'df0fd3bb9b50125cb48805f5c4ad4ed384200c709db9fe7b964bdec55b39e090'
    print(f"txid:{txid}")

    #3c. wait deposit - UB
    ub_wait_deposit(upbit2, txid)
    ub_wait_balance(upbit, asset, t_q_fee)  #wait balance available

    #### 4. Sell & UnHedge ####
    #4a. Spot Sell
    ub_pair = ub_krw_pair(asset)

    ub_p_krw, bn_p_usd = wait_kimp_inTh(binance, bn_pair, ub_pair, krwPerUSD, inTh) #ensure target kimp is maintained

    #t_p, av_q = ub_spot_1st_bid(ub_pair)
    ub_order_s = ub_spot_trade(upbit, ub_pair, TRADE_SELL, ub_p_krw, t_q_fee, krwPerUSD, TEST)

    #4b. Futures Long
    #f_t_p, f_av_q = bn_fut_1st_ask(binance, bn_pair)
    bn_order_f = bn_fut_trade(binance, bn_pair, TRADE_BUY, bn_p_usd, t_q_fee, TEST)

    ub_wait_order(upbit, ub_order_s, TEST)
    bn_wait_order(binance, bn_order_f, BN_FUT, TEST)

    return True
    
def arbi_out_ub_to_bn(binance, upbit, upbit2, asset, ub_p_krw, bn_p_usd, maxKRW, krwPerUSD, TEST=True):
    assert check_fee_bnb(binance, maxKRW/krwPerUSD)

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
    #t_p, av_q = ub_spot_1st_ask(ub_pair) #market
    #t_p = 5730 #fixed
    t_q = floor_1(maxKRW/ub_p_krw)
    ub_order = bn_order = None
    #try:
    ub_order = ub_spot_trade(upbit, ub_pair, TRADE_BUY, ub_p_krw, t_q, TEST); #<-
    ub_wait_order(upbit, ub_order) #<-

    # #2b. Futures Short
    f_t_p, f_av_q = wait_bn_future_settle(binance, bn_pair, bn_p_usd)

    bn_order = bn_fut_trade(binance, bn_pair, TRADE_SELL, f_t_p, t_q, TEST) #<-
    bn_wait_order(binance, bn_order, BN_FUT, TEST) #<-
    #except Exception as e:
        #if ub_order:    ub_cancel_or_refund(upbit, ub_order, ub_pair, TEST)
        #if bn_order:    bn_cancel_or_refund(binance, bn_order, bn_pair, TEST)

    #### 3. swap exchange ####
    #3a. withdraw
    ub_wait_balance(upbit, asset, t_q)
    withdraw_uuid = ub_withdraw(upbit2, asset, t_q, bn_eos_addr, bn_eos_memo)
    #withdraw_uuid = '3ff3c7be-014e-4c08-b851-4c5d68cb5992'
    print(f"withdraw_uuid:{withdraw_uuid}")

    #3b. wait finished - UB
    txid = ub_wait_withdraw(upbit2, withdraw_uuid)
    print(f"txid:{txid}")

    #3c. wait deposit - BN
    bn_wait_deposit(binance, asset, txid)
    bn_wait_balance(binance, asset, t_q) #wait balance available

    #### 4. Sell & UnHedge ####
    #no need -> kimp is fixed when BU spot + Bn shot bought
    #ub_p_krw, bn_p_usd = wait_kimp_outTh(binance, bn_pair, ub_pair, krwPerUSD, outTh) #ensure target kimp is maintained

    #4a. Spot Sell
    bn_pair = bn_usdt_pair(asset)
    t_p, av_q = bn_spot_1st_bid(binance, bn_pair) #market
    bn_order_s = bn_spot_trade(binance, bn_pair, TRADE_SELL, t_p, t_q, TEST)

    #4b. Futures Long
    f_t_p, f_av_q = bn_fut_1st_ask(binance, bn_pair)
    bn_order_f = bn_fut_trade(binance, bn_pair, TRADE_BUY, f_t_p, t_q, TEST)

    bn_wait_order(binance, bn_order_s, BN_SPOT, TEST)
    bn_wait_order(binance, bn_order_f, BN_FUT, TEST)

    return True

