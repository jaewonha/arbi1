import pyupbit
import time

#const
TRADE_BUY = 6010
TRADE_SELL = 6011

FUT_SHORT = 7010
FUT_LONG  = 7011


#func
def ub_get_spot_balance(client, asset):
    return client.get_balance(asset)

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

def ub_spot_trade(client, pair, tradeMode, t_p, t_q, TEST = True):
    print(f"[ub_spot_{ub_get_trade_type(tradeMode)}]{pair} {t_q}q @ {t_p}$, TEST={TEST}")
    if TEST:
        return

    if tradeMode == TRADE_BUY:
        return client.buy_limit_order(ticker=pair, price=t_p, volume=t_q) #price volue 반대로 들어갔엇음!!!!!
    elif tradeMode == TRADE_SELL:
        return client.sell_limit_order(ticker=pair, price=t_p, volume=t_q)
    else:
        print(f"ub_get_trade_type:invalide mode={tradeMode}")
        exit(0)
        
def ub_wait_order(client, order, TEST):
    if TEST:
        return
        
    print(order)
    while True:
        result = client.get_order(order['uuid'])
        state = result['state']
        print(f"order_state:{state}")

        if state == 'done':
            return True
        elif state == 'cancel':
            raise Exception('ub_wait_order:order canceled')
        #fixme: rest of error case check

        time.sleep(1)