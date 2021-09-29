#https://github.com/sharebook-kr/pyupbit/blob/955a2bf87d1951294dd32e2a900b8f1a8ace38cc/pyupbit/exchange_api.py

import pyupbit
#from pyupbit import WebSocketManager
import pprint

from exchange import *

acc_key = "p2uhQ8xdqxhEvslccOPkwzreXiuTWysaNTcYigWq"          # 본인 값으로 변경
sec_key = "k55DdoFw2sPRSYGMzB4IzwNna7ywPHYj1562QykN"          # 본인 값으로 변경
upbit = pyupbit.Upbit(acc_key, sec_key)

asset = 'EOS'
print(ub_raw_get_deposit(acc_key, sec_key, asset))

#             #     입출금 현황 
#     def get_deposit_withdraw_status(self, contain_req=False):


#             #     개별 출금 조회
#     def get_individual_withdraw_order(self, uuid: str, currency: str, contain_req=False):


#             #     코인 출금하기  
#     def withdraw_coin(self, currency, amount, address, secondary_address='None', transaction_type='default', contain_req=False):


#             #     원화 출금하기
#     def withdraw_cash(self, amount: str, contain_req=False):


