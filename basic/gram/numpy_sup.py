import numpy as np
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