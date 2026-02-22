"""---
name: AC
expectation: AC
---
"""

n = int(input())
a = list(map(int, input().split()))
m = max(a)
if a[0] == m:
    print(m, a[1])
else:
    print(m, a[0])
