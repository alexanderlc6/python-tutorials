import math
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