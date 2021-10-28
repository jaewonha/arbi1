from classes.Exchanges import Exchanges
from exchange import *
from util.math import *

#addresses

##eos
ub_eos_addr = 'eosupbitsusr'
ub_eos_memo = '5772f423-5c5a-4361-9678-2e070338fec1'

bn_eos_addr = 'binancecleos'
bn_eos_memo = '109642124'

##trx
ub_trx_addr = 'TSCaN4rUp3VXcu7Eb6QPmU7Xg2QR1hJkh6' #1confirm
bn_trx_addr = 'TPa9XVdUUj3UeTX8vJ6FYcY8vS3vq9WH1S'

##xrp
ub_xrp_addr = 'raQwCVAJVqjrVm1Nj5SFRcX8i22BhdC9WA'
ub_xrp_memo = '1047636641'

bn_xrp_addr = 'rEb8TK3gBgk5auZkwc6sHnwrGVJH8DuaLh'
bn_xrp_memo = '100196247'

##doge
ub_doge_addr = 'DHAuNjyov8KuLxLGQ4C7PbXykYixtKvPhk' #6confirm
bn_doge_addr = 'DCbpph4x46jDtnNp6h648vrWFCJUkCbwG6'

##sc
bn_sc_addr = '31be1f97f7f71e18a9323c56463ab705cca7e1acff112310e3dbcb22872d4009128eaab766a5'
ub_sc_addr = '2cba9e8f39146ec5d28247afe74639b0c4edd172e97e20f9fd39fb5ddf0ab7d274a945060d51' #6confirm


def wait_bn_future_settle(ex: Exchanges, asset: str, bn_p_usd: float)->tuple[float,float]:
    max_wait = 10
    permit_diff = 0.004 #asset -> price -> 3ticks
    for i in range(1,max_wait+1):
        f_t_p, f_av_q = bn_fut_depth(ex, asset, 0)[BID]
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
    bnb_fut_q = bn_fut_acc_asset_balance(ex, 'BNB') 
    bnb_price = float(ex.binance.get_symbol_ticker(symbol='BNBUSDT')['price'])
    
    bnb_usdt = bnb_q * bnb_price
    bnb_fut_usdt = bnb_fut_q * bnb_price

    feeUSDT = maxUSD * 0.0010
    feeFutUSDT = maxUSD * 0.0004*2

    if bnb_usdt < feeUSDT: 
        print(f"insufficient bnbUSDT: {bnb_usdt} < {feeUSDT}")
        return False
    
    if bnb_fut_usdt < feeFutUSDT: 
        print(f"insufficient bnbFutUSDT: {bnb_fut_usdt} < {feeFutUSDT}")
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

def check_bn_fut_margin_balance(ex: Exchanges, asset: str, maxUSD: float)->bool:
    futMarBal = bn_get_fut_margin_balance(ex, asset)
    if futMarBal < maxUSD:
        print(f"insufficient BN Fut balance {futMarBal} < {maxUSD}")
        return False
    return True