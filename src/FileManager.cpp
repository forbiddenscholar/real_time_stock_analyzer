#include "FileManager.h"

FileManager :: FileManager(const string & filename){
    file.open(filename);

    //header
    file << "time,price,span,profit\n";
}

void FileManager :: write(int time, int price, int span, int profit){
    file << time << ","
         << price << ","
         << span << ","
         << profit << "\n";
}

FileManager :: ~FileManager(){
    file.close();
}