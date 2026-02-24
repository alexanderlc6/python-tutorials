# CoRoutine: Single and micro thread, trigger manually
import time
# Generator function
# def task1():
#     while True:
#         yield 'Hello'
#         time.sleep(1)
# def task2():
#     while True:
#         yield 'God'
#         time.sleep(1)
#
# if __name__ == '__main__':
#     t1 = task1()
#     t2 = task2()
#     print(t1)
#     # print(next(t1))
#     # print(next(t2))
#     # print(next(t1))
#     # print(next(t2))
#
#     while True:
#         try:
#             print(next(t2))
#             print(next(t1))
#         except StopIteration:
#             break

# Using 3rd-party lib - greenlet, should manually switch tasks(e.g. often used in I/O operations)
# import greenlet
# def sing():
#     print('Sing...')
#     g2.switch()
#     print('Sing completed.')
#
# def dance():
#     print('Dance...')
#     print('Dance completed.')
#     g1.switch()
#
# if __name__ == '__main__':
#     # Create coroutine object
#     g1 = greenlet.greenlet(sing)
#     g2 = greenlet.greenlet(dance)
#     g1.switch()
#     g2.switch()

# Using 3rd-party lib - gevent, will auto switch tasks
import gevent
import time

def sing():
    print('Sing...')
    gevent.sleep(3)
    print('Sing completed.')
def dance():
    print('Dance...')
    gevent.sleep(2)
    print('Dance completed.')

if __name__ == '__main__':
    # Create coroutine object
    g1 = gevent.spawn(sing)
    g2 = gevent.spawn(dance)
    # Block until thread completed
    g1.join()
    g2.join()

# joinall()
def sing(name):
    for i in range(5):
        gevent.sleep(1)
        print(f'{name} is Singing for {i} times.')

if __name__ == '__main__':
    # Wait for all co-routine execute completed and then exit
    gevent.joinall([
        gevent.spawn(sing, 'Alex'),
        gevent.spawn(sing, 'Bob'),
    ])

# gevent Monkey plugin
from gevent import monkey
# Replace time.sleep() to gevent.sleep()
monkey.patch_all()
def sing(name):
    for i in range(5):
        time.sleep(1)
        print(f'{name} is Singing for {i} times.')

if __name__ == '__main__':
    # Wait for all co-routine execute completed and then exit
    gevent.joinall([
        gevent.spawn(sing, 'Alex'),
        gevent.spawn(sing, 'Bob'),
    ])
