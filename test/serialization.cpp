// Copyright (C) 2020-2024 George Cave - gcave@stablecoder.ca
//
// SPDX-License-Identifier: Apache-2.0

#include <catch2/catch_test_macros.hpp>
#include <vk_value_serialization.hpp>
#include <vulkan/vulkan.h>

#include <cstring>
#include <string>

namespace {
std::string cDummyStr = "AAABBBCCC";
}

TEST_CASE("Serialize: Failure cases") {
  std::string dummyStr = cDummyStr;

  CHECK(vk_serialize("", 0, &dummyStr) == STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND);
  CHECK(dummyStr == cDummyStr);
  CHECK(vk_serialize("", 0, &dummyStr) == STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND);
  CHECK(dummyStr == cDummyStr);
}

TEST_CASE("Serialize: Enum") {
  std::string retVal = cDummyStr;

  SECTION("Failure case where a bad type is given") {
    CHECK(vk_serialize(nullptr, VK_IMAGE_TYPE_3D, &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND);
    CHECK(retVal == cDummyStr);

    CHECK(vk_serialize("", VK_IMAGE_TYPE_3D, &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND);
    CHECK(retVal == cDummyStr);

    CHECK(vk_serialize("VkGarbagio", VK_IMAGE_TYPE_3D, &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND);
    CHECK(retVal == cDummyStr);

    CHECK(vk_serialize("AMDX", VK_IMAGE_TYPE_3D, &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND);
    CHECK(retVal == cDummyStr);
  }

  SECTION("Failure case where bad enum given") {
    CHECK(vk_serialize("VkImageType", -1U, &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND);
    CHECK(retVal == cDummyStr);
  }

  SECTION("Failure case where a zero value is given to a type that can't be empty") {
    CHECK(vk_serialize("VkPipelineCacheHeaderVersion", 0, &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND);
    CHECK(retVal == cDummyStr);
  }

  SECTION("Success cases") {
    CHECK(vk_serialize("VkImageType", VK_IMAGE_TYPE_3D, &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == "3D");

    CHECK(vk_serialize("VkImageType", VK_IMAGE_TYPE_2D, &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == "2D");
  }

  SECTION("Vendor Tag Success") {
    CHECK(vk_serialize("VkPresentModeKHR", VK_PRESENT_MODE_IMMEDIATE_KHR, &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == "IMMEDIATE");
  }
}

TEST_CASE("Serialize: Bitmask") {
  std::string retVal = cDummyStr;

  SECTION("Failure case where a bad type is given") {
    CHECK(vk_serialize("VkGarbagio", VK_CULL_MODE_BACK_BIT, &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND);
    CHECK(retVal == cDummyStr);
  }

  SECTION("Failure case where a garbage non-existant bit is given") {
    CHECK(vk_serialize("VkCullModeFlagBits", VK_CULL_MODE_BACK_BIT | 0x777, &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND);
    CHECK(retVal == cDummyStr);
  }

  SECTION(
      "Success case where a zero-value is allowed since there was a time when no flags existed") {
    CHECK(vk_serialize("VkPipelineDepthStencilStateCreateFlagBits", 0, &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == "");
  }

  SECTION("Success case where there's extra vendor bits on the type name (such as after a promoted "
          "extension)") {
    CHECK(vk_serialize("VkCullModeFlagBitsVIV", VK_CULL_MODE_BACK_BIT, &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == "BACK");
  }

  SECTION("Successfully returns an empty string when the given type has no actual flags") {
    CHECK(vk_serialize("VkAcquireProfilingLockFlagBitsKHR", 0, &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == "");

    CHECK(vk_serialize("VkShaderCorePropertiesFlagBitsAMD", 0, &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == "");
  }

  SECTION("Successfully returns an when the bitflag has a zero-value enum") {
    CHECK(vk_serialize("VkCullModeFlagBits", 0, &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == "NONE");
  }

  SECTION("Regular success cases") {
    SECTION("FlagBits") {
      CHECK(vk_serialize("VkDebugReportFlagBitsEXT", VK_DEBUG_REPORT_ERROR_BIT_EXT, &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == "ERROR");

      CHECK(vk_serialize("VkDebugReportFlagBitsEXT",
                         VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT,
                         &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == "DEBUG | ERROR");
    }
    SECTION("Flags") {
      CHECK(vk_serialize("VkDebugReportFlagsEXT", VK_DEBUG_REPORT_ERROR_BIT_EXT, &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == "ERROR");

      CHECK(vk_serialize("VkDebugReportFlagsEXT",
                         VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT,
                         &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == "DEBUG | ERROR");
    }
  }

  SECTION("Combined bitmask will use larger items first") {
    SECTION("FlagBits") {
      CHECK(vk_serialize("VkCullModeFlagBits", VK_CULL_MODE_BACK_BIT | VK_CULL_MODE_FRONT_BIT,
                         &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == "FRONT_AND_BACK");
    }
    SECTION("Flags") {
      CHECK(vk_serialize("VkCullModeFlags", VK_CULL_MODE_BACK_BIT | VK_CULL_MODE_FRONT_BIT,
                         &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == "FRONT_AND_BACK");
    }
  }

#if VK_HEADER_VERSION >= 134
  SECTION("Ensure that previously reserved values that have been replaced with real names use the "
          "real names instead") {
    SECTION("FlagBits") {
      CHECK(vk_serialize("VkRenderPassCreateFlagBits", VK_RENDER_PASS_CREATE_TRANSFORM_BIT_QCOM,
                         &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == "TRANSFORM_BIT_QCOM");
    }
    SECTION("Flags") {
      CHECK(vk_serialize("VkRenderPassCreateFlags", VK_RENDER_PASS_CREATE_TRANSFORM_BIT_QCOM,
                         &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == "TRANSFORM_BIT_QCOM");
    }
  }
#endif

  SECTION("Passing in a string of varying sizes for serialization") {
    char testStr[20];
    memset(testStr, 0, 20);

    SECTION("Passing in more than required returns success and the serialized length of 13") {
      uint32_t serializedLength = 20;
      CHECK(vk_serialize32("VkDebugReportFlagsEXT",
                           VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT,
                           &serializedLength, testStr) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(serializedLength == 13);
      CHECK(std::string{testStr, serializedLength} == "DEBUG | ERROR");
    }
    SECTION(
        "Passing in more the precisely required returns success and the serialized length of 13") {
      uint32_t serializedLength = 13;
      CHECK(vk_serialize32("VkDebugReportFlagsEXT",
                           VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT,
                           &serializedLength, testStr) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(serializedLength == 13);
      CHECK(std::string{testStr, serializedLength} == "DEBUG | ERROR");
    }
    SECTION("Passing in just under the rrequired returns incomplete data") {
      uint32_t serializedLength = 8;
      CHECK(vk_serialize32("VkDebugReportFlagsEXT",
                           VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT,
                           &serializedLength,
                           testStr) == STEC_VK_SERIALIZATION_RESULT_ERROR_INCOMPLETE);
      CHECK(serializedLength == 8);
      CHECK(std::string{testStr, serializedLength} == "DEBUG | ");
    }
    SECTION("Passing in just under the rrequired returns incomplete data") {
      uint32_t serializedLength = 6;
      CHECK(vk_serialize32("VkDebugReportFlagsEXT",
                           VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT,
                           &serializedLength,
                           testStr) == STEC_VK_SERIALIZATION_RESULT_ERROR_INCOMPLETE);
      CHECK(serializedLength == 6);
      CHECK(std::string{testStr, serializedLength} == "DEBUG ");
    }
    SECTION("Passing in just under the rrequired returns incomplete data") {
      uint32_t serializedLength = 5;
      CHECK(vk_serialize32("VkDebugReportFlagsEXT",
                           VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT,
                           &serializedLength,
                           testStr) == STEC_VK_SERIALIZATION_RESULT_ERROR_INCOMPLETE);
      CHECK(serializedLength == 5);
      CHECK(std::string{testStr, serializedLength} == "DEBUG");
    }
    SECTION("Passing in a zero-sized length returns incomplete and no written data") {
      uint32_t serializedLength = 0;
      CHECK(vk_serialize32("VkDebugReportFlagsEXT",
                           VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT,
                           &serializedLength,
                           testStr) == STEC_VK_SERIALIZATION_RESULT_ERROR_INCOMPLETE);
      CHECK(serializedLength == 0);
      CHECK(testStr[0] == '\0');
    }

    SECTION("Check for enum") {
      uint32_t serializedLength = 1;
      CHECK(vk_serialize32("VkImageType", VK_IMAGE_TYPE_3D, &serializedLength, testStr) ==
            STEC_VK_SERIALIZATION_RESULT_ERROR_INCOMPLETE);
      CHECK(serializedLength == 1);
      CHECK(std::string{testStr, serializedLength} == "3");
    }
  }
}