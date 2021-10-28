from classes.Exchanges import Exchanges
from exchange import *
from util.math import *
from util.time import *
from arbi.arbi_common import *

import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool
from concurrent.futures import ThreadPoolExecutor

def arbi_in_bnSpotBuy_bnFutShort(ex: Exchanges, asset: str, bn_p_usd: float, bn_f_usd: float, maxUSD: float, TEST: bool) -> tuple[float, float]:
    #calc numbers
    prec_p, prec_q = bn_get_precision_pq(asset)
    bn_p_usd = floor(bn_p_usd, prec_p) #eos price q 4. #!fixme: according to coin
    bn_f_usd = floor(bn_f_usd, prec_p)
    t_q = floor(maxUSD/bn_p_usd, prec_q) #spot 4, future 1 #<-
    fee = bn_get_withdraw_fee(asset)
    t_q_fee = floor(t_q-fee, prec_q) 

    #BN Spot Buy
    #BN Futures Short
    #f_t_p, f_av_q = wait_bn_future_settle(ex, asset, bn_p_usd)
    f_t_p = bn_f_usd

    pool = ThreadPoolExecutor(2)
    ret1 = pool.submit(lambda p: bn_spot_trade(*p), [ex, asset, TRADE_BUY, bn_p_usd, t_q, TEST])
    ret2 = pool.submit(lambda p: bn_fut_trade(*p),  [ex, asset, TRADE_SELL, f_t_p, t_q_fee, TEST])
    bn_order_s = ret1.result()
    bn_order_f = ret2.result()
    
    time.sleep(1)
    bn_wait_order(ex, bn_order_s, BN_SPOT, TEST)
    bn_wait_order(ex, bn_order_f, BN_FUT, TEST)

    return t_q, t_q_fee

def arbi_in_withdraw_bn_to_ub(ex: Exchanges, asset: str, t_q: float, t_q_fee: float):
    bn_wait_balance(ex, asset, t_q)

    #3a. withdraw
    addr = ub_get_asset_addr(asset)
    memo = ub_get_asset_memo(asset)
    withdraw_id = bn_withdraw(ex, asset, addr, memo, t_q)
    print(f"withdraw_id:{withdraw_id}")

    #3b. wait finished - BN
    txid = bn_wait_withdraw(ex, withdraw_id)
    print(f"txid:{txid}")

    #3c. wait deposit - UB
    ub_wait_deposit(ex, txid)
    ub_wait_balance(ex, asset, t_q_fee)  #wait balance available


def wait_kimp_inTh(ex: Exchanges, asset: str, inTh: float):
    cnt = 0
    while True:
        #t0 = get_ms()
        #fixme: fut이 spot보다 좀 더 높아서... 처음에 spot-fut 비율을 가져와야할것같은데..
        bn_p_usd, _  = bn_fut_depth(ex, asset, 0)[ASK]  #long from futures - ask #ub_spot_1st(..)[ASK] some times lose
        #t1 = get_ms()
        ub_p_krw, _  = ub_spot_depth(ex, asset, 0)[BID] #sell spot - bid
        #t2 = get_ms()
        #print(f"[arbi_in_ubSpotSell_bnFutBuy] bn_fut_depth0ASK({t1-t0}ms), ub_spot_1st_bid({t2-t1}ms)")
        ub_p_usd  = round(ub_p_krw / ex.krwPerUsd, 4)
        kimp  = round( (ub_p_usd/bn_p_usd-1)*100,2)    
        if cnt%10==0: print(f"[wait_kimp_inTh]({cnt}) kimp({kimp}) > inTh({inTh}) ?")
        if kimp > inTh:
            print(f"[wait_kimp_inTh] proceed: ({cnt}) kimp({kimp}) > inTh({inTh}) ?")
            return ub_p_krw, bn_p_usd
        cnt = cnt + 1
        time.sleep(1)

def arbi_in_ubSpotSell_bnFutBuy(ex: Exchanges, asset: str, t_q_fee: float, inTh: float, TEST: bool):
    pool = ThreadPoolExecutor(2)
    ub_p_krw, bn_p_usd = wait_kimp_inTh(ex, asset, inTh) #ensure target kimp is maintained
    #balance availability check!
    #!fixme ub - bn_fut async 
    #python binance async https://sammchardy.github.io/async-binance-basics/
    #python coroutine...
    #t0 = get_ms()
    ret1 = pool.submit(lambda p: ub_spot_trade(*p), [ex, asset, TRADE_SELL, ub_p_krw, t_q_fee, TEST])
    ret2 = pool.submit(lambda p: bn_fut_trade(*p),  [ex, asset, TRADE_BUY, bn_p_usd, t_q_fee, TEST])
    #t1 = get_ms()
    ub_order_s = ret1.result()
    bn_order_f = ret2.result()
    #t2 = get_ms()
    ub_wait_order(ex, ub_order_s, TEST)
    bn_wait_order(ex, bn_order_f, BN_FUT, TEST)
    #t3 = get_ms()

    #print(f"[arbi_in_ubSpotSell_bnFutBuy] trade call({t1-t0}ms), getResult({t2-t1}ms), wait_order({t3-t2}ms)")
    