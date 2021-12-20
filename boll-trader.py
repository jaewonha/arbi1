from classes.Exchanges import Exchanges
from arbi.arbi_common import *
from arbi.arbi_in import *
from arbi.arbi_out import *
from main import *

import time
from binance import ThreadedWebsocketManager
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
    

def main():

    symbol = 'BTCUSDT'

    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=sec_key)
    # start is required to initialise its internal loop
    twm.start()

    def cb_kline(msg):
        print(f'[kline]{msg}')
    twm.start_kline_socket(callback=cb_kline, symbol=symbol, interval=KLINE_INTERVAL_3MINUTE)

    def cb_depth(msg):
        print(f'[depth]{msg}')
    #twm.start_depth_socket(callback=cb_depth, symbol=symbol)
    
    twm.join()


if __name__ == "__main__":
   main()