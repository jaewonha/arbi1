import pprint
import time
import traceback
from exchange import *
from arbi import *
from util.log import *

ex = Exchanges()
asset = 'EOS'

t_q = 1
TEST = False
UB_TEST = True
BN_TEST = False

if UB_TEST:
    try:
        t_p, av_q = ub_spot_depth(ex, asset, 1)[ASK] #ask
        order = ub_spot_trade(ex, asset, TRADE_BUY, t_p, t_q, TEST)

        ub_wait_order(ex, order, TEST)
        print(ex.pyupbit.get_order(order['uuid']))
        time.sleep(3)

        t_p, av_q = ub_spot_depth(ex, asset, 1)[BID] #bid
        order = ub_spot_trade(ex, asset, TRADE_SELL, t_p, t_q, TEST)

        ub_wait_order(ex, order, TEST)
        print(ex.pyupbit.get_order(order['uuid']))
    except Exception as e:
        print('error:', e)

if BN_TEST:
    try:
        t_p, av_q = bn_spot_depth(ex, asset, 0)[BID] #ask
        order = bn_spot_trade(ex, asset, TRADE_BUY, t_p, t_q, TEST)

        bn_wait_order(ex, asset, order, TEST)
        time.sleep(3)

        t_p, av_q = bn_spot_depth(ex, asset, 0)[ASK] #bid
        order = bn_spot_trade(ex, asset, TRADE_SELL, t_p, t_q, TEST)

        bn_wait_order(ex, asset, order, TEST)
        print('done')
        print(order)
    except Exception as e:
        traceback.print_exc()