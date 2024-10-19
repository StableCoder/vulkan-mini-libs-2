# Copyright (C) 2022-2024 George Cave.
#
# SPDX-License-Identifier: Apache-2.0

include(code-coverage.cmake)
include(sanitizers.cmake)

find_package(Catch2 3 REQUIRED)
find_package(Vulkan REQUIRED)

set_sanitizer_options(address DEFAULT -fsanitize-address-use-after-scope
                      -fsanitize-address-use-after-return=runtime)
set_sanitizer_options(leak DEFAULT)
set_sanitizer_options(memory DEFAULT -fsanitize-memory-track-origins)
set_sanitizer_options(undefined DEFAULT -fno-sanitize-recover=undefined)

if(USE_SANITIZER)
  add_sanitizer_support(${USE_SANITIZER})
endif()

add_code_coverage_all_targets(EXCLUDE ".*/test/.*")

include_directories(../include)
link_libraries(Catch2::Catch2WithMain Vulkan::Vulkan)

# Compilation Test
add_library(compilation_test STATIC c_compilation.c cpp_compilation.cpp)

# Error Code
add_executable(VkErrorCodeTests error_code.cpp)
target_code_coverage(VkErrorCodeTests AUTO ALL EXCLUDE ".*/test/.*")

add_test(NAME VkErrorCodeTests-Tests COMMAND VkErrorCodeTests)

# Serialization
add_executable(VkSerializationTests parsing.cpp serialization.cpp
                                    serialization64.cpp)
target_code_coverage(VkSerializationTests AUTO ALL EXCLUDE ".*/test/.*")

add_test(NAME VkSerializationTests-Tests COMMAND VkSerializationTests)
