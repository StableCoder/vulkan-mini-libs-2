cmake_minimum_required(VERSION 3.2)
project(VkMiniLibs2)

option(BUILD_EXAMPLES "Build examples" OFF)
option(BUILD_TESTS "Build tests" OFF)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(BUILD_EXAMPLES)
  add_subdirectory(example)
endif()
if(BUILD_TESTS)
  enable_testing()
  add_subdirectory(test)
endif()
