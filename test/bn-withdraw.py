
from datetime import datetime, date, timedelta
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.exceptions import BinanceAPIException, BinanceOrderException
import pprint
from arbi import *
#from binance import Client, AsyncClient, DepthCacheManager, BinanceSocketManager

#BN - tadable
api_key = 'xc88zHqhZjLhTlYLlHRy2k30tKVVEV3oZq2GodtGP8gQloThM2R1KfMMED4goG3c'
sec_key = 'xzZ8D5qiSXCIJgirSSbD9fLqVFkjcDIHgms17j1u1SwdklCEClSSjqbRk83ZRmO1'
client = Client(api_key, sec_key)


asset = 'EOS'

withdraws = client.get_withdraw_history()
#pprint.pprint(withdraws)
asset_withdraws = client.get_withdraw_history(coin=asset)
pprint.pprint(asset_withdraws)
'''
 [{'address': 'huobideposit',
  'addressTag': '8255358',
  'amount': '817.3',
  'applyTime': '2021-08-28 03:48:42',
  'coin': 'EOS',
  'confirmNo': 1,
  'id': 'f3a9ee41c02a47dcaa136ad28b119e4b', <-
  'network': 'EOS',
  'status': 6, <-
  'transactionFee': '0.1',
  'transferType': 0,
  'txId': '4611d28f7996f0dff64033853cddeb64f85d93d3afc4e53b34bbf7de5e703ace'}]
'''
asset_deposit_addr = client.get_deposit_address(coin=asset)
print(asset_deposit_addr)
#{'coin': 'EOS', 'address': 'binancecleos', 'tag': '109642124', 'url': 'https://bloks.io/account/binancecleos'}
exit(0)
try:
    # name parameter will be set to the asset value by the client if not passed
    result = client.withdraw(
        coin=asset,
        address=ub_eos_addr,
        addressTag=ub_eos_memo,
        amount=1)
    print(result)
    withdraw_id = result['id']
    print(withdraw_id)
except BinanceAPIException as e:
    print(e)
else:
    print("Success")

print(client.get_withdraw_history(withdraw_id=withdraw_id)) #<- check
