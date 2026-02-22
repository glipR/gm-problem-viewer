"""---
name: TLE (random crap on input list)
expectation: TLE
---
"""

import random

n = int(input())
a = list(map(int, input().split()))
i = 0
for v1 in a:
    for v2 in a:
        i += 1
m = max(a)
if a[0] == m:
    print(m, a[1])
else:
    print(m, a[0])
