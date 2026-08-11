cmake_minimum_required(VERSION 3.10)
project(merlin_webrtc)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(merlin_webrtc_native SHARED 
    src/native_webrtc.cpp
)
