from classes.Exchanges import Exchanges
from arbi.arbi_common import *
from arbi.arbi_in import *
from arbi.arbi_out import *
from main import *

ex = Exchanges()

#f = open('.config.ini','r')
#config = json.load(f)['remedy']


asset = 'EOS'
t_q = 2824.3 #303.3
t_q_fee = 1086.8 #upbit spot, binance fut short q
#outTh = 3.5
TEST = False

#asset_before = get_asset_total(ex, asset)
#arbi_out_withdraw_ub_to_bn(ex, asset, t_q)
arbi_out_bnSpotSell_bnFutBuy(ex, asset, t_q, TEST)
#asset_after = get_asset_total(ex, asset)
#maxUSD = 4.475*1086.8
#print_arbi_stat(asset_before, asset_after, +inTh, maxUSD, ex.krwPerUsd)
