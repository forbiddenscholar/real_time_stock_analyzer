#include "Analyzer.h"
#include "Stream.h"
#include "FileManager.h"
#include <bits/stdc++.h>
using namespace std;

int main(int argc, char* argv[]) {

    if (argc < 2) {
        cout << "Usage: ./app <input_file>\n";
        return 1;
    }

    string filename = argv[1];

    Stream stream(filename);
    Analyzer analyzer;
    FileManager file("../data/output.csv");

    int time = 0;

    while (stream.hasNext()) {
        double price = stream.getNext();

        analyzer.update(price);

        file.write(
            time,
            price,
            analyzer.getSpan(),
            analyzer.getMaxProfit(),
            analyzer.getHeapMin(),
            analyzer.getHeapMax(),
            analyzer.getBestBuyDate(),
            analyzer.getBestSellDate()
        );

        time++;
    }

    return 0;
}