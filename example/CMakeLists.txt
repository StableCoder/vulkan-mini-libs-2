find_package(Vulkan REQUIRED)

include_directories(../include)

add_executable(example_error_code error_code.cpp)
target_link_libraries(example_error_code PRIVATE Vulkan::Vulkan)

add_executable(example_string_parsing string_parsing.cpp)
target_link_libraries(example_string_parsing PRIVATE Vulkan::Vulkan)

add_library(standalone_lib standalone.cpp)
target_link_libraries(standalone_lib PRIVATE Vulkan::Vulkan)