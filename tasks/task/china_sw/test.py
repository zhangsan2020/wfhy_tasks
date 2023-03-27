from copy import copy

a = [23]
b = [24]
a.extend(b)
print(id(a))
c = copy(a)
print(id(c))