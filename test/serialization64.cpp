// Copyright (C) 2020-2024 George Cave - gcave@stablecoder.ca
//
// SPDX-License-Identifier: Apache-2.0

#include <catch2/catch_test_macros.hpp>
#include <vk_value_serialization.hpp>

#ifdef VK_KHR_synchronization2

namespace {
std::string cDummyStr = "AAABBBCCC";
}

TEST_CASE("Serialize64: Serializing one of the few 64-bit flag types, VkAccessFlagBits2KHR") {
  std::string retVal = cDummyStr;

  SECTION("Failure case where a bad type is given") {
    CHECK(vk_serialize("VkGarbagio", VK_ACCESS_2_INDEX_READ_BIT_KHR, &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND);
    CHECK(retVal == cDummyStr);
  }

  SECTION("Failure case where a garbage non-existant bit is given") {
    CHECK(vk_serialize("VkAccessFlagBits2KHR", VK_ACCESS_2_INDEX_READ_BIT_KHR | 0xFFFFFFFF,
                       &retVal) == STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND);
    CHECK(retVal == cDummyStr);
  }

  SECTION("Successfully returns an when the bitflag has a zero-value enum") {
    CHECK(vk_serialize("VkAccessFlagBits2KHR", (VkAccessFlagBits2KHR)0, &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == "NONE");
  }

  SECTION("Regular success cases") {
    SECTION("FlagBits") {
      CHECK(vk_serialize("VkAccessFlagBits2KHR", VK_ACCESS_2_INDEX_READ_BIT_KHR, &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == "INDEX_READ");

      CHECK(vk_serialize("VkAccessFlagBits2KHR",
                         VK_ACCESS_2_INDEX_READ_BIT_KHR |
                             VK_ACCESS_2_ACCELERATION_STRUCTURE_WRITE_BIT_NV,
                         &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == "ACCELERATION_STRUCTURE_WRITE_BIT_KHR | INDEX_READ");
    }
    SECTION("Flags") {
      CHECK(vk_serialize("VkAccessFlags2KHR", VK_ACCESS_2_INDEX_READ_BIT_KHR, &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == "INDEX_READ");

      CHECK(vk_serialize("VkAccessFlags2KHR",
                         VK_ACCESS_2_INDEX_READ_BIT_KHR |
                             VK_ACCESS_2_ACCELERATION_STRUCTURE_WRITE_BIT_NV,
                         &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == "ACCELERATION_STRUCTURE_WRITE_BIT_KHR | INDEX_READ");
    }
  }
}

#endif // VK_KHR_synchronization2