import pandas as pd
import matplotlib
#from pylab import get_current_fig_manager
import matplotlib.pyplot as plt
#import mplcursors #pip install plotly
import numpy as np
import math
import datetime as dt

import pyupbit
import asyncio
import json

import time
from datetime import datetime, date, timedelta

from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from conv.krw2usd import krw_per_usd


#from util import move_figure
from classes.ArbiRange import ArbiRange
from util.time import *
    
days = 1
bn_pair = 'EOSUSDT'

krwPerUsd = krw_per_usd()
if True: #True: force new download, False: use cached csv file
    client = Client()

    yesterday = date.today() - timedelta(days)
    from_ts = time.mktime(yesterday.timetuple())

    klines = []
    #KLINE_INTERVAL_1DAY, KLINE_INTERVAL_1HOUR, KLINE_INTERVAL_1MINUTE
    klines = client.get_historical_klines(bn_pair, Client.KLINE_INTERVAL_1MINUTE, str(from_ts))
    klines2 = np.delete(klines, range(5,12), axis=1)

    
    for i in range(0, len(klines2)):
        klines2[i][0] = utc_to_str(klines2[i][0], True)
        
    df_bn = pd.DataFrame(klines2, columns=['ts','open','high','low','close']).set_index('ts')
    #df.to_csv('BN-'+symbol+'-'+str(days)+'d.csv')

    df_ub = pyupbit.get_ohlcv("KRW-EOS", count=24*60*days, interval="minute1")
    #df_ub = pyupbit.get_ohlcv("KRW-EOS", count=24*days, interval="minute60")
    #df.to_csv('UB-KRW-EOS-'+str(days)+'d.csv')


    df_ub.drop(columns=['volume','value'], axis=1, inplace=True)
    df_ub.reset_index(inplace=True)
    df_bn.reset_index(inplace=True)

    df_ub.rename({'index':'ts'}, axis=1, inplace=True)
    df_bn.rename({0:'ts'}, axis=1, inplace=True)

    df_bn['ts'] = df_bn['ts'].values.astype(dtype='datetime64[ns]')

    df_ub.sort_values(by='ts', ascending=True, inplace=True)
    df_bn.sort_values(by='ts', ascending=True, inplace=True)

    print(df_ub.head())
    print(df_bn.head())

    df_join = pd.merge(df_bn, df_ub, left_on='ts', right_on='ts', how='outer').dropna().reset_index().drop(columns=['index'], axis=1)
    print(df_join.head())

    df_join.to_csv('df_join-'+str(days)+'d.csv')

df_join = pd.read_csv('df_join-'+str(days)+'d.csv', index_col=0, parse_dates=True) 
df_join['ts'] = pd.to_datetime(df_join['ts'])

print(df_join.head())
df_ub = pd.DataFrame()
df_bn = pd.DataFrame()

df_ub.index = df_join.index
df_ub['ts'] = df_join['ts']
df_ub['open'] = df_join['open_y']
df_ub['high'] = df_join['high_y']
df_ub['low'] = df_join['low_y']
df_ub['close'] = df_join['close_y']
df_ub.set_index('ts', inplace=True)

df_bn.index = df_join.index
df_bn['ts'] = df_join['ts']
df_bn['open'] = df_join['open_x']
df_bn['high'] = df_join['high_x']
df_bn['low'] = df_join['low_x']
df_bn['close'] = df_join['close_x']
df_bn.set_index('ts', inplace=True)

df_usd = pd.DataFrame(df_bn, copy=True)
df_usd['open'] = df_usd['high'] = df_usd['low'] = df_usd['close'] = krwPerUsd

arbiRanges = []
# arbiRanges.append(ArbiRange(pd.datetime(2021, 7,  1), pd.datetime(2021, 7, 25), 3.5,  2.5))
# arbiRanges.append(ArbiRange(pd.datetime(2021, 7, 26), pd.datetime(2021, 9,  6), 0.6, -0.3))
# arbiRanges.append(ArbiRange(pd.datetime(2021, 9,  7), pd.datetime(2021, 9, 26), 3.5,  2.5))
# #arbiRanges.append(ArbiRange(pd.datetime(2021, 9, 27), pd.datetime(2021, 9, 30), 3.4,  2.8))
# arbiRanges.append(ArbiRange(pd.datetime(2021, 9, 29), pd.datetime(2021, 10, 5), 3.0,  2.3))
#arbiRanges.append(ArbiRange(pd.datetime(2021, 10, 3), pd.datetime(2021, 10, 5), 2.8,  2.2))
#arbiRanges.append(ArbiRange(pd.datetime(2021, 10, 10), pd.datetime(2021, 10, 11), 2.35,  1.65))
arbiRanges.append(ArbiRange(pd.datetime(2021, 10, 10), pd.datetime(2021, 10, 12), 2.65,  2.15))

#crop range
if False:
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


#df_bn['close'] = df_bn['close']*df_usd['close']  # $ to KRW conv.
df_ub['close'] = df_ub['close']/df_usd['close']  # KRW to $ conv. 

# Kimp gen.
kimp = ( df_ub['close'] / df_bn['close'] - 1.0 ) * 100
kimp.dropna(inplace=True)
#n_kimp = kimp * 1600 + 4000 #normalized


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
#use above range instead
#IN_TH  = 0.6
#OUT_TH = -0.3
#IN_TH = 2.6
#OUT_TH = 2.0

selRanges = []
actions = []
tss = []

def getRangeForDate(ranges, date):
    for r in ranges:
        if r.dateStart <= date and date <= r.dateEnd:
            return r


## iterate kimp index - get target arbitrage range
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
secs = float((kimp.index[-1]-kimp.index[0]).total_seconds())

for r in arbiRanges:
    plt.axhline(y=r.inTh , color='r', linestyle='-', 
        xmin=(r.dateStart-kimp.index[0]).total_seconds()/secs,
        xmax=(r.dateEnd  -kimp.index[0]).total_seconds()/secs)
    plt.axhline(y=r.outTh, color='b', linestyle='-',
        xmin=(r.dateStart-kimp.index[0]).total_seconds()/secs,
        xmax=(r.dateEnd  -kimp.index[0]).total_seconds()/secs)


## gain calc
_balance=balance
gain = 0

#fee
up_fee = 0.0005
bn_fee = 0.001
bn_fut_fee = 0.0004

#calc arbitrage gains
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
            if ts+5 >= len(df_bn):
                print('end reached')
                break
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

            mode = 'OT'
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

            mode = 'IN'
        else:
            print('error:178')
            exit(0)
        
        #stat
        bn_ch = (1-df_bn.iloc[ts+5]['close'] / df_bn.iloc[ts]['close'])*100
        ub_ch = (1-df_ub.iloc[ts+5]['close'] / df_ub.iloc[ts]['close'])*100
        k_ch = kimp.iloc[ts+5] - kimp.iloc[ts]
        
        print(
                f"[{mode}]: t_q={round(t_q,2)}, "
                f"k=({round(kimp.iloc[ts],2)},{round(kimp.iloc[ts+5],2)}), "
                f"\tgain(s,f):{round(spotGain,2)}+{round(futGain,2)}={round(totalGain,2)},"
                f"\tR={round(gainRatio*100,2)}, $={round(balance,2)},"
                f"\tub_ch%={round(ub_ch,2)}, bn_ch%={round(bn_ch,2)}")
    else:
        gain = gain + (+v if a is IN else -v)
        print(f"[{date}]:({selRanges[i]}):{'IN ' if a == IN else 'OUT'} at {v} => {gain}")

gain = (balance/_balance - 1)*100
days = 60*60*24 / float(secs)
print(f"total gain%:{gain}")
print(f"days:{days}")
print(f"APR%:{round(gain/days*365.0,2)}")
plt.show()


