# Example for ayncio + non-async operation
import asyncio
import requests
async def download_img(url):
    print('Start downloading...', url)

    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(None, requests.get, url)

    response = await future
    print('Download complete.')

    file_name = url.split('-')[-1]
    with open(file_name, mode='wb') as file_object:
        file_object.write(response.content)

async def main():
    url_list = [
        'https://www.testin.cn/website/image/pc/brand/pro2info1-12x.png',
        'https://www.testin.cn/website/image/pc/brand/pro2info1-22x.png'
    ]

    # Method 1
    # tasks = [asyncio.create_task(download_img(url)) for url in url_list]
    # done, pending = await asyncio.wait(tasks, timeout=None)
    # print(done)

    # Failed, but why?
    # async with asyncio.TaskGroup() as tg:
    #     for url in url_list:
    #         tg.create_task(download_img(url))

    # Method 2 - Recommended:
    tasks = [asyncio.create_task(download_img(url)) for url in url_list]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())

# ======Below method not available after python 3.10, must declare await in outer function =======
# if __name__ == '__main__':
#     url_list = [
#         'https://www.testin.cn/website/image/pc/brand/pro2info1-12x.png',
#         'https://www.testin.cn/website/image/pc/brand/pro2info1-22x.png'
#     ]

#     tasks = [asyncio.create_task(download_img(url)) for url in url_list]

    # Method 1
    # asyncio.run(asyncio.wait(tasks))

    # Method 2
    # loop = asyncio.get_event_loop()
    # if not loop:
    #     loop = asyncio.new_event_loop()
    # loop.run_until_complete(asyncio.wait(tasks))

    # Method 3
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(asyncio.wait(tasks))
    # loop.close()

    # Method 4
    # tasks = [download_img(url) for url in url_list]
    # asyncio.run(asyncio.gather(*tasks))
