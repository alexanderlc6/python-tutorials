import torch
# Add
print("===Add===")
a = torch.rand(2,3)
b = torch.rand(2,3)
print(a)
print(b)
print(a + b)
print(a.add(b))
print(torch.add(a,b))
print(a.add_(b))    # Will change a value
print(a)

# Sub
print("===Sub===")
print(torch.sub(a,b))
print(a.sub(b))
print(a.sub_(b))
print(a)

# Multiply
print("===Multiply===")
print(a * b)
print(torch.mul(a,b))
print(a.mul(b))
print(a.mul_(b))
print(a)

# Divide
print("===Divide===")
print(a / b)
print(torch.div(a,b))
print(a.div(b))
print(a.div_(b))
print(a)

# Matrix calculations
print("===Matrix calculations===")
a = torch.ones(2, 1)
b = torch.ones(1, 2)
print(a @ b)
print(a.matmul(b))
print(torch.matmul(a, b))
print(torch.mm(a, b))
print(a.mm(b))

# Multi-dimensions calculation
print("===Multi-dimensions calculation===")
a = torch.ones(1,2,3,4)
b = torch.ones(1,2,4,3)
print(a.matmul(b).shape)

a = torch.Tensor([1,2])
print(torch.pow(a, 2))
print(a.pow(3))
print(a ** 3)
print(a.pow_(2))
print(a)

a = torch.tensor([1,2], dtype=torch.float32)
print(torch.exp(a))
print(torch.exp_(a))

print(a.exp())
print(a.exp_())

a = torch.tensor([10,2], dtype=torch.float32)
print(a)

print(torch.log(a))
print(torch.log_(a))
print(a.log())
print(a.log_())

a = torch.tensor([10,2], dtype=torch.float32)
print(torch.sqrt(a))
print(torch.sqrt_(a))
print(a.sqrt())
print(a.sqrt_())
print(a)

print(torch.log2(a))
print(torch.log10(a))
print(torch.log_(a))

