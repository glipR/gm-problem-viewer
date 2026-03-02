/*---
name: AC
expectation: AC
---
*/

#include <bits/stdc++.h>
using namespace std;

int main() {

    int n;
    cin >> n;

    int m = 0;

    vector<int> a(n, 0);
    for (int i=0; i<n; i++) {
        cin >> a[i];
        m = max(m, a[i]);
    }

    if (a[0] == m) {
        cout << m << " " << a[1] << endl;
    } else {
        cout << m << " " << a[0] << endl;
    }

    return 0;
}
