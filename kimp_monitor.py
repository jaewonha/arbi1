#import pyupbit
from requests.exceptions import ConnectionError, ReadTimeout

import json
import pprint

from datetime import datetime
import time

import signal
import sys
from classes import *
from util.log import *
from arbi import *

ex = Exchanges()

date = datetime.now().strftime("%Y%m%d_%H%M%S")

lastMin = None
delay = 1

while True:
    now = datetime.now()
    if now.minute != lastMin:
        ex.updateCurrency()
        lastMin = now.minute
        print(f"update krwPerUsd:{ex.krwPerUsd} at min:{lastMin}")
        log_flush()

    ub_pair = ub_krw_pair(asset)
    bn_pair = bn_usdt_pair(asset)
    
    #get price
    IN = 0
    OUT = 1
    ub_p_krw = [0.0,0.0]
    ub_p_usd = [0.0,0.0]
    bn_p_usd = [0.0,0.0]
    bn_p_krw = [0.0,0.0]
    kimp     = [0.0,0.0]

    if True: #strict
        try:
            bn_p_usd[IN], _  = bn_spot_1st_ask(ex, asset) #market 
            ub_p_krw[IN], _  = ub_spot_1st_bid(asset)          #market
            ub_p_krw[OUT], _ = ub_spot_1st_ask(asset)          #market
            bn_p_usd[OUT], _ = bn_spot_1st_bid(ex, asset) #market 
        except ReadTimeout as rt:
            print('[read_market_price] read time out.. retry')
            time.sleep(delay)
        except Exception as e:
            print('[read_market_price] error.. retry:' + str(e))
            time.sleep(delay)
    else: #use native api
        ub_p_krw[IN] = ub_p_krw[OUT] = ex.pyupbit.get_current_price(ub_pair)
        bn_p_usd[IN] = bn_p_usd[OUT] = ex.binance.get_symbol_ticker(symbol=bn_pair)["price"]
    
    #conv currency
    ub_p_usd[IN]  = round(ub_p_krw[IN]  / ex.krwPerUsd, 4)
    bn_p_krw[IN]  = round(bn_p_usd[IN]  * ex.krwPerUsd, 4)
    ub_p_usd[OUT] = round(ub_p_krw[OUT] / ex.krwPerUsd, 4)
    bn_p_krw[OUT] = round(bn_p_usd[OUT] * ex.krwPerUsd, 4)

    #print
    #print(f"[UB]KRW={ub_p_krw}, USD={ub_p_usd}")
    #print(f"[BN]KRW={bn_p_krw}, USD={bn_p_usd}")
    kimp[IN]  = round( (ub_p_usd[IN]/bn_p_usd[IN]-1)*100,2)
    kimp[OUT] = round( (ub_p_usd[OUT]/bn_p_usd[OUT]-1)*100,2)
    print(f"KIMP[IN] :{kimp[IN] }% (UB={ub_p_usd[IN] }, BN={bn_p_usd[IN] })")
    print(f"KIMP[OUT]:{kimp[OUT]}% (UB={ub_p_usd[OUT]}, BN={bn_p_usd[OUT]}), KIMPDiff:{round(kimp[IN]-kimp[OUT], 2)}%")
    
    time.sleep(delay)


