from arbi import *
from exchange import * #incase need bn_, un_ lower api
from util.log import *
from main import *

import datetime
from time import time, ctime

ex = Exchanges()

def bn_get_time_diff(verbose:bool = False):
    #https://stackoverflow.com/questions/66625958/convert-binance-timestamp-into-valid-datetime
    time_bn = float(ex.binance.get_server_time()['serverTime'])/1000
    time_local = round(time())
    #time_local = datetime.datetime.now()
    #time_local = datetime.utcnow()

    time_diff = time_bn - time_local
    
    if verbose:
        print(f"binance time(s):{time_bn} => {ctime(time_bn)}")
        print(f"local time(s):{time_local} => {ctime(time_local)}")

        print(f"time_diff(s):{time_diff}")

    return time_diff


for cnt in range(1, 10):
    bn_get_time_diff(True)
    #time.sleep(1)