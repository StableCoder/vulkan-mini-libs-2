/*
    Copyright (C) 2021-2023 George Cave - gcave@stablecoder.ca

    SPDX-License-Identifier: Apache-2.0

    This file was auto-generated by the Vulkan Mini Libs 2 utility:
    https://github.com/stablecoder/vulkan-mini-libs-2.git
    or
    https://git.stabletec.com/utilities/vulkan-mini-libs-2.git

    Check for an updated version anytime, or state concerns/bugs.
*/

#ifndef VK_RESULT_TO_STRING_H
#define VK_RESULT_TO_STRING_H

/*  USAGE
    To use, include this header where the declarations for the boolean checks are required.

    On *ONE* compilation unit, include the definition of:
    #define VK_RESULT_TO_STRING_CONFIG_MAIN

    so that the definitions are compiled somewhere following the one definition rule.
*/

#ifdef __cplusplus
extern "C" {
#endif

#include <vulkan/vulkan.h>

#ifdef __cplusplus
static_assert(VK_HEADER_VERSION >= 72,
              "vulkan header version is from before the minimum supported version of v72.");
static_assert(VK_HEADER_VERSION <= 254,
              "vulkan header version is from after the maximum supported version of v254.");
#else
_Static_assert(VK_HEADER_VERSION >= 72,
               "vulkan header version is from before the minimum supported version of v72.");
_Static_assert(VK_HEADER_VERSION <= 254,
               "vulkan header version is from after the maximum supported version of v254.");
#endif

/// Returns a string representing the given VkResult parameter. If there is no known representation,
/// returns NULL.
char const *VkResult_to_string(VkResult result);

/// Similar to VkResult_to_string, except in the case where it is an unknown value, returns a string
/// stating '(unrecognized positive/negative VkResult value)', thus never returning NULL.
char const *vkResultToString(VkResult result);

#ifdef VK_RESULT_TO_STRING_CONFIG_MAIN

char const *VkResult_to_string(VkResult result) {
  // Check in descending order to get the 'latest' version of the error code text available.
  // Also, because codes have been re-used over time, can't use a switch and have to do this large
  // set of ifs. Luckily this *should* be a relatively rare call.
#if VK_HEADER_VERSION >= 246 && VK_EXT_shader_object
  if (result == VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT)
    return "VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT";
#endif
#if VK_HEADER_VERSION >= 243 && VK_KHR_video_encode_queue
  if (result == VK_ERROR_INVALID_VIDEO_STD_PARAMETERS_KHR)
    return "VK_ERROR_INVALID_VIDEO_STD_PARAMETERS_KHR";
#endif
#if VK_HEADER_VERSION >= 218 && VK_KHR_video_queue
  if (result == VK_ERROR_IMAGE_USAGE_NOT_SUPPORTED_KHR)
    return "VK_ERROR_IMAGE_USAGE_NOT_SUPPORTED_KHR";
#endif
#if VK_HEADER_VERSION >= 218 && VK_KHR_video_queue
  if (result == VK_ERROR_VIDEO_PICTURE_LAYOUT_NOT_SUPPORTED_KHR)
    return "VK_ERROR_VIDEO_PICTURE_LAYOUT_NOT_SUPPORTED_KHR";
#endif
#if VK_HEADER_VERSION >= 218 && VK_KHR_video_queue
  if (result == VK_ERROR_VIDEO_PROFILE_OPERATION_NOT_SUPPORTED_KHR)
    return "VK_ERROR_VIDEO_PROFILE_OPERATION_NOT_SUPPORTED_KHR";
#endif
#if VK_HEADER_VERSION >= 218 && VK_KHR_video_queue
  if (result == VK_ERROR_VIDEO_PROFILE_FORMAT_NOT_SUPPORTED_KHR)
    return "VK_ERROR_VIDEO_PROFILE_FORMAT_NOT_SUPPORTED_KHR";
#endif
#if VK_HEADER_VERSION >= 218 && VK_KHR_video_queue
  if (result == VK_ERROR_VIDEO_PROFILE_CODEC_NOT_SUPPORTED_KHR)
    return "VK_ERROR_VIDEO_PROFILE_CODEC_NOT_SUPPORTED_KHR";
#endif
#if VK_HEADER_VERSION >= 218 && VK_KHR_video_queue
  if (result == VK_ERROR_VIDEO_STD_VERSION_NOT_SUPPORTED_KHR)
    return "VK_ERROR_VIDEO_STD_VERSION_NOT_SUPPORTED_KHR";
#endif
#if VK_HEADER_VERSION >= 213 && VK_EXT_image_compression_control
  if (result == VK_ERROR_COMPRESSION_EXHAUSTED_EXT)
    return "VK_ERROR_COMPRESSION_EXHAUSTED_EXT";
#endif
#if VK_HEADER_VERSION >= 204
  if (result == VK_PIPELINE_COMPILE_REQUIRED)
    return "VK_PIPELINE_COMPILE_REQUIRED";
#endif
#if VK_HEADER_VERSION >= 204 && VK_KHR_global_priority
  if (result == VK_ERROR_NOT_PERMITTED_KHR)
    return "VK_ERROR_NOT_PERMITTED_KHR";
#endif
#if VK_HEADER_VERSION >= 136 && VK_EXT_pipeline_creation_cache_control
  if (result == VK_PIPELINE_COMPILE_REQUIRED_EXT)
    return "VK_PIPELINE_COMPILE_REQUIRED_EXT";
#endif
#if VK_HEADER_VERSION >= 135 && VK_KHR_deferred_host_operations
  if (result == VK_THREAD_IDLE_KHR)
    return "VK_THREAD_IDLE_KHR";
#endif
#if VK_HEADER_VERSION >= 135 && VK_KHR_deferred_host_operations
  if (result == VK_THREAD_DONE_KHR)
    return "VK_THREAD_DONE_KHR";
#endif
#if VK_HEADER_VERSION >= 135 && VK_KHR_deferred_host_operations
  if (result == VK_OPERATION_DEFERRED_KHR)
    return "VK_OPERATION_DEFERRED_KHR";
#endif
#if VK_HEADER_VERSION >= 135 && VK_KHR_deferred_host_operations
  if (result == VK_OPERATION_NOT_DEFERRED_KHR)
    return "VK_OPERATION_NOT_DEFERRED_KHR";
#endif
#if VK_HEADER_VERSION >= 135 && VK_EXT_pipeline_creation_cache_control
  if (result == VK_ERROR_PIPELINE_COMPILE_REQUIRED_EXT)
    return "VK_ERROR_PIPELINE_COMPILE_REQUIRED_EXT";
#endif
#if VK_HEADER_VERSION >= 135 && VK_HEADER_VERSION <= 161 && VK_KHR_ray_tracing
  if (result == VK_ERROR_INCOMPATIBLE_VERSION_KHR)
    return "VK_ERROR_INCOMPATIBLE_VERSION_KHR";
#endif
#if VK_HEADER_VERSION >= 131
  if (result == VK_ERROR_UNKNOWN)
    return "VK_ERROR_UNKNOWN";
#endif
#if VK_HEADER_VERSION >= 131
  if (result == VK_ERROR_FRAGMENTATION)
    return "VK_ERROR_FRAGMENTATION";
#endif
#if VK_HEADER_VERSION >= 131
  if (result == VK_ERROR_INVALID_OPAQUE_CAPTURE_ADDRESS)
    return "VK_ERROR_INVALID_OPAQUE_CAPTURE_ADDRESS";
#endif
#if VK_HEADER_VERSION >= 129 && VK_KHR_buffer_device_address
  if (result == VK_ERROR_INVALID_OPAQUE_CAPTURE_ADDRESS_KHR)
    return "VK_ERROR_INVALID_OPAQUE_CAPTURE_ADDRESS_KHR";
#endif
#if VK_HEADER_VERSION >= 104 && VK_EXT_full_screen_exclusive
  if (result == VK_ERROR_FULL_SCREEN_EXCLUSIVE_MODE_LOST_EXT)
    return "VK_ERROR_FULL_SCREEN_EXCLUSIVE_MODE_LOST_EXT";
#endif
#if VK_HEADER_VERSION >= 97 && VK_EXT_buffer_device_address
  if (result == VK_ERROR_INVALID_DEVICE_ADDRESS_EXT)
    return "VK_ERROR_INVALID_DEVICE_ADDRESS_EXT";
#endif
#if VK_HEADER_VERSION >= 88 && VK_EXT_image_drm_format_modifier
  if (result == VK_ERROR_INVALID_DRM_FORMAT_MODIFIER_PLANE_LAYOUT_EXT)
    return "VK_ERROR_INVALID_DRM_FORMAT_MODIFIER_PLANE_LAYOUT_EXT";
#endif
  if (result == VK_SUCCESS)
    return "VK_SUCCESS";
  if (result == VK_NOT_READY)
    return "VK_NOT_READY";
  if (result == VK_TIMEOUT)
    return "VK_TIMEOUT";
  if (result == VK_EVENT_SET)
    return "VK_EVENT_SET";
  if (result == VK_EVENT_RESET)
    return "VK_EVENT_RESET";
  if (result == VK_INCOMPLETE)
    return "VK_INCOMPLETE";
  if (result == VK_ERROR_OUT_OF_HOST_MEMORY)
    return "VK_ERROR_OUT_OF_HOST_MEMORY";
  if (result == VK_ERROR_OUT_OF_DEVICE_MEMORY)
    return "VK_ERROR_OUT_OF_DEVICE_MEMORY";
  if (result == VK_ERROR_INITIALIZATION_FAILED)
    return "VK_ERROR_INITIALIZATION_FAILED";
  if (result == VK_ERROR_DEVICE_LOST)
    return "VK_ERROR_DEVICE_LOST";
  if (result == VK_ERROR_MEMORY_MAP_FAILED)
    return "VK_ERROR_MEMORY_MAP_FAILED";
  if (result == VK_ERROR_LAYER_NOT_PRESENT)
    return "VK_ERROR_LAYER_NOT_PRESENT";
  if (result == VK_ERROR_EXTENSION_NOT_PRESENT)
    return "VK_ERROR_EXTENSION_NOT_PRESENT";
  if (result == VK_ERROR_FEATURE_NOT_PRESENT)
    return "VK_ERROR_FEATURE_NOT_PRESENT";
  if (result == VK_ERROR_INCOMPATIBLE_DRIVER)
    return "VK_ERROR_INCOMPATIBLE_DRIVER";
  if (result == VK_ERROR_TOO_MANY_OBJECTS)
    return "VK_ERROR_TOO_MANY_OBJECTS";
  if (result == VK_ERROR_FORMAT_NOT_SUPPORTED)
    return "VK_ERROR_FORMAT_NOT_SUPPORTED";
  if (result == VK_ERROR_FRAGMENTED_POOL)
    return "VK_ERROR_FRAGMENTED_POOL";
  if (result == VK_ERROR_OUT_OF_POOL_MEMORY)
    return "VK_ERROR_OUT_OF_POOL_MEMORY";
  if (result == VK_ERROR_INVALID_EXTERNAL_HANDLE)
    return "VK_ERROR_INVALID_EXTERNAL_HANDLE";
#if VK_KHR_surface
  if (result == VK_ERROR_SURFACE_LOST_KHR)
    return "VK_ERROR_SURFACE_LOST_KHR";
#endif
#if VK_KHR_surface
  if (result == VK_ERROR_NATIVE_WINDOW_IN_USE_KHR)
    return "VK_ERROR_NATIVE_WINDOW_IN_USE_KHR";
#endif
#if VK_KHR_swapchain
  if (result == VK_SUBOPTIMAL_KHR)
    return "VK_SUBOPTIMAL_KHR";
#endif
#if VK_KHR_swapchain
  if (result == VK_ERROR_OUT_OF_DATE_KHR)
    return "VK_ERROR_OUT_OF_DATE_KHR";
#endif
#if VK_KHR_display_swapchain
  if (result == VK_ERROR_INCOMPATIBLE_DISPLAY_KHR)
    return "VK_ERROR_INCOMPATIBLE_DISPLAY_KHR";
#endif
#if VK_EXT_debug_report
  if (result == VK_ERROR_VALIDATION_FAILED_EXT)
    return "VK_ERROR_VALIDATION_FAILED_EXT";
#endif
#if VK_NV_glsl_shader
  if (result == VK_ERROR_INVALID_SHADER_NV)
    return "VK_ERROR_INVALID_SHADER_NV";
#endif
#if VK_KHR_maintenance1
  if (result == VK_ERROR_OUT_OF_POOL_MEMORY_KHR)
    return "VK_ERROR_OUT_OF_POOL_MEMORY_KHR";
#endif
#if VK_KHR_external_memory
  if (result == VK_ERROR_INVALID_EXTERNAL_HANDLE_KHR)
    return "VK_ERROR_INVALID_EXTERNAL_HANDLE_KHR";
#endif
#if VK_EXT_descriptor_indexing
  if (result == VK_ERROR_FRAGMENTATION_EXT)
    return "VK_ERROR_FRAGMENTATION_EXT";
#endif
#if VK_EXT_global_priority
  if (result == VK_ERROR_NOT_PERMITTED_EXT)
    return "VK_ERROR_NOT_PERMITTED_EXT";
#endif

  return NULL;
}

char const *vkResultToString(VkResult result) {
  char const *pResultString = VkResult_to_string(result);
  if (pResultString != NULL)
    return pResultString;

  if (result > 0)
    return "(unrecognized positive VkResult value)";
  else
    return "(unrecognized negative VkResult value)";
}

#endif // VK_RESULT_TO_STRING_CONFIG_MAIN

#ifdef __cplusplus
}
#endif

#endif // VK_RESULT_TO_STRING_H
