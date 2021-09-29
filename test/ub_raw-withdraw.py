import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode

import pprint
import requests

access_key = "p2uhQ8xdqxhEvslccOPkwzreXiuTWysaNTcYigWq"          # 본인 값으로 변경
secret_key = "k55DdoFw2sPRSYGMzB4IzwNna7ywPHYj1562QykN"          # 본인 값으로 변경
server_url = 'https://api.upbit.com'

query = {
    'currency': 'EOS',
}
query_string = urlencode(query)

txids = [
    '9e37c537-6849-4c8b-a134-57313f5dfc5a',
    #...
]
txids_query_string = '&'.join(["txids[]={}".format(txid) for txid in txids])

#query['txids[]'] = txids
#query_string = "{0}&{1}".format(query_string, txids_query_string).encode()
#query_string = "{0}".format(query_string, txids_query_string).encode()
query_string = query_string.encode()

m = hashlib.sha512()
m.update(query_string)
query_hash = m.hexdigest()

payload = {
    'access_key': access_key,
    'nonce': str(uuid.uuid4()),
    'query_hash': query_hash,
    'query_hash_alg': 'SHA512',
}

jwt_token = jwt.encode(payload, secret_key)
authorize_token = 'Bearer {}'.format(jwt_token)
headers = {"Authorization": authorize_token}

res = requests.get(server_url + "/v1/deposits", params=query, headers=headers)

pprint.pprint(res.json())