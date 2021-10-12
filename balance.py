import numpy as np

from arbi import *
from util.log import *
from main import *


ex = Exchanges()
asset = 'EOS'

log_open('log.txt')
log_asset_total(ex, asset)