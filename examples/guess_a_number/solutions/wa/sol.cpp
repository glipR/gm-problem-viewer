/*---
name: WA Try random
expectation: WA
---

Simple approach that just guesses numbers at random.
*/

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    mt19937 rng((uint32_t)chrono::steady_clock::now().time_since_epoch().count());
    uniform_int_distribution<int> dist(1, 10000);

    for (int i = 0; i < 50; ++i) {
        int guess = dist(rng);
        cout << guess << endl;  // flush for interactive judge

        string q;
        if (!(cin >> q)) {
            break;  // input ended unexpectedly
        }

        if (q == "YES" || q == "DONE") {
            break;
        }
    }

    return 0;
}

