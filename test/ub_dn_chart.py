import pyupbit

#print(pyupbit.get_tickers(fiat="KRW"))
#print(pyupbit.get_current_price("KRW-EOS"))

day = 30
min = 5
asset = 'KRW-BTC'
df = pyupbit.get_ohlcv(asset, count=24*int(60/min)*day, interval=("minutes" + str(min)))
# day = 180
# df = pyupbit.get_ohlcv(asset, count=24*day, interval="minute60")
#print(df)
#df.plot()
df.to_csv('UB-'+asset+'-'+str(day)+'d-'+str(min)+'m.csv')
#input('any key...')