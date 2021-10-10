from arbi import *
from util.log import *
from main import *


ex = Exchanges()

asset = 'EOS'
maxUSD = 20
OUT_TH = 100.0 #숫자가 작을때 (손해) 나가려고 하니 큰 숫자를 쓰면 무조건 나감
IN_TH = 0.0 #숫자가 클떄 들어오(이득)려고 하니 작은 숫자를 쓰면 무조건 들어옴
ORDER_TEST = False

arbi_check_balace(ex, asset, maxUSD) #opt
ub_p_krw, bn_p_usd, bn_f_usd, kimp = calc_kimp(ex, asset)

print("test in")
asset_before = get_asset_total(ex, asset) #opt. before calc KIMP
arbi_in_bn_to_ub(ex, asset, bn_p_usd[IN], bn_f_usd[IN], maxUSD, IN_TH, ORDER_TEST, True)
asset_after = get_asset_total(ex, asset)
print_arbi_stat(asset_before, asset_after, +IN_TH, maxUSD, ex.krwPerUsd)

print("test out")
asset_before = get_asset_total(ex, asset) #opt. before calc KIMP
arbi_out_ub_to_bn(ex, asset, ub_p_krw[OUT], bn_f_usd[OUT], maxUSD, ORDER_TEST)
asset_after = get_asset_total(ex, asset)
print_arbi_stat(asset_before, asset_after, +IN_TH, maxUSD, ex.krwPerUsd)

print("done")
