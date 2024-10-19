// Copyright (C) 2020-2024 George Cave - gcave@stablecoder.ca
//
// SPDX-License-Identifier: Apache-2.0

#include <catch2/catch_test_macros.hpp>
#include <vulkan/vulkan.h>

#define VK_VALUE_SERIALIZATION_CONFIG_MAIN
#include <vk_value_serialization.hpp>

constexpr uint64_t cDummyNum = 999999;

TEST_CASE("Parsing: Failure Cases") {
  uint64_t dummy = cDummyNum;

  SECTION("Garbage type fails") {
    CHECK(vk_parse(nullptr, "2D", &dummy) == STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND);
    CHECK(dummy == cDummyNum);

    CHECK(vk_parse("", "2D", &dummy) == STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND);
    CHECK(dummy == cDummyNum);

    CHECK(vk_parse("AMDX", "2D", &dummy) == STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND);
    CHECK(dummy == cDummyNum);

    CHECK(vk_parse("VkGarbagio", "2D", &dummy) ==
          STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND);
    CHECK(dummy == cDummyNum);

    CHECK(vk_parse("VkGarbagioFlags", "2D", &dummy) ==
          STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND);
    CHECK(dummy == cDummyNum);
  }
  SECTION("Garbage values fails") {
    CHECK(vk_parse("VkImageType", "6D", &dummy) ==
          STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND);
    CHECK(dummy == cDummyNum);
    CHECK(vk_parse("VkDebugReportFlagBitsEXT", "NOT_EXIST", &dummy) ==
          STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND);
    CHECK(dummy == cDummyNum);
  }
  SECTION("Attempting to do a bitmask for an enum returns nothing") {
    CHECK(vk_parse("VkImageType", "2D | 3D", &dummy) ==
          STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND);
    CHECK(dummy == cDummyNum);
  }
  SECTION("Parsing an enum type with a blank value that doesn't allow empty values fails") {
    CHECK(vk_parse("VkImageType", "", &dummy) ==
          STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_HAS_NO_EMPTY_VALUE);
    CHECK(dummy == cDummyNum);
  }
  SECTION("Parsing with an empty type fails") {
    CHECK(vk_parse("", "2D", &dummy) == STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND);
  }
}

TEST_CASE("Parsing: Odd success cases") {
  uint32_t retVal = cDummyNum;

  SECTION("Parsing a type that allows null with an empty string succeeds, returns 0") {
    CHECK(vk_parse("VkPipelineDepthStencilStateCreateFlagBits", "", &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == 0);
  }
}

TEST_CASE("Parsing: Checking enum conversions from strings to the values from the  actual header") {
  uint32_t retVal = cDummyNum;

  SECTION("Success where the value is also a vendor name") {
    CHECK(vk_parse("VkVendorId", "VIV", &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == VK_VENDOR_ID_VIV);
  }

  SECTION("With original shortened strings") {
    CHECK(vk_parse("VkImageLayout", "UNDEFINED", &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == VK_IMAGE_LAYOUT_UNDEFINED);

    CHECK(vk_parse("VkImageLayout", "TRANSFER_DST_OPTIMAL", &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);

    CHECK(vk_parse("VkImageType", "2D", &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == VK_IMAGE_TYPE_2D);
  }
  SECTION("With extra spaces around the type") {
    CHECK(vk_parse("VkImageLayout", "    VK_IMAGE_LAYOUT_UNDEFINED    ", &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == VK_IMAGE_LAYOUT_UNDEFINED);
  }
  SECTION("With mixed capitalization and mixture of underscores/spaces") {
    CHECK(vk_parse("VkImageLayout", "    vK IMagE_LAyOUt UNDEFIned    ", &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == VK_IMAGE_LAYOUT_UNDEFINED);
  }
  SECTION("With full strings") {
    CHECK(vk_parse("VkImageLayout", "VK_IMAGE_LAYOUT_UNDEFINED", &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == VK_IMAGE_LAYOUT_UNDEFINED);

    CHECK(vk_parse("VkImageLayout", "VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL", &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);

    CHECK(vk_parse("VkImageType", "VK_IMAGE_TYPE_2D", &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == VK_IMAGE_TYPE_2D);
  }

  SECTION("With Vendor Tags") {
    CHECK(vk_parse("VkPresentModeKHR", "VK_PRESENT_MODE_IMMEDIATE_KHR", &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == VK_PRESENT_MODE_IMMEDIATE_KHR);

    CHECK(vk_parse("VkPresentModeKHR", "IMMEDIATE_KHR", &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == VK_PRESENT_MODE_IMMEDIATE_KHR);

    CHECK(vk_parse("VkPresentModeKHR", "VK_PRESENT_MODE_IMMEDIATE", &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == VK_PRESENT_MODE_IMMEDIATE_KHR);

    CHECK(vk_parse("VkPresentModeKHR", "IMMEDIATE", &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == VK_PRESENT_MODE_IMMEDIATE_KHR);
  }

  SECTION("With replaced enum sets through promotion") {
    CHECK(vk_parse("VkExternalMemoryFeatureFlagBits", "EXPORTABLE_BIT_KHR", &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == VK_EXTERNAL_MEMORY_FEATURE_EXPORTABLE_BIT);

    CHECK(vk_parse("VkExternalMemoryFeatureFlagBits", "EXPORTABLE", &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == VK_EXTERNAL_MEMORY_FEATURE_EXPORTABLE_BIT);

    CHECK(vk_parse("VkExternalMemoryFeatureFlagBitsNV", "EXPORTABLE_BIT_KHR", &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == VK_EXTERNAL_MEMORY_FEATURE_EXPORTABLE_BIT);

    CHECK(vk_parse("VkExternalMemoryFeatureFlagBitsNV", "EXPORTABLE", &retVal) ==
          STEC_VK_SERIALIZATION_RESULT_SUCCESS);
    CHECK(retVal == VK_EXTERNAL_MEMORY_FEATURE_EXPORTABLE_BIT);
  }
}

TEST_CASE("Parsing: Checking bitmask conversions from string to bitmask values") {
  uint32_t retVal = cDummyNum;

  SECTION("With a bad extra bitmask fails") {
    CHECK(vk_parse("VkDebugReportFlagBitsEXT", "PERFORMANCE_WARNING_BIT | NON_EXISTING_BIT",
                   &retVal) == STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND);
    CHECK(retVal == cDummyNum);

    CHECK(vk_parse("VkDebugReportFlagBitsEXT", "NON_EXISTING_BIT | PERFORMANCE_WARNING_BIT",
                   &retVal) == STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND);
    CHECK(retVal == cDummyNum);
  }

  SECTION("With original shortened strings") {
    SECTION("FlagBits") {
      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "PERFORMANCE_WARNING_BIT", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "PERFORMANCE_WARNING", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "DEBUG_BIT", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_DEBUG_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "DEBUG", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_DEBUG_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "ERROR_BIT", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_ERROR_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "ERROR", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_ERROR_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "DEBUG_BIT | ERROR_BIT", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "DEBUG | ERROR", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));
    }
    SECTION("Flags") {
      CHECK(vk_parse("VkDebugReportFlagsEXT", "PERFORMANCE_WARNING_BIT", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "PERFORMANCE_WARNING", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "DEBUG_BIT", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_DEBUG_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "DEBUG", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_DEBUG_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "ERROR_BIT", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_ERROR_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "ERROR", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_ERROR_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "DEBUG_BIT | ERROR_BIT", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));

      CHECK(vk_parse("VkDebugReportFlagsEXT", "DEBUG | ERROR", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));
    }
  }
  SECTION("With full strings") {
    SECTION("FlagBits") {
      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT",
                     &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "VK_DEBUG_REPORT_PERFORMANCE_WARNING", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "VK_DEBUG_REPORT_DEBUG_BIT", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_DEBUG_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "VK_DEBUG_REPORT_DEBUG", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_DEBUG_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "VK_DEBUG_REPORT_ERROR_BIT", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_ERROR_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "VK_DEBUG_REPORT_ERROR", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_ERROR_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagBitsEXT",
                     "VK_DEBUG_REPORT_DEBUG_BIT | VK_DEBUG_REPORT_ERROR_BIT",
                     &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "VK_DEBUG_REPORT_ERROR | VK_DEBUG_REPORT_DEBUG",
                     &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));
    }
    SECTION("Flags") {
      CHECK(vk_parse("VkDebugReportFlagsEXT", "VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "VK_DEBUG_REPORT_PERFORMANCE_WARNING", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_PERFORMANCE_WARNING_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "VK_DEBUG_REPORT_DEBUG_BIT", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_DEBUG_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "VK_DEBUG_REPORT_DEBUG", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_DEBUG_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "VK_DEBUG_REPORT_ERROR_BIT", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_ERROR_BIT_EXT);

      CHECK(vk_parse("VkDebugReportFlagsEXT", "VK_DEBUG_REPORT_ERROR", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == VK_DEBUG_REPORT_ERROR_BIT_EXT);

      CHECK(
          vk_parse(
              "VkPipelineColorBlendStateCreateFlags",
              "VK_PIPELINE_COLOR_BLEND_STATE_CREATE_RASTERIZATION_ORDER_ATTACHMENT_ACCESS_BIT_ARM",
              &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == 0x00000001);

      CHECK(vk_parse("VkDebugReportFlagsEXT",
                     "VK_DEBUG_REPORT_DEBUG_BIT | VK_DEBUG_REPORT_ERROR_BIT",
                     &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));

      CHECK(vk_parse("VkDebugReportFlagsEXT", "VK_DEBUG_REPORT_ERROR | VK_DEBUG_REPORT_DEBUG",
                     &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));
    }
  }
  SECTION("With mixed short/full strings") {
    SECTION("FlagBits") {
      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "DEBUG_BIT | VK_DEBUG_REPORT_ERROR_BIT",
                     &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));

      CHECK(vk_parse("VkDebugReportFlagBitsEXT", "VK_DEBUG_REPORT_ERROR_BIT | DEBUG_BIT",
                     &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));
    }
    SECTION("Flags") {
      CHECK(vk_parse("VkDebugReportFlagsEXT", "DEBUG_BIT | VK_DEBUG_REPORT_ERROR_BIT", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));

      CHECK(vk_parse("VkDebugReportFlagsEXT", "VK_DEBUG_REPORT_ERROR_BIT | DEBUG_BIT", &retVal) ==
            STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == (VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT));
    }
  }

  SECTION("With mixed short/full strings (64-bit)") {
    uint64_t retVal = 0;

    SECTION("FlagBits") {
      CHECK(vk_parse("VkPipelineStageFlagBits2",
                     "INVOCATION_MASK_BIT_HUAWEI | VK_PIPELINE_STAGE_2_TOP_OF_PIPE_BIT",
                     &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == (0x10000000000ULL | 0x00000001ULL));

      CHECK(vk_parse64("VkPipelineStageFlagBits2",
                       "INVOCATION_MASK_BIT_HUAWEI | VK_PIPELINE_STAGE_2_TOP_OF_PIPE_BIT",
                       &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == (0x10000000000ULL | 0x00000001ULL));

      CHECK(vk_parse64("VkPipelineStageFlagBits2",
                       "VK_PIPELINE_STAGE_2_TOP_OF_PIPE_BIT | INVOCATION_MASK_BIT_HUAWEI",
                       &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == (0x10000000000ULL | 0x00000001ULL));
    }
    SECTION("Flags") {
      CHECK(vk_parse("VkPipelineStageFlags2",
                     "INVOCATION_MASK_BIT_HUAWEI | VK_PIPELINE_STAGE_2_TOP_OF_PIPE_BIT",
                     &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == (0x10000000000ULL | 0x00000001ULL));

      CHECK(vk_parse64("VkPipelineStageFlags2",
                       "INVOCATION_MASK_BIT_HUAWEI | VK_PIPELINE_STAGE_2_TOP_OF_PIPE_BIT",
                       &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == (0x10000000000ULL | 0x00000001ULL));

      CHECK(vk_parse64("VkPipelineStageFlags2",
                       "VK_PIPELINE_STAGE_2_TOP_OF_PIPE_BIT | INVOCATION_MASK_BIT_HUAWEI",
                       &retVal) == STEC_VK_SERIALIZATION_RESULT_SUCCESS);
      CHECK(retVal == (0x10000000000ULL | 0x00000001ULL));
    }
  }
}