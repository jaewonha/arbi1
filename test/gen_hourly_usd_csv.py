import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import math
import datetime as dt
from pandas.tseries.offsets import Day, Hour, Minute, Second


_df = pd.read_csv("./BN-EOSUSDT-3d-1m.csv", parse_dates=True)
#_df = pd.read_csv("./USD_KRW_1Y.csv", parse_dates=True)
_df = _df.sort_values(by='date', ascending=True)
#_df = _df.reset_index().rename(columns={"index":"date"})
#_df.head()
#nn = _df.to_numpy()

_df['date'] = pd.to_datetime(_df['date'])

#freq = 'H'
freq=Minute(1)
date_range = pd.to_datetime(pd.date_range(_df['date'].min(), _df['date'].max(), freq=freq).strftime('%Y-%m-%d %H:%M:%S'))
print(len(date_range))
df_usd = pd.DataFrame( np.zeros((len(date_range), 1), dtype=float), columns=['date'] ) #krw/usd
df_usd['date'] = date_range

df_usd = pd.merge(df_usd, _df, left_on='date', right_on='date', how='left')

filled_row = None
for i, row in df_usd.iterrows():
    if pd.isnull(row['close']):
        filled_row['date'] = df_usd.iloc[i]['date']
        df_usd.iloc[i] = filled_row
    else:
    #if not pd.isnull(row['close']):
        filled_row = row

#df_usd.to_csv('hourly.csv')
df_usd.to_csv('min-interpolated.csv')