from classes.Exchanges import Exchanges
from arbi.arbi_common import *
from arbi.arbi_in import *
from arbi.arbi_out import *

ex = Exchanges()

asset = 'EOS'
t_q_fee = 213.2
inTh = 2.7
TEST = False
arbi_in_ubSpotSell_bnFutBuy(ex, asset, t_q_fee, inTh, TEST)
