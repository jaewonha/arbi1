from classes.Exchanges import Exchanges
from arbi.arbi_common import *
from arbi.arbi_in import *
from arbi.arbi_out import *
from main import *

ex = Exchanges()

#f = open('.config.ini','r')
#config = json.load(f)['remedy']


asset = 'EOS'
if True:
    t_q = 213.8
    t_q_fee = 1433.4
    inTh = 5.8
else:
    t_q_fee = 1333.0 #upbit spot, binance fut short q
    inTh = 3.6
TEST = False

asset_before = get_asset_total(ex, asset)
#arbi_in_withdraw_bn_to_ub(ex, asset, t_q, t_q_fee)
arbi_in_ubSpotSell_bnFutBuy(ex, asset, t_q_fee, inTh, TEST)
asset_after = get_asset_total(ex, asset)
maxUSD = 100
print_arbi_stat(asset_before, asset_after, +inTh, maxUSD, ex.krwPerUsd)