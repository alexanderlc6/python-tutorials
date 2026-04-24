import multiprocessing
import random
import threading

# Example 1
# class MyThread(threading.Thread):
#     def run(self):
#         print('Execute this thread:', self._args)
#
# t = MyThread(args=(100,))
# t.start()


# Example 2: download page contents
# import requests
# import threading
#
# class DouyinThread(threading.Thread):
#     def run(self):
#         file_name, video_url = self._args
#         res = requests.get(video_url)
#         with open(file_name, mode='wb') as f:
#             f.write(res.content)
#
# url_list = [
#     ('东北P4根伤秀,mp4', 'https://aweme.snssdk,com/aweme/vi/playsm/?video_id=v03001570000bvbmace0gvch71o53oog'),
#     ('卡特拟篮.mp4', 'hetps://aweme.snssdk.com/aweme/vi/piaywm/?video_id=v02001300000bv52fpn5t6p007e34g1g'),
#     ('罗斯vp.mp4', 'https://aweme.snssdk.com/aweme/v1/playwm/?video_id-v0200f240000buuer5aa4tij4gv6ajqg')
# ]
#
# for item in url_list:
#     t = DouyinThread(args=(item[0], item[1]))
#     t.start()

# Use thread pool
# import time
# from concurrent.futures import ThreadPoolExecutor, Future
#
# def task(video_url, num):
#     print('Start task executing:', video_url)
#     time.sleep(5)
#     return random.randint(0, 10)
#
# pool = ThreadPoolExecutor(10)
# future_list = []
#
# url_list = ['www.xxx-{}.com'.format(i) for i in range(200)]
#
# def done(res):
#     print('End...')
#
# for url in url_list:
#     future = pool.submit(task, url, 2)
#     future.add_done_callback(done)
#     future_list.append(future)
#
# pool.shutdown(True)
#
# for ft in future_list:
#     print(ft.result())


# import threading
# def task(row_list):
#     num_list = [int(row.split(',')[-1]) for row in row_list]
#     result = sum(num_list)
#     print(result)
#
# def run():
#     file_object = open('data.txt', mode='r', encoding='utf-8')
#     file_object.readline()
#
#     row_list = []
#     for line in file_object:
#         row_list.append(line.strip())
#         if len(row_list) == 100:
#             t = threading.Thread(target=task, args=(row_list,))
#             t.start()
#             row_list = []
#
#     if row_list:
#         t = threading.Thread(target=task, args=(row_list,))
#         t.start()
#
#     file_object.close()
#
# if __name__ == '__main__':
#     run()

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

import time
import multiprocessing

def task(lock):
    print('Start')
    lock.acquire()
    with open('f1.txt', mode='r', encoding='utf-8') as f:
        current_num = int(f.read())

    print('Queue get value...')
    time.sleep(0.5)
    current_num -= 1

    with open('f1.txt', mode='w', encoding='utf-8') as f:
        f.write(str(current_num))

    lock.release()


if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')
    lock = multiprocessing.RLock()

    process_list = []
    for i in range(10):
        p = multiprocessing.Process(target=task, args=(lock,))
        p.start()
        process_list.append(p)

    # Spawn mode should wait sub-process completed
    # time.sleep(7)
    for item in process_list:
        item.join()