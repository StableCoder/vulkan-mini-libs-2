/*
    Copyright (C) 2021 George Cave - gcave@stablecoder.ca

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
*/

/*
    This file was auto-generated by the Vulkan Mini Libs 2 utility:
    https://github.com/stablecoder/vulkan-mini-libs-2.git
    or
    https://git.stabletec.com/utilities/vulkan-mini-libs-2.git

    Check for an updated version anytime, or state concerns/bugs.
*/

#ifndef VK_ERROR_CODE_HPP
#define VK_ERROR_CODE_HPP

#include <vulkan/vulkan.h>

#include <system_error>

/*  USAGE
    To use, include this header where the declarations for the boolean checks are required.

    On *ONE* compilation unit, include the definition of `#define VK_ERROR_CODE_CONFIG_MAIN`
    so that the definitions are compiled somewhere following the one definition rule.
*/

namespace std {
template <>
struct is_error_code_enum<VkResult> : true_type {};
} // namespace std

std::error_code make_error_code(VkResult);

#ifdef VK_ERROR_CODE_CONFIG_MAIN

namespace {

struct VulkanErrCategory : std::error_category {
  const char *name() const noexcept override;
  std::string message(int ev) const override;
};

const char *VulkanErrCategory::name() const noexcept { return "VkResult"; }

std::string VulkanErrCategory::message(int ev) const {
  VkResult const vkRes = static_cast<VkResult>(ev);
  if (vkRes == VK_SUCCESS)
    return "VK_SUCCESS";
  if (vkRes == VK_NOT_READY)
    return "VK_NOT_READY";
  if (vkRes == VK_TIMEOUT)
    return "VK_TIMEOUT";
  if (vkRes == VK_EVENT_SET)
    return "VK_EVENT_SET";
  if (vkRes == VK_EVENT_RESET)
    return "VK_EVENT_RESET";
  if (vkRes == VK_INCOMPLETE)
    return "VK_INCOMPLETE";
  if (vkRes == VK_ERROR_OUT_OF_HOST_MEMORY)
    return "VK_ERROR_OUT_OF_HOST_MEMORY";
  if (vkRes == VK_ERROR_OUT_OF_DEVICE_MEMORY)
    return "VK_ERROR_OUT_OF_DEVICE_MEMORY";
  if (vkRes == VK_ERROR_INITIALIZATION_FAILED)
    return "VK_ERROR_INITIALIZATION_FAILED";
  if (vkRes == VK_ERROR_DEVICE_LOST)
    return "VK_ERROR_DEVICE_LOST";
  if (vkRes == VK_ERROR_MEMORY_MAP_FAILED)
    return "VK_ERROR_MEMORY_MAP_FAILED";
  if (vkRes == VK_ERROR_LAYER_NOT_PRESENT)
    return "VK_ERROR_LAYER_NOT_PRESENT";
  if (vkRes == VK_ERROR_EXTENSION_NOT_PRESENT)
    return "VK_ERROR_EXTENSION_NOT_PRESENT";
  if (vkRes == VK_ERROR_FEATURE_NOT_PRESENT)
    return "VK_ERROR_FEATURE_NOT_PRESENT";
  if (vkRes == VK_ERROR_INCOMPATIBLE_DRIVER)
    return "VK_ERROR_INCOMPATIBLE_DRIVER";
  if (vkRes == VK_ERROR_TOO_MANY_OBJECTS)
    return "VK_ERROR_TOO_MANY_OBJECTS";
  if (vkRes == VK_ERROR_FORMAT_NOT_SUPPORTED)
    return "VK_ERROR_FORMAT_NOT_SUPPORTED";
  if (vkRes == VK_ERROR_FRAGMENTED_POOL)
    return "VK_ERROR_FRAGMENTED_POOL";
#if VK_HEADER_VERSION >= 131
  if (vkRes == VK_ERROR_UNKNOWN)
    return "VK_ERROR_UNKNOWN";
#endif
  if (vkRes == VK_ERROR_OUT_OF_POOL_MEMORY)
    return "VK_ERROR_OUT_OF_POOL_MEMORY";
  if (vkRes == VK_ERROR_INVALID_EXTERNAL_HANDLE)
    return "VK_ERROR_INVALID_EXTERNAL_HANDLE";
#if VK_HEADER_VERSION >= 131
  if (vkRes == VK_ERROR_FRAGMENTATION)
    return "VK_ERROR_FRAGMENTATION";
#endif
#if VK_HEADER_VERSION >= 131
  if (vkRes == VK_ERROR_INVALID_OPAQUE_CAPTURE_ADDRESS)
    return "VK_ERROR_INVALID_OPAQUE_CAPTURE_ADDRESS";
#endif
#if VK_KHR_surface
  if (vkRes == VK_ERROR_SURFACE_LOST_KHR)
    return "VK_ERROR_SURFACE_LOST_KHR";
#endif
#if VK_KHR_surface
  if (vkRes == VK_ERROR_NATIVE_WINDOW_IN_USE_KHR)
    return "VK_ERROR_NATIVE_WINDOW_IN_USE_KHR";
#endif
#if VK_KHR_swapchain
  if (vkRes == VK_SUBOPTIMAL_KHR)
    return "VK_SUBOPTIMAL_KHR";
#endif
#if VK_KHR_swapchain
  if (vkRes == VK_ERROR_OUT_OF_DATE_KHR)
    return "VK_ERROR_OUT_OF_DATE_KHR";
#endif
#if VK_KHR_display_swapchain
  if (vkRes == VK_ERROR_INCOMPATIBLE_DISPLAY_KHR)
    return "VK_ERROR_INCOMPATIBLE_DISPLAY_KHR";
#endif
#if VK_EXT_debug_report
  if (vkRes == VK_ERROR_VALIDATION_FAILED_EXT)
    return "VK_ERROR_VALIDATION_FAILED_EXT";
#endif
#if VK_NV_glsl_shader
  if (vkRes == VK_ERROR_INVALID_SHADER_NV)
    return "VK_ERROR_INVALID_SHADER_NV";
#endif
#if VK_KHR_maintenance1
  if (vkRes == VK_ERROR_OUT_OF_POOL_MEMORY_KHR)
    return "VK_ERROR_OUT_OF_POOL_MEMORY_KHR";
#endif
#if VK_KHR_external_memory
  if (vkRes == VK_ERROR_INVALID_EXTERNAL_HANDLE_KHR)
    return "VK_ERROR_INVALID_EXTERNAL_HANDLE_KHR";
#endif
#if VK_HEADER_VERSION >= 86 && VK_EXT_image_drm_format_modifier
  if (vkRes == VK_ERROR_INVALID_DRM_FORMAT_MODIFIER_PLANE_LAYOUT_EXT)
    return "VK_ERROR_INVALID_DRM_FORMAT_MODIFIER_PLANE_LAYOUT_EXT";
#endif
#if VK_EXT_descriptor_indexing
  if (vkRes == VK_ERROR_FRAGMENTATION_EXT)
    return "VK_ERROR_FRAGMENTATION_EXT";
#endif
#if VK_EXT_global_priority
  if (vkRes == VK_ERROR_NOT_PERMITTED_EXT)
    return "VK_ERROR_NOT_PERMITTED_EXT";
#endif
#if VK_HEADER_VERSION >= 97 && VK_EXT_buffer_device_address
  if (vkRes == VK_ERROR_INVALID_DEVICE_ADDRESS_EXT)
    return "VK_ERROR_INVALID_DEVICE_ADDRESS_EXT";
#endif
#if VK_HEADER_VERSION >= 104 && VK_EXT_full_screen_exclusive
  if (vkRes == VK_ERROR_FULL_SCREEN_EXCLUSIVE_MODE_LOST_EXT)
    return "VK_ERROR_FULL_SCREEN_EXCLUSIVE_MODE_LOST_EXT";
#endif
#if VK_HEADER_VERSION >= 129 && VK_KHR_buffer_device_address
  if (vkRes == VK_ERROR_INVALID_OPAQUE_CAPTURE_ADDRESS_KHR)
    return "VK_ERROR_INVALID_OPAQUE_CAPTURE_ADDRESS_KHR";
#endif
#if VK_HEADER_VERSION >= 135 && VK_KHR_deferred_host_operations
  if (vkRes == VK_THREAD_IDLE_KHR)
    return "VK_THREAD_IDLE_KHR";
#endif
#if VK_HEADER_VERSION >= 135 && VK_KHR_deferred_host_operations
  if (vkRes == VK_THREAD_DONE_KHR)
    return "VK_THREAD_DONE_KHR";
#endif
#if VK_HEADER_VERSION >= 135 && VK_KHR_deferred_host_operations
  if (vkRes == VK_OPERATION_DEFERRED_KHR)
    return "VK_OPERATION_DEFERRED_KHR";
#endif
#if VK_HEADER_VERSION >= 135 && VK_KHR_deferred_host_operations
  if (vkRes == VK_OPERATION_NOT_DEFERRED_KHR)
    return "VK_OPERATION_NOT_DEFERRED_KHR";
#endif
#if VK_HEADER_VERSION >= 136 && VK_EXT_pipeline_creation_cache_control
  if (vkRes == VK_PIPELINE_COMPILE_REQUIRED_EXT)
    return "VK_PIPELINE_COMPILE_REQUIRED_EXT";
#endif
#if VK_HEADER_VERSION >= 135 && VK_EXT_pipeline_creation_cache_control
  if (vkRes == VK_ERROR_PIPELINE_COMPILE_REQUIRED_EXT)
    return "VK_ERROR_PIPELINE_COMPILE_REQUIRED_EXT";
#endif
#if VK_HEADER_VERSION >= 135 && VK_HEADER_VERSION <= 161 && VK_KHR_ray_tracing
  if (vkRes == VK_ERROR_INCOMPATIBLE_VERSION_KHR)
    return "VK_ERROR_INCOMPATIBLE_VERSION_KHR";
#endif
#if VK_HEADER_VERSION >= 128 && VK_HEADER_VERSION <= 134 && VK_EXT_extension_298
  if (vkRes == VK_RESULT_EXT_298_RESERVED_VALUE_0_EXT)
    return "VK_RESULT_EXT_298_RESERVED_VALUE_0_EXT";
#endif

  if (vkRes > 0)
    return "(unrecognized positive VkResult value)";
  else
    return "(unrecognized negative VkResult value)";
}

const VulkanErrCategory vulkanErrCategory{};

} // namespace

std::error_code make_error_code(VkResult e) { return {static_cast<int>(e), vulkanErrCategory}; }

#endif // VK_ERROR_CODE_CONFIG_MAIN
#endif // VK_ERROR_CODE_HPP
