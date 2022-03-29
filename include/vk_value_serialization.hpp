/*
    Copyright (C) 2021-2022 George Cave - gcave@stablecoder.ca

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
    result = vk_serialize32(pVkType, static_cast<uint32_t>(vkValue), &serializedLength, nullptr);
    if (result == STEC_VK_SERIALIZATION_RESULT_SUCCESS) {
      pString->resize(serializedLength);
      result = vk_serialize32(pVkType, static_cast<uint32_t>(vkValue), &serializedLength,
                              pString->data());
    }
  } else {
    result = vk_serialize64(pVkType, static_cast<uint64_t>(vkValue), &serializedLength, nullptr);
    if (result == STEC_VK_SERIALIZATION_RESULT_SUCCESS) {
      pString->resize(serializedLength);
      result = vk_serialize64(pVkType, static_cast<uint64_t>(vkValue), &serializedLength,
                              pString->data());
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
    uint32_t retVal;
    result = vk_parse32(pVkType, pVkString, &retVal);
    if (result == STEC_VK_SERIALIZATION_RESULT_SUCCESS) {
      *pValue = static_cast<T>(retVal);
    }
  } else {
    uint64_t retVal;
    result = vk_parse64(pVkType, pVkString, &retVal);
    if (result == STEC_VK_SERIALIZATION_RESULT_SUCCESS) {
      *pValue = static_cast<T>(retVal);
    }
  }
  return result;
}

#endif // VK_VALUE_SERIALIZATION_HPP
