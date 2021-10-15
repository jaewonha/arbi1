#import pyupbit
from requests.exceptions import ConnectionError, ReadTimeout

import json
import pprint

from datetime import datetime
import time

import signal
import sys
from classes import *
from util.log import *
from arbi import *
from main import *

ex = Exchanges()

lastMin = None
delay = 1
asset ='EOS'
# check asset is listed on futres market

while True:
    now = datetime.now()
    if now.minute != lastMin:
        ex.updateCurrency()
        lastMin = now.minute
        print(f"update krwPerUsd:{ex.krwPerUsd} at min:{lastMin}")
        log_flush()

    ub_p_krw, bn_p_usd, bn_f_usd, kimp = calc_kimp(ex, asset, CHECK_BACKWARD = False)

    print(f"KIMP[IN] :{kimp[IN]}% (UB={toUsd(ex, ub_p_krw[IN])}, BN={bn_p_usd[IN] })")
    print(f"KIMP[OUT]:{kimp[OUT]}% (UB={toUsd(ex, ub_p_krw[OUT])}, BN={bn_p_usd[OUT]}), KIMPDiff:{round(kimp[IN]-kimp[OUT], 2)}%")
    time.sleep(delay)


