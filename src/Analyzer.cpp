#include "Analyzer.h"
#include <bits/stdc++.h>

Analyzer::Analyzer(){
    minPrice = INT_MAX;
    maxProfit = 0;
    lastSpan = 0;
    lastNGE = -1;
}

void Analyzer::update(int price){
    
    // stock span
    int span = 1;
    while(!spanStack.empty() && spanStack.top().first <= price){
        span += spanStack.top().second;
        spanStack.pop();
    }

    spanStack.push({price, span});
    lastSpan = span;

    // Max profit
    minPrice = min(minPrice, price);
    maxProfit = max(maxProfit, price - minPrice);

    //Next greater element
    lastNGE = -1;

    while (!ngeStack.empty() && price > ngeStack.top()) {
        lastNGE = price;
        ngeStack.pop();
    }

    ngeStack.push(price);
}

// getters 
int Analyzer::getSpan() { return lastSpan; }
int Analyzer::getMaxProfit() { return maxProfit; }
int Analyzer::getLastNGE() { return lastNGE; }