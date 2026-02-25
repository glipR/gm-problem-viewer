"""---
name:  WA Try random
expectation: WA
---

Simple approach that just guesses numbers at random.
"""

import random

for _ in range(50):
    print(random.randint(1, 10000))
    q = input()
    if q == "YES" or q == "DONE":
        break
