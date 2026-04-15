#include "Stream.h"
#include <fstream>

Stream::Stream(const string& filename) {
    ifstream file(filename);
    string line;

    getline(file, line); // skip header

    while (getline(file, line)) {
        if (line.empty()) continue;

        prices.push_back(stod(line));
    }

    index = 0;
}

bool Stream::hasNext() {
    return index < prices.size();
}

double Stream::getNext() {
    return prices[index++];
}