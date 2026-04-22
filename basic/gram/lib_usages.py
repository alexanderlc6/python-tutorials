import math
import time

print(math.ceil(2.3))
print(math.floor(2.3))
print(math.ceil(-2.3))
print(math.floor(-2.3))
print(math.pow(5,3))
print(math.sqrt(3.6))
print(math.log(math.e))
print(math.log(125, 5))
print(math.log10(125))
print(math.degrees(math.pi/2))

import datetime
d = datetime.datetime(2024, 2, 13)
print(d)
d = datetime.datetime(2024, 2, 13, 12, 30, 45, 10000)
print(d)
d = datetime.datetime.now()
print(d)
# Methods
print(datetime.datetime.today())
print(datetime.datetime.fromtimestamp(899292981.289, tz = None))

dt = datetime.date(2024, 2, 16)
print(dt)
print(datetime.date.today())
print(datetime.date.fromtimestamp(899292981.289))
print(datetime.time(3, 58, 59, 38999))

td = datetime.date.today()
tmDelta = datetime.timedelta(10)
td += tmDelta
print(td)
tmDelta = datetime.timedelta(weeks=5)
td -= tmDelta
print(td)

tdtm = datetime.datetime.today()
print(tdtm.strftime('%Y-%m-%d %H:%M:%S'))
print(tdtm.strftime('%Y-%m-%d'))

str_date = '2024-02-19 15:56:01'
print(datetime.datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S'))

# Regular Expressions
import re
p = r'\w+@star-tech\.com'
email = 'alexlu@star-tech.com'
m = re.match(p, email)
# <class 're.Match'>
print(type(m))
# <re.Match object; span=(0, 20), match='alexlu@star-tech.com'>
print(m)

email = 'alex.lu@126.com'
m = re.match(p, email)
# None
print(m)

# Find
text = 'we send a email to the address alexlu@star-tech.com'
m = re.search(p, text)
print(m)

p = r'Java|java|JAVA'
text = 'I like Java and java and JAVA.'
match_list = re.findall(p, text)
print(match_list)

pt = r'\d+'
text = 'ABC123D563EF'
replace_text = re.sub(pt, '*', text)
print(replace_text)
replace_text = re.sub(pt, '*', text, count=1)
print(replace_text)

split_text = re.split(pt, text, maxsplit=1)
print(split_text)

# Inner functions and constant variables
import builtins
print(dir(builtins))
print(abs(-10))
print(abs(10))

print(sum([1,2,3]))
print(sum((1,2,3)))
print(min(1,5,4))
print(max(1,5,4))
print(min(-8, 5, key=abs))
print(max(-8, 5, key=abs))

li = [1,2,3]
li2 = ['a', 'b']
print(zip(li, li2))

for i in zip(li, li2):
    print(i, type(i))
# Result:
# (1, 'a') <class 'tuple'>
# (2, 'b') <class 'tuple'>

# Convert to List
print(list(zip(li, li2)))

# Mapping function:map(func, iter1), execute func for each element of the List object
# def func(x):
#     return x * 5
func = lambda x : x * 5
mp = map(func, li)
print(mp)
# for i in mp:
#     print(i)

print(list(mp))

# Reduce usage - accumulate value result: reduce(func, sequence)
from functools import reduce
def add(x, y):
    return x + 2 * y
res = reduce(add, li)
print(res)

# Split package data
tua = (1,2,3,4)
print(tua)
a,b,c,d = tua
print(a,b,c,d)

# b is *args
a, *b = tua
print(a,b)
c,d,e = b
print(c,d,e)
c,*d = b
print(c,d)

def funa(a,b,*args):
    print(a,b)
    print(args, type(args))

funa(1,2,3,4,5,6,7)

args = (1,2,3,4,5,6,7)
funa(*args)

# os module
import os
print(os.name)
print(os.getenv('PATH'))
print(type(os.path.split('/Users/alexlc/Products/src/AI/python-tutorials/basic/gram/lib_usages.py')))
print(os.path.dirname('/Users/alexlc/Products/src/AI/python-tutorials/basic/gram/lib_usages.py'))
print(os.path.basename('/Users/alexlc/Products/src/AI/python-tutorials/basic/gram/lib_usages.py'))
print(os.path.exists('/Users/alexlc/Products/src/AI/python-tutorials/basic/gram'))
print(os.path.isdir('/Users/alexlc/Products/src/AI/python-tutorials/basic/gram'))
print(os.path.isfile('/Users/alexlc/Products/src/AI/python-tutorials/basic/gram/lib_usages.py'))
print(os.path.abspath('lib_usages.py'))
print(os.path.isabs('lib_usages.py'))

# sys module
import sys
print(sys.getdefaultencoding())
# Current work dir
print(sys.path[0])
print(sys.platform)
# Get python interpreter version
print(sys.version)

# time module
# Delay seconds
time.sleep(1)
# Timestamp, Formatted time
print(time.time())
t = time.localtime()
print(type(t))
print(t.tm_wday)
print(time.asctime(t))
print(time.ctime())
t = time.time()
print(time.ctime(t))

# Time conversion(struct_time <=> time)
print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
print(time.strptime('2024-02-19 15:56:01', '%Y-%m-%d %H:%M:%S'))

# logging module
import logging
# Log level: DEBUG, INFO, WARNING(default log level), ERROR, CRITICAL
logging.basicConfig(filename='log.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logging.debug('Debuging...')
logging.info('Info...')
logging.warning('Warning...')
logging.error('Error occurring...')
logging.critical('Critical error occurring...')

# random module
import random
print(random.random())
print(random.uniform(1,3))
print(random.randint(1,4))
print(random.randrange(2,6, 2))
