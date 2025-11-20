import urllib.request

#下载网页内容
def download_html(url):
    header = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                     " AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/132.0.0.0 Safari/537.36"
    }

    req = urllib.request.Request(url=url,headers=header)
    response = urllib.request.urlopen(req)
    html = response.read().decode('utf-8')
    return html

url = 'https://movie.douban.com/top250'
html = download_html(url)

import re

#网页内容提取
def extract_html(html):
    pattern = 'https://movie.douban.com/subject/[0-9]+/'
    urls = re.findall(pattern, html)
    # urls = set(urls)
    # print('urls count=%d'%len(urls))
    return set(urls)

file = open('../../resources/douban.txt','r')
output = open('../../resources/movies.txt','w')
lines = file.readlines()

for url in lines:
    url = url.strip()
    print(url)

    html = download_html(url)
    urls = extract_html(html)

    for url in urls:
        output.write(url + '\n')

file.close()
output.close()