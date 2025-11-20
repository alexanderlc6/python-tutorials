import numpy as np
from spicy import linalg

# 假设有两位武林高手，我们用向量表示他们不同时间内力分布
# 高手A的内力分布
master_a = np.array([120,150,200])

# 高手B的内力分布
master_b = np.array([130,160,210])

# 使用SciPy的线性代数模块计算他们的内力之和
# 计算高手A、B的内力总和
total_force_a = np.sum(master_a)
total_force_b = np.sum(master_b)

# 比较两位高手的内力大小
if total_force_a > total_force_b:
    print("A's power is larger than B.")
elif total_force_a < total_force_b:
    print("A's power is smaller than B.")
else:
    print("A is equal with B!")