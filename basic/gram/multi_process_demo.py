# from multiprocessing import Process,Value,Array
#
# def func(n, m1, m2):
#     n.Value = 555
#     m1.Value = 'a'.encode('utf-8')
#     m2.Value = 'Alex'
#
# def f(data_arr):
#     data_arr[0] = 666
#
# if __name__ == '__main__':
#     num = Value('i', 222)
#     v1 = Value('c')
#     v2 = Value('u')
#
#     arr = Array('i', [11,22,33,44])
#     # p = Process(target=func, args=(num, v1, v2, ))
#     p = Process(target=f, args=(arr,))
#     p.start()
#     p.join()
#
#     print(num.value)
#     print(v1.value)
#     print(v2.value)
#     print(arr[:])
import multiprocessing
# from multiprocessing import Process,Manager
# def func(dict, list):
#     dict[1] = 'a'
#     dict[2] = 23
#     dict[1.25] = None
#     list.append(222)
#
# if __name__ == '__main__':
#     with Manager() as manager:
#         dict = manager.dict()
#         list = manager.list()
#
#         p = Process(target=func, args=(dict, list,))
#         p.start()
#         p.join()
#
#         print(dict)
#         print(list)

# from multiprocessing import Process
# def task(queue):
#     for i in range(10):
#         queue.put(i)
#
# if __name__ == '__main__':
#     queue = multiprocessing.Queue()
#     p = Process(target=task, args=(queue,))
#     p.start()
#     p.join()
#
#     print('Main process:')
#     print(queue.get())
#     print(queue.get())
#     print(queue.get())
#     print(queue.get())
#     print(queue.get())

import time
# import multiprocessing
#
# def task(conn):
#     time.sleep(1)
#     conn.send([11,22,33,44])
#     data = conn.recv()
#     print('Sub-process received:', data)
#     time.sleep(2)
#
# if __name__ == '__main__':
#     parent_conn, child_conn = multiprocessing.Pipe()
#
#     p = multiprocessing.Process(target=task, args=(child_conn, ))
#     p.start()
#
#     info = parent_conn.recv()
#     print('Main process received:', info)
#     parent_conn.send(666)

# import time
# import multiprocessing
#
# def task(lock):
#     print('Start')
#     lock.acquire()
#     with open('f1.txt', mode='r', encoding='utf-8') as f:
#         current_num = int(f.read())
#
#     print('Queueing get value...')
#     time.sleep(0.5)
#     current_num -= 1
#
#     with open('f1.txt', mode='w', encoding='utf-8') as f:
#         f.write(str(current_num))
#
#     lock.release()
#
#
# if __name__ == '__main__':
#     multiprocessing.set_start_method('spawn')
#     lock = multiprocessing.RLock()
#
#     process_list = []
#     for i in range(10):
#         p = multiprocessing.Process(target=task, args=(lock,))
#         p.start()
#         process_list.append(p)
#
#     # Spawn mode should wait sub-process completed
#     # time.sleep(7)
#     for item in process_list:
#         item.join()


# from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
#
# def task(num):
#     print('Executing:', num)
#     time.sleep(2)
#     return num * 5
#
# def done(res):
#     print('done() invoke process:', multiprocessing.current_process().pid)
#     time.sleep(1)
#     print(res.result())
#     time.sleep(1)
#
# if __name__ == '__main__':
#     pool = ProcessPoolExecutor(4)
#     for i in range(10):
#         fur = pool.submit(task, i)
#         # Main process will call done()
#         fur.add_done_callback(done)
#
#     print('Main process:', multiprocessing.current_process().pid)
#     pool.shutdown(True)
#     print('tg1')
#     print('tg2')

import time
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

def task(lock):
    with lock:
        with open('f1.txt', mode='r', encoding='utf-8') as f:
            current_num = int(f.read())

        print('Queueing get value...')
        time.sleep(1)
        current_num -= 1

        with open('f1.txt', mode='w', encoding='utf-8') as f:
            f.write(str(current_num))
        return current_num

if __name__ == '__main__':
    pool = ProcessPoolExecutor()
    manager = multiprocessing.Manager()
    # Cannot use multiprocessing.RLock for ProcessPoolExecutor
    lock_object = manager.RLock()

    for i in range(10):
        fur = pool.submit(task, lock_object)
        print(fur.result())