import pyupbit
from upbit.client import Upbit
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from classes import *
from conv.krw2usd import krw_per_usd
import json

class Exchanges:
    #def __init__(self, pyupbit: PyUpbit, upbitClient: UpbitClient, binance: Binance):
    def __init__(self):
        f = open('.key.ini','r')
        keyJson = json.load(f)
        #UB - tradable
        access = keyJson['upbit']['accKey']
        secret = keyJson['upbit']['secKey']
        self.pyupbit = pyupbit.Upbit(access, secret)
        self.upbitClient = Upbit(access, secret)

        #BN - tadable
        api_key = keyJson['binance']['apiKey']
        sec_key = keyJson['binance']['secKey']
        self.binance = Client(api_key, sec_key)

        self.updateCurrency()
        f.close()

    def updateCurrency(self):
        self.krwPerUsd: float= float(krw_per_usd())
    