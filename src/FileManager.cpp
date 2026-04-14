#include "FileManager.h"

FileManager::FileManager(const string& filename) {
    file.open(filename);
    file << "time,price,span,profit,heap_min,heap_max,best_buy_index,best_sell_index\n";
}

void FileManager::write(
    int time,
    double price,
    int span,
    double profit,
    double heapMin,
    double heapMax,
    int bestBuyIndex,
    int bestSellIndex
) {
    file << time << ","
         << price << ","
         << span << ","
         << profit << ","
         << heapMin << ","
         << heapMax << ","
         << bestBuyIndex << ","
         << bestSellIndex << "\n";
    file.flush();
}

FileManager::~FileManager() {
    file.close();
}
