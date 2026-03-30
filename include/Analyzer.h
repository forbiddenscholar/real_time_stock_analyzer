#ifndef ANALYZER_H
#define ANALYZER_H

#include<bits/stdc++.h>
using namespace std;

class Analyzer{
private :
    stack<pair<int, int>> spanStack;
    stack<int> ngeStack;

    int minPrice;
    int maxProfit;
    int lastSpan;
    int lastNGE;

public : 
    Analyzer();

    void update(int price);

    int getSpan();
    int getMaxProfit();
    int getLastNGE();
};

#endif