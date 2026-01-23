// Copyright (C) 2021-2022 George Cave - gcave@stablecoder.ca
//
// SPDX-License-Identifier: Apache-2.0

#ifndef VK_VALUE_SERIALIZATION_HPP
#define VK_VALUE_SERIALIZATION_HPP

/*  USAGE:
    To use, include this header where the declarations for the boolean checks are required.

    On *ONE* compilation unit, include the definition of:
    #define VK_VALUE_SERIALIZATION_CONFIG_MAIN

    so that the definitions are compiled somewhere following the one definition rule, either from
    this header *OR* the vk_value_serialization.hpp header.
*/

#include "vk_value_serialization.h"

#include <string>
#include <type_traits>

/**
 * @brief Macro that automatically stringifies the given Vulkan type for serialization
 * @param VKTYPE Actual Vulkan type
 * @param VALUE Value to be serialized
 * @param STRPTR Pointer to the string to store the serialization in. Only modified if true is
 * returned.
 * @return True if serialization was successful. False otherwise.
 */
#define VK_SERIALIZE(VKTYPE, VALUE, STRPTR) vk_serialize<VKTYPE>(#VKTYPE, VALUE, STRPTR)

/**
 * @brief Macro that automatically stringifies the given Vulkan type for parsing
 * @param VKTYPE Actual Vulkan type
 * @param STRING String to be parsed
 * @param VALPTR Pointer to the value to store the parsed value in. Only modified if true is
 * returned.
 * @return True if serialization was successful. False otherwise.
 */
#define VK_PARSE(VKTYPE, STRING, VALPTR) vk_parse<VKTYPE>(#VKTYPE, STRING, VALPTR)

/**
 * @brief Serializes a Vulkan enumerator/flag type
 * @tparam Vulkan type being serialized
 * @param pVkType Name of the Vulkan enumerator/flag type
 * @param vkValue Value being serialized
 * @param pString Pointer to a string that will be modified with the serialized value. Only modified
 * if true is returned.
 * @return True the value was successfully serialized. False otherwise.
 */
template <typename T>
STecVkSerializationResult vk_serialize(char const *pVkType, T vkValue, std::string *pString) {
  // Only have parse/serialize for 32/64-bit flag types
  static_assert(sizeof(T) == 4 || sizeof(T) == 8,
                "vk_serialize only supports 32 and 64-bit types currently.");

  STecVkSerializationResult result;
  uint32_t serializedLength;
  if constexpr (sizeof(T) == 4) {
    result = vk_serialize32(pVkType, vkValue, &serializedLength, nullptr);
    if (result == STEC_VK_SERIALIZATION_RESULT_SUCCESS) {
      pString->resize(serializedLength);
      result = vk_serialize32(pVkType, vkValue, &serializedLength, pString->data());
    }
  } else if constexpr (sizeof(T) == 8) {
    result = vk_serialize64(pVkType, vkValue, &serializedLength, nullptr);
    if (result == STEC_VK_SERIALIZATION_RESULT_SUCCESS) {
      pString->resize(serializedLength);
      result = vk_serialize64(pVkType, vkValue, &serializedLength, pString->data());
    }
  }

  return result;
}

/**
 * @brief Parses a Vulkan enumerator/flag serialized string
 * @tparam Vulkan type being parsed
 * @param pVkType Name of the Vulkan enumerator/flag type
 * @param pVkString String being parsed
 * @param pValue Pointer to a value that will be modified with the parsed value. Only modified if
 * true is returned.
 * @return True the value was successfully serialized. False otherwise.
 */
template <typename T>
STecVkSerializationResult vk_parse(char const *pVkType, char const *pVkString, T *pValue) {
  // Only have parse/serialize for 32/64-bit flag types
  static_assert(sizeof(T) == 4 || sizeof(T) == 8,
                "vk_parse only supports 32 and 64-bit types currently.");

  STecVkSerializationResult result;
  if constexpr (sizeof(T) == 4) {
    result = vk_parse32(pVkType, pVkString, pValue);
  } else if constexpr (sizeof(T) == 8) {
    result = vk_parse64(pVkType, pVkString, pValue);
  }

  return result;
}

#endif // VK_VALUE_SERIALIZATION_HPP
