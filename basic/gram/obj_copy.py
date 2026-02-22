li = [1,2,3,4]
li2 = li
print(li2)

li.append(5)
print(li)
print(li2)
# Look up memory address(same object)
print("Memory address of li:", id(li))
print("Memory address of li2:", id(li2))

import copy
li = [1,2,3,[4,5,6]]
li2 = copy.copy(li)
print(li)
print(li2)
# Look up memory address(Different, not same object)
print("Memory address of li:", id(li))
print("Memory address of li2:", id(li2))
li.append(8)
print(li)
print(li2)

# Cascade element, same memory address(light copy only for outer layer)
li[3].append(7)
print(li)
print(li2)
print("Memory address of li[3]:", id(li[3]))
print("Memory address of li2[3]:", id(li2[3]))

# Deep copy(data never share, changes not affect original object)
li3 = copy.deepcopy(li)
print(li)
print(li3)
print("Memory address of li[3]:", id(li[3]))
print("Memory address of li3[3]:", id(li3[3]))

li.append(9)
li[3].append(10)
print(li)
print(li3)
print("Memory address of li[3]:", id(li))
print("Memory address of li3[3]:", id(li3))
print("Memory address of li[3]:", id(li[3]))
print("Memory address of li3[3]:", id(li3[3]))