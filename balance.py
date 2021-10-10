import numpy as np

from arbi import *
from util.log import *
from main import *


ex = Exchanges()
asset = 'EOS'

log_open('log.txt')
log(f"date:{datetime.now().strftime('%Y%m%d_%H%M%S')}")

asset_total = get_asset_total(ex, asset) #opt. before calc KIMP
log(f"balance:{asset_total}=>{np.sum(asset_total)}")