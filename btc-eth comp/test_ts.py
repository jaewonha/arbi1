from datetime import datetime
import time

s_ep_ts = time.time()
i_ep_ts = int(s_ep_ts)

s_ts = '1631695373749'
i_ts = int(s_ts)/1000

print(s_ep_ts)
print(s_ts)
print('\n')

print(i_ep_ts)
print(i_ts)
print('\n')

diff = i_ts - i_ep_ts
print(diff)
print('\n')

#print(time.ctime(i_ts))

print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(i_ep_ts)))
print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(i_ts)))
