// Copyright (C) 2020 George Cave - gcave@stablecoder.ca
//
// SPDX-License-Identifier: Apache-2.0

#include <cassert>
#include <iostream>

#define VK_RESULT_TO_STRING_CONFIG_MAIN
#define VK_ERROR_CODE_CONFIG_MAIN
#include "vk_error_code.hpp"

int main(int argc, char **argv) {
  std::error_code ec = VK_ERROR_DEVICE_LOST;
  assert(ec);
  assert(ec == VK_ERROR_DEVICE_LOST);
  assert(ec != VK_SUCCESS);
  std::cout << ec << std::endl;
}