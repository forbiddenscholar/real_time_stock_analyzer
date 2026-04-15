#pragma once
#include <bits/stdc++.h>
using namespace std;

class Stream {
private:
    vector<double> prices;
    int index;

public:
    Stream(const string& filename);

    bool hasNext();
    double getNext();
};