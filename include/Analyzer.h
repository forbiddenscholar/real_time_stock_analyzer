#ifndef ANALYZER_H
#define ANALYZER_H

#pragma once
#include<bits/stdc++.h>
using namespace std;

class Analyzer{
private :
    stack<pair<int, int>> spanStack; // stock span 
    stack<pair<int, int>> ngeStack; // {price, index}
    vector <int> nge;
    int currentIndex;

    int minPrice;
    int maxProfit;
    int lastSpan;

public : 
    Analyzer();

    void update(int price);

    int getSpan();
    int getMaxProfit();
    int getLastNGE();
    int getNGEAt(int index);
};

#endif