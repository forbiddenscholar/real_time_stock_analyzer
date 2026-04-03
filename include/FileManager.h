#pragma once
#include <bits/stdc++.h>
using namespace std;

class FileManager{
private :
    ofstream file;

public : 
    FileManager(const string & filename);

    void write(int time, int price, int span, int profit);

    ~FileManager();
};