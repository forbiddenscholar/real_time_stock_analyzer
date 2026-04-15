cmake_minimum_required(VERSION 3.10)
project(stock_analyzer)

set(CMAKE_CXX_STANDARD 17)

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/include)

# Main analyzer executable
add_executable(app 
    src/main.cpp 
    src/Analyzer.cpp 
    src/Stream.cpp
    src/FileManager.cpp
)
