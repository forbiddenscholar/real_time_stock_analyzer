#include <bits/stdc++.h>
using namespace std;

vector <double> computeNGE(vector <double> & nums){
    int n = nums.size();
    vector <double> result(n);
    stack <double> st;

    for(int i=n-1; i>=0; i--){
        while(!st.empty() && st.top() <= nums[i]){
            st.pop();
        }

        result[i] = st.empty() ? -1.0 : st.top();
        st.push(nums[i]);
    }

    return result;
}

int main() {

    ifstream in("data/output.csv");

    if (!in.is_open()) {
        cout << "Error opening input file\n";
        return 1;
    }

    vector<string> rows;
    vector<double> prices;

    string line;

    // read header
    getline(in, line);

    // read data
    while (getline(in, line)) {
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        
        rows.push_back(line);

        stringstream ss(line);
        string temp;

        getline(ss, temp, ','); // time
        getline(ss, temp, ','); // price

        prices.push_back(stod(temp));
    }

    in.close();

    // compute NGE
    vector<double> nge = computeNGE(prices);

    // write final file
    ofstream out("data/final.csv", ios::trunc);
    if (!out.is_open()) {
        cerr << "Error opening output file data/final.csv\n";
        return 1;
    }

    out << "time,price,span,profit,heap_min,heap_max,best_buy_index,best_sell_index,nge\n";

    for (size_t i = 0; i < rows.size(); i++) {
        out << rows[i] << "," << nge[i] << "\n";
    }

    out.close();

    cout << "NGE processing complete. Output -> data/final.csv\n";

    return 0;
}
