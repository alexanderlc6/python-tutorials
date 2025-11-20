import tkinter as tk
# 1. String variables input and swap
# glass1=input("Glass1:").strip()
# glass2=input("Glass2:").strip()
# temp = ""
#
# temp = glass1
# glass1 = glass2
# glass2 = temp
# print(glass1 + " " + glass2)

# 2.Bool judgement
# a = int(input("Course A score:"))
# b = int(input("Course B score:"))
# c = int(input("Course C score:"))
# a = (a > 90) * 2 + (60 <= a < 90) * 1
# b = (a > 90) * 2 + (60 <= a < 90) * 1
# c = (a > 90) * 2 + (60 <= a < 90) * 1
# score = a+b+c
# print('Total score%d' % score)

# 3. for loop
# e.g. Calculate rabbit amount after n years)
# rabbit = 3
# n = int(input("Input n years:"))
# for i in range(0,n):
#     rabbit *= 2
# print("%d years later, rabbit amount:%d" %(n, rabbit))

# e.g. Summary value for 1+2+3+...+n
# s = 0
# n = int(input("Input last number for summary:"))
# for i in range(0, n):
#     s = s + i+1
# print("Summary is:%d" % s)

# 4.Dictionary
container = {'apple': 'A', 'pear': 'B', "orange": 'C', 'banana':'D'}
print(container)
print(container["pear"])

price = dict()
price['apple']=5
price['pear']=7
price['orange']=11
price['banana']=8
print(price)

# fruit = input("Please search for a fruit:")
# if fruit in price:
#     print('Apple price:%d' %(price['apple']))
# else:
#     print("Not on sale!")

# print("Totay market price list:")
# for fruit in price:
#     print('%s %d Y/Kg' %(fruit, price[fruit]))
# print('')
# n = int(input("Input buy count:"))
# sum_price = 0
#
# for i in range(0, n):
#     fruit = input("Buying fruit [%d] name:" %(i + 1))
#     num = int(input('Buying fruit amount(Kg):%d' %(i+1)))
#
#     if fruit in price:
#         sum_price += price[fruit] * num
# print('Total amount is:%d' %(sum_price))

# List
class1 = ["John", "Bill", "Niki", "Mark", "Mark"]
class2 = ['Tom', 'Linda', 'Bill']
# for name1 in class1:
#     for name2 in class2:
#         if(name1 == name2):
#             print(name1)
str = 'abcde'
tt = set(str)
print(tt)

arr=[1,2,3]
print(set(arr))

yz = (1,4,'ce')
print(set(yz))

dt = { 'aa':1, 'bb':5, 'cc': 9, 'dd':12}
print(set(dt))

st = set(yz)
st.add('2f')
print(st)
st.remove(1)
print(st)

# 交/并/差集
a={1,2,3,4}
b={3,1,5,6}
print(a&b)
print(a.intersection(b))
#Same intersection result
print(b&a)
print(b.intersection(a))

print(a|b)
print(a.union(b))
#Same union result
print(b|a)
print(b.union(a))

print(a-b)
print(a.difference(b))
#Different result
print(b-a)
print(b.difference(a))

# cls1Set = set()
# for i in range(0, len(class1)):
#     cls1Set.add(class1[i])
# cls2Set = set()
# for i in range(0, len(class2)):
#     cls2Set.add(class2[i])
# onlyInCls2 = cls2Set - cls1Set
#
# print("Students only in class2:")
# for name in onlyInCls2:
#     print(name)

#Find duplicate students
# num1=int(input('Input class1 stu count:'))
# class11 = set()
# for i in range(0, num1):
#     name = input('Input stu %d name:'%(i + 1))
#     class11.add(name)
#
# num2=int(input('Input class2 stu count:'))
# class22 = set()
# for i in range(0, num2):
#     name = input('Input stu %d name:'%(i + 1))
#     class22.add(name)
#
# sameStuList = class11 & class22
# print('Duplicate students:')
# for name in sameStuList:
#     print(name)


def rect_area(width = 400, height=500):
    area = width * height
    return area

r_area = rect_area(320, 480)
# r_area = rect_area(height=480, width=320)
# r_area = rect_area()
print("{0} * {1} Area is:{2:.2f}".format(320, 480, r_area))

#可变参数(*或**修饰定义)
#基于元祖的可变参数
def sum(*numbers):
    total = 0.0
    for num in numbers:
        total += num
    return total

print(sum(100.0,40.0,24.0))
print(sum(42.0,120.0))

#基于字典的可变参数
def show_info(**info):
    print('=====show info=====')
    for key,value in info.items():
        print('{0}-{1}'.format(key, value))

show_info(name='Jack', age=21, sex=True)
show_info(stu_name='Linda', stu_no='233313')

#Variable functional zone
x = 20
def print_value():
    x = 10
    print("In function var x={0}".format(x))

print_value()
print('Global var x={0}'.format(x))

a='Hello'
# Sequence
print(a[-5])
print(a * 2 + '**')

#Section:[start:end:step]-not include [end] index
print(a[1:3])
print(a[:3])
print(a[0:])
print(a[0:4])
print(a[:])
print(a[1:-1])
print(a[0:3:2])
print('e' in a)
print('E' in a)

myList = list('hello')  #['h','e','l','l','o']
print(myList)
a=[]
print(type(a))
myList.append('G')
print(myList)

t = [1,2,3]
myList += t
print(myList)
myList.extend(t)
print(myList)

#Add element
lst = [20,10,40,80]
lst.insert(2,89)
print(lst)

#Update element
lst[1]=78
print(lst)

#Remove element
lst.remove(40)
print(lst)

#Tuple
tt = (12,32,43,55)
print(tt)

tg = tuple([1,4,5,3,7])
print(tg)

tg= 1,
print(tg)
print(type(tg))

a = ()
a = 1,3,4,5,6
print(type(a))
a = (4,3,2)
print(type(a))

s_id, s_name = (102, 'Alex')
print(s_name)

st = set('hello')
print(st)
st = {30,14,15,14,29}
print(st)

#dict
b = {}
print(type(b))

b = {12,342,14}
b.add('acd')
print(b)
print(12 in b)
b.remove(14)
print(b)
b.clear()

#dict
d = dict({'A':12, 'B':35, 'C':98})
print(d)
d = dict(((10, 'a'), (11, 'b'), (12, 'c')))
print(d)
print(d[10])

d[15]='ddc'
print(d)

d.pop(11)
print(d)

d = dict([(10, 'a'), (11, 'b'), (12, 'c')])
print(d)
d = dict(zip([10,11,12],['a','b','c']))
print(d)

print(list(d.items()))
print(list(d.keys()))
print(list(d.values()))

# root = tk.Tk()
# root.title("Test multi input")
#
# def submit():
#     in1 = tk.Entry(root)
#     in2 = tk.Entry(root)
#     in3 = tk.Entry(root)
#     in1.pack()
#     in2.pack()
#     in3.pack()
#     print(f"Input result:{in1},{in2},{in3}")
