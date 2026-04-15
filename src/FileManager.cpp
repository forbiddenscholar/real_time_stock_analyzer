#include "FileManager.h"

FileManager::FileManager(const string& filename) {
    file.open(filename);
    file << "time,price,span,profit,min,max,buy,sell\n";
}

void FileManager::write(int time,
    double price,
    int span,
    double profit,
    double heapMin,
    double heapMax,
    int bestBuy,
    int bestSell
    ) {
    file << time << ","
         << price << ","
         << span << ","
         << profit << ","
         << heapMin << ","
         << heapMax << ","
         << bestBuy << ","
         << bestSell << "\n";
    }

FileManager::~FileManager() {
    file.close();
}