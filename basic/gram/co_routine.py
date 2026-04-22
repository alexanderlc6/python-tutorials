# CoRoutine: Single and micro thread, trigger manually
import time
from asyncio import create_task
from types import coroutine


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
    # print(next(t1))
    # print(next(t2))
    # print(next(t1))
    # print(next(t2))

    # while True:
    #     try:
    #         print(next(t2))
    #         print(next(t1))
    #     except StopIteration:
    #         break

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
# import gevent
# import time
#
# def sing():
#     print('Sing...')
#     gevent.sleep(3)
#     print('Sing completed.')
# def dance():
#     print('Dance...')
#     gevent.sleep(2)
#     print('Dance completed.')
#
# if __name__ == '__main__':
#     # Create coroutine object
#     g1 = gevent.spawn(sing)
#     g2 = gevent.spawn(dance)
#     # Block until thread completed
#     g1.join()
#     g2.join()
#
# # joinall()
# def sing(name):
#     for i in range(5):
#         gevent.sleep(1)
#         print(f'{name} is Singing for {i} times.')
#
# if __name__ == '__main__':
#     # Wait for all co-routine execute completed and then exit
#     gevent.joinall([
#         gevent.spawn(sing, 'Alex'),
#         gevent.spawn(sing, 'Bob'),
#     ])
#
# # gevent Monkey plugin
# from gevent import monkey
# # Replace time.sleep() to gevent.sleep()
# monkey.patch_all()
# def sing(name):
#     for i in range(5):
#         time.sleep(1)
#         print(f'{name} is Singing for {i} times.')
#
# if __name__ == '__main__':
#     # Wait for all co-routine execute completed and then exit
#     gevent.joinall([
#         gevent.spawn(sing, 'Alex'),
#         gevent.spawn(sing, 'Bob'),
#     ])

# greenlet, gevent, asyncio, yield, async/await
# yield demo
def func1():
    yield 1
    yield from func2()
    yield 2

def func2():
    yield 3
    yield 4

f1 = func1()
for item in f1:
    print(item)

# asyncio demo
import asyncio
# @asyncio.coroutine
# def func1():
#     print(1)
#     # Auto switch to other task in task coroutine list when I/O blocked or network request
#     yield from asyncio.sleep(2)
#     print(2)
#
# @asyncio.coroutine
# def func2():
#     print(3)
#     yield from asyncio.sleep(2)
#     print(4)
#
# tasks = {
#     asyncio.ensure_future(func1()),
#     asyncio.ensure_future(func2())
# }
#
# loop = asyncio.get_event_loop()
# loop.run_util_complete(asyncio.wait(tasks))

# async/await demo
async def func1():
    print(1)
    # Auto switch to other task in task coroutine list when I/O blocked or network request
    await asyncio.sleep(2)
    print(2)

async def func2():
    print(3)
    # Auto switch to other task in task coroutine list when I/O blocked or network request
    await asyncio.sleep(2)
    print(4)

# =====Download operation demo=====
# Normal mode - sync
# import requests
# def download_image(url):
#     print('Start downloading...', url)
#     response = requests.get(url)
#     print('Download completed.')
#     file_name = url.split('-')[-1]
#     with open(file_name, 'wb') as file_obj:
#         file_obj.write(response.content)
#
# if __name__=='__main__':
#     url_list = [
#         'https://www.testin.cn/website/image/pc/brand/pro2info1-12x.png',
#         'https://www.testin.cn/website/image/pc/brand/pro2info1-22x.png'
#     ]
#     for item in url_list:
#         download_image(item)

# Coroutine mode - async
import aiohttp
import asyncio

async def fetch(session, url):
    print('Sending request...')
    async with session.get(url, verify_ssl=False) as response:
        content = await response.content.read()
        file_name = url.split('-')[-1]
        with open(file_name, mode='wb') as file_obj:
            file_obj.write(content)
        print('Download completed.', url)

async def main():
    async with aiohttp.ClientSession() as session:
        url_list = [
            'https://www.testin.cn/website/image/pc/brand/pro2info1-12x.png',
            'https://www.testin.cn/website/image/pc/brand/pro2info1-22x.png'
        ]
        tasks = [asyncio.create_task(fetch(session, url)) for url in url_list]
        await asyncio.wait(tasks)

if __name__ == '__main__':
    asyncio.run(main())

# Event loop(same effect with while True)
# Generate or get existing event loop
# loop = asyncio.get_event_loop()
# Put a task into task list
# loop.run_until_complete((tasks))

# Coroutine object
# async def func():
#     print('Doing...')
#
# # Only define but not execute func()
# ad = func()
# # loop = asyncio.get_event_loop()
# # # Execute the task
# # loop.run_until_complete(ad)
# asyncio.run(ad)

# await object: wait for object e.g. coroutine object, future object, task object, I/O waiting
# import asyncio
# async def func():
#     print('Execute coroutine function code...')
#     response1 = await others()
#     print('Result1:', response1)
#
#     response2 = await others()
#     print('Result2:', response2)
#
# async def others():
#     print('Start...')
#     await asyncio.sleep(2)
#     print('Completed!')
#     return 'Done'

# asyncio.run(func())

# Task object: Used for schedule coroutines concurrently,adding tasks into task list asynchronously
async def func():
    print(1)
    await asyncio.sleep(2)
    print(2)
    return 'Done'

async def main():
    print('main start...')
    task1 = asyncio.create_task(func(), name='task1')
    task2 = asyncio.create_task(func(), name='task2')
    print('main completed.')

    tasks = [task1, task2]

    # res1 = await task1
    # res2 = await task2
    done, pending = await asyncio.wait(tasks, timeout=None)
    print(done)

asyncio.run(main())

# Add tasks before main function create event loop
# async def func():
#     print(1)
#     await asyncio.sleep(2)
#     print(2)
#     return 'Done'
#
# async def main():
#     task_list = [
#         # No event loop yet
#         func(),
#         func()
#     ]
#     # Will create an event loop when asyncio.wait(task_list)
#     done, pending = await asyncio.wait(task_list, timeout=None)
#     print(done)

# Future object
