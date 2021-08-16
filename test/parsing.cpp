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

#define VK_VALUE_SERIALIZATION_CONFIG_MAIN
#include "vk_value_serialization.hpp"

constexpr uint32_t cDummyNum = 999999;

TEST_CASE("Parsing: Failure Cases") {
  uint32_t dummy = cDummyNum;

  SECTION("Garbage type fails") {
    CHECK_FALSE(vk_parse("VkGarbagio", "2D", &dummy));
    CHECK(dummy == cDummyNum);
    CHECK_FALSE(vk_parse("VkGarbagioFlags", "2D", &dummy));
    CHECK(dummy == cDummyNum);
  }
  SECTION("Garbage values fails") {
    CHECK_FALSE(vk_parse("VkImageType", "6D", &dummy));
    CHECK(dummy == cDummyNum);
    CHECK_FALSE(vk_parse("VkDebugReportFlagBitsEXT", "NOT_EXIST", &dummy));
    CHECK(dummy == cDummyNum);
  }
  SECTION("Attempting to do a bitmask for an enum returns nothing") {
    CHECK_FALSE(vk_parse("VkImageType", "2D | 3D", &dummy));
    CHECK(dummy == cDummyNum);
  }
  SECTION("Parsing with an empty type fails") { CHECK_FALSE(vk_parse("", "2D", &dummy)); }
}

TEST_CASE("Parsing: Odd success cases") {
  uint32_t retVal = cDummyNum;
  SECTION("Parsing with an empty string succeeds, returns 0") {
    CHECK(vk_parse("VkImageType", "", &retVal));
    CHECK(retVal == 0);
  }
}

TEST_CASE("Parsing: Checking enum conversions from strings to the values from the  actual header") {
  uint32_t retVal = cDummyNum;

  SECTION("Success where the value is also a vendor name") {
    CHECK(vk_parse("VkVendorId", "VIV", &retVal));
    CHECK(retVal == VK_VENDOR_ID_VIV);
  }

  SECTION("With original shortened strings") {
    CHECK(vk_parse("VkImageLayout", "UNDEFINED", &retVal));
    CHECK(retVal == VK_IMAGE_LAYOUT_UNDEFINED);

    CHECK(vk_parse("VkImageLayout", "TRANSFER_DST_OPTIMAL", &retVal));
    CHECK(retVal == VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);

    CHECK(vk_parse("VkImageType", "2D", &retVal));
    CHECK(retVal == VK_IMAGE_TYPE_2D);
  }
  SECTION("With extra spaces around the type") {
    CHECK(vk_parse("VkImageLayout", "    VK_IMAGE_LAYOUT_UNDEFINED    ", &retVal));
    CHECK(retVal == VK_IMAGE_LAYOUT_UNDEFINED);
  }
  SECTION("With mixed capitalization and mixture of underscores/spaces") {
    CHECK(vk_parse("VkImageLayout", "    vK IMagE_LAyOUt UNDEFIned    ", &retVal));
    CHECK(retVal == VK_IMAGE_LAYOUT_UNDEFINED);
  }
  SECTION("With full strings") {
    CHECK(vk_parse("VkImageLayout", "VK_IMAGE_LAYOUT_UNDEFINED", &retVal));
    CHECK(retVal == VK_IMAGE_LAYOUT_UNDEFINED);

    CHECK(vk_parse("VkImageLayout", "VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL", &retVal));
    CHECK(retVal == VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);

    CHECK(vk_parse("VkImageType", "VK_IMAGE_TYPE_2D", &retVal));
    CHECK(retVal == VK_IMAGE_TYPE_2D);
  }

  SECTION("With Vendor Tags") {
    CHECK(vk_parse("VkPresentModeKHR", "VK_PRESENT_MODE_IMMEDIATE_KHR", &retVal));
    CHECK(retVal == VK_PRESENT_MODE_IMMEDIATE_KHR);

    CHECK(vk_parse("VkPresentModeKHR", "IMMEDIATE_KHR", &retVal));
    CHECK(retVal == VK_PRESENT_MODE_IMMEDIATE_KHR);

    CHECK(vk_parse("VkPresentModeKHR", "VK_PRESENT_MODE_IMMEDIATE", &retVal));
    CHECK(retVal == VK_PRESENT_MODE_IMMEDIATE_KHR);

    CHECK(vk_parse("VkPresentModeKHR", "IMMEDIATE", &retVal));
    CHECK(retVal == VK_PRESENT_MODE_IMMEDIATE_KHR);
  }
}

TEST_CASE("Parsing: Checking bitmask conversions from string to bitmask values") {
  uint32_t retVal = cDummyNum;

  SECTION("With a bad extra bitmask fails") {
    CHECK_FALSE(vk_parse("VkDebugReportFlagBitsEXT", "PERFORMANCE_WARNING_BIT | NON_EXISTING_BIT",
                         &retVal));
    CHECK(retVal == cDummyNum);

    CHECK_FALSE(vk_parse("VkDebugReportFlagBitsEXT", "NON_EXISTING_BIT | PERFORMANCE_WARNING_BIT",
                         &retVal));
    CHECK(retVal == cDummyNum);
  }

  SECTION("With original shortened strings") {
    SECTION("FlagBits") {
      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "PERFORMANCE_WARNING_BIT", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "PERFORMANCE_WARNING", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "DEBUG_BIT", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_DEBUG_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "DEBUG", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_DEBUG_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "ERROR_BIT", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_ERROR_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "ERROR", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_ERROR_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "DEBUG_BIT | ERROR_BIT", &retVal));
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "DEBUG | ERROR", &retVal));
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));
    }
    SECTION("Flags") {
      CHECK(vk_parse("VkDebugReportFlagsEXT", "PERFORMANCE_WARNING_BIT", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "PERFORMANCE_WARNING", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "DEBUG_BIT", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_DEBUG_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "DEBUG", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_DEBUG_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "ERROR_BIT", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_ERROR_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "ERROR", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_ERROR_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "DEBUG_BIT | ERROR_BIT", &retVal));
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));

      CHECK(vk_parse("VkDebugReportFlagsEXT", "DEBUG | ERROR", &retVal));
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));
    }
  }
  SECTION("With full strings") {
    SECTION("FlagBits") {
      CHECK(
          vk_parse("VkDebugReportFlagBitsEXT", "VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "VK_DEBUG_REPORT_PERFORMANCE_WARNING", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "VK_DEBUG_REPORT_DEBUG_BIT", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_DEBUG_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "VK_DEBUG_REPORT_DEBUG", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_DEBUG_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "VK_DEBUG_REPORT_ERROR_BIT", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_ERROR_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "VK_DEBUG_REPORT_ERROR", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_ERROR_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT",
                     "VK_DEBUG_REPORT_DEBUG_BIT | VK_DEBUG_REPORT_ERROR_BIT", &retVal));
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "VK_DEBUG_REPORT_ERROR | VK_DEBUG_REPORT_DEBUG",
                     &retVal));
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));
    }
    SECTION("Flags") {
      CHECK(vk_parse("VkDebugReportFlagsEXT", "VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT_EXT);

      CHECK(

          vk_parse("VkDebugReportFlagsEXT", "VK_DEBUG_REPORT_PERFORMANCE_WARNING", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "VK_DEBUG_REPORT_DEBUG_BIT", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_DEBUG_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "VK_DEBUG_REPORT_DEBUG", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_DEBUG_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "VK_DEBUG_REPORT_ERROR_BIT", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_ERROR_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "VK_DEBUG_REPORT_ERROR", &retVal));
      CHECK(retVal == VK_DEBUG_REPORT_ERROR_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT",
                     "VK_DEBUG_REPORT_DEBUG_BIT | VK_DEBUG_REPORT_ERROR_BIT", &retVal));
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));

      CHECK(vk_parse("VkDebugReportFlagsEXT", "VK_DEBUG_REPORT_ERROR | VK_DEBUG_REPORT_DEBUG",
                     &retVal));
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));
    }
  }
  SECTION("With mixed short/full strings") {
    SECTION("FlagBits") {
      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "DEBUG_BIT | VK_DEBUG_REPORT_ERROR_BIT", &retVal));
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "VK_DEBUG_REPORT_ERROR_BIT | DEBUG_BIT", &retVal));
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));
    }
    SECTION("Flags") {
      CHECK(vk_parse("VkDebugReportFlagsEXT", "DEBUG_BIT | VK_DEBUG_REPORT_ERROR_BIT", &retVal));
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));

      CHECK(vk_parse("VkDebugReportFlagsEXT", "VK_DEBUG_REPORT_ERROR_BIT | DEBUG_BIT", &retVal));
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));
    }
  }
}