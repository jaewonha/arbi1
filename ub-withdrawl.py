#https://github.com/sharebook-kr/pyupbit/blob/955a2bf87d1951294dd32e2a900b8f1a8ace38cc/pyupbit/exchange_api.py

import pprint
import time
import traceback

from upbit.client import Upbit
import pyupbit

from arbi import *
from exchange import *


#from pyupbit import WebSocketManager
ub_acc_key = "p2uhQ8xdqxhEvslccOPkwzreXiuTWysaNTcYigWq"          # 본인 값으로 변경
ub_sec_key = "k55DdoFw2sPRSYGMzB4IzwNna7ywPHYj1562QykN"          # 본인 값으로 변경
upbit = pyupbit.Upbit(ub_acc_key, ub_sec_key)

upbit2 = Upbit(ub_acc_key, ub_sec_key)
# resp = upbit2.Withdraw.Withdraw_info_all()
# print(resp['result'])

from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
bn_api_key = 'xc88zHqhZjLhTlYLlHRy2k30tKVVEV3oZq2GodtGP8gQloThM2R1KfMMED4goG3c'
bn_sec_key = 'xzZ8D5qiSXCIJgirSSbD9fLqVFkjcDIHgms17j1u1SwdklCEClSSjqbRk83ZRmO1'
binance = Client(bn_api_key, bn_sec_key)

asset = 'EOS'
ub_pair = ub_krw_pair(asset)
bn_pair = bn_usdt_pair(asset)

IN_BN2UB_TEST = True
OUT_UB2BN_TEST = True


#exit(0)1
#bn->ub

if IN_BN2UB_TEST:
    print("IN_BN2UB_TEST")
    # asset_withdraws = binance.get_withdraw_history(coin=asset)
    # print(asset_withdraws)
    
    #txid = '78b146e80e38ee0274d0f92fc5bbbcc54cf769dfcc6fa41e18544bd43b012233'
    t_q = bn_get_spot_balance(binance, asset, False) #fixme:withdraw chance q
    print(f"t_q:{t_q}")

    #3a. withdraw
    addr = ub_get_asset_addr(asset)
    memo = ub_get_asset_memo(asset)
    withdraw_id = bn_withdraw(binance, asset, addr, memo, t_q)
    #withdraw_id = '43fa4ae2f0ee4d1198287a454a0bd72f'
    print(f"withdraw_id:{withdraw_id}")

    #3b. wait finished - BN
    txid = bn_wait_withdraw(binance, withdraw_id)
    print(f"txid:{txid}")

    #3c. wait deposit - UB
    ub_wait_deposit(upbit2, txid)

    #check balance
    print(ub_get_spot_balance(upbit, asset))


if OUT_UB2BN_TEST:
    print("OUT_UB2BN_TEST")
    # resp = upbit2.Withdraw.Withdraw_info_all()
    # pprint.pprint(resp['result'])
    # exit(0)

    withdraw_chance = upbit2.Withdraw.Withdraw_chance(
        currency=asset
    )['result']
    assert withdraw_chance['account']['currency'] == asset
    t_q = round(float(withdraw_chance['account']['balance']), 4)
    print(f"t_q:{t_q}")

    #3a. withdraw
    addr = bn_get_asset_addr(asset)
    memo = bn_get_asset_memo(asset)
    uuid = ub_withdraw(upbit2, asset, t_q, addr, memo)
    #uuid = 'ca81f1e3-d019-4350-b739-d6b110a03f08'
    print(f"uuid:{uuid}")

    #3b. wait finished - UB
    txid = ub_wait_withdraw(upbit2, uuid)
    print(f"txid:{txid}")

    #3c. wait deposit - BN
    bn_wait_deposit(binance, asset, txid)
    
    #check balance
    print(bn_get_spot_balance(binance, asset))
