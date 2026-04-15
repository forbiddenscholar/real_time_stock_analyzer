#ifndef ANALYZER_H
#define ANALYZER_H

#pragma once
#include<bits/stdc++.h>
using namespace std;

class Analyzer{
private :
    stack<pair<double, int>> spanStack; // stock span 
    priority_queue<double> maxHeap;
    priority_queue<double, vector<double>, greater<double>> minHeap;
    
    int currentIndex;

    double minPrice;
    int minPriceIndex;

    double maxProfit;
    int bestBuyDate;
    int bestSellDate;

    int lastSpan;

public : 
    Analyzer();

    void update(double price);

    int getSpan();
    double getMaxProfit();
    int getBestBuyDate();
    int getBestSellDate();
    bool hasBestTrade() const;

    double getHeapMin();
    double getHeapMax();
};

#endif