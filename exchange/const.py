#const
ASK = 0
BID = 1
P = 0
Q = 1

BN_SPOT     = 5010
BN_FUT      = 5011

TRADE_BUY   = 6010
TRADE_SELL  = 6011

FUT_SHORT   = 7010
FUT_LONG    = 7011

## upbit주소경우 api관리 -> 디지털 자산 출금주소 관리에 등록해야 함

#addresses
##eos
ub_eos_addr = 'eosupbitsusr'
ub_eos_memo = '5772f423-5c5a-4361-9678-2e070338fec1'

bn_eos_addr = 'binancecleos'
bn_eos_memo = '109642124'

##trx #not tested
ub_trx_addr = 'TSCaN4rUp3VXcu7Eb6QPmU7Xg2QR1hJkh6' #1confirm
bn_trx_addr = 'TPa9XVdUUj3UeTX8vJ6FYcY8vS3vq9WH1S'

##xrp #not tested
ub_xrp_addr = 'raQwCVAJVqjrVm1Nj5SFRcX8i22BhdC9WA'
ub_xrp_memo = '1047636641'

bn_xrp_addr = 'rEb8TK3gBgk5auZkwc6sHnwrGVJH8DuaLh'
bn_xrp_memo = '100196247'

##doge #not tested
ub_doge_addr = 'DHAuNjyov8KuLxLGQ4C7PbXykYixtKvPhk' #6confirm
bn_doge_addr = 'DCbpph4x46jDtnNp6h648vrWFCJUkCbwG6'

##sc #not tested
ub_sc_addr = '2cba9e8f39146ec5d28247afe74639b0c4edd172e97e20f9fd39fb5ddf0ab7d274a945060d51' #6confirm
bn_sc_addr = '31be1f97f7f71e18a9323c56463ab705cca7e1acff112310e3dbcb22872d4009128eaab766a5'

#storj, #sc -> erc20. #not tested

#flow #not tested
ub_flow_addr = '0x7465574909f5641d'
bn_flow_addr = '0x71ce64836c9caff3'

#atom

#ub mainnet
ub_atom_addr = 'cosmos1hjyde2kfgtl78twvhs53u5j2gcsxrt649nn8j5' #n8j5
ub_atom_memo = '184bc7dbeb8b8f1b' #f1b

#bn atom cosmos
bn_atom_addr = 'cosmos1j8pp7zvcu9z8vd882m284j29fn2dszh05cqvf9' #qvf9
bn_atom_memo = '101078951' #951


#zil

#near

#celo
ub_celo_addr = '0x88a5ea49cc944d22755b77939b8d2fafa37b905f' #b905f
bn_celo_addr = '0xf9d7a88e0e8a32c17dfbe9fa4e374f5d04d3fe8d' #fe8d

#elf, mbl <- no fut on binance

#add asset checklist
#1a. addr & memo 
 #- const.py
 #- bn.py bn_get_asset_addr(), bn_get_asset_memo()
#1b. network type
 # bn_get_asset_network
#2. withdrawl fee
 # bn_get_withdraw_fee(asset):
#3. precision
 # bn_get_precision_pq
 # bn_fut_precision_pq


