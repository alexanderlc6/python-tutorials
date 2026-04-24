import threading
import time
from multiprocessing import Process
import os

# def sing():
#     print('Sing Process id:', os.getpid())
#     print('Sing Parent Process id', os.getppid())
#     print('Sing...')
#
# def dance():
#     print('Dance Process id:', os.getpid())
#     print('Dance Parent Process id', os.getppid())
#     print('Dance...')

# if __name__ == '__main__':
#     print('Main thread ID:', os.getpid())
#     print('Main thread parent thread ID:', os.getppid())
#     p1 = Process(target=sing, name='sub-process1')
#     p2 = Process(target=dance, name='sub-process2')
#     p1.start()
#     p2.start()
#     print('p1:', p1.name, p1.pid)
#     print('p2:', p2.name, p2.pid)

# def eat(name):
#     print(f'{name} eating...')
# def sleep(name):
#     print(f'{name} sleeping...')
#
# if __name__ == '__main__':
#     p1 = Process(target=eat, args = ('Alex',))
#     p2 = Process(target=sleep, args = ('Bob',))
#     p1.start()
#
#     # Main thread is waiting while join(), p1 thread is running
#     p1.join()
#     p2.start()
#     p2.join()
#     print('p1 status:', p1.is_alive())
#     print('p2 status:', p2.is_alive())

# Processes not share global variable, e.g. below
# li = []
# def wdata():
#     for i in range(5):
#         li.append(i)
#         time.sleep(0.2)
#     print('Write data:', li)
#
# # Read data
# def rdata():
#     print('Read data:', li)
#
# if __name__ == '__main__':
#     p1 = Process(target=wdata)
#     p2 = Process(target=rdata)
#     p1.start()
#     p1.join()
#     p2.start()

# Process communications via Queue: FIFO sequence
# from multiprocessing import Queue
# q = Queue(maxsize=3)
# q.put('a')
# q.put('b')
# q.put('c')
# print('Is full?',q.full())
# # print(q.qsize())
# print(q.get())
# print(q.get())
# print(q.empty())
# print(q.get())
# print(q.empty())
# # print(q.qsize())

# Refactoring with Queue
# from multiprocessing import Queue, set_start_method
# li = ['aa', 'bb', 'cc', 'dd']
# def wdata(q1):
#     for i in range(5):
#         print(f'Put {i} in the queue.')
#         q1.put(i)
#         time.sleep(0.2)
#     print('Write data:', li)
#
# # Read data
# def rdata(q2):
#     while True:
#         if q2.empty():
#             break
#         else:
#             print('Get data:', q2.get())
#     print('Read data:', li)
#
# if __name__ == '__main__':
#     # Force use fork mode, only available for macOS/Linux OS
#     try:
#         set_start_method('spawn')
#     except RuntimeError:
#         pass
#
#     q = Queue()
#     p1 = Process(target=wdata, args=(q,))
#     p2 = Process(target=rdata, args=(q,))
#     p1.start()
#     p1.join()
#     p2.start()

# import multiprocessing
#
# def task(start, end, queue):
#     result = 0
#     for i in range(start,end):
#         result += i
#     queue.put(result)
#
# if __name__ == '__main__':
#     queue = multiprocessing.Queue()
#     start_time = time.time()
#
#     p1 = multiprocessing.Process(target=task, args=(0, 50000, queue))
#     p1.start()
#
#     p2 = multiprocessing.Process(target=task, args=(50000, 100000, queue))
#     p2.start()
#
#     v1 = queue.get(block=True)
#     v2 = queue.get(block=True)
#     print(v1 + v2)
#
#     end_time = time.time()
#     print('Time cost:', end_time - start_time)

# File sub-process demo
# import multiprocessing
# def task():
#     print(name)
#     file_object.write('David\n')
#     file_object.flush()
#
# if __name__ == '__main__':
#     multiprocessing.set_start_method('fork')
#
#     name = []
#     file_object = open('x1.txt', mode='a+', encoding='utf-8')
#     file_object.write('Alex\n')
#     # file_object.flush()
#
#     p1 = multiprocessing.Process(target=task)
#     p1.start()
#
#     #Output:
#     # Alex
#     # David
#     # Alex

import multiprocessing
import os
import threading

def func():
    # All sub threads will pending here, wait release of lock in the sub-process
    print('Pending...')
    with lock:
        print(777)
        time.sleep(1)

def task():
    print('Current sub-process:', os.getpid(), multiprocessing.current_process().name)
    print('Parent Process ID:', os.getppid())
    print(lock)

    for i in range(10):
        t = threading.Thread(target=func)
        t.start()
    print('Thread count:', len(threading.enumerate()))
    time.sleep(2)
    lock.release()

    lock.acquire()
    print(666)

if __name__ == '__main__':
    print('Main Process:', os.getpid())
    print(multiprocessing.cpu_count())
    multiprocessing.set_start_method('spawn')

    name = []
    lock = threading.RLock()
    lock.acquire()

    p1 = multiprocessing.Process(target=task)
    p1.name = 'test-fork-lock'
    # Set true if sub-process end with parent process(Default is False - main process will wait for complete of sub-process)
    p1.daemon = True
    p1.start()
