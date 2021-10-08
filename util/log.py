

fp = None

def log_open(path):
    global fp
    fp = open(f"log.txt", "a")

def log_flush():
    fp.flush()

def log_close():
    fp.close()

def log(msg):
    print(msg)
    if fp:
        print(msg, file=fp)