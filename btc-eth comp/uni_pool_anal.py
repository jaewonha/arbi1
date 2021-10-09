import json
import matplotlib.pyplot as plt
import pandas as pd
import mplcursors


#from get-klines.py
from datetime import datetime, date, timedelta
def utc_to_str(utc_ts_bn, div1000=False):
        if div1000:
            ts = int(utc_ts_bn)/1000
        else:
            ts = int(utc_ts_bn)
        #return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%SZ')
        #return datetime.fromtimestamp(ts).strftime('%Y/%m/%d %H:%M')
        return datetime.fromtimestamp(ts).strftime('%Y/%m/%d')


#path = "uni_pool_ethusdt_4e68.json"
#path = "uni_pool_ethusdc_030_8ad5.json"
#path = "uni_pool_ethusdc_005_88e6.json"
#path = "uni_pool_daieth_005_6059.json"
path = "uni_pool_snxeth_030.json"
#path = "uni_pool_eth2xeth.json"
#path = "uni_arbi_ethusdc_0300.json"
#path = "uni_pool_maticusdt_003.json"

unit1M = float(1000*1000)

with open(path, "r") as file:
    _loaded = json.load(file)
    pools = _loaded['data']['pools']

    for pool in pools:
        feeRate = float(pool['feeTier'])/unit1M
        print(f"pool id:{pool['id']}")
        print(f"pool name:{pool['token0']['symbol']}-{pool['token1']['symbol']}")
        print(f"pool fee%:{feeRate*100}")
        print(f"pool createdAt:{utc_to_str(pool['createdAtTimestamp'], False, True)}")
        print(f"pool #day data:{len(pool['poolDayData'])}")

        poolDayData = pool['poolDayData']

        columns = ['day', 'date', 'volumeUSD', 'tvlUSD']
        day = []
        date = []
        volumeUSD = []
        tvlUSD = []

        for data in poolDayData:
            day.append(utc_to_str(data['date'], False, True))
            date.append(int(data['date']))
            volumeUSD.append(float(data['volumeUSD'])/unit1M)
            tvlUSD.append( float(data['tvlUSD'])/unit1M )
            
        _data = {'day': day, 'date': date, 'volumeUSD': volumeUSD, 'tvlUSD': tvlUSD}

        df = pd.DataFrame(_data, columns = columns)
        df['feeAcc'] = df['volumeUSD'].cumsum()*feeRate
        df['date'] = (((df['date']-date[0])/86400)+1)#/365.0
        #df['APR%'] = df['feeAcc'] / (df['date']/365.0) / df['tvlUSD'] * 100
        df['APR%/10'] = df['feeAcc'] / (df['date']/365.0) / df['tvlUSD'] * 10
        #df['APR*1'] = df['feeAcc'] / (df['date']/365.0) / df['tvlUSD'] * 1

        #df.drop('date', inplace=True, axis=1)
        df = df.set_index('date')

        df.plot()
        mplcursors.cursor(hover=True)

        print('end')







