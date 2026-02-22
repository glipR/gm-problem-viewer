"""---
name:  Complete constraint
---

Checks the basic constraints of the problem:

* 1 <= x <= 100000
* q >= 15
"""

x, q = list(map(int, input().split()))

assert 1 <= x <= 100000
assert q >= 15