import json
import pandas as pd
import numpy as np

from datetime import datetime, date, timedelta
from binance import AsyncClient, DepthCacheManager, BinanceSocketManager

df_btc = pd.read_csv('BTCUSDT.csv').sort_index()
df_eth = pd.read_csv('MATICUSDT.csv').sort_index()

def print_idx(idx):
    print(f"print idx:{idx}")
    print(df_btc.loc[idx:idx,:])
    print(df_eth.loc[idx:idx,:])

print("==== data =====")
print(df_btc.head())
print(df_btc.tail())

print(df_eth.head())
print(df_eth.tail())
print("===============")

#diff_c = df_btc['c'] - df_eth['c']
ratio_c = df_btc['c'] / df_eth['c']
#print(ratio_c)
#print(ratio_c.min())
maxidx = ratio_c.idxmax()
minidx = ratio_c.idxmin()

print_idx(maxidx)
print_idx(minidx)

#plot graph

#plot IL

#plot eth2x - eth, too
print('end')