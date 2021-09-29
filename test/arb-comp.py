import pandas as pd
import matplotlib
#from pylab import get_current_fig_manager
import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import math
import datetime as dt

from util import move_figure
from classes.ArbiRange import ArbiRange

#load
df_bn = pd.read_csv("./BN-EOSUSDT-180d.csv", index_col=0, parse_dates=True)
df_ub = pd.read_csv("./UB-KRW-EOS-180d.csv", index_col=0, parse_dates=True).drop(['volume', 'value'], axis=1)

df_usd = pd.read_csv("./USD_KRW_H_1Y.csv", index_col=0, parse_dates=True)
df_usd['date'] = pd.to_datetime(df_usd['date']); df_usd = df_usd.set_index('date')

arbiRanges = []
arbiRanges.append(ArbiRange(pd.datetime(2021, 7,  1), pd.datetime(2021, 7, 25), 3.5,  2.5))
arbiRanges.append(ArbiRange(pd.datetime(2021, 7, 26), pd.datetime(2021, 9,  6), 0.6, -0.3))
arbiRanges.append(ArbiRange(pd.datetime(2021, 9,  7), pd.datetime(2021, 9, 24), 3.5,  2.5))

#crop range
if True:
    #8/1~9/7
    range_start = pd.datetime(2021, 7, 1)
    range_end = pd.datetime(2021, 9, 20)
    # range_start = pd.datetime(2021, 7, 26)
    # range_end = pd.datetime(2021, 9, 6)
    #9/8~2/20
    
    df_bn = df_bn[range_start:range_end]
    df_ub = df_ub[range_start:range_end]
    df_usd = df_usd[range_start:range_end]

# $ to KRW conv.
df_bn['close'] = df_bn['close']*df_usd['close'] 

# Kimp gen.
kimp = ( df_ub['close'] / df_bn['close'] - 1.0 ) * 100
kimp.dropna(inplace=True)
n_kimp = kimp * 1600 + 4000 #normalized

#plot
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
gain = 0
for i in range(1,len(tss)):
    a = actions[i]
    ts = tss[i]
    date = kimp.index[ts]
    v = kimp[ts]
    gain = gain + (+v if a is IN else -v)
    print(f"[{date}]:({selRanges[i]}):{'IN ' if a == IN else 'OUT'} at {v} => {gain}")


print(f"total gain%:{gain}")
print(f"days:{days}")
print(f"APR%:{gain/days*365.0}")
plt.show()


