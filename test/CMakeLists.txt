include(prepare_catch.cmake)
include(code-coverage.cmake)

prepare_catch(COMPILED_CATCH)

find_package(Vulkan REQUIRED)

include_directories(../include)
link_libraries(catch Vulkan::Vulkan)

# Serialization
add_executable(VkSerializationTests parsing.cpp serialization.cpp)
target_code_coverage(VkSerializationTests EXCLUDE ".*/test/.*")

add_test(NAME VkSerializationTests-Tests COMMAND VkSerializationTests)
