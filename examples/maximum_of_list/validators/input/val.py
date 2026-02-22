"""---
name:  Complete constraint
---

Checks the basic constraints of the problem:

* $2 \leq n \leq 10^5$
* $1 \leq a_i \leq 10^8$
* All elements will be unique
"""

n = int(input())
a = list(map(int, input().split()))

assert len(a) == n

assert 2 <= n <= 10**5
for ai in a:
    assert 1 <= ai <= 10**8
# Uniqueness
assert len(set(a)) == len(a)