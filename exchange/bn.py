
from datetime import datetime, date, timedelta
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.exceptions import BinanceAPIException, BinanceOrderException
#from binance import Client, AsyncClient, DepthCacheManager, BinanceSocketManager
import time
import math

#const
TRADE_BUY = 6010
TRADE_SELL = 6011

FUT_SHORT = 7010
FUT_LONG  = 7011

#func
def bn_get_spot_balance(client, asset, doRound = True):
    #print('### spot balance ###')
    balance = client.get_asset_balance(asset=asset)
    assert ( balance['asset'] == 'EOS' or balance['asset'] == 'USDT' or balance['asset'] == 'BNB')
    if doRound:
        s_q = math.floor(float(balance['free'])*10)/10 #2자리 미만 안쓰임
    else:
        s_q = float(balance['free'])
    #print(f"eos: q={s_q}")
    return s_q

def bn_wait_balance(client, asset, t_q):
    time.sleep(3)
    while True:
        q = bn_get_spot_balance(client, asset)
        print(f"[bn_wait_balance]{asset}:{q} < {t_q}")
        if q >= t_q:
            break
        time.sleep(1)
        
def bn_get_fut_balance(client, asset, _type):
    assert asset == 'EOS'
    EOS_IDX = 67 #fixme: NO IDX or ADD XRP or ETC
    #print('### futures balance ###')
    acc = client.futures_account()
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

def bn_usdt_pair(asset):
    return asset + 'USDT'

def bn_spot_1st_bid(client, pair): #highest buying bids
    depth = client.get_order_book(symbol=pair)
    t_p = round(float(depth['bids'][0][0]), 4)
    av_q = float(depth['bids'][0][1])
    return t_p, av_q

def bn_spot_1st_ask(client, pair): #lowest selling price
    depth = client.get_order_book(symbol=pair)
    t_p = round(float(depth['asks'][0][0]), 4)
    av_q = float(depth['asks'][0][1])
    return t_p, av_q

def bn_fut_1st_bid(client, pair):
    depth = client.futures_order_book(symbol=pair)
    t_p = round(float(depth['bids'][0][0]), 4)
    av_q = float(depth['bids'][0][1])
    return t_p, av_q

def bn_fut_1st_ask(client, pair):
    depth = client.futures_order_book(symbol=pair)
    t_p = round(float(depth['asks'][0][0]), 4)
    av_q = float(depth['asks'][0][1])
    return t_p, av_q

def bn_get_trade_type(tradeMode):
    if tradeMode == TRADE_BUY:
        return Client.SIDE_BUY
    if tradeMode == TRADE_SELL:
        return Client.SIDE_SELL
    print(f"bn_get_trade_type:invalide mode={tradeMode}")
    exit(0)
        

def bn_spot_trade(client, pair, tradeMode, t_p, t_q, TEST = True):
    tradeType = bn_get_trade_type(tradeMode)
    print(f"[bn_spot_{tradeType}]{pair} {t_q}q @ {t_p}$, TEST={TEST}")
    if TEST:
        return client.create_test_order(
            symbol=pair,
            side=tradeType,
            type=Client.ORDER_TYPE_LIMIT,
            timeInForce='GTC',
            price=t_p,
            quantity=t_q)
    else:
        return client.create_order(
            symbol=pair,
            side=tradeType,
            type=Client.ORDER_TYPE_LIMIT,
            timeInForce='GTC',
            price=t_p,
            quantity=t_q)

def bn_fut_trade(client, pair, tradeMode, t_p, t_q, TEST = True):
    tradeType = bn_get_trade_type(tradeMode)
    print(f"[bn_fut_{tradeType}]{pair} {t_q}q @ {t_p}$, TEST={TEST}")
    if TEST:
        return client.create_test_order(
            symbol=pair,
            side=tradeType,
            type=Client.ORDER_TYPE_LIMIT,
            timeInForce='GTC',
            price=t_p,
            quantity=t_q)
    else:
        return client.futures_create_order(
            symbol=pair,
            side=tradeType,
            type=Client.ORDER_TYPE_LIMIT,
            timeInForce='GTC',
            price=t_p,
            quantity=t_q)

def bn_wait_order(client, pair, order, TEST):
    if TEST:
        return

    print(order)
    while True:
        result = client.get_order(symbol=pair,orderId=order['orderId'])
        state = result['status']
        print(f"order_state:{state}")

        if state == 'FILLED':
            return True
        elif state == 'CANCELED':
            raise Exception('bn_wait_order:order canceled')
        #fixme: rest of error case check
        
        time.sleep(1)

def bn_get_deposit(client, asset, txid):
    result = client.get_deposit_history(coin=asset)
    filtered = list(filter(lambda x: x['txId'] == txid, result))
    return filtered

def bn_wait_deposit(client, asset, txid):
    cnt = 0
    while True:
        ret = bn_get_deposit(client, asset, txid)
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

def bn_withdraw(client, asset, addr, tag, t_q):
    withdraw = client.withdraw(
        coin=asset,
        address=addr,
        addressTag=tag, #or TAG
        amount=t_q)    
    return withdraw['id']

def bn_wait_withdraw(client, withdraw_id):
    time.sleep(10)
    cnt = 10
    txid = None
    while True:
        try:
            withdraw_result = client.get_withdraw_history_id(withdraw_id)
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

def bn_wait_order(binance, pair, orderId):
    cnt = 0
    while True:
        order = binance.get_order(symbol=pair,orderId=orderId)
        state = order['status']
        print(f"({cnt})bn_wait_order: state={state}")
        if state =='FILLED': #PARTIALLY_FILLED CANCELED REJECTED EXPIRED NEW
            break
        time.sleep(1)
        cnt = cnt + 1

def bn_wait_fut_order(binance, pair, orderId):
    cnt = 0
    while True:
        order = binance.futures_get_order(symbol=pair,orderId=orderId)
        state = order['status']
        print(f"({cnt})bn_wait_fut_order: state={state}")
        if state =='FILLED': #PARTIALLY_FILLED CANCELED REJECTED EXPIRED NEW
            break
        time.sleep(1)
        cnt = cnt + 1