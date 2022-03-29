include(prepare_catch.cmake)
include(code-coverage.cmake)
include(sanitizers.cmake)

add_code_coverage_all_targets(EXCLUDE ".*/test/.*")

prepare_catch(COMPILED_CATCH)

find_package(Vulkan REQUIRED)

include_directories(../include)
link_libraries(catch Vulkan::Vulkan)

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
