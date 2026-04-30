import numpy as np

# Creation
from numpy.ma.core import ndim
arr = np.array([[1,3,5], [4,1,6]])
print(arr.ndim)
print(arr.shape)
print(arr.T)

arr = np.array([56,92,65,76,63,83,91,82,72])
print('Median:', np.median(arr))
print('Percentile:', np.percentile(arr, 80))
print(np.greater(arr, 60))
print(np.where(arr<60, 'Fail', 'Pass'))
print(np.select([arr>80,(arr>=60) & (arr<=80), arr<60], ['Excellent','Good','Fail'], default='Unknown'))

# Sort
np.random.seed(0)
arr = np.random.randint(1, 100, 20)
print('Raw data', arr)
# Original sort
# arr.sort()
# New sort
print(np.sort(arr))
print('Sorted data:', arr)
print('Sorted indexes:', np.argsort(arr))

# Remove duplicate and sort
print(np.unique(arr))

# Concat
a1 = np.array([1,2,3])
a2 = np.array([4,5,6])
print(np.concatenate([a1,a2]))

# Split
print(np.split(arr, 4))
print(np.split(arr, [6,12,18]))

# Adjust array shape
print(np.reshape(arr, [4,5]))
print(np.reshape(arr, [2,10]))

# Example1: Find the highest and lowest temperature within a week
temps = np.array([[28, 30, 29, 31, 32, 30, 29]])
print(temps)
print('Avg temp:%.3f' % np.mean(temps))
print('Max temp:', np.max(temps))
print('Max temp:', np.min(temps))
print('Days more than 30 degree:', len(temps[temps > 30]))
print(np.cumsum(np.where(temps > 30, 1, 0))[-1])
print(np.count_nonzero(temps > 30))

# Example2:
score = np.array([85, 90, 78, 92,88])
print(score)
print('Average score:', np.mean(score))
print('Median score:', np.median(score))
print('Standard var: %.3f' %np.std(score))
# Convert score to 1-10 unit scope
print(score / 10)

# Example3: matrix calculations
a = np.array([[1,2], [3,4]])
b = np.array([[5,6], [7,8]])
print(a + b)
print(a * b)
print(a @ b)

# Example4: Random data generation
np.random.seed(0)
arr = np.random.randint(0, 10, (3,4))
print(arr)
# axis: 0-column, 1-row
print('Max value in each column:', np.max(arr, axis=0))
print('Min value in each row:', np.min(arr, axis=1))
# Replace each even value to -1
# Method 1
print(np.where(arr % 2 == 1, -1, arr))
# Method 2(e.g. change row numbers: arr[0]=-1, change column numbers: arr[,1]=-1)
arr[arr % 2 == 1] = -1
print(arr)

# Example5: Array reshape
arr = np.arange(1, 13)
print(arr)
arr = np.reshape(arr, [3,4])
print('Reshape to:', arr)
print('Each row sum:', np.sum(arr, axis=1))
print('Each column average:', np.mean(arr, axis=0))
print(np.reshape(arr, (12)))

# Example6: Element replacement
np.random.seed(0)
arr = np.random.randint(0, 20, (5,5))
print(arr)
print(arr[arr > 10])
arr[arr > 10] = 0
print(arr)

# Example7: Statistics
money = np.array([120,135,110,125,130,140])
print('Summary:', np.sum(money))
print('Mean:', np.var(money))
# Find out month of highest and lowest sales amount
print('Max:', np.argmax(money) + 1)
print('Min:', np.argmin(money) + 1)
# Example8: Array concatenation
a = np.array([1,2,3])
b = np.array([4,5,6])
c = np.concatenate([a,b])
print(c)
print(np.reshape(c, (2,3)))

# Example8: Unique value and sort
arr = np.array([2,1,2,3,1,4,3])
u_arr, count = np.unique(arr, return_counts= True)
print(u_arr)
print(count)

d = list()
for i in range(len(u_arr)):
    d.append(len(arr[arr==u_arr[i]]))
print(d)

# Example9: Sales amount calculation
money = np.array([20, 25, 22, 30, 28])
cost = np.array([15, 18, 16, 22, 20])
r = money - cost
# [5 7 6 8 8]
print('Total revenue:', r)
print('Revenue mean:', np.mean(r))
print('Revenue standard deviation:', round(np.std(r), 3))
# [8, 8]
print('Max revenue days:', len(r[r==np.max(r)]))