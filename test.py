from arbi import *
from exchange import * #incase need bn_, un_ lower api
from util.log import *
from main import *

ex = Exchanges()

asset = 'ATOM'
maxUSD = 50
OUT_TH = 100.0 #숫자가 작을때 (손해) 나가려고 하니 큰 숫자를 쓰면 무조건 나감
IN_TH = 0.0 #숫자가 클떄 들어오(이득)려고 하니 작은 숫자를 쓰면 무조건 들어옴
TEST = False
TEST_OUT = True
TEST_IN = False

#test
#q = ub_get_spot_balance(ex, ub_krw_pair('boba'))
#print(q)
#exit(0)

if True: #exchange test
    arbi_check_balace(ex, asset, maxUSD) #opt

    if TEST_OUT:
        while True:
            ub_p_krw, bn_p_usd, bn_f_usd, kimp, validity = calc_kimp(ex, asset, maxUSD=maxUSD, CHECK_BACKWARD=False)
            if validity[OUT]: break
    
        print("test out")
        asset_before = get_asset_total(ex, asset) #opt. before calc KIMP
        arbi_out_ub_to_bn(ex, asset, ub_p_krw[OUT], bn_f_usd[OUT], maxUSD, TEST)
        asset_after = get_asset_total(ex, asset)
        print_arbi_stat(asset_before, asset_after, +IN_TH, maxUSD, ex.krwPerUsd)

    if TEST_IN:
        while True:
            ub_p_krw, bn_p_usd, bn_f_usd, kimp, validity = calc_kimp(ex, asset, maxUSD=maxUSD)
            if validity[IN]: break

        print("test in")
        asset_before = get_asset_total(ex, asset) #opt. before calc KIMP
        arbi_in_bn_to_ub(ex, asset, bn_p_usd[IN], bn_f_usd[IN], maxUSD, IN_TH, TEST, True)
        asset_after = get_asset_total(ex, asset)
        print_arbi_stat(asset_before, asset_after, +IN_TH, maxUSD, ex.krwPerUsd)
else: #buy sell test without withdraw
    ub_p_krw, bn_p_usd, bn_f_usd, kimp, _ = calc_kimp(ex, asset)
    #manually sell t_q=0.1!
    t_q, t_q_fee = arbi_in_bnSpotBuy_bnFutShort(ex, asset, bn_p_usd[IN], bn_f_usd[IN], maxUSD, TEST) 
    arbi_out_bnSpotSell_bnFutBuy(ex, asset, t_q_fee, TEST)

    print('wait')

    ub_p_krw, bn_p_usd, bn_f_usd, kimp, _ = calc_kimp(ex, asset)
    t_q = arbi_out_ubSpotBuy_bnFutShort(ex, asset, ub_p_krw[OUT], bn_f_usd[OUT], maxUSD, TEST)
    arbi_in_ubSpotSell_bnFutBuy(ex, asset, t_q_fee, IN_TH, TEST)    
    
print("done")
