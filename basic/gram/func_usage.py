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