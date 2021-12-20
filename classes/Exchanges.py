#import pyupbit
#from upbit.client import Upbit
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance import AsyncClient, DepthCacheManager, BinanceSocketManager
from classes import *
from conv.krw2usd import krw_per_usd
import asyncio
import json

class Exchanges:
    #def __init__(self, pyupbit: PyUpbit, upbitClient: UpbitClient, binance: Binance):
    def __init__(self, testnet:bool = False):
        f = open('.key.ini','r')
        keyJson = json.load(f)

        #UB - tradable
        access = keyJson['upbit']['accKey']
        secret = keyJson['upbit']['secKey']
        self.pyupbit = pyupbit.Upbit(access, secret)
        self.upbitClient = Upbit(access, secret)

        #BN - tadable
        if testnet:
            api_key = keyJson['binance-testnet']['apiKey']
            sec_key = keyJson['binance-testnet']['secKey']
        else:
            api_key = keyJson['binance']['apiKey']
            sec_key = keyJson['binance']['secKey']
        self.binance = Client(api_key, sec_key)

        self.api_key = api_key
        self.sec_key = sec_key

        self.updateCurrency()
        f.close()
        
    async def prepare_async(self):
        self.a_binance = await AsyncClient(self.api_key, self.sec_key).create()

    def updateCurrency(self):
        self.krwPerUsd: float= float(krw_per_usd())
    