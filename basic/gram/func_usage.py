def add(a,b):
    return a + b
def sub(a,b):
    return a - b
def square(a):
    return a * a

def calc(opr):
    if opr == '+':
        return add
    else:
        return sub
f1 = calc('+')
f2 = calc('-')
print(type(f1))
print("10 + 5 = {0}".format(f1(10, 5)))
print("10 - 5 = {0}".format(f2(10, 5)))

# Filter Function:filter(function, iterable)
def f11(x):
    return x > 50
data1 = [60,34,29,45,66,77,99,12,45]
filtered = filter(f11, data1)
data2 = list(filtered)
print(data2)

def f22(x):
    return x * 2
mapped = map(f22, data1)
data2 = list(mapped)
print(data2)

# Lambda usages
def calcNew(opr):
    if opr == '+':
        return lambda a, b:(a + b)
    else:
        return lambda a, b:(a - b)
f1 = calc('+')
f2 = calc('-')
print(calc('+')(12,10))
print("10 + 5 = {0}".format(f1(10, 5)))
print("10 - 5 = {0}".format(f2(10, 5)))

import re
res = re.match('cd', 'cdabdcde')
print(res)
# Fetch: group()
print(res.group())

# Match single char
# .: match any char
res = re.match('h.l', 'hello')
print(res.group())
# []: match any char listed in the [], only match a char
res = re.match('[he].', 'hello')
print(res.group())

res = re.match('[1-5].', '423')
print(res.group())

res = re.match('[0-9].', '5432')
print(res.group())
res = re.match('[1-45-9].', '5432')
print(res.group())

res = re.match('[a-zA-Z].', 'Hello')
print(res.group())

# \d:Match digit number
res = re.match('.\d\d\d.', 'g543t')
print(res.group())

# \D:Match non-digit number
res = re.match('\D', 'g543t')
print(res.group())

# \s:Match blank(\s\s: one tab)
res = re.match('\s...', '  g543t')
print(res.group())

# \S:Match non-blank
res = re.match('\S..', 't943t')
print(res.group())

# \w:Match word char(a-z,A-Z,0-9,CN char)
res = re.match('\w', 'Alex')
print(res.group())

# \W:Match non word char
res = re.match('\W', '.Alex')
print(res.group())

# Match multiple chars(*:0+ times, +: 1+ times, ?: 0 or 1 time, {m}: match m times, {m,n}: match m~n times)
res = re.match('\w*', 'David.')
print(res.group())

res = re.match('\d+', '124ttr.')
res = re.match('.+', '124ttr.')
print(res.group())

res = re.match('\d?', '124gg')
print(res.group())

res = re.match('\d{3}', '124gg')
print(res.group())

# Should be m < n
res = re.match('\w{3,9}', 'abcded')
print(res.group())

# Match begin and end char(^ and $)
res = re.match('^py', 'python')
print(res.group())
res = re.match('.{4}t$', 'afwet')
print(res.group())

# Not match char(^)
res = re.match('[^ab]', 'egcd')
print(res.group())

# Match any expression
res = re.match("abc|def", 'abc')
print(res.group())
# Left match
res = re.match(".|\d", 'abcd')
print(res.group())

# Group match in ()
res = re.match('\w*@(126|163|qq).com', 'ab@126.com')
print(res.group())

# Match specific num pointed string(1 stands for html)
res = re.match(r'<(\w*)>\w*</\1>', '<html>login</html>')
res = re.match(r'<(\w*)><(\w*)>.*</\2></\1>', '<html><body>login</body></html>')
print(res.group())

# Group with alias
res = re.match(r'<(?P<L1>\w*)><(?P<L2>\w*)>.*</(?P=L2)></(?P=L1)>', '<html><body>login</body></html>')
print(res.group())

# Match web page URL(www,.com,.cn,.org)
li = ['www.baidu.com','www.py.org', 'http.jd.cn', 'www.abc.en','www.dt.cn']
res = re.match(r'www(\.)\w*\1(com|cn|org)','www.baidu.com')
print(res.group())

for i in li:
    res = re.match(r'www(\.)\w*\1(com|cn|org)', i)
    if res:
        print(res.group())
    else:
        print(f'Web page url {i} is error format!')

# search()
res = re.search("\d", 'pyth2onth')
print(res.group())

# findall()
res = re.findall("\d", 'pyt3233h2onth')
# res is list type
print(res)

# sub()
res = re.sub("Alex", 'aa', 'helloAlexAlex', 1)
print(res)

res = re.sub('\d', '2', 'The 30 day of the month', 1)
print(res)

# split()
res = re.split(',', 'hello,Alex,2323,5ggg', 1)
print(res)

# Greed match
res = re.match('et*', 'etttt...')
print(res.group())

# Non-greed match
res = re.match('et?', 'etttt...')
print(res.group())

res = re.match('m+?', 'mmmmm')
res = re.match('m{3,4}?', 'mmmmm')
print(res.group())

# Origin raw string(\\ replace for \)
res = re.match(r'www\.baidu\.com', 'www.baidu.com')
res = re.match(r'\\\\\\', r'\\\game')
print(res.group())