import time
import math
import itertools

from util.log import log
from classes import *

#const
BN_SPOT     = 5010
BN_FUT      = 5011
TRADE_BUY   = 6010
TRADE_SELL  = 6011

FUT_SHORT   = 7010
FUT_LONG    = 7011


#func
def bn_get_spot_balance(ex: Exchanges, asset: str, doRound: bool = True):
    #print('### spot balance ###')
    balance = ex.binance.get_asset_balance(asset=asset)
    assert ( balance['asset'] == 'EOS' or balance['asset'] == 'USDT' or balance['asset'] == 'BNB')
    if doRound:
        s_q = math.floor(float(balance['free'])*10)/10 #2자리 미만 안쓰임
    else:
        s_q = float(balance['free'])
    #print(f"eos: q={s_q}")
    return s_q

def bn_wait_balance(ex: Exchanges, asset: str, t_q: float):
    time.sleep(3)
    while True:
        q = bn_get_spot_balance(ex, asset)
        print(f"[bn_wait_balance]{asset}:{q} < {t_q}")
        if q >= t_q:
            break
        time.sleep(1)

def bn_get_fut_margin_balance(ex: Exchanges, acc: dict = None):
    acc = ex.binance.futures_account() if acc == None else acc
    asset = acc['assets'][1]
    assert asset['asset'] == 'USDT'

    #float(asset['walletBalance'])
    #pendingAmt = float(asset['unrealizedProfit'])
    #if abs(pendingAmt) > 0:
        #log(f"[bn_get_fut_margin_balance]pendingAmt:{pendingAmt}")
    return float(asset['marginBalance'])

def bn_get_fut_asset_q(ex: Exchanges, asset: str, _type: str):
    assert asset == 'EOS'
    EOS_IDX = 67 #fixme: NO IDX or ADD XRP or ETC
    #print('### futures balance ###')
    acc = ex.binance.futures_account()
    f_eos = acc['positions'][EOS_IDX]
    assert f_eos['symbol'] == 'EOSUSDT' #<-- check!
    f_p = float(f_eos['entryPrice'])
    f_q = float(f_eos['positionAmt'])
    
    if _type == FUT_SHORT:
        assert f_q < 0 #short
        return -f_q
    elif _type == FUT_LONG:
        assert f_q > 0 #long
        return f_q
    else:
        print('unknown type:' + _type)

def bn_get_fut_balance(ex: Exchanges, asset: str):
    assert asset == 'EOS'
    EOS_IDX = 67 #fixme: NO IDX or ADD XRP or ETC
    #print('### futures balance ###')
    acc = ex.binance.futures_account()
    f_eos = acc['positions'][EOS_IDX]
    assert f_eos['symbol'] == 'EOSUSDT' #<-- check!
    leverage = float(f_eos['leverage'])
    marginBalance = bn_get_fut_margin_balance(ex, acc)

    return marginBalance*leverage*0.8 #safe 10%


def bn_usdt_pair(asset):
    return asset + 'USDT'

def bn_spot_1st_bid(ex: Exchanges, asset: str): #highest buying bids
    depth = ex.binance.get_order_book(symbol=bn_usdt_pair(asset))
    t_p = round(float(depth['bids'][0][0]), 4)
    av_q = float(depth['bids'][0][1])
    return t_p, av_q

def bn_spot_1st_ask(ex: Exchanges, asset: str): #lowest selling price
    depth = ex.binance.get_order_book(symbol=bn_usdt_pair(asset))
    t_p = round(float(depth['asks'][0][0]), 4)
    av_q = float(depth['asks'][0][1])
    return t_p, av_q

def bn_fut_1st_bid(ex: Exchanges, asset: str):
    depth = ex.binance.futures_order_book(symbol=bn_usdt_pair(asset))
    t_p = round(float(depth['bids'][0][0]), 4)
    av_q = float(depth['bids'][0][1])
    return t_p, av_q

def bn_fut_1st_ask(ex: Exchanges, asset: str):
    depth = ex.binance.futures_order_book(symbol=bn_usdt_pair(asset))
    t_p = round(float(depth['asks'][0][0]), 4)
    av_q = float(depth['asks'][0][1])
    return t_p, av_q

def bn_get_trade_type(tradeMode: int):
    if tradeMode == TRADE_BUY:
        return Client.SIDE_BUY
    if tradeMode == TRADE_SELL:
        return Client.SIDE_SELL
    print(f"bn_get_trade_type:invalide mode={tradeMode}")
    exit(0)
        

def bn_spot_trade(ex: Exchanges, asset: str, tradeMode: int, t_p: float, t_q: float, TEST: bool = True):
    pair = bn_usdt_pair(asset)
    tradeType = bn_get_trade_type(tradeMode)
    log(f"[bn_spot_{tradeType}]{pair} {t_q}q @ {t_p}$, TEST={TEST}")
    if TEST:
        return ex.binance.create_test_order(
            symbol=pair,
            side=tradeType,
            type=Client.ORDER_TYPE_LIMIT,
            timeInForce='GTC',
            price=t_p,
            quantity=t_q)
    else:
        return ex.binance.create_order(
            symbol=pair,
            side=tradeType,
            type=Client.ORDER_TYPE_LIMIT,
            timeInForce='GTC',
            price=t_p,
            quantity=t_q)

def bn_fut_trade(ex: Exchanges, asset: str, tradeMode: int, t_p: float, t_q: float, TEST: bool = True):
    tradeType = bn_get_trade_type(tradeMode)
    pair = bn_usdt_pair(asset)
    log(f"[bn_fut_{tradeType}]{pair} {t_q}q @ {t_p}$, TEST={TEST}")
    if TEST:
        return ex.binance.create_test_order(
            symbol=pair,
            side=tradeType,
            type=Client.ORDER_TYPE_LIMIT,
            timeInForce='GTC',
            price=t_p,
            quantity=t_q)
    else:
        return ex.binance.futures_create_order(
            symbol=pair,
            side=tradeType,
            type=Client.ORDER_TYPE_LIMIT,
            timeInForce='GTC',
            price=t_p,
            quantity=t_q)

def bn_wait_order(ex: Exchanges, order: dict, type: int, TEST: bool):
    if TEST: return

    symbol = order['symbol']
    for i in itertools.count():
        if type==BN_SPOT:
            _order = ex.binance.get_order(symbol=symbol, orderId=order['orderId'])
        elif type==BN_FUT:
            _order = ex.binance.futures_get_order(symbol=symbol, orderId=order['orderId'])
        else:
            raise Exception('unknown type:{type}')

        state = _order['status']
        print(f"[bn_wait_order]({i}) state={state}")
        #PARTIALLY_FILLED CANCELED REJECTED EXPIRED NEW
        if state == 'NEW' or state == 'PARTIALLY_FILLED':
            pass
        elif state == 'CANCELED' or state == 'REJECTED' or state == 'EXPIRED':
            raise Exception('[bn_wait_order]:order {state}')
        elif state == 'FILLED':
            break

        time.sleep(1)

def bn_get_deposit(ex: Exchanges, asset: str, txid: str):
    result = ex.binance.get_deposit_history(coin=asset)
    filtered = list(filter(lambda x: x['txId'] == txid, result))
    return filtered

def bn_wait_deposit(ex: Exchanges, asset: str, txid: str):
    cnt = 0
    while True:
        ret = bn_get_deposit(ex, asset, txid)
        if len(ret) > 0:
            state = ret[0]['status']
            print(f"({cnt})bn_get_deposit: state={state}")
            if state == 0: #pending
                pass
            elif state == 6: #credited but cannot withdraw
                pass
            elif state == 1: #success
                return
        time.sleep(3)
        cnt = cnt + 3

def bn_withdraw(ex: Exchanges, asset: str, addr: str, tag: str, t_q: float):
    withdraw = ex.binance.withdraw(
        coin=asset,
        address=addr,
        addressTag=tag, #or TAG
        amount=t_q)    
    return withdraw['id']

def bn_wait_withdraw(ex: Exchanges, withdraw_id: str):
    time.sleep(10)
    cnt = 10
    txid = None
    while True:
        try:
            withdraw_result = ex.binance.get_withdraw_history_id(withdraw_id)
            #pprint.pprint(withdraw_result)
            print(f"({cnt})bn_wait_withdraw: state={withdraw_result['status']}")
            if 'txId' in withdraw_result:
                if txid is None:
                    txid = withdraw_result['txId']
                    print(f"txid:{txid}")
            else:
                _id = withdraw_result['id']
                #print(f"id{_id}")
            
            '''
            https://binance-docs.github.io/apidocs/spot/en/#deposit-history-supporting-network-user_data
            0(0:Email Sent,1:Cancelled 2:Awaiting Approval 3:Rejected 4:Processing 5:Failure 6:Completed)
            '''
            if withdraw_result['status'] == 1:
                raise Exception('ub_wait_withdraw:order canceled')
            elif withdraw_result['status'] == 3:
                raise Exception('ub_wait_withdraw:order rejected')
            elif withdraw_result['status'] == 4:
                #print(f"processing..")
                pass
            elif withdraw_result['status'] == 6:
                print('complete..')
                return txid
        except ConnectionError as ce:
            print('consume connection error')
        time.sleep(3)
        cnt = cnt + 3

def bn_cancel_or_refund(ex: Exchanges, order: dict, mode: int, pair: str, TEST: bool):
    if TEST: return

    assert pair == order['symbol']
    _type = mode
    func_getOrder = {
        BN_SPOT:ex.binance.get_order,
        BN_FUT:ex.binance.futures_get_order
    }

    func_cancelOrder = {
        BN_SPOT:ex.binance.cancel_order,
        BN_FUT:ex.binance.futures_cancel_order
    }

    orderId = order['orderId']
    for i in itertools.count():
        _order = func_getOrder[_type](symbol=pair, orderId=orderId)
        state = _order['status']
        print(f"[bn_cancel_or_refund]({i}) state={state}")

        #PARTIALLY_FILLED CANCELED REJECTED EXPIRED NEW
        if state == 'NEW' or state == 'PARTIALLY_FILLED':
            ret = func_cancelOrder[_type](symbol=pair, orderId=orderId)
            print(f"[bn_cancel_or_refund] cancel:{ret}")
            #re-iter -> check state changed to 'canceled'
        elif state == 'CANCELED' or state == 'REJECTED' or state == 'EXPIRED':
            print(f"canceled")
        elif state == 'FILLED':

            break
        time.sleep(1)

def bn_get_withdraw_fee(asset):
    assert asset == 'EOS'
    return 0.1