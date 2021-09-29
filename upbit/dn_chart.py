import pyupbit

#print(pyupbit.get_tickers(fiat="KRW"))
#print(pyupbit.get_current_price("KRW-EOS"))

day = 180
df = pyupbit.get_ohlcv("KRW-EOS", count=24*day, interval="minute60")
print(df)
#df.plot()
df.to_csv('UB-KRW-EOS-'+str(day)+'d.csv')
input('any key...')