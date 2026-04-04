#include "Stream.h"
#include <fstream>

vector<int> loadPrices(const string& filename) {
    vector<int> prices;
    ifstream file(filename);
    string line;

    // skip header
    getline(file, line);

    while (getline(file, line)) {
        if (line.empty()) continue;

        // remove possible carriage return / spaces
        line.erase(remove(line.begin(), line.end(), '\r'), line.end());
        line.erase(remove_if(line.begin(), line.end(), ::isspace), line.end());

        prices.push_back(stoi(line));
    }

    return prices;
}