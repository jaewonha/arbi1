from classes.Exchanges import Exchanges
from arbi.arbi_common import *
from arbi.arbi_in import *
from arbi.arbi_out import *
from main import *

ex = Exchanges()

asset = 'EOS'
t_q_fee = 207.6 + 206.3 + 206.3
inTh = 2.45
maxUSD = 1000
TEST = False

asset_before = [34288.62, 13584.6, 6079.52, 53952.74]
#arbi_in_ubSpotSell_bnFutBuy(ex, asset, t_q_fee, inTh, TEST)
asset_after = get_asset_total(ex)
print_arbi_stat(asset_before, asset_after, +inTh, maxUSD, ex.krwPerUsd)
