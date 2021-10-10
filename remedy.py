from classes.Exchanges import Exchanges
from arbi.arbi_common import *
from arbi.arbi_in import *
from arbi.arbi_out import *
from main import *

ex = Exchanges()

asset = 'EOS'
t_q_fee = 40.6
inTh = 2.65
maxUSD = 1000
TEST = False

asset_before = get_asset_total(ex, asset)
arbi_in_ubSpotSell_bnFutBuy(ex, asset, t_q_fee, inTh, TEST)
asset_after = get_asset_total(ex)
print_arbi_stat(asset_before, asset_after, +inTh, maxUSD, ex.krwPerUsd)
