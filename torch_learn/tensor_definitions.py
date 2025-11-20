import torch
a = torch.Tensor([[1, 2], [3, 4]])
print(a)
print(a.type())

a = torch.Tensor(2, 3)
print(a)
print(a.type())

# Some tensor definition types
a = torch.ones(2,2)
a = torch.eye(2,2)
a = torch.zeros(2,2)
print(a)
print(a.type())

# Define shape like 2*3 tensor
b = torch.Tensor(2,3)
b = torch.zeros_like(b)
b = torch.ones_like(b)
print(b)
print(b.type())

# Random tensor
a = torch.rand(2, 2)
print(a)
print(a.type())

# Normal distribution tensor: 5 groups avg value and std
a = torch.normal(mean = 0.0, std = torch.rand(5))
# Random mean
a = torch.normal(mean = torch.rand(5), std = torch.rand(5))
print(a)
print(a.type())

# Uniform distribution tensor
a = torch.Tensor(2, 2).uniform_(-1, 1)
print(a)
print(a.type())

# Generate random sequence(not include the end number)
c = torch.arange(0, 11, 3)
print(c)
print(c.type())

# Get same space gap N number
d = torch.linspace(2, 10, 4)
print(d)
print(d.type())

# Get random sequence samples
e = torch.randperm(10)
print(e)
print(e.type())

#### Use numpy to define tensor ####
import numpy as np
a = np.array([[1,2], [2,3]])
print(a)
f = np.ones_like(torch.Tensor(2,3))
print(f)

######## Tensor attribute type:dtype(uint8,int16),device(storage device name),layout(memory layout object) ########
torch.tensor([1,2,3], dtype=torch.float32, device=torch.device('cpu'))

# Define sparse tensor, coo type: Non-zero elements
# Sparse: 1)Reduce params count.2)Reduce memory cost, only store non-zero elements axis
# indices = torch.tensor([[0,1,1],[2,0,2]])   # Axis values:(0,2),(1,0),(1,2),corresponding with non-zero elements:3,4,5
# values = torch.tensor([3,4,5], dtype=torch.float32) # Specific values
# x = torch.sparse_coo_tensor(i, v, [2,4])    # Specify shape: 2*4 matrix

dev = torch.device('cpu')
# dev = torch.device('cuda:0')    # Specify GPU
# Default definition is dense tensor
a = torch.tensor([2,2], dtype=torch.float32, device=dev)
print(a)

print('=====Sparse tensor:=====')
i = torch.tensor([[0,1,2],[0,1,2]])
v = torch.tensor([1,2,3])
s = torch.sparse_coo_tensor(i,v,(4,4),
                            dtype=torch.float32, device=dev).to_dense()
print(s)



