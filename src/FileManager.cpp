#include "FileManager.h"

FileManager::FileManager(const string& filename) {
    file.open(filename);
    file << "time,price,span,profit,heap_min,heap_max\n";
}

void FileManager::write(int time, double price, int span, double profit, double heapMin, double heapMax) {
    file << time << ","
         << price << ","
         << span << ","
         << profit << ","
         << heapMin << ","
         << heapMax << "\n";
    file.flush();
}

FileManager::~FileManager() {
    file.close();
}