import asyncio

async def func():
    print('executing...')

result = func()

# Before python 3.7, use:
# loop = asyncio.get_event_loop()
# loop.run_until_complete(result)
# After  python 3.7, use:
asyncio.run(result)

# ===== await I/O executing[co-routine/Future/Task object] =====
# co-routine object
# async def others():
#     print('starting...')
#     response = await asyncio.sleep(2)
#     print('ended', response)
#     return 'Mock value 123'
#
# async def func():
#     print('Executing co-routine function inner code...')
#     response1 = await others()
#     print('I/O request 1 completed, result:', response1)
#
#     response2 = await others()
#     print('I/O request 2 completed, result:', response2)
#
# asyncio.run(func())

# Task object: create multiple task in event loop async to schedule co-routines
# asyncio.create_task()
# import asyncio
# async def func():
#     print(1)
#     await asyncio.sleep(2)
#     print(2)
#     return 'Mock result 111'
#
# async def main():
#     print('Main starting...')
#
#     # Add func() task to event loop
#     # task1 = asyncio.create_task(func())
#     # task2 = asyncio.create_task(func())
#     task_list = [
#         asyncio.create_task(func(), name='t1'),
#         asyncio.create_task(func(), name='t2')
#     ]
#     print('Main result')
#
#     # res1 = await task1
#     # res2 = await task2
#     # print(res1, res2)
#     done, pending = await asyncio.wait(task_list, timeout=None)
#     print(done)
#
# # Will create event loop first
# asyncio.run(main())


# =============== Define tasks first(before event loop created) ===============
# =============== Only use before python 3.11 ====================
# import asyncio
# async def func():
#     print(1)
#     await asyncio.sleep(2)
#     print(2)
#     return 'Mock result 111'

# Only add func() co-routine objects
# task_list = [
#     asyncio.create_task(func()),
#     asyncio.create_task(func())
# ]

# asyncio.wait() will create event loop
# done, pending = await asyncio.wait(task_list)
# print(done)
#
# for task in done:
#     print(task.result())

# Or use invocation as below:
# results = asyncio.run(asyncio.gather(func(), func()))
# print(results)

# Or use method:
# task_list = [
#     func(),
#     func()
# ]
# done, pending = asyncio.run(asyncio.wait(task_list))
# print(done)

async def set_after(fut):
    await asyncio.sleep(2)
    fut.set_result('abc')

async def main():
    loop = asyncio.get_running_loop()
    fut = loop.create_future()
    await loop.create_task(set_after(fut))
    print(fut.result())

    # Convert concurrent.futures future object to asyncio future object
    # fut = loop.run_in_executor(None, func)
    # result = await fut

    data = await fut
    print(data)
asyncio.run(main())

# concurrent.futures.Future: use process pool or thread pool to implement async operation
import time
from concurrent.futures import Future, ThreadPoolExecutor, ProcessPoolExecutor

def func(value):
    time.sleep(1)
    print(value)
    return 1234

pool = ThreadPoolExecutor(max_workers=5)
# pool = ProcessPoolExecutor(max_workers=5)

for i in range(10):
    fut = pool.submit(func, i)
    print(fut)


# ========Async Iterator===========
class Reader(object):
    def __init__(self):
        self.count = 0

    async def readline(self):
        # await asyncio.sleep(1)
        self.count += 1
        if self.count == 100:
            return None

        return self.count

    def __aiter__(self):
        return self

    async def __anext__(self):
        val = await self.readline()
        if val == None:
            raise StopAsyncIteration
        return val

async def func():
    obj = Reader()
    async for item in obj:
        print(item)

asyncio.run(func())

# ======Async context manager ========
class AsyncContextManager:
    def __init__(self, conn):
        self.conn = conn

    async def do_sth(self):
        return 123

    async def __aenter__(self):
        self.conn = await asyncio.sleep(1)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await asyncio.sleep(1)

async def func():
    async with AsyncContextManager() as f:
        result = await f.do_sth()
        print(result)

asyncio.run(func())