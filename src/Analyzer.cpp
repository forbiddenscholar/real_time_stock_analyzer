#include "Analyzer.h"
#include <iostream>
#include <cfloat>

Analyzer::Analyzer() {
    minPrice = DBL_MAX;
    maxProfit = 0.0;
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
    // Track minimum price seen so far, profit = current - min
    minPrice = min(minPrice, price);
    maxProfit = max(maxProfit, price - minPrice);

    // ---- Heap: push into both min-heap and max-heap ----
    maxHeap.push(price);
    minHeap.push(price);

    currentIndex++;
}

// Compute NGE for all prices using right-to-left stack scan
// This is called once after all prices are processed
void Analyzer::computeNGE(const vector<double>& prices) {
    int n = prices.size();
    nge.resize(n, -1.0);
    stack<double> st;

    for (int i = n - 1; i >= 0; i--) {
        while (!st.empty() && st.top() <= prices[i]) {
            st.pop();
        }
        nge[i] = st.empty() ? -1.0 : st.top();
        st.push(prices[i]);
    }
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

double Analyzer::getHeapMin() {
    return minHeap.empty() ? 0.0 : minHeap.top();
}

double Analyzer::getHeapMax() {
    return maxHeap.empty() ? 0.0 : maxHeap.top();
}

double Analyzer::getNGEAt(int index) {
    if (index < 0 || index >= (int)nge.size()) return -1.0;
    return nge[index];
}

int Analyzer::getNGESize() {
    return (int)nge.size();
}