#https://github.com/sharebook-kr/pyupbit/blob/955a2bf87d1951294dd32e2a900b8f1a8ace38cc/pyupbit/exchange_api.py

import pprint
import time
import traceback

from exchange import *

import pyupbit
#from pyupbit import WebSocketManager
ub_acc_key = "p2uhQ8xdqxhEvslccOPkwzreXiuTWysaNTcYigWq"          # 본인 값으로 변경
ub_sec_key = "k55DdoFw2sPRSYGMzB4IzwNna7ywPHYj1562QykN"          # 본인 값으로 변경
upbit = pyupbit.Upbit(ub_acc_key, ub_sec_key)

from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
bn_api_key = 'xc88zHqhZjLhTlYLlHRy2k30tKVVEV3oZq2GodtGP8gQloThM2R1KfMMED4goG3c'
bn_sec_key = 'xzZ8D5qiSXCIJgirSSbD9fLqVFkjcDIHgms17j1u1SwdklCEClSSjqbRk83ZRmO1'
binance = Client(bn_api_key, bn_sec_key)

asset = 'EOS'
ub_pair = ub_krw_pair(asset)
bn_pair = bn_usdt_pair(asset)

t_q = bn_get_spot_balance(binance, asset, False)
print(t_q)
#TEST = False
#UB_TEST = False
#BN_TEST = True

#exit(0)
#bn->ub

ub_eos_addr = 'eosupbitsusr'
ub_eos_memo = '5772f423-5c5a-4361-9678-2e070338fec1'

#3a. withdraw
# withdraw = binance.withdraw(
#     coin=asset,
#     address=ub_eos_addr,
#     addressTag=ub_eos_memo, #or TAG
#     amount=t_q)
    
#withdraw_id = withdraw['id']

withdraw_id = 'e08eaa9dde9c4e078bc0a9e2ad84fc88'
#3b. wait finished - BN
while True:
    withdraw_result = binance.get_withdraw_history_id(withdraw_id)
    pprint.pprint(withdraw_result)
    print(f"withdraw_staus:{withdraw_result['status']}")
    txid = withdraw_result['txId']
    if withdraw_result['status'] == 4:
        print('processing..')
    elif withdraw_result['status'] == 6:
        print('complete..')
        break
    time.sleep(1)

#3c. wait deposit - UB
#txid = '79116e44a26b12f8b9921f201270b9cfa21f59ae8900823525b6851404e3bc4f'
while True:
    state = ub_raw_get_deposit(ub_acc_key, ub_sec_key, txid, asset)[0]['state']
    print('ub_raw_get_deposit:state:' + state)
    if state =='ACCEPTED': #state == 'DONE' or 
        break

#check balance
print(ub_get_spot_balance(upbit, asset))

#             #     입출금 현황 
#     def get_deposit_withdraw_status(self, contain_req=False):


#             #     개별 출금 조회
#     def get_individual_withdraw_order(self, uuid: str, currency: str, contain_req=False):


#             #     코인 출금하기  
#     def withdraw_coin(self, currency, amount, address, secondary_address='None', transaction_type='default', contain_req=False):


#             #     원화 출금하기
#     def withdraw_cash(self, amount: str, contain_req=False):


