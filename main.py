#import pyupbit
from requests.exceptions import ConnectionError, ReadTimeout

import json
import pprint

import datetime
import time

import signal
import sys

from common import *
from classes import *
from util.log import *
from arbi import *

#config
# status = 'UB'
# OUT_TH = 2.0
# IN_TH = 3.5
status = 'BN'
#status = 'UB' 
OUT_TH = 1.25
IN_TH = 2.75
IN_TRF_R = 0.9
#maxUSD = 50
maxUSD = 1000
asset = "EOS" #target asset to trade arbi
print(f"config: assets={asset}, OUT_TH={OUT_TH}, IN_TH={IN_TH}")
ORDER_TEST = False
ARBI_SEQ_TEST = False

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    print('closing file')
    log_close()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def get_asset_total(ex):
   ub_usd = ub_get_spot_balance(ex, 'KRW') / ex.krwPerUsd
   bn_usd = bn_get_spot_balance(ex, 'USDT')
   total_usd = ub_usd + bn_usd
   return [round(ub_usd,2), round(bn_usd,2), round(total_usd,2)]

def print_arbi_stat(before, after, th, maxUSD, krwPerUsd):
    assetGain = round( (after[2]/before[2]-1)*100, 2 )

    diff = round(after[2] - before[2],2)
    actualKimp = round((diff/maxUSD)*100, 2)
    kimpGain = round(actualKimp-th, 2)

    log(f"[total_asset]ub/bn: [{before[0]} + {before[1]} = {before[2]}] -> ({after[0]} + {after[1]} = {after[2]}), diff={diff}$, a_kimp={actualKimp}%, kimpGain={kimpGain}%, maxUSD={maxUSD}$, assetGain={assetGain}%, krwPerUsd={krwPerUsd}")
    log_flush()

ex = Exchanges()

date = datetime.now().strftime("%Y%m%d_%H%M%S")
#f = open(f"kimp{date}.txt", "a")
log_open("log.txt")
log(date)

if ORDER_TEST:
    print('test order')
else:
    msg = input('execute real order? type "go" to do that >> ')
    if msg == 'go':
        print('go real trading')
    else:
        print('not go')
        exit(0)

lastMin = None
cnt = 0
delay = 2
SKIP_STATUS_CHECK = True

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
    
    if (SKIP_STATUS_CHECK or status=='BN') and (kimp[IN]>(IN_TH*IN_TRF_R) or ARBI_SEQ_TEST):
        log(f"time to get-in(BN->UB)! kimp={kimp[IN]} (UB={ub_p_usd[IN]}, BN={bn_p_usd[IN]}) @{now}")
        asset_before = get_asset_total(ex)
        if arbi_in_bn_to_ub(ex, asset, bn_p_usd[IN], maxUSD, IN_TH, ORDER_TEST):
            cnt = cnt + 1
            status = 'UB'
            asset_after = get_asset_total(ex)
            print_arbi_stat(asset_before, asset_after, +IN_TH, maxUSD, ex.krwPerUsd)

    elif (SKIP_STATUS_CHECK or status=='UB') and (kimp[OUT]<OUT_TH or ARBI_SEQ_TEST):
        log(f"time to flight(UB->BN)! kimp={kimp[OUT]} (UB={ub_p_usd[OUT]}, BN={bn_p_usd[OUT]}) @{now}")
        asset_before = get_asset_total(ex)
        if arbi_out_ub_to_bn(ex, asset, ub_p_krw[OUT], bn_p_usd[OUT], maxUSD, ORDER_TEST):
            cnt = cnt + 1
            status = 'BN'
            asset_after = get_asset_total(ex)
            print_arbi_stat(asset_before, asset_after, -OUT_TH, maxUSD, ex.krwPerUsd)
    
    if cnt > 5:
        exit(0)
    time.sleep(delay)


