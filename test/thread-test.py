import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool
import time

def get_ms():
    return round(time.time() * 1000)

def worker(param):
    #print('worker:' + str(param))
    return param + 1

def start_process():
    print('start process')


def test1():
    POOL_SIZE = 4

    pool = ThreadPool(POOL_SIZE)

    input = [1, 2, 3, 4]
    t0 = get_ms()
    result = pool.map(worker, input)
    t1 = get_ms()
    pool.close()
    t2 = get_ms()
    pool.join()
    t3 = get_ms()

    print(result)
    print(t1-t0)
    print(t2-t1)
    print(t3-t2)

from concurrent.futures import ThreadPoolExecutor

def test2():
    t0 = get_ms()
    executor = ThreadPoolExecutor(max_workers=10)
    t1 = get_ms()
    fut1 = executor.submit(worker, 1)
    fut2 = executor.submit(worker, 2)
    fut3 = executor.submit(worker, 3)
    fut4 = executor.submit(worker, 4)
    t2 = get_ms()
    print(fut4.result())
    t3 = get_ms()
    print(fut2.result())
    t4 = get_ms()
    print(fut3.result())
    t5 = get_ms()
    print(fut1.result())
    t6 = get_ms()

    print("ms")
    print(t1-t0)
    print(t2-t1)
    print(t3-t2)
    print(t4-t3)
    print(t5-t4)
    print(t6-t5)

def test3():
    def say_something (var1, var2, var3):
        print('{}: {} = {}'.format(var1, var2, var3))
        return var3

    pool = ThreadPoolExecutor(2)
    ret1 = pool.submit(lambda p: say_something(*p), ['name', 'Joldnine', 'aa'])
    ret2 = pool.submit(lambda p: say_something(*p), ['email', 'heyhey@hey.com', 'bb'])
    print(ret1.result())
    print(ret2.result())
test3()