/*---
name: Complete AC
expectation: AC
---

Solution for entire problem

Approach - standard binary search
*/

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int l = 1;
    int r = 100001;

    while (true) {
        int mid = (l + r) / 2;
        cout << mid << endl;  // endl flushes output for interactive judge

        string ans;
        if (!(cin >> ans)) {
            break;  // input ended unexpectedly
        }

        if (ans == "YES") {
            break;
        } else if (ans == "HIGHER") {
            l = mid + 1;
        } else if (ans == "LOWER") {
            r = mid;
        } else if (ans == "DONE") {
            break;
        } else {
            // Unexpected response; terminate.
            break;
        }
    }

    return 0;
}

