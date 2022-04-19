from classes.Exchanges import Exchanges
from exchange import *
from util.math import *
from arbi.arbi_common import *

import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool
from concurrent.futures import ThreadPoolExecutor

import keyboard

def arbi_out_ubSpotBuy_bnFutShort(ex: Exchanges, asset: str, ub_p_krw: float, bn_f_usd: float, maxUSD: float, TEST: bool):
    # #2a. Spot Buy
    maxKRW = maxUSD*ex.krwPerUsd
    prec_p, prec_q = bn_get_precision_pq(asset)
    ub_p_krw = floor(ub_p_krw, prec_p) #floor target price to precision
    t_q = floor(maxKRW/ub_p_krw, prec_q) #spot 4, future 1 #<-
    fee = ub_get_withdraw_fee(asset)
    t_q_fee = floor(t_q-fee, prec_q) 
    ub_order = bn_order = None

    # #2b. Futures Short
    #f_t_p, f_av_q = wait_bn_future_settle(ex, asset, bn_p_usd)
    f_t_p = bn_f_usd #assume fut price is used calc kimp

    #thread order
    if False: #seq
        ub_order = ub_spot_trade(ex, asset, TRADE_BUY, ub_p_krw, t_q, TEST)
        ub_wait_order(ex, ub_order, TEST) 
        bn_order = bn_fut_trade(ex, asset, TRADE_SELL, f_t_p, t_q, TEST)
        bn_wait_order(ex, bn_order, BN_FUT, TEST)
    else: #thread
        pool = ThreadPoolExecutor(2)
        ret1 = pool.submit(lambda p: ub_spot_trade(*p), [ex, asset, TRADE_BUY, ub_p_krw, t_q, TEST])
        ret2 = pool.submit(lambda p: bn_fut_trade(*p),  [ex, asset, TRADE_SELL, f_t_p, t_q, TEST])
        ub_order = ret1.result()
        bn_order = ret2.result()    
        ub_wait_order(ex, ub_order, TEST) #multi thread
        bn_wait_order(ex, bn_order, BN_FUT, TEST)

    #except Exception as e:
        #if ub_order:    ub_cancel_or_refund(upbit, ub_order, UB_SPOT, asset, TEST)
        #if bn_order:    bn_cancel_or_refund(binance, bn_order, BN_FUT, asset, TEST)

    return t_q, t_q_fee

def arbi_out_withdraw_ub_to_bn(ex: Exchanges, asset: str, t_q: float, t_q_fee: float, MANUAL_WITHDRAW: bool = False):
    ub_wait_balance(ex, asset, t_q)

    withdraw_uuid = None
    addr = bn_get_asset_addr(asset)
    memo = bn_get_asset_memo(asset)
    
    if MANUAL_WITHDRAW:
        print(f"Manual Withdraw Mode, Please With as follows")
        print(f"Asset:{asset}, Q:{t_q}")
        print(f"TargetAddr:{addr}")
        print(f"TargetMemo:{memo}")
        print(f"Press any key after your manual withdraw done")
        
        while True:
            pendings = ub_get_pending_withdraw(ex)
            print(f"#pending withdraw:{len(pendings)}, waiting Q:{t_q}, press 's' to skip")
            if len(pendings)==1 and float(pendings[0]['amount'])==t_q: #float comp?
                withdraw_uuid = pendings[0]['uuid']

            if keyboard.is_pressed("s"):
                print(f"no withdraw uuid captured. wait Q:{t_q} on binance")
                break
            
            time.sleep(1)

    else:
        withdraw_uuid = ub_withdraw(ex, asset, t_q, addr, memo)

    if withdraw_uuid != None:
        print(f"withdraw_uuid:{withdraw_uuid}")

        #3b. wait finished - UB
        txid = ub_wait_withdraw(ex, withdraw_uuid)
        print(f"txid:{txid}")

        #3c. wait deposit - BN
        bn_wait_deposit(ex, asset, txid)
    bn_wait_balance(ex, asset, t_q_fee) #wait balance available

'''
def wait_kimp_outTh(binance, asset, krwPerUsd, outTh):
    cnt = 0
    while True:
        bn_p_usd, _  = bn_spot_depth(ex, asset, 0)[BID] #market 
        ub_p_krw, _  = ub_spot_depth(ex, asset, 0)[ASK] #market
        ub_p_usd  = round(ub_p_krw / krwPerUsd, 4)
        kimp  = round( (ub_p_usd/bn_p_usd-1)*100,2)
        print(f"[wait_kimp_outTh]({cnt}) kimp({kimp}) < inTh({outTh}) ?")
        if kimp < outTh:
            return ub_p_krw, bn_p_usd
        cnt = cnt + 1
        time.sleep(1)
'''

def arbi_out_bnSpotSell_bnFutBuy(ex: Exchanges, asset: str, t_q: float, TEST):
    #no need -> kimp is fixed when BU spot + Bn shot bought
    #ub_p_krw, bn_p_usd = wait_kimp_outTh(binance, bn_pair, ub_pair, krwPerUsd, outTh) #ensure target kimp is maintained
    pool = ThreadPoolExecutor(2)

    #4a. Spot Sell
    while True:
        bnSpot1st = bn_spot_depth(ex, asset, 0)
        #t_p, av_q = bn_spot_depth(ex, asset, 0)[BID] #market
        t_p = bnSpot1st[BID][0]
        
        #4b. Futures Long
        #f_t_p, f_av_q = bn_fut_depth(ex, asset, 0)[ASK]
        bnFut1st = bn_fut_depth(ex, asset, 0)
        f_t_p = bnFut1st[ASK][0]

        if bn_is_backward(bnSpot1st, bnFut1st):
            print(f"[arbi_out_bnSpotSell_bnFutBuy]backward ({t_p}) < ({f_t_p}) fail")
            time.sleep(1)
        else:
            break
        
    #thread order
    ret1 = pool.submit(lambda p: bn_spot_trade(*p), [ex, asset, TRADE_SELL, t_p, t_q, TEST])
    ret2 = pool.submit(lambda p: bn_fut_trade(*p),  [ex, asset, TRADE_BUY, f_t_p, t_q, TEST])
    bn_order_s = ret1.result()
    bn_order_f = ret2.result()
    
    #if bn_is_backward(bnSpot1st, bnFut1st):
        #print(f"[arbi_out_bnSpotSell_bnFutBuy]Traded at BackWard!: futBid={bnFut1st[1][0]} > spotAsk={bnSpot1st[0][0]} failed")
                
    bn_wait_order(ex, bn_order_s, BN_SPOT, TEST)
    bn_wait_order(ex, bn_order_f, BN_FUT, TEST)
