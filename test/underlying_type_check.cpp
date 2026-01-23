// Copyright (C) 2026 George Cave - gcave@stablecoder.ca
//
// SPDX-License-Identifier: Apache-2.0

#include <vulkan/vulkan.h>

#include <cstdint>
#include <type_traits>

static_assert(std::is_same_v<uint32_t, VkFlags>,
              "Expected 'uint32_t' to be the underlying type of 'VkFlags'");

static_assert(std::is_same_v<uint64_t, VkFlags64>,
              "Expected 'uint64_t' to be the underlying type of 'VkFlags64'");

static_assert(std::is_same_v<int32_t, std::underlying_type_t<VkResult>>,
              "Expected 'int32_t' to be the underlying type of 'VkResult'");