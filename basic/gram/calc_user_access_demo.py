import os
import time
from multiprocessing import Manager
from concurrent.futures import ProcessPoolExecutor

# def task(file_name, count_dict):
#     ip_set = set()
#     total_count = 0
#     ip_count = 0
#     file_path = os.path.join('../../resources/test_logs', file_name)
#     file_object = open(file_path, mode='r', encoding='utf-8')
#     for line in file_object:
#         if not line.strip():
#             continue
#         user_ip = line.split(' - -', maxsplit=1)[0].split(',')[0]
#         total_count += 1
#         if user_ip in ip_set:
#             continue
#         ip_count += 1
#         ip_set.add(user_ip)
#
#     count_dict[file_name] = {'total': total_count, 'ip': ip_count}
#     time.sleep(1)
#
#
# def run1():
#     pool = ProcessPoolExecutor(4)
#     with Manager() as manager:
#         count_dict = manager.dict()
#
#         for file_name in os.listdir('../../resources/test_logs'):
#             pool.submit(task, file_name, count_dict)
#         pool.shutdown(True)
#
#         for k, v in count_dict.items():
#             print(k, v)

# if __name__ == '__main__':
#     run1()

def run2():
    info = {}
    pool = ProcessPoolExecutor(4)

    for file_name in os.listdir('../../resources/test_logs'):
        fur = pool.submit(task, file_name)
        fur.add_done_callback(outer(info, file_name))

    pool.shutdown(True)
    for k, v in info.items():
        print(k, v)


def task(file_name):
    ip_set = set()
    total_count = 0
    ip_count = 0
    file_path = os.path.join('../../resources/test_logs', file_name)
    file_object = open(file_path, mode='r', encoding='utf-8')
    for line in file_object:
        if not line.strip():
            continue
        user_ip = line.split(' - -', maxsplit=1)[0].split(',')[0]
        total_count += 1
        if user_ip in ip_set:
            continue
        ip_count += 1
        ip_set.add(user_ip)

    time.sleep(1)
    return {'total': total_count, 'ip': ip_count}

def outer(info, file_name):
    def done(res, *args, **kwargs):
        info[file_name] = res.result()

    return done

if __name__ == '__main__':
    run2()

    