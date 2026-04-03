#include <bits/stdc++.h>
using namespace std;

vector <int> computeNGE(vector <int> & nums){
    int n = nums.size();
    vector <int> result(n);
    stack <int> st;

    for(int i=n-1; i>=0; i--){
        while(!st.empty() && st.top() <= nums[i]){
            st.pop();
        }

        result[i] = st.empty() ? -1 : st.top();
        st.push(nums[i]);
    }

    return result;
}

int main() {
    ifstream in("../data/output.csv");

    if (!in.is_open()) {
        cout << "Error opening input file\n";
        return 1;
    }

    vector<string> rows;
    vector<int> prices;

    string line;

    // read header
    getline(in, line);

    // read data
    while (getline(in, line)) {
        rows.push_back(line);

        stringstream ss(line);
        string temp;

        getline(ss, temp, ','); // time
        getline(ss, temp, ','); // price

        prices.push_back(stoi(temp));
    }

    in.close();

    // compute NGE
    vector<int> nge = computeNGE(prices);

    // write final file
    ofstream out("../data/final.csv");

    out << "time,price,span,profit,nge\n";

    for (int i = 0; i < rows.size(); i++) {
        out << rows[i] << "," << nge[i] << "\n";
    }

    out.close();

    cout << "NGE processing complete. Output → data/final.csv\n";

    return 0;
}