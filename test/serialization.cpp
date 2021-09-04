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

#include "vk_value_serialization.hpp"

namespace {
std::string cDummyStr = "AAABBBCCC";
}

TEST_CASE("Serialize: Failure cases") {
  std::string dummyStr = cDummyStr;

  CHECK_FALSE(vk_serialize("", 0, &dummyStr));
  CHECK(dummyStr == cDummyStr);
  CHECK_FALSE(vk_serialize("", 0, &dummyStr));
  CHECK(dummyStr == cDummyStr);
}

TEST_CASE("Serialize: Enum") {
  std::string retVal = cDummyStr;

  SECTION("Failure case where a bad type is given") {
    CHECK_FALSE(vk_serialize("VkGarbagio", VK_IMAGE_TYPE_3D, &retVal));
    CHECK(retVal == cDummyStr);
  }

  SECTION("Failure case where bad enum given") {
    CHECK_FALSE(vk_serialize("VkImageType", -1U, &retVal));
    CHECK(retVal == cDummyStr);
  }

  SECTION("Success cases") {
    CHECK(vk_serialize("VkImageType", VK_IMAGE_TYPE_3D, &retVal));
    CHECK(retVal == "3D");

    CHECK(vk_serialize("VkImageType", VK_IMAGE_TYPE_2D, &retVal));
    CHECK(retVal == "2D");
  }

  SECTION("Vendor Tag Success") {
    CHECK(vk_serialize("VkPresentModeKHR", VK_PRESENT_MODE_IMMEDIATE_KHR, &retVal));
    CHECK(retVal == "IMMEDIATE");
  }
}

TEST_CASE("Serialize: Bitmask") {
  std::string retVal = cDummyStr;

  SECTION("Failure case where a bad type is given") {
    CHECK_FALSE(vk_serialize("VkGarbagio", VK_CULL_MODE_BACK_BIT, &retVal));
    CHECK(retVal == cDummyStr);
  }

  SECTION("Failure case where a garbage non-existant bit is given") {
    CHECK_FALSE(vk_serialize("VkCullModeFlagBits", VK_CULL_MODE_BACK_BIT | 0x777, &retVal));
    CHECK(retVal == cDummyStr);
  }

  SECTION("Success case where there's extra vendor bits on the type name (such "
          "as after a "
          "promoted extension)") {
    CHECK(vk_serialize("VkCullModeFlagBitsVIV", VK_CULL_MODE_BACK_BIT, &retVal));
    CHECK(retVal == "BACK");
  }

  SECTION("Successfully returns an empty string when the given type has no "
          "actual flags") {
    CHECK(vk_serialize("VkAcquireProfilingLockFlagBits", 0, &retVal));
    CHECK(retVal == "");

    CHECK(vk_serialize("VkShaderCorePropertiesFlagBitsAMD", 0, &retVal));
    CHECK(retVal == "");
  }

  SECTION("Successfully returns an when the bitflag has a zero-value enum") {
    CHECK(vk_serialize("VkCullModeFlagBits", 0, &retVal));
    CHECK(retVal == "NONE");
  }

  SECTION("Fails to serialize when given a zero-value to a type that has enums "
          "but NOT a zero "
          "value") {
    CHECK_FALSE(vk_serialize("VkShaderStageFlagBits", 0, &retVal));
    CHECK(retVal == cDummyStr);
  }

  SECTION("Regular success cases") {
    SECTION("FlagBits") {
      CHECK(vk_serialize("VkDebugReportFlagBitsEXT", VK_DEBUG_REPORT_ERROR_BIT_EXT, &retVal));
      CHECK(retVal == "ERROR");

      CHECK(vk_serialize("VkDebugReportFlagBitsEXT",
                         VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT, &retVal));
      CHECK(retVal == "DEBUG | ERROR");
    }
    SECTION("Flags") {
      CHECK(vk_serialize("VkDebugReportFlagsEXT", VK_DEBUG_REPORT_ERROR_BIT_EXT, &retVal));
      CHECK(retVal == "ERROR");

      CHECK(vk_serialize("VkDebugReportFlagsEXT",
                         VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT, &retVal));
      CHECK(retVal == "DEBUG | ERROR");
    }
  }

  SECTION("Combined bitmask will use larger items first") {
    SECTION("FlagBits") {
      CHECK(vk_serialize("VkCullModeFlagBits", VK_CULL_MODE_BACK_BIT | VK_CULL_MODE_FRONT_BIT,
                         &retVal));
      CHECK(retVal == "FRONT_AND_BACK");
    }
    SECTION("Flags") {
      CHECK(
          vk_serialize("VkCullModeFlags", VK_CULL_MODE_BACK_BIT | VK_CULL_MODE_FRONT_BIT, &retVal));
      CHECK(retVal == "FRONT_AND_BACK");
    }
  }
}