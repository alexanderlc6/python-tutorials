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
#
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
from multiprocessing import Queue, set_start_method
li = ['aa', 'bb', 'cc', 'dd']
def wdata(q1):
    for i in range(5):
        print(f'Put {i} in the queue.')
        q1.put(i)
        time.sleep(0.2)
    print('Write data:', li)

# Read data
def rdata(q2):
    while True:
        if q2.empty():
            break
        else:
            print('Get data:', q2.get())
    print('Read data:', li)

if __name__ == '__main__':
    # Force use fork mode, only available for macOS/Linux OS
    try:
        set_start_method('fork')
    except RuntimeError:
        pass

    q = Queue()
    p1 = Process(target=wdata, args=(q,))
    p2 = Process(target=rdata, args=(q,))
    p1.start()
    p1.join()
    p2.start()