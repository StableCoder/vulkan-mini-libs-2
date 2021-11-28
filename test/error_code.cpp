/*
    Copyright (C) 2020 George Cave - gcave@stablecoder.ca

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless CHECKd by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
*/

#include <catch.hpp>
#include <vulkan/vulkan.h>

#define VK_RESULT_TO_STRING_CONFIG_MAIN
#define VK_ERROR_CODE_CONFIG_MAIN
#include "vk_error_code.hpp"

TEST_CASE("Success Case") {
  std::error_code test = VK_SUCCESS;

  REQUIRE_FALSE(test);

  REQUIRE(test.value() == VK_SUCCESS);

  REQUIRE(test.category().name() == std::string{"VkResult"});
  REQUIRE(test.message() == std::string{"VK_SUCCESS"});
}

#define TEST_CODE(X)                                                                               \
  {                                                                                                \
    std::error_code test = X;                                                                      \
    CHECK(test);                                                                                   \
    CHECK(test.value() == X);                                                                      \
    CHECK(test.category().name() == std::string{"VkResult"});                                      \
    CHECK(test.message() == std::string{#X});                                                      \
  }

TEST_CASE("Specific positive-value cases") {
  TEST_CODE(VK_NOT_READY);
  TEST_CODE(VK_TIMEOUT);
  TEST_CODE(VK_EVENT_SET);
  TEST_CODE(VK_EVENT_RESET);
  TEST_CODE(VK_INCOMPLETE);
}

TEST_CASE("Unknown positive error cases") {
  for (int i = 1000; i < 1050; ++i) {
    std::error_code test = static_cast<VkResult>(i);

    REQUIRE(test);
    REQUIRE(test.value() == static_cast<VkResult>(i));

    REQUIRE(test.category().name() == std::string{"VkResult"});
    REQUIRE(test.message() == std::string{"(unrecognized positive VkResult value)"});
  }
}

TEST_CASE("Specific negative-value cases") {
  TEST_CODE(VK_ERROR_OUT_OF_HOST_MEMORY);
  TEST_CODE(VK_ERROR_OUT_OF_DEVICE_MEMORY);
  TEST_CODE(VK_ERROR_INITIALIZATION_FAILED);
  TEST_CODE(VK_ERROR_DEVICE_LOST);
  TEST_CODE(VK_ERROR_MEMORY_MAP_FAILED);
  TEST_CODE(VK_ERROR_LAYER_NOT_PRESENT);
  TEST_CODE(VK_ERROR_EXTENSION_NOT_PRESENT);
  TEST_CODE(VK_ERROR_FEATURE_NOT_PRESENT);
  TEST_CODE(VK_ERROR_INCOMPATIBLE_DRIVER);
  TEST_CODE(VK_ERROR_TOO_MANY_OBJECTS);
  TEST_CODE(VK_ERROR_FORMAT_NOT_SUPPORTED);
  TEST_CODE(VK_ERROR_FRAGMENTED_POOL);
}

TEST_CASE("Unknown negative error cases") {
  for (int i = -1000; i > -1050; --i) {
    std::error_code test = static_cast<VkResult>(i);

    REQUIRE(test);
    REQUIRE(test.value() == static_cast<VkResult>(i));

    REQUIRE(test.category().name() == std::string{"VkResult"});
    REQUIRE(test.message() == std::string{"(unrecognized negative VkResult value)"});
  }
}