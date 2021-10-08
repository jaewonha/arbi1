import pyupbit
from upbit.client import Upbit
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from classes import *
'''
def createExchange():        
    #init
    #UB - tradable
    access = "p2uhQ8xdqxhEvslccOPkwzreXiuTWysaNTcYigWq"
    secret = "k55DdoFw2sPRSYGMzB4IzwNna7ywPHYj1562QykN"
    upbit = pyupbit.Upbit(access, secret)
    upbit2 = Upbit(access, secret)

    #BN - tadable
    api_key = 'xc88zHqhZjLhTlYLlHRy2k30tKVVEV3oZq2GodtGP8gQloThM2R1KfMMED4goG3c'
    sec_key = 'xzZ8D5qiSXCIJgirSSbD9fLqVFkjcDIHgms17j1u1SwdklCEClSSjqbRk83ZRmO1'
    binance = Client(api_key, sec_key)
    return Exchanges(PyUpbit(upbit), UpbitClient(upbit2), Binance(binance))
'''