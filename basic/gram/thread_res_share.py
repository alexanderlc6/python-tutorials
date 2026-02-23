import threading
from threading import Thread, Lock
import time

# Global share variable
li = []

# Write data
def write_data():
    for i in range(5):
        li.append(i)
        time.sleep(0.2)
    print('Write data:', li)

# Read data
def read_data():
    print("Read data:", li)

if __name__ == '__main__':
    # Create sub thread
    t1 = Thread(target=write_data)
    t2 = Thread(target=read_data)
    t1.start()

    # Block sub thread, or use time.sleep(0.2*5) for same effect
    t1.join()
    t2.start()

# Resource competition
a = 0
b = 1000000

def add(name):
    for i in range(b):
        global a
        a += 1
    # time.sleep(2)
    print(f'{name}-First time:', a)

def add2(name):
    for i in range(b):
        global a
        a += 1
    # time.sleep(2)
    print(f'{name}-Second time:', a)

# Raw invocation method
# add()
# add2()

if __name__ == '__main__':
    t1 = Thread(target=add, args=('Alex',))
    t2 = Thread(target=add2, args=('Alex',))

    # Multiple thread demo
    # Set as daemon thread
    # t1.daemon = True
    # t2.daemon = True
    t1.start()
    t2.start()
    # t1.join()
    # t2.join()
    t1.name = 'TH-01'
    t2.name = 'TH-02'
    print(t1.name)
    print(t2.name)
    print('Completed...')

# Multiple thread with no sequence
def task():
    time.sleep(1)
    print('Current thread is:', threading.current_thread().name)

if __name__ == '__main__':
    for i in range(5):
        t = Thread(target=task)
        t.start()

# Thread synchronization:join() or mutex(acquire(), release() -- must be used in pair, or will be dead lock)
a = 0
b = 1000000
lock = Lock()
def add():
    lock.acquire()
    for i in range(b):
        global a
        a += 1
    print('First time:', a)
    lock.release()

def add2():
    lock.acquire()
    for i in range(b):
        global a
        a += 1
    print('Second time:', a)
    lock.release()

if __name__ == '__main__':
    t1 = Thread(target=add)
    t2 = Thread(target=add2)
    t1.start()
    t2.start() 