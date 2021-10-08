from classes.Exchanges import Exchanges
from exchange import *
from util.math import *
from arbi.arbi_common import *

def arbi_in_bnSpotBuy_bnFutShort(ex: Exchanges, asset: str, bn_p_usd: float, maxUSD: float, TEST: bool) -> tuple[float, float]:
    #cale numbers
    t_q = floor_1(maxUSD/bn_p_usd) #spot 4, future 1 #<-
    fee = bn_get_withdraw_fee(asset)
    t_q_fee = round(t_q-fee, 1)

    #BN Spot Buy
    bn_order_s = bn_spot_trade(ex, asset, TRADE_BUY, bn_p_usd, t_q, TEST)
    bn_wait_order(ex, bn_order_s, BN_SPOT, TEST)
    
    #BN Futures Short
    f_t_p, f_av_q = wait_bn_future_settle(ex, asset, bn_p_usd)

    bn_order_f = bn_fut_trade(ex, asset, TRADE_SELL, f_t_p, t_q_fee, TEST)
    bn_wait_order(ex, bn_order_f, BN_FUT, TEST)

    return t_q, t_q_fee

def arbi_in_withdraw_bn_to_ub(ex: Exchanges, asset: str, t_q: float, t_q_fee: float):
    bn_wait_balance(ex, asset, t_q)

    #3a. withdraw
    withdraw_id = bn_withdraw(ex, asset, ub_eos_addr, ub_eos_memo, t_q)
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
        bn_p_usd, _  = bn_spot_1st_ask(ex, asset) #market 
        ub_p_krw, _  = ub_spot_1st_bid(asset)          #market
        ub_p_usd  = round(ub_p_krw / ex.krwPerUsd, 4)
        kimp  = round( (ub_p_usd/bn_p_usd-1)*100,2)
        print(f"[wait_kimp_inTh]({cnt}) kimp({kimp}) > inTh({inTh}) ?")
        if kimp > inTh:
            return ub_p_krw, bn_p_usd
        cnt = cnt + 1
        time.sleep(1)

def arbi_in_ubSpotSell_bnFutBuy(ex: Exchanges, asset: str, t_q_fee: float, inTh: float, TEST: bool):
    ub_p_krw, bn_p_usd = wait_kimp_inTh(ex, asset, inTh) #ensure target kimp is maintained

    ub_order_s = ub_spot_trade(ex, asset, TRADE_SELL, ub_p_krw, t_q_fee, TEST)  #4a. Spot Sell
    bn_order_f = bn_fut_trade(ex, asset, TRADE_BUY, bn_p_usd, t_q_fee, TEST)    #4b. Futures Long

    ub_wait_order(ex, ub_order_s, TEST)
    bn_wait_order(ex, bn_order_f, BN_FUT, TEST)

