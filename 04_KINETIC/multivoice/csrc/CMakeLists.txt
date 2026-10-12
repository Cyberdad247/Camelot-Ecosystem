cmake_minimum_required(VERSION 3.18)
project(VibeASR VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Optimization flags for CPU-only inference (AVX2 / SIMD)
if(MSVC)
    add_compile_options(/O2 /arch:AVX2 /W4)
else()
    add_compile_options(-O3 -mavx2 -mfma -Wall -Wextra)
endif()

# Source file
add_executable(vibe_asr vibe_asr.cpp)

# Output directory
set_target_properties(vibe_asr PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)

message(STATUS "[VibeASR] Configured CPU-only binary target under 1.58GB RAM ceiling.")
