import pandas as pd
import matplotlib
#from pylab import get_current_fig_manager
import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import math
import datetime as dt

import pyupbit
import asyncio
import json
from datetime import datetime, date, timedelta
from binance import AsyncClient, DepthCacheManager, BinanceSocketManager


#from util import move_figure
from classes.ArbiRange import ArbiRange

def utc_to_str(utc_ts_bn, div1000=False):
    if div1000:
        ts = int(utc_ts_bn)/1000
    else:
        ts = int(utc_ts_bn)
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    
#load
# df_bn = pd.read_csv("./BN-EOSUSDT-180d.csv", index_col=0, parse_dates=True)
# df_ub = pd.read_csv("./UB-KRW-EOS-180d.csv", index_col=0, parse_dates=True).drop(['volume', 'value'], axis=1)
#df_bn = pd.read_csv("./BN-EOSUSDT-3d-1m-interpolated.csv", index_col=1, parse_dates=True)
#df_ub = pd.read_csv("./UB-KRW-EOS-3d-1m-interpolated.csv", index_col=1, parse_dates=True).drop(['volume', 'value'], axis=1)

#df_usd = pd.read_csv("./usd-3day-min_filled.csv", index_col=0, parse_dates=True)
#df_usd['date'] = pd.to_datetime(df_usd['date']); df_usd = df_usd.set_index('date')

day = 3
df_ub = pyupbit.get_ohlcv("KRW-EOS", count=24*60*day, interval="minute1")
# df = pyupbit.get_ohlcv("KRW-EOS", count=24*day, interval="minute60")
#df.to_csv('UB-KRW-EOS-'+str(day)+'d.csv')

 # initialise the client
#api_key = 'xc88zHqhZjLhTlYLlHRy2k30tKVVEV3oZq2GodtGP8gQloThM2R1KfMMED4goG3c'
#api_secret = 'xzZ8D5qiSXCIJgirSSbD9fLqVFkjcDIHgms17j1u1SwdklCEClSSjqbRk83ZRmO1'
#client = Client(api_key, api_secret)
client = await AsyncClient.create()
bn_pair = 'EOSUSDT'

days=3
#days=180
#yesterday = date.today() - timedelta(365*2-1) #2 years
yesterday = date.today() - timedelta(days)
unix_time= yesterday.strftime("%s")
#print(unix_time)
from_ts = unix_time

klines = []
async for ohlc in await client.get_historical_klines_generator(bn_pair, AsyncClient.KLINE_INTERVAL_1MINUTE, from_ts):
#async for ohlc in await client.get_historical_klines_generator(bn_pair, AsyncClient.KLINE_INTERVAL_1DAY, from_ts):
#async for ohlc in await client.get_historical_klines_generator(bn_pair, AsyncClient.KLINE_INTERVAL_1HOUR, from_ts):
    #print(f"{bn_utc_to_str(str(ohlc[0]))}:[{ohlc[1]},{ohlc[2]},{ohlc[3]},{ohlc[4]}]")
    klines.append( [utc_to_str(str(ohlc[0]), True), ohlc[1], ohlc[2], ohlc[3], ohlc[4]] )
df_bn = pd.DataFrame(klines, columns=['ts','o','h','l','c']).set_index('ts')
#print(df)
#df.to_csv('BN-'+symbol+'-'+str(days)+'d.csv')



arbiRanges = []
arbiRanges.append(ArbiRange(pd.datetime(2021, 7,  1), pd.datetime(2021, 7, 25), 3.5,  2.5))
arbiRanges.append(ArbiRange(pd.datetime(2021, 7, 26), pd.datetime(2021, 9,  6), 0.6, -0.3))
arbiRanges.append(ArbiRange(pd.datetime(2021, 9,  7), pd.datetime(2021, 9, 26), 3.5,  2.5))
#arbiRanges.append(ArbiRange(pd.datetime(2021, 9, 27), pd.datetime(2021, 9, 30), 3.4,  2.8))
arbiRanges.append(ArbiRange(pd.datetime(2021, 9, 29), pd.datetime(2021, 10, 5), 3.0,  2.3))


# lastIdx = 0
# while True:
#     mismatch = False
#     for i in range(lastIdx,len(df_ub.index)):
#         if df_ub.index[i] != df_bn.index[i]:
#             df_bn = df_bn.drop(df_bn.index[i])
#             print(f"mismatch at {i}")
#             mismatch = True
#             lastIdx = i-2
#             break

#     if not mismatch:
#         break

# df_bn.to_csv('ub-corrected.csv')
# exit(0)

#crop range
if True:
    #8/1~9/7
    # range_start = pd.datetime(2021, 7, 1)
    # range_end = pd.datetime(2021, 9, 20)

    # range_start = pd.datetime(2021, 7, 26)
    # range_end = pd.datetime(2021, 9, 6)
    #9/8~2/20
    
    #9/29~9/30
    range_start = pd.datetime(2021, 9, 29)
    range_end = pd.datetime(2021, 10, 1)
    
    df_bn = df_bn[range_start:range_end]
    df_ub = df_ub[range_start:range_end]
    df_usd = df_usd[range_start:range_end]

if False:
    df_bn = df_bn.rolling(window=5).mean()
    df_ub = df_ub.rolling(window=5).mean()

# $ to KRW conv.
df_bn['close'] = df_bn['close']*df_usd['close'] 

# Kimp gen.
kimp = ( df_ub['close'] / df_bn['close'] - 1.0 ) * 100
kimp.dropna(inplace=True)
n_kimp = kimp * 1600 + 4000 #normalized


#plot
if True:
    kimp.plot(marker='o', linestyle='-', markersize=1); #axes[1,1].set_title('KIMP')
else:
    fig, axes = plt.subplots(nrows=2, ncols=2)

    df_bn['close'].plot(ax=axes[0,0]); axes[0,0].set_title('BN')
    df_ub['close'].plot(ax=axes[1,0]); axes[1,0].set_title('UB')

    #df_usd['close'].plot(ax=axes[1,0]); axes[1,0].set_title('KRW/USDT')
    df_bn['close'].plot(ax=axes[0,1])
    df_ub['close'].plot(ax=axes[0,1]) 
    n_kimp.plot(ax=axes[0,1], marker='o', linestyle='-', markersize=1);
    axes[0,1].set_title('UB & BN + n_KIMP')

    kimp.plot(ax=axes[1,1], marker='o', linestyle='-', markersize=1); axes[1,1].set_title('KIMP')

# data confirm
# for i in range(355, 365, 2):
#     _kimp = ( ( df_ub['close'][i] / (df_bn['close'][i]*df_usd['close'][i]) ) - 1.0 ) * 100
#     print(f"{_kimp} = ( ( {df_ub['close'][i]} / ({df_bn['close'][i]}*{df_usd['close'][i]}) ) - 1.0 ) * 100")

#move_figure(fig, 150, 100)
#thismanager = get_current_fig_manager()
#thismanager.window.SetPosition((500, 0))

#back-testing

## init state
### const
UB = 0
BN = 1
IN  = 10
OUT = 11
### var
state = UB
balance = 1000
### config
# IN_TH  = 0.6
# OUT_TH = -0.3
IN_TH = 3.5
OUT_TH = 2.5

selRanges = []
actions = []
tss = []

def getRangeForDate(ranges, date):
    for r in ranges:
        if r.dateStart <= date and date <= r.dateEnd:
            return r


## iterate kimp index
for i in range(1,len(kimp)):
    date = kimp.index[i]
    v = kimp[i]
    r = getRangeForDate(arbiRanges, date)
    if r:
        didAction = False
        if state == BN:
            if v > r.inTh:
                state = UB
                actions.append(IN)
                didAction = True
        else: # UB
            if v < r.outTh:
                state = BN
                actions.append(OUT)
                didAction = True

        if didAction:
            selRanges.append(arbiRanges.index(r))
            tss.append(i)

## plot th
# line_x = np.linspace(n_kimp[0], n_kimp[len(n_kimp)-1], len(n_kimp))
# plt.plot(line_x, np.linspace(IN_TH , IN_TH , len(n_kimp)))
# plt.plot(line_x, np.linspace(OUT_TH, OUT_TH, len(n_kimp)))
days = float((kimp.index[-1]-kimp.index[0]).days)

for r in arbiRanges:
    plt.axhline(y=r.inTh , color='r', linestyle='-', 
        xmin=(r.dateStart-kimp.index[0]).days/days,
        xmax=(r.dateEnd  -kimp.index[0]).days/days)
    plt.axhline(y=r.outTh, color='b', linestyle='-',
        xmin=(r.dateStart-kimp.index[0]).days/days,
        xmax=(r.dateEnd  -kimp.index[0]).days/days)

## gain calc
_balance=balance
gain = 0

#fee
up_fee = 0.0005
bn_fee = 0.001
bn_fut_fee = 0.0002
for i in range(1,len(tss)):
    a = actions[i]
    ts = tss[i]
    date = kimp.index[ts]
    v = kimp[ts]
    if True:
        if a == OUT:
            #UB: buy spot
            t_p = float(df_ub.iloc[ts]['close'])
            t_q = balance / t_p
            spotBuy = t_p * t_q * (1-up_fee) #fee 0.05%

            #BN: sell future
            f_p = float(df_bn.iloc[ts]['close'])
            futShort = f_p * t_q * (1-bn_fut_fee) #fee 0.02%

            ## change exchange in 5min..
            #BN: spot sell
            t_p2 = float(df_bn.iloc[ts+5]['close'])
            spotSell = t_p2 * t_q * (1-bn_fee) #fee 0.1#
            spotGain = spotSell - spotBuy

            #BN: buy future
            futLong = t_p2 * t_q
            futGain = futShort - futLong

            #Gain Calc
            totalGain = spotGain + futGain
            gainRatio = totalGain / balance

            balance = totalGain + balance

            #stat
            bn_ch = df_bn.iloc[ts+5]['close'] / df_bn.iloc[ts]['close']
            ub_ch = df_ub.iloc[ts+5]['close'] / df_ub.iloc[ts]['close']
            k_ch = kimp.iloc[ts+5] - kimp.iloc[ts]
            print(f"[OT]: t_q={round(t_q,2)}, ub_pr={round(ub_ch,2)}, bn_pr={round(bn_ch,2)}, k=({round(kimp.iloc[ts],2)},{round(kimp.iloc[ts+5],2)}), gain(s,f)=({round(spotGain,2)},{round(futGain,2)}) => {round(totalGain,2)}, R={round(gainRatio*100,2)}, $={round(balance,2)}")
            #stat
        elif a == IN:
            #BN: buy spot
            t_p = float(df_bn.iloc[ts]['close'])
            t_q = balance / t_p * (1-bn_fee) #fee 0.1#
            spotBuy = t_p * t_q

            #BN: sell future
            f_p = t_p # -2~3tick?
            futShort = f_p * t_q * (1-bn_fut_fee) #fee 0.02%

            ## change exchange in 5min..
            #t_q = t_q - 0.1 only for spot... fixed... ignore..

            #UB: spot sell
            t_p2 = float(df_ub.iloc[ts+5]['close'])
            spotSell = t_p2 * t_q * (1-up_fee) #fee 0.05%
            spotGain = spotSell - spotBuy

            #BN: buy future
            f_p2 = float(df_bn.iloc[ts+5]['close'])
            futLong = f_p2 * t_q * (1-bn_fut_fee) #fee 0.02%
            futGain = futShort - futLong

            #Gain Calc
            totalGain = spotGain + futGain
            gainRatio = totalGain / balance

            balance = totalGain + balance

            #stat
            bn_ch = df_bn.iloc[ts+5]['close'] / df_bn.iloc[ts]['close']
            ub_ch = df_ub.iloc[ts+5]['close'] / df_ub.iloc[ts]['close']
            k_ch = kimp.iloc[ts+5] - kimp.iloc[ts]
            print(f"[IN]: t_q={round(t_q,2)}, ub_pr={round(ub_ch,2)}, bn_pr={round(bn_ch,2)}, k=({round(kimp.iloc[ts],2)},{round(kimp.iloc[ts+5],2)}), gain(s,f)=({round(spotGain,2)},{round(futGain,2)}) => {round(totalGain,2)}, R={round(gainRatio*100,2)}, $={round(balance,2)}")
        else:
            print('error:178')
            exit(0)
    else:
        gain = gain + (+v if a is IN else -v)
        print(f"[{date}]:({selRanges[i]}):{'IN ' if a == IN else 'OUT'} at {v} => {gain}")

gain = (balance/_balance - 1)*100
print(f"total gain%:{gain}")
print(f"days:{days}")
print(f"APR%:{round(gain/days*365.0,2)}")
plt.show()


