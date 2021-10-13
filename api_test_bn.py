from classes.Exchanges import Exchanges
from arbi.arbi_common import *
from arbi.arbi_in import *
from arbi.arbi_out import *
from main import *

ex = Exchanges()
bn = ex.binance

print('test')

#bn_fut_acc_asset_balance(ex, 'BNB')
#bn_fut_acc_asset_balance(ex, 'USDT')
#f = open('.config.ini','r')
#config = json.load(f)['remedy']

#ex.binance.get_trade_fee(symbol='EOSUSDT')

#time_res = client.get_server_time()

import requests
import pprint
 
'''
ep='https://api.binance.com'
ping='/api/v1/ping'
url='/sapi/v1/capital/config/getall'
params = None#{'symbol': 'BTCUSDT'}
 
r1=requests.get(ep+ping)
r2 = requests.get(ep+url, params=params) #use parameter
pprint.pprint(r1.json())
pprint.pprint(r2.json())
'''

#출처: https://pizzaplanet.tistory.com/entry/Binance-API-이용해보기 [pizzaplanet]


import time
import json
import hmac
import hashlib
import requests
from urllib.parse import urljoin, urlencode

#https://code.luasoftware.com/tutorials/cryptocurrency/python-connect-to-binance-api/

API_KEY = 'xc88zHqhZjLhTlYLlHRy2k30tKVVEV3oZq2GodtGP8gQloThM2R1KfMMED4goG3c'
SECRET_KEY = 'xzZ8D5qiSXCIJgirSSbD9fLqVFkjcDIHgms17j1u1SwdklCEClSSjqbRk83ZRmO1'
BASE_URL = 'https://api.binance.com'

headers = {
    'X-MBX-APIKEY': API_KEY
}

PATH = '/sapi/v1/capital/config/getall'
timestamp = int(time.time() * 1000)
params = {
    #'symbol': 'BTCUSDT'
    'timestamp' : timestamp,
    'asset': 'EOS'
}
query_string = urlencode(params)
params['signature'] = hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

url = urljoin(BASE_URL, PATH)
r = requests.get(url, headers=headers, params=params)
'''
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2))
else:
    print(f"error:{r.status_code}")
    print(r.json())
'''
import json

with open("binance_coins_info.json", "w") as json_file:
    json.dump(r.json(), json_file)

