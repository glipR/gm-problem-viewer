"""---
name:  Complete wrong boundary
expectation: WA
---

Solution for entire problem, however the right boundary is off.

Approach - standard binary search. But it ignores 100000 as an option.
"""

l = 1
r = 100000

while True:
    mid = (l + r) // 2
    print(mid)
    ans = input()
    if ans == "YES":
        break
    elif ans == "HIGHER":
        l = mid + 1
    elif ans == "LOWER":
        r = mid
    elif ans == "DONE":
        break
    else:
        raise ValueError("???")
