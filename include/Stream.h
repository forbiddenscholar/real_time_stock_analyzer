#pragma once
#include <bits/stdc++.h>
using namespace std;

class Stream{
private :
    vector <int> prices;
    int index;

public : 
    Stream(const vector <int> & data);

    bool hasNext();
    int getNext();
};