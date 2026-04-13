#pragma once
#include <bits/stdc++.h>
using namespace std;

class FileManager {
private:
    ofstream file;

public:
    FileManager(const string& filename);

    void write(int time, double price, int span, double profit, double heapMin, double heapMax);

    ~FileManager();
};