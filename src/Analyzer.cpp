#include "Analyzer.h"
#include <iostream>
#include <cfloat>

Analyzer::Analyzer() {
    minPrice = DBL_MAX;
    minPriceIndex = -1;
    maxProfit = 0.0;
    bestBuyDate = -1;
    bestSellDate = -1;
    lastSpan = 0;
    currentIndex = 0;
}

void Analyzer::update(double price) {
    // ---- Stock Span (Stack-based) ----
    // Span = number of consecutive days (including today) where price <= today's price
    int span = 1;
    while (!spanStack.empty() && spanStack.top().first <= price) {
        span += spanStack.top().second;
        spanStack.pop();
    }
    spanStack.push({price, span});
    lastSpan = span;

    // ---- Max Profit (Greedy) ----
    if (price < minPrice) {
        minPrice = price;
        minPriceIndex = currentIndex;
    }
    
    if (price - minPrice > maxProfit) {
        maxProfit = price - minPrice;
        bestBuyDate = minPriceIndex;
        bestSellDate = currentIndex;
    }

    // ---- Heap: push into both min-heap and max-heap ----
    maxHeap.push(price);
    minHeap.push(price);

    currentIndex++;
}

// Custom Merge Sort Implementation to analyze historical trends
void merge(vector<double>& arr, int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;
    vector<double> L(n1), R(n2);
    for (int i = 0; i < n1; i++) L[i] = arr[left + i];
    for (int j = 0; j < n2; j++) R[j] = arr[mid + 1 + j];
    int i = 0, j = 0, k = left;
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) { arr[k] = L[i]; i++; }
        else { arr[k] = R[j]; j++; }
        k++;
    }
    while (i < n1) { arr[k] = L[i]; i++; k++; }
    while (j < n2) { arr[k] = R[j]; j++; k++; }
}

void mergeSort(vector<double>& arr, int left, int right) {
    if (left >= right) return;
    int mid = left + (right - left) / 2;
    mergeSort(arr, left, mid);
    mergeSort(arr, mid + 1, right);
    merge(arr, left, mid, right);
}

vector<double> Analyzer::getSortedPrices(const vector<double>& originalPrices) {
    vector<double> sorted = originalPrices;
    if (!sorted.empty()) {
        mergeSort(sorted, 0, sorted.size() - 1);
    }
    return sorted;
}

// Getters
int Analyzer::getSpan() { return lastSpan; }
double Analyzer::getMaxProfit() { return maxProfit; }
int Analyzer::getBestBuyDate() { return bestBuyDate; }
int Analyzer::getBestSellDate() { return bestSellDate; }
bool Analyzer::hasBestTrade() const { return bestBuyDate >= 0 && bestSellDate >= 0; }


double Analyzer::getHeapMin() {
    return minHeap.empty() ? 0.0 : minHeap.top();
}

double Analyzer::getHeapMax() {
    return maxHeap.empty() ? 0.0 : maxHeap.top();
}