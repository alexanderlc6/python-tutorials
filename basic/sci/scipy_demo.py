import numpy as np
import scipy as sp

A = np.mat('[1 2 3;2 5 6;3 2 6]')
B = np.mat('[5;8;3]')
A.I * B
result = np.linalg.solve(A,B)
print(result)

'''Optimization and Data Statistics'''
import scipy.optimize as opt
import scipy.stats as stats
# Get solution for equation y = x^2 + 5
def getMinY(x):
    return x ** 2 + 5
print(opt.fmin(getMinY, 4))

