#include "Analyzer.h"
#include <bits/stdc++.h>

Analyzer::Analyzer(){
    minPrice = DBL_MAX;
    minPriceIndex = -1;
    maxProfit = 0.0;
    bestBuyDate = -1;
    bestSellDate = -1;
    lastSpan = 0;
    currentIndex = 0;

}

void Analyzer::update(double price){
    
    // stock span
    int span = 1;
    while(!spanStack.empty() && spanStack.top().first <= price){
        span += spanStack.top().second;
        spanStack.pop();
    }

    spanStack.push({price, span});
    lastSpan = span;

    // profit and Best Trade
    if (price < minPrice) {
        minPrice = price;
        minPriceIndex = currentIndex;
    }

    if (price - minPrice > maxProfit) {
        maxProfit = price - minPrice;
        bestBuyDate = minPriceIndex;
        bestSellDate = currentIndex;
    }

    // using heaps
    minHeap.push(price);
    maxHeap.push(price);

    currentIndex++;
}

// getters 
int Analyzer::getSpan() { return lastSpan; }
double Analyzer::getMaxProfit() { return maxProfit; }
int Analyzer::getBestBuyDate() { return bestBuyDate; }
int Analyzer::getBestSellDate() { return bestSellDate; }
bool Analyzer::hasBestTrade() const {
    return bestBuyDate >= 0 && bestSellDate >= 0;
}
double Analyzer::getHeapMin() {
    return minHeap.empty() ? 0.0 : minHeap.top();
}
double Analyzer::getHeapMax() {
    return maxHeap.empty() ? 0.0 : maxHeap.top();
}