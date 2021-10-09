from classes.Exchanges import Exchanges
from exchange import *
from util.math import *

ub_eos_addr = 'eosupbitsusr'
ub_eos_memo = '5772f423-5c5a-4361-9678-2e070338fec1'

bn_eos_addr = 'binancecleos'
bn_eos_memo = '109642124'

def wait_bn_future_settle(ex: Exchanges, asset: str, bn_p_usd: float)->tuple[float,float]:
    max_wait = 10
    permit_diff = 0.004 #asset -> price -> 3ticks
    for i in range(1,max_wait+1):
        f_t_p, f_av_q = bn_fut_1st_bid(ex, asset)
        diff = bn_p_usd - f_t_p #for short, f_t_p higher is okay
        if diff < permit_diff:
            break
        print(f"[wait_bn_future_settle]price wait bn:{bn_p_usd} - f_p:{f_t_p} < diff:{diff}")
        time.sleep(1)
        if i == max_wait:
            print(f"[wait_bn_future_settle]spot-future diff not converge:{diff}. taking risks")
    return f_t_p, f_av_q


def check_fee_bnb(ex: Exchanges, maxUSD: float)->bool:
    bnb_q = bn_get_spot_balance(ex, 'BNB') 
    bnb_price = float(ex.binance.get_symbol_ticker(symbol='BNBUSDT')['price'])
    bnb_usdt = bnb_q * bnb_price
    feeUSDT = maxUSD * (0.0010 + 0.0004*2 + 0.03) #spot fee + future fee 2x + pad
    if bnb_usdt < feeUSDT: 
        print(f"insufficient bnbUSDT: {bnb_usdt} < {feeUSDT}")
        return False
    return True

def check_bn_balance(ex: Exchanges, maxUSD: float)->bool:
    balUSDT = bn_get_spot_balance(ex, 'USDT')
    if balUSDT < maxUSD:
        print(f"insufficient USDT balance {balUSDT} < {maxUSD}")
        return False
    return True

def check_ub_balance(ex: Exchanges, maxUSD: float)->bool:
    balKRW = ub_get_spot_balance(ex, 'KRW')
    maxKRW = maxUSD*ex.krwPerUsd
    if balKRW < maxKRW:
        print(f"insufficient KRW balance {balKRW} < {maxKRW}")
        return False
    return True

def check_bn_fut_balance(ex: Exchanges, asset: str, maxUSD: float)->bool:
    futBal = bn_get_fut_balance(ex, asset)
    if futBal < maxUSD:
        print(f"insufficient BN Fut balance {futBal} < {maxUSD}")
        return False
    return True