#include "Analyzer.h"
#include <bits/stdc++.h>
using namespace std;

int main(){
    Analyzer analyzer;

    vector <int> test = {100, 80, 60, 70, 75, 85};

    for(int price : test){
        analyzer.update(price);

        cout << "Price: " << price
             << " Span: " << analyzer.getSpan()
             << " Profit: " << analyzer.getMaxProfit()
             << " NGE: " << analyzer.getLastNGE()
             << endl;
    }
}