import pyupbit
#from pyupbit import WebSocketManager
import pprint
import time

from exchange import *

acc_key = "p2uhQ8xdqxhEvslccOPkwzreXiuTWysaNTcYigWq"          # 본인 값으로 변경
sec_key = "k55DdoFw2sPRSYGMzB4IzwNna7ywPHYj1562QykN"          # 본인 값으로 변경
upbit = pyupbit.Upbit(acc_key, sec_key)

asset = 'EOS'
ub_pair = ub_krw_pair(asset)

t_q = 10
TEST = False

try:
    t_p, av_q = ub_spot_1st_ask(upbit, ub_pair)
    order = ub_spot_trade(upbit, ub_pair, TRADE_BUY, t_p, t_q, TEST)

    ub_wait_order(upbit, order)
    time.sleep(3)

    t_p, av_q = ub_spot_1st_bid(upbit, ub_pair)
    order = ub_spot_trade(upbit, ub_pair, TRADE_SELL, t_p, t_q, TEST)

    ub_wait_order(upbit, order)
    print(order)
except Exception as e:
    print('error:', e)