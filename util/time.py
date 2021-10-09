from datetime import datetime, date, timedelta

def utc_to_str(utc_ts_bn, div1000=False, forGraph=False):
    if div1000:
        ts = int(utc_ts_bn)/1000
    else:
        ts = int(utc_ts_bn)
    
    if forGraph:
        return datetime.fromtimestamp(ts).strftime('%Y/%m/%d')
    else:
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        