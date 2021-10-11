from classes.Exchanges import Exchanges
from arbi.arbi_common import *
from arbi.arbi_in import *
from arbi.arbi_out import *
from main import *

ex = Exchanges()

asset = 'EOS'
t_q_fee = 425.4 #upbit spot, binance fut short q
inTh = 3.5
maxUSD = 2000
TEST = False

asset_before = get_asset_total(ex, asset)
arbi_in_ubSpotSell_bnFutBuy(ex, asset, t_q_fee, inTh, TEST)
asset_after = get_asset_total(ex, asset)
print_arbi_stat(asset_before, asset_after, +inTh, maxUSD, ex.krwPerUsd)
