#include "Analyzer.h"
#include <bits/stdc++.h>

Analyzer::Analyzer(){
    minPrice = INT_MAX;
    maxProfit = 0;
    lastSpan = 0;
    currentIndex = 0;
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
    int index = currentIndex;

    while (!ngeStack.empty() && price > ngeStack.top().first) {
        int prevIndex = ngeStack.top().second;
        nge[prevIndex] = price;
        ngeStack.pop();
    }

    ngeStack.push({price, index});
    // for default value of current
    nge.push_back(-1);

    currentIndex++;
}

// getters 
int Analyzer::getSpan() { return lastSpan; }
int Analyzer::getMaxProfit() { return maxProfit; }
int Analyzer::getLastNGE() { return nge[currentIndex-1]; }
int Analyzer::getNGEAt(int index){ return nge[index]; }