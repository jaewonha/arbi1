import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode

import pprint
import requests

#access_key = "p2uhQ8xdqxhEvslccOPkwzreXiuTWysaNTcYigWq"          # 본인 값으로 변경
#secret_key = "k55DdoFw2sPRSYGMzB4IzwNna7ywPHYj1562QykN"          # 본인 값으로 변경
server_url = 'https://api.upbit.com'

def ub_raw_get_deposit(acc_key, sec_key, txid, asset):
    query = {
        'currency': asset
    }
    query_string = urlencode(query)

    txids = [txid]
    txids_query_string = '&'.join(["txids[]={}".format(txid) for txid in txids])

    query['txids[]'] = txids
    query_string = "{0}&{1}".format(query_string, txids_query_string).encode()
    #query_string = "{0}".format(query_string).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': acc_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, sec_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(server_url + "/v1/deposits", params=query, headers=headers)

    #pprint.pprint(res.json())
    return res.json()


def ub_raw_get_withdraw(acc_key, sec_key, txid, asset):
    query = {
        'currency': asset
    }
    query_string = urlencode(query)

    txids = [txid]
    txids_query_string = '&'.join(["txids[]={}".format(txid) for txid in txids])

    query['txids[]'] = txids
    query_string = "{0}&{1}".format(query_string, txids_query_string).encode()
    #query_string = "{0}".format(query_string).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': acc_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, sec_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(server_url + "/v1/withdraws", params=query, headers=headers)

    #pprint.pprint(res.json())
    return res.json()

if __name__ == "__main__":
    ub_acc_key = "p2uhQ8xdqxhEvslccOPkwzreXiuTWysaNTcYigWq"          # 본인 값으로 변경
    ub_sec_key = "k55DdoFw2sPRSYGMzB4IzwNna7ywPHYj1562QykN"          # 본인 값으로 변경
    asset = "EOS"
    #print(ub_raw_get_deposit(acc_key, sec_key, 'EOS'))
    print(ub_raw_get_deposit(ub_acc_key, ub_sec_key, '3db0d30279011cca22e32c52876d02877ceb400362a52fbc093cac498b454fe4', asset))
    print(ub_raw_get_withdraw(ub_acc_key, ub_sec_key, '7e7d101e64b2b319c5311c282547d8540dff666d0db1bce9c42b9727c198f515', asset))

