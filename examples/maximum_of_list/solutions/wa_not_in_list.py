"""---
name: WA (Second number not in list)
expectation: WA
---
"""

import random

n = int(input())
a = list(map(int, input()))
m = max(a)
print(m, random.randint(1, 1000000))
