import torch
import torch.nn as nn

# model = nn.Sequential(nn.Conv2d(1,20,5), nn.ReLU(), nn.Conv2d(20,64,5), nn.ReLU())
model = nn.Sequential(nn.Linear(1,3), nn.ReLU(), nn.Linear(3,1))
print(model)

# Delivery data
distances = torch.tensor([[3.0],[7.0],[12.0],[18.0],[22.0],[28.0]])
print(distances.shape)
# Expects 1 feature per sample
simple_model = nn.Linear(1,1)
output = simple_model(distances)
print(output)

distances = torch.tensor([[3.0,7.0,1.0],[18.0,22.0,2.0]])
simple_model = nn.Linear(3,1)
output = simple_model(distances)
print(output)

single_distances = torch.tensor(25.0)
print(single_distances.shape)
simple_model = nn.Linear(1,1)
print(simple_model)

# Add dimensions
with_batch = single_distances.unsqueeze(0)
print(with_batch)
# Remove dimensions
with_batch = single_distances.squeeze(0)
print(with_batch.shape)

prediction = torch.tensor([[11.9],[23.9],[19.4],[49.2]])
first_pred = prediction[0]
print(first_pred)

first_three_pred = prediction[:3]
print(first_three_pred)

# Get item value
value = prediction[0].item()
print(value)

# Get indexed item by crossing multiple dimensions
data = torch.tensor([[3.0,7.0,1.0],[18.0,22.0,2.0],[11.0,9.0,1.0]])
distances = data[:, 0]
print(distances)

