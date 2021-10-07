import pyupbit
import time
import pprint
import itertools
from util.log import log

#const
TRADE_BUY = 6010
TRADE_SELL = 6011

FUT_SHORT = 7010
FUT_LONG  = 7011


#func
def ub_get_spot_balance(client, asset):
    return float(client.get_balance(asset))

def ub_wait_balance(client, asset, t_q):
    while True:
        q = ub_get_spot_balance(client, asset)
        if not (q < t_q):
            break
        print(f"[ub_wait_balance]{asset} < {t_q}")
        time.sleep(1)

def ub_krw_pair(asset):
    return 'KRW-' + asset

def ub_spot_1st_bid(pair): #highest buying bids
    orderMeta = pyupbit.get_orderbook(tickers=pair)[0]
    orderBook = orderMeta['orderbook_units']
    od_1st = orderBook[0]
    t_p = od_1st['bid_price']
    av_q = od_1st['bid_size']
    return t_p, av_q

def ub_spot_1st_ask(pair): #lowest selling price
    orderMeta = pyupbit.get_orderbook(tickers=pair)[0]
    orderBook = orderMeta['orderbook_units']
    od_1st = orderBook[0]
    t_p = od_1st['ask_price']
    av_q = od_1st['ask_size']
    return t_p, av_q


def ub_get_trade_type(tradeMode):
    if tradeMode == TRADE_BUY:
        return 'buy'
    if tradeMode == TRADE_SELL:
        return 'sell'
    print(f"ub_get_trade_type:invalide mode={tradeMode}")
    exit(0)

def ub_spot_trade(client, pair, tradeMode, t_p, t_q, krwPerUSD, TEST):
    log(f"[ub_spot_{ub_get_trade_type(tradeMode)}]{pair} {t_q}q @ {t_p}W({round(t_p/krwPerUSD,4)}$), TEST={TEST}")
    if TEST:
        return

    if tradeMode == TRADE_BUY:
        return client.buy_limit_order(ticker=pair, price=t_p, volume=t_q) #price volue 반대로 들어갔엇음!!!!!
    elif tradeMode == TRADE_SELL:
        return client.sell_limit_order(ticker=pair, price=t_p, volume=t_q)
    else:
        print(f"ub_get_trade_type:invalide mode={tradeMode}")
        exit(0)

def ub_withdraw(client2, asset, t_q, addr, tag):
    print(f"ub_withdraw:{asset} {t_q}q to {addr} with {tag}")
    try:
        result = client2.Withdraw.Withdraw_coin(
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

def ub_wait_withdraw(client2, uuid):
    time.sleep(10)
    cnt = 10
    while True:
        result = client2.Withdraw.Withdraw_info(uuid=uuid)['result']
        #pprint.pprint(result)
        state = result['state']
        txid = result['txid']
        #print(txid)
        print(f"({cnt})ub_wait_withdraw: state={state}")
        if state == 'DONE':
            return txid
        time.sleep(3)
        cnt = cnt + 3

def ub_wait_deposit(client2, txid):
    cnt = 0
    while True:
        #state = ub_raw_get_deposit(ub_acc_key, ub_sec_key, txid, asset)[0]['state']
        #print('ub_raw_get_deposit:state:' + state)
        result = client2.Deposit.Deposit_info(
            #uuid='35a4f1dc-1db5-4d6b-89b5-7ec137875956'
            txid=txid
        )['result']
        state = result['state']
        print(f"({cnt})ub_wait_deposit: state={state}")
        if state =='ACCEPTED' or state == 'DONE':
            break
        time.sleep(3)
        cnt = cnt + 3

def ub_safe_order(client, order, key):
    while True:
        try:
            uuid = order['uuid']
            _order = client.get_order(uuid)
            return _order[key]
        except Exception as e:
                # key error 주문을 찾을 수 없습니다 -> 좀 있으면 들어옴
                print("error", order)
        time.sleep(1)

def ub_wait_order(client, order, TEST):
    if TEST: return

    for i in itertools.count():
        state = ub_safe_order(client, order, 'state')
        print(f"[ub_wait_order]({i}) state={state}")

        if state =='wait' or state =='watch':
            pass
        elif state =='cancel':
            raise Exception(f"ub_order cancled:uuid={uuid}")     
        elif state =='done':
            break

        time.sleep(1)

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
                ub_order = ub_spot_trade(client, ub_pair, TRADE_SELL, t_p, r_q, krwPerUSD, TEST);
                ub_wait_order(client, ub_order)
                log(f"remain sell done")
            break
        elif state =='done':
            if order['side']=='bid': #bought
                ub_pair = order['market']
                t_p = float(order['price'])
                t_q = float(order['volume']) - float(order['remaining_volume'])
                log(f"[ub_cancel_or_refund]({i}) refund t_p:{t_p}, t_q:{t_q}")
                ub_order = ub_spot_trade(client, ub_pair, TRADE_SELL, t_p, t_q, krwPerUSD, TEST);
                ub_wait_order(client, ub_order)
                log(f"refund done")
            break

        time.sleep(1)