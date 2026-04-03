#include "Stream.h"

Stream :: Stream(const vector <int> & data){
    prices = data;
    index = 0;
}

bool Stream :: hasNext(){
    return index < prices.size();
}

int Stream :: getNext(){
    return prices[index++];
}