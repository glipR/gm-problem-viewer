/*---
name: Set A AC
expectation:
  sample: AC
  setA: AC
  setB: WA
---

Solution for subtask A only - that assumes we have 51 queries available.

Approach - figure out each digit of the number.
*/

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    // First query: 100000
    cout << 100000 << endl;
    string q;
    if (!(cin >> q)) {
        return 0;
    }
    if (q == "YES") {
        return 0;
    }

    array<int, 5> digits = {0, 0, 0, 0, 0};

    for (int i = 0; i < 5; ++i) {
        // Figure out the value in digit i
        bool found = false;
        for (int v = 0; v < 10; ++v) {
            int num = 0;
            for (int d = 0; d < 5; ++d) {
                num = num * 10 + digits[d];
            }

            cout << num << endl;
            if (!(cin >> q)) {
                return 0;
            }

            if (q == "YES") {
                return 0;
            } else if (q == "HIGHER") {
                digits[i] ++;
                continue;
            } else if (q == "LOWER") {
                digits[i] = v - 1;
                found = true;
                break;
            } else {
                return 0;
            }
        }
        if (!found) {
            digits[i] = 9;
        }
    }

    return 0;
}

