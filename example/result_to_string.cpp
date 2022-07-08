// Copyright (C) 2021 George Cave - gcave@stablecoder.ca
//
// SPDX-License-Identifier: Apache-2.0

#define VK_RESULT_TO_STRING_CONFIG_MAIN
#include "vk_result_to_string.h"
#include <iostream>

int main(int, char **) {
  char const *resStr = vkResultToString(VK_ERROR_DEVICE_LOST);
  std::cout << resStr << std::endl;
}