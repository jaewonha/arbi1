import time
import math
import itertools

from util.log import log
from classes import *

from exchange.const import *


#func
def bn_get_spot_balance(ex: Exchanges, asset: str, doRound: bool = True):
    #print('### spot balance ###')
    balance = ex.binance.get_asset_balance(asset=asset)
    #assert ( balance['asset'] == 'EOS' or balance['asset'] == 'USDT' or balance['asset'] == 'BNB')
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

def bn_fut_acc_asset_balance(ex:Exchanges, asset:str):
    assert asset == 'USDT' or asset == 'BNB'
    fut_acc = ex.binance.futures_account_balance()
    fut_acc_asset = list(filter(lambda acc: acc['asset']==asset, fut_acc))[0]
    return float(fut_acc_asset['balance'])

def bn_get_fut_margin_usdt(ex: Exchanges, acc: dict = None):
    acc = ex.binance.futures_account() if acc == None else acc
    assets = acc['assets']
    asset_usdt = list(filter(lambda asset: asset['asset']=='USDT', assets))[0]
    assert asset_usdt['asset'] == 'USDT' #fixme

    #float(asset['walletBalance']) = total net + funding fee - tx fee
    #float(asset['marginBalance']) = unrealizedProfit applied
    #float(asset['unrealizedProfit'])
    return float(asset_usdt['marginBalance'])


def bn_get_fut_asset_q(ex: Exchanges, asset: str):
    f_asset = ex.binance.futures_position_information(symbol=bn_usdt_pair(asset))[0]
    f_p = float(f_asset['entryPrice'])
    f_q = float(f_asset['positionAmt'])
    return f_p, f_q

def bn_get_fut_margin_balance(ex: Exchanges, asset: str):
    acc = ex.binance.futures_account()
    pos = acc['positions']

    if str == 'EOS':
        f_asset = pos[67]
        assert f_asset['symbol'] == 'EOSUSDT' #<-- check!
    else:
        bn_pair = bn_usdt_pair(asset)
        f_asset = list(filter(lambda p: p['symbol']==bn_pair, pos))[0]

    leverage = float(f_asset['leverage'])
    marginBalance = bn_get_fut_margin_usdt(ex, acc)

    return marginBalance*leverage*0.8 #safe 20%


def bn_usdt_pair(asset):
    return asset + 'USDT'

def bn_spot_orderbook(ex: Exchanges, asset: str):
    return ex.binance.get_order_book(symbol=bn_usdt_pair(asset))

def bn_spot_depth(ex: Exchanges, asset: str, depth: int, ob: dict=None): #highest buying bids
    if ob is None:
        ob = bn_spot_orderbook(ex, asset)    
    
    a_t_p = round(float(ob['asks'][depth][0]), 6)
    a_av_q = float(ob['asks'][depth][1])

    b_t_p = round(float(ob['bids'][depth][0]), 6)
    b_av_q = float(ob['bids'][depth][1])

    return [[a_t_p, a_av_q],[b_t_p, b_av_q]]

def bn_fut_orderbook(ex: Exchanges, asset: str):
    return ex.binance.futures_order_book(symbol=bn_usdt_pair(asset))

def bn_fut_depth(ex: Exchanges, asset: str, depth: int, ob: dict=None): #highest buying bids
    if ob is None:
        ob = bn_fut_orderbook(ex, asset)

    b_t_p = round(float(ob['bids'][depth][0]), 6)
    b_av_q = float(ob['bids'][depth][1])
    
    a_t_p = round(float(ob['asks'][depth][0]), 6)
    a_av_q = float(ob['asks'][depth][1])

    return [[a_t_p, a_av_q],[b_t_p, b_av_q]]

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

async def a_bn_fut_trade(ex: Exchanges, asset: str, tradeMode: int, t_p: float, t_q: float, TEST: bool = True):
    tradeType = bn_get_trade_type(tradeMode)
    pair = bn_usdt_pair(asset)
    log(f"[a_bn_fut_{tradeType}]{pair} {t_q}q @ {t_p}$, TEST={TEST}")
    if TEST:
        return ex.a_binance.create_test_order(
            symbol=pair,
            side=tradeType,
            type=Client.ORDER_TYPE_LIMIT,
            timeInForce='GTC',
            price=t_p,
            quantity=t_q)
    else:
        return ex.a_binance.futures_create_order(
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
            if cnt==10 or cnt%60==0:
                print(f"({cnt})bn_wait_withdraw: state={withdraw_result['status']}")
            if 'txId' in withdraw_result:
                if txid is None:
                    txid = withdraw_result['txId']
                    print(f"({cnt}) txid:{txid}")
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
                print(f'({cnt}) complete..')
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

def bn_get_precision(asset):
    if asset == 'EOS': return 4
    elif asset == 'TRX': return 5
    elif asset == 'XRP': return 4
    else: raise Exception(f'bn_get_precision] unknown asset: {asset}')

def bn_get_withdraw_fee(asset):
    if asset == 'EOS': return 0.1
    elif asset == 'TRX': return 1
    elif asset == 'XRP': return 0.25
    else: raise Exception(f'bn_get_withdraw_fee] unknown asset: {asset}')

def bn_get_pending_amt(ex: Exchanges, asset: str)->float:
    #todo:
    #query pending order by asset
    #amount t_q *t_p
    #ret
    return 0.0

def bn_get_fut_pending_amt(ex: Exchanges, asset: str)->float:
    f_p, f_q = bn_get_fut_asset_q(ex, asset)
    assert not f_q > 0 #short only
    f_q = -f_q

    bn_pair = bn_usdt_pair(asset)
    orders = ex.binance.futures_get_open_orders(symbol=bn_pair)
    sum_q = 0.0
    gain = 0.0
    for order in orders:
        assert order['symbol'] == bn_pair
        assert order['side'] == 'BUY'
        p = float(order['price'])
        q = float(order['origQty']) - float(order['executedQty'])

        gain = gain + (f_p - p) * q
        sum_q = sum_q + q

    #when both is running at sametime... count withdraw..? or signaling each other..?
    #if abs(sum_q - f_q) > 0.00000001:
        #log(f"[bn_get_fut_pending_amt]:open orders q mismatch(open orders sum q:{sum_q}, f short q:{f_q})")
    
    return gain

def bn_is_backward(bnSpot1st, bnFut1st)->bool: #type hint float array
    return bnFut1st[BID][0] + 0.002 < bnSpot1st[ASK][0] #2tick

def bn_get_precision_pq(asset: str):
    if asset == 'EOS': return 3, 1 #p, q
    else: raise Exception(f'[bn_get_precision_p] not supported asset={asset}')
