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

