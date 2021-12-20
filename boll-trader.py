import time
import json
from binance import Client, ThreadedWebsocketManager
from binance.enums import *

f = open('.key.ini','r')
keyJson = json.load(f)

testnet = False
if testnet:
    api_key = keyJson['binance-testnet']['apiKey']
    sec_key = keyJson['binance-testnet']['secKey']
else:
    api_key = keyJson['binance']['apiKey']
    sec_key = keyJson['binance']['secKey']
    

config = {
    "symbol":"btcusdt",
    "interval":"3m",
}

def main():
    initGraph(config)
    downloadPrev(config)
    launchStream(config)

def initGraph(config):
    pass

def downloadPrev(config):
    pass

def launchStream(config):
    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=sec_key)
    # start is required to initialise its internal loop
    twm.start()

    twm.start_kline_socket(callback=cb_kline, symbol=config['symbol'], interval=KLINE_INTERVAL_3MINUTE)

    #twm.start_multiplex_socket(callback=cb_book, streams=['btcusdt@bookTicker'])
    twm.start_multiplex_socket(callback=cb_book, streams=['btcusdt@depth5@100ms'])

    #twm.start_depth_socket(callback=cb_depth, symbol=symbol)
    
    twm.join()


## callbacks

def cb_kline(msg):
    print(f'[kline]{msg}')

    #check buy condition
    #update graph

#def cb_depth(msg):
    #print(f'[depth]{msg}')
    #check buy condition
    #update graph

def cb_book(msg):
    print(f'[book]{msg}')


if __name__ == "__main__":
    main()

'''
import asyncio

from binance import AsyncClient, DepthCacheManager


async def main():
    client = await AsyncClient.create()
    dcm = DepthCacheManager(client, 'BNBBTC')

    async with dcm as dcm_socket:
        while True:
            depth_cache = await dcm_socket.recv()
            print("symbol {}".format(depth_cache.symbol))
            print("top 5 bids")
            print(depth_cache.get_bids()[:5])
            print("top 5 asks")
            print(depth_cache.get_asks()[:5])
            print("last update time {}".format(depth_cache.update_time))

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
'''
