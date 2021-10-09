from classes.Exchanges import Exchanges
from arbi.arbi_common import *
from arbi.arbi_in import *
from arbi.arbi_out import *

def arbi_in_bn_to_ub(ex: Exchanges, asset: str, bn_p_usd: float, maxUSD: float, inTh: float, TEST: bool =True):
    #1. check balance
    assert check_fee_bnb(ex, maxUSD)
    assert check_bn_balance(ex, maxUSD)
    assert check_bn_fut_balance(ex, maxUSD)

    # 2. Hedge & Buy
    t_q, t_q_fee = arbi_in_bnSpotBuy_bnFutShort(ex, asset, bn_p_usd, maxUSD, TEST)

    # 3. swap exchange
    arbi_in_withdraw_bn_to_ub(ex, asset, t_q, t_q_fee)

    # 4. Sell & UnHedge
    arbi_in_ubSpotSell_bnFutBuy(ex, asset, t_q_fee, inTh, TEST)

    return True
    

def arbi_out_ub_to_bn(ex: Exchanges, asset: str, ub_p_krw: float, bn_p_usd: float, maxUSD: float, TEST: bool =True):
    #1. check balance
    assert check_fee_bnb(ex, maxUSD)
    assert check_ub_balance(ex, maxUSD)
    assert check_bn_fut_balance(ex, maxUSD)
    #future account balance & leverage check
    #ex.binance.futures_change_leverage(bn_usdt_pair(asset), leverage=1)

    ### 2. Hedge & Buy ####
    t_q = arbi_out_unSpotBuy_bnFutShort(ex, asset, ub_p_krw, bn_p_usd, maxUSD, TEST)

    #### 3. swap exchange ####
    arbi_out_withdraw_ub_to_bn(ex, asset, t_q)

    #### 4. Sell & UnHedge ####
    arbi_out_bnSpotSell_bnFutBuy(ex, asset, t_q, TEST)

    return True
