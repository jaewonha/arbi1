import signal
import sys

import numpy as np
import time
from datetime import datetime
from requests.exceptions import ConnectionError, ReadTimeout

from classes import *
from util.log import *
from arbi import *

IN = 0
OUT = 1

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    print('closing file')
    log_close()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def get_asset_total(ex: Exchanges, asset: str):
   ub_usd = ub_get_spot_balance(ex, 'KRW') / ex.krwPerUsd
   ub_pending = ub_get_pending_amt(ex, asset) / ex.krwPerUsd

   bn_usd = bn_get_spot_balance(ex, 'USDT')
   bn_pending = bn_get_pending_amt(ex, asset)

   bn_fut_usd = bn_fut_acc_asset_balance(ex, 'USDT')
   bn_fut_pending = bn_get_fut_pending_amt(ex, asset)

   pending = ub_pending + bn_pending + bn_fut_pending
   return [round(ub_usd,2), round(bn_usd,2), round(bn_fut_usd,2), round(pending,2)]

def print_arbi_stat(before, after, th, maxUSD, krwPerUsd):
    if before is None: before = after

    sum = [np.sum(before), np.sum(after)]
    assetGain = round((sum[1]/sum[0]-1)*100, 2)
    diff = round(sum[1]-sum[0], 2)

    actualKimp = round((diff/maxUSD)*100, 2)
    kimpGain = round(actualKimp-th, 2)

    if before:
        log(f"[total_asset]ub/bn:"
            f"[{before[0]} + ({before[1]} + |{before[2]} + {before[3]}|) = {sum[0]}] -> "
            f"[{after[0]} + ({after[1]} + |{after[2]} + {after[3]}|) = {sum[1]}]")
    else:
        assetGain = -999.0

    log(f"\tdiff={diff}$, a_kimp={actualKimp}%, kimpGain={kimpGain}%, "
        f"maxUSD={maxUSD}$, assetGain={assetGain}%, krwPerUsd={krwPerUsd}")
    log_flush()


def calc_kimp(ex: Exchanges, asset: str, maxUSD: float = 1000000000, CHECK_BACKWARD = True):
    ub_p_krw = [0.0,0.0]
    ub_p_usd = [0.0,0.0]
    bn_p_usd = [0.0,0.0]
    #bn_p_krw = [0.0,0.0]
    bn_f_usd = [0.0,0.0]
    kimp     = [0.0,0.0]

    while True:
        try:
            bnFut1st  = bn_fut_1st(ex, asset)
            bnSpot1st = bn_spot_1st(ex, asset)
            ubSpot1st = ub_spot_1st(ex, asset) #ask=0, bid=1
            #선물이 백워데이션이면 안정될때까지 기다림
            if bn_is_backward(bnSpot1st, bnFut1st) and CHECK_BACKWARD:
                print(f"[calc_kimp]Bn Fut BackWard futBid={bnFut1st[BID][0]} > spotAsk={bnSpot1st[ASK][0]} failed")
                time.sleep(1)
                continue
            #들어올 때(toUB)
            bn_p_usd[IN]  = bnSpot1st[ASK][0]   #바이낸스의 Spot을 Buy
            ub_p_krw[IN]  = ubSpot1st[BID][0]   #업비트의 Spot에 판다
            bn_f_usd[IN]  = bnFut1st[BID][0]    #Bn Spot Sell
            #나갈 때(toBN)
            ub_p_krw[OUT] = ubSpot1st[ASK][0]   #업비트에서 Spot Buy.
            bn_p_usd[OUT] = bnSpot1st[BID][0]   #바이낸스에서 Spot Sell
            bn_f_usd[OUT] = bnFut1st[BID][0]    #Bn Spot Sell
            break;
        except ReadTimeout as rt:
            print('[read_market_price] read time out.. retry')
            time.sleep(1)
       

    #conv currency
    ub_p_usd[IN]  = round(ub_p_krw[IN]  / ex.krwPerUsd, 6)
    #bn_p_krw[IN]  = round(bn_p_usd[IN]  * ex.krwPerUsd, 6)
    ub_p_usd[OUT] = round(ub_p_krw[OUT] / ex.krwPerUsd, 6)
    #bn_p_krw[OUT] = round(bn_p_usd[OUT] * ex.krwPerUsd, 6)

    #print
    #print(f"[UB]KRW={ub_p_krw}, USD={ub_p_usd}")
    #print(f"[BN]KRW={bn_p_krw}, USD={bn_p_usd}")
    kimp[IN]  = round( (ub_p_usd[IN]/bn_p_usd[IN]-1)*100, 2)
    kimp[OUT] = round( (ub_p_usd[OUT]/bn_p_usd[OUT]-1)*100, 2)

    return ub_p_krw, bn_p_usd, bn_f_usd, kimp 

def toUsd(ex: Exchanges, krw: float):
    return round(krw/ex.krwPerUsd,6)

def log_asset_total(ex: Exchanges, asset: str):
    asset_total = get_asset_total(ex, asset) #opt. before calc KIMP
    log(
        f"[{datetime.now().strftime('%Y%m%d_%H%M%S')}]"
        f"balance:{asset_total}=>{round(np.sum(asset_total),2)}"
    )

def main():
    #config
    #status = 'UB'
    f = open('.config.ini','r')
    config = json.load(f)['main']

    print(config)
    status          = config['status']
    STATUS_CHANGE   = config['STATUS_CHANGE'] #only in or only out mode
    STATUS_SKIP     = config['STATUS_SKIP']
    IN_TH           = config['IN_TH'] #4.25  #high - in
    OUT_TH          = config['OUT_TH'] #2.6  #low - out
    IN_TH_INC       = config['IN_TH_INC']
    OUT_TH_DEC      = config['OUT_TH_DEC']
    maxUSD          = config['maxUSD'] 
    maxUSDInF       = config['maxUSDInF'] 
    maxUSDOutF      = config['maxUSDOutF'] 
    asset           = config['asset'] #"EOS" #target asset to trade arbi
    IN_TRF_R        = config['IN_TRF_R'] #0.9
    ORDER_TEST      = config['ORDER_TEST'] #False

    ex = Exchanges()
    
    log_open('log.txt')
    log(f"date:{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    log(f"config: asset={asset}, status={status} STATUS_CHANGE={STATUS_CHANGE} OUT_TH={OUT_TH}, IN_TH={IN_TH}, maxUSD={maxUSD}")
    
    if ORDER_TEST:
        print('test order')
    else:
        msg = input('execute real order? type "go" to do that >> ')
        if msg == 'go':
            print('go real trading')
        else:
            print('not go')
            exit(0)

    cnt = 0
    delay = 1
    lastMin = None
    
    log_asset_total(ex, asset)
    while True:
        now = datetime.now()
        if now.minute != lastMin:
            ex.updateCurrency()
            lastMin = now.minute
            print(f"update krwPerUsd:{ex.krwPerUsd} at min:{lastMin}")
            log_flush()

        #asset_before = None #asset_before = get_asset_total(ex, asset) #opt. before calc KIMP
        arbi_check_balace(ex, asset, maxUSD) #opt
        ub_p_krw, bn_p_usd, bn_f_usd, kimp = calc_kimp(ex, asset)

        print(f"KIMP[IN] :{kimp[IN]}% (UB={toUsd(ex, ub_p_krw[IN])}, BN={bn_p_usd[IN] })")
        print(f"KIMP[OUT]:{kimp[OUT]}% (UB={toUsd(ex, ub_p_krw[OUT])}, BN={bn_p_usd[OUT]}), KIMPDiff:{round(kimp[IN]-kimp[OUT], 2)}%")
    
        if (STATUS_SKIP or status=='BN') and kimp[IN]>(IN_TH*IN_TRF_R):
            log(f"<<< time to get-in(BN->UB)! kimp={kimp[IN]} (UB={toUsd(ex, ub_p_krw[IN])}, BN={bn_p_usd[IN]}) maxUSD={maxUSD*maxUSDInF} @ {now}")
            #asset_before = get_asset_total(ex, asset) 
            #log(f"(temp)asset_before:{asset_before}")
            if arbi_in_bn_to_ub(ex, asset, bn_p_usd[IN], bn_f_usd[IN], maxUSD*maxUSDInF, IN_TH, ORDER_TEST, True):
                cnt = cnt + 1
                if STATUS_CHANGE: status = 'UB'
                #asset_after = get_asset_total(ex, asset)
                #print_arbi_stat(asset_before, asset_after, +IN_TH, maxUSD*maxUSDInF, ex.krwPerUsd)
                log_asset_total(ex, asset)
                IN_TH = IN_TH + IN_TH_INC

        elif (STATUS_SKIP or status=='UB') and kimp[OUT]<OUT_TH:
            #maxUSD = 650
            log(f">>> time to flight(UB->BN)! kimp={kimp[OUT]} (UB={toUsd(ex, ub_p_krw[OUT])}, BN={bn_p_usd[OUT]}) maxUSD={maxUSD*maxUSDOutF} @{now}")
            #asset_before = get_asset_total(ex, asset)
            #log(f"(temp)asset_before:{asset_before}")
            if arbi_out_ub_to_bn(ex, asset, ub_p_krw[OUT], bn_f_usd[OUT], maxUSD*maxUSDOutF, ORDER_TEST, True):
                cnt = cnt + 1
                if STATUS_CHANGE: status = 'BN'
                #asset_after = get_asset_total(ex, asset)
                #print_arbi_stat(asset_before, asset_after, -OUT_TH, maxUSD*maxUSDOutF, ex.krwPerUsd)
                log_asset_total(ex, asset)
                OUT_TH = OUT_TH + OUT_TH_DEC

        if cnt > 5:
            print(f"cnt{cnt} exit")
            exit(0)
        time.sleep(delay)


if __name__ == "__main__":
    main()
