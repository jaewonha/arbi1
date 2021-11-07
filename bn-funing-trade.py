import pprint
import time
import traceback
from exchange import *
from arbi import *
from util.log import *

import datetime
import sched
import time as time_module


ex = Exchanges()
asset = 'OMG'

t_q = 10
TEST = False

def timed_task():
    t1 = datetime.datetime.now()
    print(t1)

    print('Long 1x')
    bn_fut_trade_market(ex, asset, TRADE_BUY, t_q, TEST)

    while True: #wait next seconds
        t2 = datetime.datetime.now()
        if int(t1.second) != int(t2.second):
            break

    print(t2)
    print('Short 2x') #clear long and short 1x
    order = bn_fut_trade_market(ex, asset, TRADE_SELL, t_q*2, TEST)
    order = bn_wait_order(ex, order, BN_FUT, TEST)

    for cnt in range(1, 60):
        lastPrice = float(order['avgPrice'])
        curPrice = bn_fut_depth(ex, asset, 0)[ASK][P]

        gain = -(curPrice/lastPrice-1)*100 #short
        priceReached = gain > 0.45
        print(f'[{cnt}] gain:{gain} priceReached:{priceReached}')
        if priceReached or cnt > 59:
            break
        time.sleep(1)

    t3 = datetime.datetime.now()
    print('Long 1x')
    bn_fut_trade_market(ex, asset, TRADE_BUY, t_q, TEST)
    print(t3)


scheduler = sched.scheduler(time_module.time, time_module.sleep)
#t = time_module.strptime('2021-11-07 23:47:59', '%Y-%m-%d %H:%M:%S')
t = time_module.strptime('2021-11-08 12:59:59', '%Y-%m-%d %H:%M:%S')
t = time_module.mktime(t)
scheduler_e = scheduler.enterabs(t, 1, timed_task, ())
scheduler.run()


#bn_spot_trade_market(ex, asset, TRADE_BUY, t_q, TEST)
#bn_spot_trade_market(ex, asset, TRADE_SELL, t_q, TEST)

#bn_fut_trade_market(ex, asset, TRADE_BUY, t_q, TEST)
#bn_fut_trade_market(ex, asset, TRADE_SELL, t_q, TEST)