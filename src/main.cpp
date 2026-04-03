#include "Analyzer.h"
#include <bits/stdc++.h>
using namespace std;

int main(){
    Analyzer analyzer;

    vector <int> test = {100, 80, 60, 70, 75, 85};

    for (int i = 0; i < test.size(); i++) {
    analyzer.update(test[i]);
    }

    for (int i=0; i<test.size(); i++){
    cout << "Price: " << test[i]
         << " Span: " << analyzer.getSpan()
         << " Profit: " << analyzer.getMaxProfit()
         << " NGE: " << analyzer.getNGEAt(i)
         << endl;
    }
}