#https://github.com/sharebook-kr/pyupbit

import pyupbit
from pyupbit import WebSocketManager
import pprint

access = "p2uhQ8xdqxhEvslccOPkwzreXiuTWysaNTcYigWq"          # 본인 값으로 변경
secret = "k55DdoFw2sPRSYGMzB4IzwNna7ywPHYj1562QykN"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

#print(pyupbit.get_tickers())

#print(pyupbit.get_tickers(fiat="KRW"))

pair="KRW-EOS"

#print(pyupbit.get_current_price(pair))

#df = pyupbit.get_ohlcv(pair, count=14)
#print(df.tail())

_ob = pyupbit.get_orderbook(tickers=pair)[0]
assert _ob['market'] == pair
#pprint.pprint(ob)

ob = _ob['orderbook_units'][0]
print(ob)

print(upbit.get_balance("KRW"))

print("=== balance ===")
eos_q = upbit.get_balance(pair)
t_p = ob['bid_price']
av_q = ob['bid_size']
print(f"[sell] eos_q:{eos_q}, t_p:{t_p}")

if eos_q > av_q:
    print(f"av_q is *not* enough (sell_q:{eos_q}>av_q:{av_q})")
else:
    #print(f"av_q is enough (sell_q:{eos_q}>av_q:{av_q})")
    pass

#order = upbit.sell_limit_order(pair, eos_q, t_p)
#print(order)


# not working
# if __name__ == "__main__":
#     wm = WebSocketManager("ticker", [pair])
#     for i in range(10):
#         data = wm.get()
#         print(data)
#     wm.terminate()
