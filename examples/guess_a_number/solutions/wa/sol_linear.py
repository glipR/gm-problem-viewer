"""---
name:  WA Try linear
expectation:
- setA: WA
- setB: WA
---

Simple approach that just guesses the first q numbers
"""

import random

for q in range(1, 10001):
    print(q)
    if input() in ["YES", "DONE"]:
        break
