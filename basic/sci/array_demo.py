import numpy as np

# Array operations
a = np.array([[1.0, 2], [2,4]])
print(a)
b = np.array([[3.5, 1.1], [2.2, 4.2]])
print(b)
# Plus/Minus/Multiply/Divide operations(with scalars,arrays)
print(a + b)
print(a - b)
print(2 * a)
print(b + 1.2)
a /= 2
print(a)

# Other operations(sqrt, power)
print(np.exp(a))
print(np.sqrt(a))
print(np.power(a, 3))
print(np.square(a))

# Get specific elements from array
a = np.arange(20).reshape(4,5)
print(a)
print('Sum result:' + str(a.sum()))
print('Max:' + str(a.max()))
print('Min:' + str(a.min()))
print('Max element in each row:' + str(a.max(axis=1)))
print('Min element in each row:' + str(a.min(axis=0)))

# Support for matrix operation(2 conversion methods)
d = np.arange(20).reshape(4,5)
d = np.asmatrix(d)
print(type(d))
m = np.matrix('1.0 2.0;4.0 5.0')
print(type(m))

m = np.arange(2, 45, 3).reshape(5,3)
m = np.mat(m)
print(m)

t = np.linspace(0, 2, 9)
print(t)

print('Matrix multiply')
print(d * m)

# Array elements access
a = np.array([[3.1,1.4], [2.9, 5]])
print(a[0][1])
print(a[0,1])

b = a
a[0][1] = 4.7
print(a)
print(b) #Changed with a

b = a.copy()
a[0][1] = 4.5
print(a)
print(b) #Not change

# Get specific column data
print('Get all rows data for column 2 to 4:')
a = np.arange(20).reshape(4, 5)
print(a[:,[1,3]])

print('Get column 3 data with the condition of first column data > 5:')
print(a[:, 2][a[:, 0] > 5])

print('Get certain position element:')
loc = np.where(a == 11)
print(loc)
print(a[loc[0][0], loc[1][0]])
