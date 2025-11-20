import numpy as np
a = np.random.rand(2, 4)
print(a)

# Transpose operation
print('Matrix Transpose:')
# Array a example
a = np.transpose(a)
print(a)
# Matrix b example
b = np.random.rand(2,4)
b = np.mat(b)
print(b)
print(b.T)

# Get inverse matrix
print('Matrix Inversion:')
import numpy.linalg as nlg
a = np.random.rand(2, 2)
a = np.mat(a)
print(a)

iva = nlg.inv(a)
print(iva)
print('a * iva:')
print(a * iva)

# Get eig version and eig value
print('=====Get eig version and eig value:===== Matrix is:')
a = np.random.rand(3, 3)
print(a)
eig_value, eig_vector = nlg.eig(a)
print('eigen value:')
print(eig_value)
print('eigen vector:')
print(eig_vector)

# Merge two arrays into a matrix
a = np.array((1,2,3))
b = np.array((2,3,5))
print(np.column_stack((a,b)))

a = np.random.rand(2, 2)
b = np.random.rand(2, 2)
print(a)
print(b)
c = np.hstack([a,b])
d = np.vstack([a,b])
print('Horizontal stacking a and b:')
print(c)
print('Vertical stacking a and b:')
print(d)

# NAN value process
a = np.random.rand(2, 2)
a[0,1] = np.nan
print(a)
print(np.isnan(a))