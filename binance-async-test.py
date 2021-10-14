from binance import AsyncClient, DepthCacheManager, BinanceSocketManager
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import asyncio
from classes import Exchanges

async def main():
# initialise the client
    api_key = 'xc88zHqhZjLhTlYLlHRy2k30tKVVEV3oZq2GodtGP8gQloThM2R1KfMMED4goG3c'
    api_secret = 'xzZ8D5qiSXCIJgirSSbD9fLqVFkjcDIHgms17j1u1SwdklCEClSSjqbRk83ZRmO1'
    
    ex = Exchanges()
    await ex.prepare_async()
    
    #exchange_info = await client.get_exchange_info()
    #tickers = await client.get_all_tickers()

    syncRet = ex.binance.get_all_tickers()

    res1, res2 = await asyncio.gather(
        ex.a_binance.get_exchange_info(),
        ex.a_binance.get_all_tickers()
    )

    syncRet2 = ex.binance.get_exchange_info(),
    print(res1)
    print(res2)

if __name__ == "__main__":

    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(main())

    asyncio.run(main())