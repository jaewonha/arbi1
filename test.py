from arbi import *
from util.log import *
from common import *

ORDER_TEST = False
maxUSD = 20

ex = Exchanges()
#krwPerUsd = float(krw_per_usd()) #fixme: error handling for float version fail

asset = 'EOS'

IN = 0
OUT = 1

ub_p_krw = [0,0]
ub_p_usd = [0,0]
bn_p_usd = [0,0]
bn_p_krw = [0,0]

bn_p_usd[IN], _  = bn_spot_1st_ask(ex, asset) #market 
ub_p_krw[IN], _  = ub_spot_1st_bid(asset)          #market
ub_p_krw[OUT], _ = ub_spot_1st_ask(asset)          #market
bn_p_usd[OUT], _ = bn_spot_1st_bid(ex, asset) #market 

OUT_TH = 100.0 #숫자가 작을때 (손해) 나가려고 하니 큰 숫자를 쓰면 무조건 나감
IN_TH = 0.0 #숫자가 클떄 들어오(이득)려고 하니 작은 숫자를 쓰면 무조건 들어옴

print("test in")
arbi_in_bn_to_ub(ex, asset, bn_p_usd[IN], maxUSD, IN_TH, ORDER_TEST)
print("test out")
arbi_out_ub_to_bn(ex, asset, ub_p_krw[OUT], bn_p_usd[OUT], maxUSD, ORDER_TEST)
print("done")