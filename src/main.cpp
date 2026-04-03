#include "Analyzer.h"
#include "Stream.h"
#include <bits/stdc++.h>
#include <unistd.h> // for sleep
using namespace std;

int main(){

    vector <int> test = {100, 80, 60, 70, 75, 85};

    Stream stream(test);
    Analyzer analyzer;

    while(stream.hasNext()){
        int price = stream.getNext();

        analyzer.update(price);
        
        cout << "Price : " << price
             << " Span : " << analyzer.getSpan()
             << " Profit : " << analyzer.getMaxProfit()
             << endl;

        sleep(1);
    }

    return 0;
}