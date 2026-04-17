#include "Analyzer.h"
#include "Stream.h"
#include "FileManager.h"
#include <bits/stdc++.h>

#ifdef _WIN32
#include <windows.h>
#define SLEEP_MS(ms) Sleep(ms)
#else
#include <unistd.h>
#define SLEEP_MS(ms) usleep((ms) * 1000)
#endif

using namespace std;

int main(int argc, char* argv[]) {

    if (argc < 2) {
        cout << "Usage: app.exe <input_file>\n";
        return 1;
    }

    string inputFile = argv[1];
    string outputFile = "data/output.csv"; // relative to PROJECT_DIR which is the cwd now

    vector<double> prices = loadPrices(inputFile);

    if (prices.empty()) {
        cerr << "Error: No prices loaded from " << inputFile << endl;
        return 1;
    }

    Analyzer analyzer;
    FileManager file(outputFile);

    int time = 0;

    for (double price : prices) {
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
        // Small delay for streaming effect (optional, can be removed)
        // SLEEP_MS(100);
    }
    // Write sorted historical trends file
    vector<double> sorted = analyzer.getSortedPrices(prices);
    ofstream sortOut("data/sorted_prices.csv");
    sortOut << "sorted_price\n";
    for(double sp : sorted) {
        sortOut << sp << "\n";
    }
    sortOut.close();

    cout << "Analysis complete. Processed " << time << " prices." << endl;
    cout << "Output written to: " << outputFile << endl;

    return 0;
}
