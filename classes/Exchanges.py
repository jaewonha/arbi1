import pyupbit
from upbit.client import Upbit
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from classes import *
from conv.krw2usd import krw_per_usd

class Exchanges:
    #def __init__(self, pyupbit: PyUpbit, upbitClient: UpbitClient, binance: Binance):
    def __init__(self):
        #UB - tradable
        access = "p2uhQ8xdqxhEvslccOPkwzreXiuTWysaNTcYigWq"
        secret = "k55DdoFw2sPRSYGMzB4IzwNna7ywPHYj1562QykN"
        self.pyupbit = pyupbit.Upbit(access, secret)
        self.upbitClient = Upbit(access, secret)

        #BN - tadable
        api_key = 'xc88zHqhZjLhTlYLlHRy2k30tKVVEV3oZq2GodtGP8gQloThM2R1KfMMED4goG3c'
        sec_key = 'xzZ8D5qiSXCIJgirSSbD9fLqVFkjcDIHgms17j1u1SwdklCEClSSjqbRk83ZRmO1'
        self.binance = Client(api_key, sec_key)

        self.updateCurrency()

    def updateCurrency(self):
        self.krwPerUsd: float= float(krw_per_usd())
    