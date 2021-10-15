from arbi import *
from util.log import *
from classes import *
from main import *

import asyncio
import time

ORDER_TEST = False
maxUSD = 20

ex = Exchanges()
#krwPerUsd = float(krw_per_usd()) #fixme: error handling for float version fail

asset = 'EOS'
OUT_TH = 100.0 #숫자가 작을때 (손해) 나가려고 하니 큰 숫자를 쓰면 무조건 나감
IN_TH = 0.0 #숫자가 클떄 들어오(이득)려고 하니 작은 숫자를 쓰면 무조건 들어옴

ub_p_krw, bn_p_usd, bn_f_usd, kimp = calc_kimp(ex, asset)

#print(bn_get_fut_pending_amt(ex, asset))
#exit(0)


async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)

async def main():
    print("test in")
    task1_in = asyncio.create_task(
        arbi_in_bn_to_ub(ex, asset, bn_p_usd[IN], maxUSD, IN_TH, ORDER_TEST)
    )

    print("test out")
    task_out = asyncio.create_task(
        arbi_out_ub_to_bn(ex, asset, ub_p_krw[OUT], bn_p_usd[OUT], maxUSD, ORDER_TEST)
    )
    
    print("wait")
    await task1_in
    await task_out
    print("done")

asyncio.run(main())