import matplotlib.pyplot as plt
import pandas as pd
import mplcursors

df_snx = pd.read_csv("./MATICUSDT.csv", index_col=0, parse_dates=True)
df_eth = pd.read_csv("./ETHUSDT.csv", index_col=0, parse_dates=True)

df_all = pd.DataFrame()
df_all['snx'] = df_snx['c']*100
df_all['eth'] = df_eth['c']
df_all['snx/eth'] = (df_snx['c'] / df_eth['c'])*1000000

#df_all.plot()
df_all['snx/eth'].plot()*100000
mplcursors.cursor(hover=True)

print("end")