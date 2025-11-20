import numpy as np
# a = np.asmatrix('1,2,3;4,5,6')
# b = np.array([[1,2,3],[4,5,6]])
# np.save('../../data_files/test-a.npy', a)
# np.save('../../data_files/test-b.npy', b)
#
# data_a = np.load('../../data_files/test-a.npy')
# data_b = np.load('../../data_files/test-b.npy')
# print('data_a \n', data_a, '\n the type is:', type(data_a))
# print('data_b \n', data_b, '\n the type is:', type(data_b))
#
# #Save all files within one function
# np.savez('../../data_files/test-ab.npz', k_a = a, k_b = b)
# c = np.load('../../data_files/test-ab.npz')
# print(c['k_a'])
# print(c['k_b'])

# # Read Scipy matrix data
# from scipy import io
# io.savemat('aa.mat', {'matrix': a })
# io.savemat('bb.mat', {'array': b })
# mat_a = io.loadmat('aa.mat')
# for v in mat_a.values():
#     print(v)

''' Array Objects '''
a = np.arange(20)
# print(a)
# print(type(a))

# Reshape operations
a = a.reshape(4, 5)
print(a)
a = a.reshape(2, 2, 5)
print(a)
print('Dimension:' + str(a.ndim))
print('Shape:' + str(a.shape))
print(a.size)
print(a.dtype)

# Define arrays
raw = [0,1,2,3,4]
a = np.array(raw)
print(a)

raw = [[0,1,2,3,4],[5,6,7,8,9]]
b = np.array(raw)
print(b)

d = (4,5)
f = np.zeros(d)
print(f)
f = np.ones(d, dtype=int)
print(f)

rd = np.random.rand(5)
print(rd)

