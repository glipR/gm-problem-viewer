"""---
name:  Set A AC
expectation:
- sample: AC
- setA: AC
- setB: WA
---

Solution for subtask A only - that assumes we have 51 queries available.

Approach - figure out each digit of the number.
"""

import sys

print(100000)
q = input()
if q == "YES":
    sys.exit(0)

digits = [0, 0, 0, 0, 0]
for i in range(5):
    # Figure out the value in digit i
    for v in range(10):
        num = int("".join(map(str, digits)))
        print(num)
        q = input()
        if q == "YES":
            sys.exit(0)
        elif q == "HIGHER":
            continue
        elif q == "LOWER":
            digits[i] = v-1
            break
        else:
            sys.exit(0)
    else:
        digits[i] = 9
