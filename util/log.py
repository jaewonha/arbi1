import datetime

fp = None

def log_open(path):
    global fp

    if path is None:
        dateStr = datetime.today().strftime("%Y%m%d_%H%M%S")
        path = f'./log-{dateStr}.txt'
        
    fp = open(path, "a")

def log_flush():
    if fp:
        fp.flush()

def log_close():
    if fp:
        fp.close()

def log(msg):
    print(msg)
    if fp:
        print(msg, file=fp)