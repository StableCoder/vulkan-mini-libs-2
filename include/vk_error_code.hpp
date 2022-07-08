// Copyright (C) 2021 George Cave - gcave@stablecoder.ca
//
// SPDX-License-Identifier: Apache-2.0

#ifndef VK_ERROR_CODE_HPP
#define VK_ERROR_CODE_HPP

#include <vk_result_to_string.h>
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
  return vkResultToString(static_cast<VkResult>(ev));
}

const VulkanErrCategory vulkanErrCategory{};

} // namespace

std::error_code make_error_code(VkResult e) { return {static_cast<int>(e), vulkanErrCategory}; }

#endif // VK_ERROR_CODE_CONFIG_MAIN
#endif // VK_ERROR_CODE_HPP
