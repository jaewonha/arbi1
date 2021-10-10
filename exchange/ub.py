import pyupbit
import time
import pprint
import itertools
from classes.Exchanges import Exchanges
from util.log import log
from classes import *

#const
TRADE_BUY = 6010
TRADE_SELL = 6011

FUT_SHORT = 7010
FUT_LONG  = 7011

#func
def ub_get_spot_balance(ex: Exchanges, asset: str):
    return float(ex.pyupbit.get_balance(asset))

def ub_wait_balance(ex: Exchanges, asset: str, t_q: float):
    while True:
        q = ub_get_spot_balance(ex, asset)
        if not (q < t_q):
            break
        print(f"[ub_wait_balance]{asset} < {t_q}")
        time.sleep(1)

def ub_krw_pair(asset: str):
    return 'KRW-' + asset

def ub_spot_1st(ex: Exchanges, asset: str): #highest buying bids
    orderMeta = pyupbit.get_orderbook(tickers=ub_krw_pair(asset))[0]
    orderBook = orderMeta['orderbook_units']
    od_1st = orderBook[0]
    a_t_p = od_1st['ask_price']
    a_av_q = od_1st['ask_size']
    b_t_p = od_1st['bid_price']
    b_av_q = od_1st['bid_size']
    return [[a_t_p, a_av_q],[b_t_p, b_av_q]]

def ub_spot_1st_bid(ex: Exchanges, asset: str): #highest buying bids
    orderMeta = pyupbit.get_orderbook(tickers=ub_krw_pair(asset))[0]
    orderBook = orderMeta['orderbook_units']
    od_1st = orderBook[0]
    t_p = od_1st['bid_price']
    av_q = od_1st['bid_size']
    return t_p, av_q

def ub_spot_1st_ask(ex: Exchanges, asset: str): #lowest selling price
    orderMeta = pyupbit.get_orderbook(tickers=ub_krw_pair(asset))[0]
    orderBook = orderMeta['orderbook_units']
    od_1st = orderBook[0]
    t_p = od_1st['ask_price']
    av_q = od_1st['ask_size']
    return t_p, av_q

def ub_get_trade_type(tradeMode: int):
    if tradeMode == TRADE_BUY:
        return 'buy'
    if tradeMode == TRADE_SELL:
        return 'sell'
    print(f"ub_get_trade_type:invalide mode={tradeMode}")
    exit(0)

def ub_spot_trade(ex: Exchanges, asset: str, tradeMode: int, t_p: float, t_q: float, TEST: bool):
    pair = ub_krw_pair(asset)
    log(f"[ub_spot_{ub_get_trade_type(tradeMode)}]{pair} {t_q}q @ {t_p}W({round(t_p/ex.krwPerUsd,4)}$), TEST={TEST}")
    if TEST:
        return

    if tradeMode == TRADE_BUY:
        return ex.pyupbit.buy_limit_order(ticker=pair, price=t_p, volume=t_q) #price volue 반대로 들어갔엇음!!!!!
    elif tradeMode == TRADE_SELL:
        return ex.pyupbit.sell_limit_order(ticker=pair, price=t_p, volume=t_q)
    else:
        print(f"ub_get_trade_type:invalide mode={tradeMode}")
        exit(0)

def ub_withdraw(ex: Exchanges, asset: str, t_q: float, addr: str, tag: str):
    print(f"ub_withdraw:{asset} {t_q}q to {addr} with {tag}")
    try:
        result = ex.upbitClient.Withdraw.Withdraw_coin(
            currency=asset,
            amount=str(t_q),
            address=addr,
            secondary_address=tag)['result']
        #Exception has occurred: KeyError
        #result['error']['message']
        uuid = result['uuid']
        #txid = result['txid'] #not avail
        #print(resp['result'])
        return uuid
    except Exception as e:
        msg = result['error']['message']
        raise Exception(msg)

def ub_wait_withdraw(ex: Exchanges, uuid: str):
    time.sleep(10)
    cnt = 10
    while True:
        result = ex.upbitClient.Withdraw.Withdraw_info(uuid=uuid)['result']
        #pprint.pprint(result)
        state = result['state']
        txid = result['txid']
        #print(txid)
        print(f"({cnt})ub_wait_withdraw: state={state}")
        if state == 'DONE':
            return txid
        time.sleep(3)
        cnt = cnt + 3

def ub_wait_deposit(ex: Exchanges, txid: str):
    cnt = 0
    while True:
        #state = ub_raw_get_deposit(ub_acc_key, ub_sec_key, txid, asset)[0]['state']
        #print('ub_raw_get_deposit:state:' + state)
        result = ex.upbitClient.Deposit.Deposit_info(
            #uuid='35a4f1dc-1db5-4d6b-89b5-7ec137875956'
            txid=txid
        )['result']
        state = result['state']
        print(f"({cnt})ub_wait_deposit: state={state}")
        if state =='ACCEPTED' or state == 'DONE':
            break
        time.sleep(3)
        cnt = cnt + 3

def ub_safe_order(ex: Exchanges, order: dict, key: str)->str:
    while True:
        try:
            uuid = order['uuid']
            _order = ex.pyupbit.get_order(uuid)
            return _order[key]
        except Exception as e:
                # key error 주문을 찾을 수 없습니다 -> 좀 있으면 들어옴
                print("error", order)
        time.sleep(1)

def ub_wait_order(ex: Exchanges, order: dict, TEST: bool)->None:
    if TEST: return

    for i in itertools.count():
        state = ub_safe_order(ex, order, 'state')
        print(f"[ub_wait_order]({i}) state={state}")

        if state =='wait' or state =='watch':
            pass
        elif state =='cancel':
            raise Exception(f"ub_order cancled:order={order}")
        elif state =='done':
            break

        time.sleep(1)

def ub_get_pending_amt(ex: Exchanges, asset: str)->float:
    #todo:
    #query pending order by asset
    #amount t_q *t_p
    #ret
    return 0.0

'''
def ub_cancel_or_refund(client, order, TEST):
    for i in itertools.count():
        state = ub_safe_order(client, order, 'state')
        log(f"[ub_cancel_or_refund]({i}) state={state}")

        if state =='wait' or state =='watch':
            ret = upbit.cancel_order(order['uuid'])
            log(f"[ub_cancel_or_refund]({i}) cancel:{ret}")
            #re-iter -> check state changed to 'canceled'
        elif state =='cancel':
            log(f"[ub_cancel_or_refund]({i}) canceled")
            r_q = float(order['remaining_volume'])
            if r_q > 0:
                ub_pair = order['market']
                side = order['side']
                t_p = float(order['price'])
                vol = float(order['volume'])
                t_q = vol - q if side=='bid' else r_q
                mode = TRADE_SELL if side =='bid' else TRADE_BUY
                #.... too complex
                
                
                log(f"[ub_cancel_or_refund]({i}) sell remain t_p:{t_p}, r_q:{r_q}")
                ub_order = ub_spot_trade(ex, asset, TRADE_SELL, t_p, r_q, TEST);
                ub_wait_order(client, ub_order, TEST)
                log(f"remain sell done")
            break
        elif state =='done':
            if order['side']=='bid': #bought
                ub_pair = order['market']
                t_p = float(order['price'])
                t_q = float(order['volume']) - float(order['remaining_volume'])
                log(f"[ub_cancel_or_refund]({i}) refund t_p:{t_p}, t_q:{t_q}")
                ub_order = ub_spot_trade(ex, asset, TRADE_SELL, t_p, t_q, TEST);
                ub_wait_order(client, ub_order, TEST)
                log(f"refund done")
            break

        time.sleep(1)
'''