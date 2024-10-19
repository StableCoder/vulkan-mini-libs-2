// Copyright (C) 2020-2024 George Cave - gcave@stablecoder.ca
//
// SPDX-License-Identifier: Apache-2.0

#include <catch2/catch_test_macros.hpp>
#include <vulkan/vulkan.h>

#define VK_RESULT_TO_STRING_CONFIG_MAIN
#define VK_ERROR_CODE_CONFIG_MAIN
#include <vk_error_code.hpp>

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
    CHECK(std::string{VkResult_to_string(X)} == std::string{#X});                                  \
    CHECK(std::string{vkResultToString(X)} == std::string{#X});                                    \
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

    CHECK(test.category().name() == std::string{"VkResult"});
    CHECK(test.message() == std::string{"(unrecognized positive VkResult value)"});
    CHECK(VkResult_to_string(static_cast<VkResult>(i)) == NULL);
    CHECK(std::string{vkResultToString(static_cast<VkResult>(i))} ==
          std::string{"(unrecognized positive VkResult value)"});
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
    CHECK(VkResult_to_string(static_cast<VkResult>(i)) == NULL);
    CHECK(std::string{vkResultToString(static_cast<VkResult>(i))} ==
          std::string{"(unrecognized negative VkResult value)"});
  }
}