"""---
name: RTE Failed Read
expectation: RTE
---
Doesn't split input on read.
"""

import random

n = int(input())
a = list(map(int, input()))
m = max(a)
print(m, random.randint(1, 1000000))
