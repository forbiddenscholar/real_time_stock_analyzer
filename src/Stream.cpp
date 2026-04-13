#include "Stream.h"
#include <fstream>
#include <algorithm>

vector<double> loadPrices(const string& filename) {
    vector<double> prices;
    ifstream file(filename);
    string line;

    // skip header
    getline(file, line);

    while (getline(file, line)) {
        if (line.empty()) continue;

        // remove possible carriage return / spaces
        line.erase(remove(line.begin(), line.end(), '\r'), line.end());
        line.erase(remove_if(line.begin(), line.end(), ::isspace), line.end());

        if(!line.empty()) {
            prices.push_back(stod(line));
        }
    }

    return prices;
}