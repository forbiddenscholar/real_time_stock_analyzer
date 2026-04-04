#include "Analyzer.h"
#include "Stream.h"
#include "FileManager.h"
#include <bits/stdc++.h>
#include <unistd.h>
using namespace std;

int main(int argc, char* argv[]) {

    if (argc < 2) {
        cout << "Usage: ./app <input_file>\n";
        return 1;
    }

    string filename = argv[1];

    vector<int> prices = loadPrices(filename);
    Analyzer analyzer;
    FileManager file("../data/output.csv");

    int time = 0;

    for (int price : prices) {
        analyzer.update(price);

        file.write(
            time,
            price,
            analyzer.getSpan(),
            analyzer.getMaxProfit()
        );

        time++;
        usleep(300000);
    }

    return 0;
}