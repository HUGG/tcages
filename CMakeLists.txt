cmake_minimum_required(VERSION 3.18)
project(tccore_native LANGUAGES C CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_C_STANDARD 99)

add_library(RDAAM MODULE src/RDAAM_He/RDAAM_He.cpp src/RDAAM_He/RDAAM.cpp)
add_library(ketch MODULE src/ketch_aft/ketch.c)

install(TARGETS RDAAM ketch DESTINATION tccore)