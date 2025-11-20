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
print("10 + 5 = {0}".format(f1(10, 5)))
print("10 - 5 = {0}".format(f2(10, 5)))