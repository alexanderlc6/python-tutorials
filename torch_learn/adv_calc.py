import torch
rd = torch.rand(2,1,1) + torch.rand(3)
print(rd)

a = torch.rand(2,3)
b = torch.rand(3)   # or rand(1) --> right-align rule
c = a + b

print('====Special case:====')
a = torch.rand(2,1,1,3)
b = torch.rand(4,2,3)
c = a + b
print(a)
print(b)
print('Result matrix is 2*4*2*3:')
print(c)
print(c.shape)