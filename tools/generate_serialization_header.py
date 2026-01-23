#!/usr/bin/env python3

# Copyright (C) 2022-2026 George Cave.
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import gen_common
import sys
import json


def processVendors(outFile, vendors):
    outFile.write(
        '#define cVendorCount sizeof(cVendorList) / sizeof(char const*)')
    outFile.write('\nchar const *cVendorList[{}] = {{\n'.format(len(vendors)))
    for vendor in vendors:
        outFile.write('  "{}",\n'.format(vendor))
    outFile.write('};\n\n')


def processEnumValue( enum, enum_data, value, value_data):
    if 'value' in value_data:
        # Spitting out plain values
        return str(value_data['value'])
    elif 'bitpos' in value_data:
        # Bitflag
        return '0x{}'.format(format(1 << int(value_data['bitpos']), '08X'))
    elif 'alias' in value_data:
        # go through to the alias target and use it's data
        aliasTarget = value_data['alias']
        if not aliasTarget in enum_data['values']:
          return ''
        return processEnumValue(enum, enum_data, aliasTarget, enum_data['values'][aliasTarget])
    else:
        print('Error: Unhandled enum value type {}::{}'.format(enum, value))
        sys.exit(1)

def processEnums(outFile, enums, vendors, first, last):
    for enum, enum_data in enums.items():
        # Skip VkResult
        if enum == 'VkResult' or enum == 'VkStructureType' or 'alias' in enum_data:
            continue
        # Skip if there's no values, MSVC can't do zero-sized arrays
        if not 'values' in enum_data:
            continue

        names = 'static char const *const {}Strings[{}] = {{\n'.format(enum, len(enum_data['values']))
        values = 'static int32_t const {}Values[{}] = {{\n'.format(enum, len(enum_data['values']))

        if 'type' in enum_data:
          if enum_data['type'] == 'VkFlags':
            values = 'static uint32_t const {}Values[{}] = {{\n'.format(enum, len(enum_data['values']))
          elif enum_data['type'] == 'VkFlags64':
            values = 'static uint64_t const {}Values[{}] = {{\n'.format(enum, len(enum_data['values']))
          else:
            print('Error: Unhandled enum type: '.format(enum_data['type']))
            sys.exit(1)

        # Determine how much to chop off the front
        strName = enum
        typeDigit = ''
        # Determine if type ends with vendor tag
        vendorName = ''
        for vendor in vendors:
            if strName.endswith(vendor):
                vendorName = vendor
                strName = strName[:-len(vendorName)]

        if strName[-1].isdigit():
            typeDigit = strName[-1]
            strName = strName[:-1]

        if strName.endswith('Flags'):
            strName = strName[:-5]

        # Construct most likely enum prefix
        mainPrefix = ''
        for char in strName:
            if mainPrefix == '':
                mainPrefix += char
            elif char.isupper():
                mainPrefix += '_'
                mainPrefix += char.upper()
            else:
                mainPrefix += char.upper()
        mainPrefix += '_'
        if typeDigit != '':
            mainPrefix += typeDigit
            mainPrefix += '_'

        # items with alias first
        current = first
        while current <= last:
            for value, value_data in enum_data['values'].items():
                if not 'alias' in value_data:
                    continue
                if value_data['first'] != current:
                    continue
                value_str = processEnumValue(enum, enum_data, value, value_data)
                if not value_str:
                  continue

                valueStr = value
                if valueStr.startswith(mainPrefix):
                    valueStr = valueStr[len(mainPrefix):]
                if vendorName != '' and valueStr.endswith(vendorName):
                    valueStr = valueStr[:-len(vendorName)-1]
                if valueStr.endswith('_BIT'):
                    valueStr = valueStr[:-4]

                # Name
                names += '  \"{}\", // {}\n'.format(valueStr, value_str)
                # Value
                values += '  {}, // {}\n'.format(value_str, valueStr)
            current += 1

        # items without alias last
        current = first
        while current <= last:
            for value, value_data in enum_data['values'].items():
                if 'alias' in value_data:
                    continue
                if value_data['first'] != current:
                    continue
                value_str = processEnumValue(enum, enum_data, value, value_data)
                if not value_str:
                  continue

                valueStr = value
                if valueStr.startswith(mainPrefix):
                    valueStr = valueStr[len(mainPrefix):]
                if vendorName != '' and valueStr.endswith(vendorName):
                    valueStr = valueStr[:-len(vendorName)-1]
                if valueStr.endswith('_BIT'):
                    valueStr = valueStr[:-4]

                # Name
                names += '  \"{}\", // {}\n'.format(valueStr, value_str)
                # Value
                values += '  {}, // {}\n'.format(value_str, valueStr)
            current += 1

        names += '};\n\n'
        values += '};\n\n'

        outFile.write(names)
        outFile.write(values)


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input',
                        help='Input JSON cache file',
                        required=True)
    parser.add_argument('-o', '--output',
                        help='Output file to write to',
                        required=True)
    args = parser.parse_args()

    try:
        file = open(args.input, 'r')
        apiData = json.load(file)
    except:
        print("Error: Could not open input file: ", args.input)
        sys.exit(1)

    firstVersion = apiData['api']['first']
    lastVersion = apiData['api']['last']

    outFile = open(args.output, "w")

    # Common Header
    gen_common.writeHeader(outFile)

     #
    outFile.write("""#ifndef VK_VALUE_SERIALIZATION_H
#define VK_VALUE_SERIALIZATION_H

/*  USAGE:
    To use, include this header where the declarations for the boolean checks are required.

    On *ONE* compilation unit, include the definition of:
    #define VK_VALUE_SERIALIZATION_CONFIG_MAIN
   
    so that the definitions are compiled somewhere following the one definition rule, either from
    this header *OR* the vk_value_serialization.hpp header.
*/

#ifdef __cplusplus
extern "C" {
#endif

#include <vulkan/vulkan.h>
""")

    # static asserts
    outFile.write('\n#ifdef __cplusplus\n')
    outFile.write(
        "static_assert(VK_HEADER_VERSION >= {0}, \"VK_HEADER_VERSION is lower than the minimum supported version (v{0})\");\n".format(firstVersion))
    outFile.write('#else\n')
    outFile.write(
        "_Static_assert(VK_HEADER_VERSION >= {0}, \"VK_HEADER_VERSION  is lower than the minimum supported version (v{0})\");\n".format(firstVersion))
    outFile.write('#endif\n')

    # version warnings
    outFile.write('\n#if VK_HEADER_VERSION > {0}\n'.format(lastVersion))
    outFile.write('#if _MSC_VER\n')
    outFile.write('#pragma message(__FILE__ ": warning: VK_HEADER_VERSION is higher than what the header fully supports (v{0})")\n'.format(lastVersion))
    outFile.write('#else\n')
    outFile.write('#warning "VK_HEADER_VERSION is higher than what the header fully supports (v{0})"\n'.format(lastVersion))
    outFile.write('#endif\n')
    outFile.write('#endif\n')

    # Function Declarataions
    outFile.write("""

typedef enum STecVkSerializationResult {
    STEC_VK_SERIALIZATION_RESULT_SUCCESS = 0,
    STEC_VK_SERIALIZATION_RESULT_ERROR_INCOMPLETE,
    STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND,
    STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_HAS_NO_EMPTY_VALUE,
    STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND,
    STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_MISMATCH,
} STecVkSerializationResult;

/**
 * @brief Serializes a Vulkan enumerator/flag type (32-bit)
 * @param pVkType is a pointer to the string name of the Vulkan enumerator/flag type
 * @param vkValue is the numeric value being serialized
 * @param pSerializedLength is a pointer to an integer related to the size of pSerialized, as
 * described below.
 * @param pSerialized is either NULL or a pointer to an character array.
 * @note pSerialized is only written to if STEC_VK_SERIALIZATION_RESULT_SUCCESS or
 * STEC_VK_SERIALIZATION_RESULT_ERROR_INCOMPLETE is returned.
 *
 * If pSerialized is NULL, then the size required to return all layer names is returned in
 * pSerializedLength. Otherwise, pSerializedLength must point to a variable set by the user to the
 * size of the pSerialized array, and on return the variable is overwritten with the characters
 * actually written to pSerialized. If pSerializedLength is less than the total size required to
 * return all, at most pSerializedLength is written, and
 * STEC_VK_SERIALIZATION_RESULT_ERROR_INCOMPLETE will be returned instead of
 * STEC_VK_SERIALIZATION_RESULT_SUCCESS, to indicate that not all names were returned.
 *
 * If the Vulkan type could not be determined or found, then
 * STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND is returned.
 *
 * If the value given in vkValue is 0 and the corresponding Vulkan type doesn't have an equivalent
 * 0-value that can be serialized, then STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_HAS_NO_EMPTY_VALUE
 * is returned. If Any other given vkValue or bitmask cannot be translated fully, then
 * STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND is returned.
 *
 * If this function is used and the Vulkan type is 64-bit, then
 * STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_MISMATCH is returned.
 */
STecVkSerializationResult vk_serialize32(char const *pVkType,
                                         uint32_t vkValue,
                                         uint32_t *pSerializedLength,
                                         char *pSerialized);

/**
 * @brief Serializes a Vulkan enumerator/flag type (64-bit)
 * @param pVkType is a pointer to the string name of the Vulkan enumerator/flag type
 * @param vkValue is the numeric value being serialized
 * @param pSerializedLength is a pointer to an integer related to the size of pSerialized, as
 * described below.
 * @param pSerialized is either NULL or a pointer to an character array.
 * @note pSerialized is only written to if STEC_VK_SERIALIZATION_RESULT_SUCCESS or
 * STEC_VK_SERIALIZATION_RESULT_ERROR_INCOMPLETE is returned.
 *
 * If pSerialized is NULL, then the size required to return all layer names is returned in
 * pSerializedLength. Otherwise, pSerializedLength must point to a variable set by the user to the
 * size of the pSerialized array, and on return the variable is overwritten with the characters
 * actually written to pSerialized. If pSerializedLength is less than the total size required to
 * return all, at most pSerializedLength is written, and
 * STEC_VK_SERIALIZATION_RESULT_ERROR_INCOMPLETE will be returned instead of
 * STEC_VK_SERIALIZATION_RESULT_SUCCESS, to indicate that not all names were returned.
 *
 * If the Vulkan type could not be determined or found, then
 * STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND is returned.
 *
 * If the value given in vkValue is 0 and the corresponding Vulkan type doesn't have an equivalent
 * 0-value that can be serialized, then STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_HAS_NO_EMPTY_VALUE
 * is returned. If Any other given vkValue or bitmask cannot be translated fully, then
 * STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND is returned.
 *
 * If this function is used and the Vulkan type is 32-bit, then
 * STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_MISMATCH is returned.
 */
STecVkSerializationResult vk_serialize64(char const *pVkType,
                                         uint64_t vkValue,
                                         uint32_t *pSerializedLength,
                                         char *pSerialized);

/**
 * @brief Parses a Vulkan enumerator/flag serialized string (32-bit)
 * @param pVkType is a pointer to the string name of the Vulkan enumerator/flag type
 * @param pVkString is a pointer to the string being parsed
 * @param pParsedValue is a pointer to a value that will be modified with the parsed value. Only
 * modified if STEC_VK_SERIALIZATION_RESULT_SUCCESS is returned.
 *
 * This attempts to parse the given Vulkan string, according to the values available for the Vulkan
 * type, and updates the return parsed value upon STEC_VK_SERIALIZATION_RESULT_SUCCESS.
 *
 * If the type cannot be determined or found, STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND is
 * returned.
 *
 * If a particular token in the parsing string cannot be determined or found, then
 * STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND is returned.
 *
 * If this function is used and the Vulkan type is 64-bit, then
 * STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_MISMATCH is returned.
 */
STecVkSerializationResult vk_parse32(char const *pVkType,
                                     char const *pVkString,
                                     void *pParsedValue);

/**
 * @brief Parses a Vulkan enumerator/flag serialized string (64-bit)
 * @param pVkType is a pointer to the string name of the Vulkan enumerator/flag type
 * @param pVkString is a pointer to the string being parsed
 * @param pParsedValue is a pointer to a value that will be modified with the parsed value. Only
 * modified if STEC_VK_SERIALIZATION_RESULT_SUCCESS is returned.
 *
 * This attempts to parse the given Vulkan string, according to the values available for the Vulkan
 * type, and updates the return parsed value upon STEC_VK_SERIALIZATION_RESULT_SUCCESS.
 *
 * If the type cannot be determined or found, STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND is
 * returned.
 *
 * If a particular token in the parsing string cannot be determined or found, then
 * STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND is returned.
 *
 * If this function is used and the Vulkan type is 32-bit, then
 * STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_MISMATCH is returned.
 */
STecVkSerializationResult vk_parse64(char const *pVkType,
                                     char const *pVkString,
                                     void *pParsedValue);

""")

    # Definition Start
    outFile.write("\n#ifdef VK_VALUE_SERIALIZATION_CONFIG_MAIN\n")
    outFile.write("#include <assert.h>\n")
    outFile.write("#include <ctype.h>\n")
    outFile.write("#include <stdbool.h>\n")
    outFile.write("#include <stdlib.h>\n")
    outFile.write("#include <string.h>\n\n")

    # Vendors
    processVendors(outFile, apiData['vendors'])

    # Enums
    processEnums(outFile, apiData['enums'], apiData['vendors'], firstVersion, lastVersion)

    # Enum Type Declaration
    outFile.write("""
typedef enum EnumType {
  ENUM_TYPE_ENUM,
  ENUM_TYPE_FLAG32,
  ENUM_TYPE_FLAG64,
} EnumType;

typedef struct ValueSet {
  char const *name;
  char const *const *valueNames;
  void const *values;
  uint32_t count;
  EnumType type;
} ValueSet;
""")

    # Enum Pointer Array
    usefulEnumCount = 0
    for enum, enum_data in apiData['enums'].items():
        if enum == 'VkResult' or enum == 'VkStructureType' or 'alias' in enum_data:
            continue
        usefulEnumCount += 1

    outFile.write("""
static const uint32_t cValueSetCount = {0};
static ValueSet const cValueSets[{0}] = {{
""".format(usefulEnumCount))
    for enum, enum_data in apiData['enums'].items():
        if enum == 'VkResult' or enum == 'VkStructureType' or 'alias' in enum_data:
            continue

        enum_type = 'ENUM_TYPE_ENUM'
        if 'type' in enum_data:
          if enum_data['type'] == 'VkFlags':
            enum_type = 'ENUM_TYPE_FLAG32'
          elif enum_data['type'] == 'VkFlags64':
            enum_type = 'ENUM_TYPE_FLAG64'
          else:
            print('Error: Unhandled enum type: '.format(enum_data['type']))
            sys.exit(1)

        valueCount = 0
        if 'values' in enum_data:
          valueCount = len(enum_data['values'])
        if valueCount == 0:
            outFile.write('  {{"{}", NULL, NULL, 0, {}}},\n'.format(enum, enum_type))
        else:
            outFile.write('  {{"{0}", {0}Strings, {0}Values, {1}, {2}}},\n'.format(
                enum, valueCount, enum_type))
    outFile.write('};\n')

    # Function definitions
    outFile.write("""
/**
 * @brief Removes a vendor tag from the end of the given string view
 * @param str string to chop the vendor tag from
 * @param size is the current length of the string being used
 * @return Length of the string without the vendor tag, if it was suffixed, otherwise the size
 * originally passed in.
 */
static size_t stripVendor(char const *str, size_t len) {
  for (size_t i = 0; i < cVendorCount; ++i) {
    char const *it = cVendorList[i];
    if (strlen(it) > len)
      continue;

    // Don't strip if it's all that's left
    if (len == strlen(it) && strncmp(str, it, len) == 0)
      break;

    if (strncmp(str + len - strlen(it), it, strlen(it)) == 0) {
      len -= strlen(it);
      break;
    }
  }

  return len;
}

/**
 * @brief Strips '_BIT' from the end of a string, if there
 * @param str string to chop the vendor tag from
 * @param size is the current length of the string being used
 * @return Length of the string without the '_BIT'' tag, if it was suffixed, otherwise the size
 * originally passed in.
 */
static size_t stripBit(char const *str, size_t len) {
  if (len > strlen("_BIT")) {
    if (strncmp(str + len - strlen("_BIT"), "_BIT", strlen("_BIT")) == 0) {
      len -= strlen("_BIT");
    }
  }

  return len;
}

/**
 * @brief Iterates through and finds the corresponding type data
 * @param pVkType is a pointer to the string name of the Vulkan type
 * @param ppStart is a double-pointer that will point to the start of any found set
 * @param ppEnd is a double-pointer that will point to the end of any found set
 * values
 * @return True if a matching type value set is found, false otherwise.
 *
 * This iterates through the big cValueSets array, attempting to find a matching type and returning
 * data about it.
 */
static ValueSet const *getValueSet(char const *pVkType) {
  // Check for a conversion from FlagBits -> Flags
  char localStr[64];
  size_t localLen = strlen(pVkType);
  memcpy(localStr, pVkType, localLen);
  localStr[localLen] = '\\0';

  {
    char const *const pSubStrStart = strstr(pVkType, "FlagBits");
    if (pSubStrStart != NULL) {
      size_t const subStrStartCount = pSubStrStart - pVkType;
      memcpy(localStr + subStrStartCount, "Flags", strlen("Flags")); // Replacement Data
      memcpy(localStr + subStrStartCount + strlen("Flags"),
             pVkType + subStrStartCount + strlen("FlagBits"),
             localLen - subStrStartCount - strlen("FlagBits")); // Trailing Data
      localLen = localLen - strlen("FlagBits") + strlen("Flags");
      localStr[localLen] = '\\0';
    }
  }

  // Try the original name (with flagbits -> flags)
  for (size_t i = 0; i < cValueSetCount; ++i) {
    ValueSet const *it = &cValueSets[i];
    if (strcmp(localStr, it->name) == 0) {
      return it;
    }
  }

  // Try a vendor-stripped name
  localStr[stripVendor(localStr, localLen)] = '\\0';
  for (size_t i = 0; i < cValueSetCount; ++i) {
    ValueSet const *it = &cValueSets[i];
    if (strcmp(localStr, it->name) == 0) {
      return it;
    }
  }

  return NULL;
}

/**
 * @brief Converts a Vulkan Flag typename into the prefix that is used for it's enums
 * @param pTypeName is the type to generate the Vulkan enum prefix for
 * @param nameLength is the length of the type name
 * @return Generated prefix string, the ownership of which passes to the caller
 *
 * Any capitalized letters except for the first has an underscore inserted before it, an underscore
 * is added to the end, and all characters are converted to upper case.
 *
 * It also removed the 'Flags' or 'FlagBits' suffixes.
 */
static char const *generateEnumPrefix(char const *pTypeName, size_t nameLength) {
  // Flag Bits
  char const *pFlags = strstr(pTypeName, "Flags");
  // Flags
  char const *pFlagBits = strstr(pTypeName, "FlagBits");

  char *pPrefixStr = (char *)malloc(nameLength * 2);
  char *pDst = pPrefixStr;
  for (char const *ch = pTypeName; ch < pTypeName + nameLength;) {
    if (ch == pFlags) {
      ch += strlen("Flags");
    } else if (ch == pFlagBits) {
      ch += strlen("FlagBits");
    } else if (ch == pTypeName) {
      *pDst++ = toupper(*ch);
      ++ch;
    } else if (isupper(*ch) || isdigit(*ch)) {
      *pDst++ = '_';
      *pDst++ = *ch;
      ++ch;
    } else {
      *pDst++ = toupper(*ch);
      ++ch;
    }
  }
  *pDst++ = '_';
  *pDst = '\\0';
  assert(pDst < pPrefixStr + (nameLength * 2));

  return pPrefixStr;
}

/**
 * @brief Finds the corresponding value for the given string
 * @param pValueStr is a pointer to the string representing the value
 * @param valueLength is the length of the pValueStr string
 * @param pPrefixStr is a pointer to a pre-determined prefix string that the value may have
 * @param prefixLength is the length of the pPrefixStr string
 * @param pSearchStart is a pointer to the start of the value set to search
 * @param pSearchEnd is a pointer to the end of the value set to search
 * @param pParsedValue is a pointer that will be updated with any found matching value
 * @return True if a matching value was found and pParsedValue updated. False otherwise.
 *
 * Using the given Vulkan token string, this function will attempt to find a matching value in the
 * given search set.
 */
static bool parseValue(char const *pValueStr,
                       size_t valueLength,
                       char const *pPrefixStr,
                       size_t prefixLength,
                       ValueSet const *pValueSet,
                       void *pParsedValue) {
  // Check if there's a matching prefix
  if (valueLength >= prefixLength && strncmp(pValueStr, pPrefixStr, prefixLength) == 0) {
    // There is, limit the searching scope to the part *after* the prefix
    pValueStr += prefixLength;
    valueLength -= prefixLength;
  }

  // Try the initial value
  char const *const *const pSearchEnd = pValueSet->valueNames + pValueSet->count;
  for (char const *const *pStart = pValueSet->valueNames; pStart != pSearchEnd; ++pStart) {
    if (valueLength == strlen(*pStart) && strncmp(pValueStr, *pStart, valueLength) == 0) {
      size_t const offset = pStart - pValueSet->valueNames;
      switch (pValueSet->type) {
      case ENUM_TYPE_ENUM:
        *(int32_t *)pParsedValue |= ((int32_t *)pValueSet->values)[offset];
        break;
      case ENUM_TYPE_FLAG32:
        *(uint32_t *)pParsedValue |= ((uint32_t *)pValueSet->values)[offset];
        break;
      case ENUM_TYPE_FLAG64:
        *(uint64_t *)pParsedValue |= ((uint64_t *)pValueSet->values)[offset];
        break;
      }
      return true;
    }
  }

  // Remove the vendor tag suffix if it's on the value
  valueLength = stripVendor(pValueStr, valueLength);
  if (valueLength > 0 && pValueStr[valueLength - 1] == '_')
    --valueLength;

  // Remove '_BIT' if it's there
  valueLength = stripBit(pValueStr, valueLength);

  for (char const *const *pStart = pValueSet->valueNames; pStart != pSearchEnd; ++pStart) {
    if (valueLength == strlen(*pStart) && strncmp(pValueStr, *pStart, valueLength) == 0) {
      size_t const offset = pStart - pValueSet->valueNames;
      switch (pValueSet->type) {
      case ENUM_TYPE_ENUM:
        *(int32_t *)pParsedValue |= ((int32_t *)pValueSet->values)[offset];
        break;
      case ENUM_TYPE_FLAG32:
        *(uint32_t *)pParsedValue |= ((uint32_t *)pValueSet->values)[offset];
        break;
      case ENUM_TYPE_FLAG64:
        *(uint64_t *)pParsedValue |= ((uint64_t *)pValueSet->values)[offset];
        break;
      }
      return true;
    }
  }

  return false;
}

/**
 * @brief Takes a given string and formats it for use with parsing
 * @param ppStart is a double-pointer to the start of the string, which can be moved
 * @param pEnd is a pointer to the current end of the string
 * @return Pointer to the new end of the formatted string
 *
 * First, any non alphanumeric characters are trimmed from both ends of the string.
 * After than, any spaces are replaced with underscores, and finally all the characters are
 * capitalized. This will generate the string closest to the original ones found in the XML spec.
 */
static char *formatString(char **ppStart, char *pEnd) {
  // Trim left
  for (; *ppStart != pEnd;) {
    if (isalnum(**ppStart))
      break;
    else
      ++(*ppStart);
  }

  // Trim right
  char *pNewEnd = *ppStart;
  for (char *ch = *ppStart; ch < pEnd; ++ch) {
    if (isalnum(*ch))
      pNewEnd = ch + 1;
  }

  for (char *ch = *ppStart; ch < pNewEnd; ++ch) {
    if (*ch == ' ')
      *ch = '_';
    else
      *ch = toupper(*ch);
  }

  return pNewEnd;
}

// Returns the smallest of two values
uint32_t serializeMin(uint32_t lhs, uint32_t rhs) {
  if (lhs < rhs) {
    return lhs;
  }
  return rhs;
}

static STecVkSerializationResult serializeBitmask(ValueSet const *pValueSet,
                                                  void const *pVkValue,
                                                  uint32_t *pSerializedLength,
                                                  char *pSerialized) {
  if (pValueSet->count == 0) {
    // If this is a non-existing bitmask, then return an empty string
    *pSerializedLength = 0;
    return STEC_VK_SERIALIZATION_RESULT_SUCCESS;
  }

  // As we want to search in reverse order (to possible catch values that encompass multiple bits)
  // we decrement both items here, so the 'end' is at a valid value and 'start' is now one 'beyond
  // the end'
  char const *const *pSearchStart = pValueSet->valueNames + pValueSet->count - 1;
  char const *const *pSearchEnd = pValueSet->valueNames - 1;

  // Number of characters serialized so far
  uint32_t serializedLength = 0;
  // Will turn true if there isn't enough space in the destination string to fully serialize all the
  // values
  bool incomplete = false;
  // Will host the temporary internal string, so we don't overwrite data in the destination string
  // unless we're successfully returning
  char *pTempStr = NULL;

  if (pSerialized != NULL) {
    // We'll only bother with the internal string if we can outputt string data
    pTempStr = (char *)malloc(*pSerializedLength);
  }

  char *pSrcStr = pTempStr;
  bool valueIsZero;

  while (pSearchStart != pSearchEnd) {
    switch (pValueSet->type) {
    case ENUM_TYPE_ENUM:
      valueIsZero = *(int32_t *)pVkValue == 0;
      break;
    case ENUM_TYPE_FLAG32:
      valueIsZero = *(uint32_t *)pVkValue == 0;
      break;
    case ENUM_TYPE_FLAG64:
      valueIsZero = *(uint64_t *)pVkValue == 0;
      break;
    }

    if (valueIsZero && serializedLength > 0) {
      // No more non-zero values to serialize, and we've serialized something,
      // so we can skip any possible zero-values
      break;
    }

    size_t offset = pSearchStart - pValueSet->valueNames;
    bool match;
    switch (pValueSet->type) {
    case ENUM_TYPE_ENUM:
      match = (((int32_t *)pValueSet->values)[offset] & *(int32_t *)pVkValue) ==
              ((int32_t *)pValueSet->values)[offset];
      break;
    case ENUM_TYPE_FLAG32:
      match = (((uint32_t *)pValueSet->values)[offset] & *(uint32_t *)pVkValue) ==
              ((uint32_t *)pValueSet->values)[offset];
      break;
    case ENUM_TYPE_FLAG64:
      match = (((uint64_t *)pValueSet->values)[offset] & *(uint64_t *)pVkValue) ==
              ((uint64_t *)pValueSet->values)[offset];
      break;
    }

    if (match) {
      // Found a compatible bit mask, add it
      if (serializedLength > 0) {
        if (pTempStr == NULL) {
          serializedLength += 3;
        } else {
          uint32_t toCopy = serializeMin(*pSerializedLength - serializedLength, 3);
          memcpy(pSrcStr, " | ", toCopy);
          pSrcStr += toCopy;
          serializedLength += toCopy;
          if (toCopy != 3) {
            incomplete = true;
            break;
          }
        }
      }

      if (pSrcStr == NULL) {
        serializedLength += strlen(*pSearchStart);
      } else {
        uint32_t toCopy =
            serializeMin(*pSerializedLength - serializedLength, strlen(*pSearchStart));
        memcpy(pSrcStr, *pSearchStart, toCopy);
        pSrcStr += toCopy;
        serializedLength += toCopy;
        if (toCopy != strlen(*pSearchStart)) {
          incomplete = true;
          break;
        }
      }

      switch (pValueSet->type) {
      case ENUM_TYPE_ENUM:
        *(int32_t *)pVkValue ^= ((int32_t *)pValueSet->values)[offset];
        break;
      case ENUM_TYPE_FLAG32:
        *(uint32_t *)pVkValue ^= ((uint32_t *)pValueSet->values)[offset];
        break;
      case ENUM_TYPE_FLAG64:
        *(uint64_t *)pVkValue ^= ((uint64_t *)pValueSet->values)[offset];
        break;
      }
    }

    --pSearchStart;
  }

  switch (pValueSet->type) {
  case ENUM_TYPE_ENUM:
    valueIsZero = *(int32_t *)pVkValue == 0;
    break;
  case ENUM_TYPE_FLAG32:
    valueIsZero = *(uint32_t *)pVkValue == 0;
    break;
  case ENUM_TYPE_FLAG64:
    valueIsZero = *(uint64_t *)pVkValue == 0;
    break;
  }

  if (!incomplete && !valueIsZero) {
    // Failed to find a valid bitmask for the value
    free(pTempStr);
    return STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND;
  }

  *pSerializedLength = serializedLength;
  if (pSerialized != NULL && serializedLength > 0) {
    memcpy(pSerialized, pTempStr, serializedLength);
  }
  free(pTempStr);
  if (incomplete) {
    return STEC_VK_SERIALIZATION_RESULT_ERROR_INCOMPLETE;
  }
  return STEC_VK_SERIALIZATION_RESULT_SUCCESS;
}

static STecVkSerializationResult serializeEnum(ValueSet const *pValueSet,
                                               void const *pVkValue,
                                               uint32_t *pSerializedLength,
                                               char *pSerialized) {
  void const *pSearchStart = pValueSet->values;
  void const *pSearchEnd;

  switch (pValueSet->type) {
  case ENUM_TYPE_ENUM:
  case ENUM_TYPE_FLAG32:
    pSearchEnd = (uint32_t *)pSearchStart + pValueSet->count;
    break;
  case ENUM_TYPE_FLAG64:
    pSearchEnd = (uint64_t *)pSearchStart + pValueSet->count;
    break;
  }

  while (pSearchStart != pSearchEnd) {
    bool match;
    switch (pValueSet->type) {
    case ENUM_TYPE_ENUM:
      match = *(int32_t *)pSearchStart == *(int32_t *)pVkValue;
      break;
    case ENUM_TYPE_FLAG32:
      match = *(uint32_t *)pSearchStart == *(uint32_t *)pVkValue;
      break;
    case ENUM_TYPE_FLAG64:
      match = *(uint64_t *)pSearchStart == *(uint64_t *)pVkValue;
      break;
    }

    if (match) {
      size_t offset;
      switch (pValueSet->type) {
      case ENUM_TYPE_ENUM:
      case ENUM_TYPE_FLAG32:
        offset = (uint32_t *)pSearchStart - (uint32_t *)pValueSet->values;
        break;
      case ENUM_TYPE_FLAG64:
        offset = (uint64_t *)pSearchStart - (uint64_t *)pValueSet->values;
        break;
      }

      uint32_t const sourceLength = strlen(pValueSet->valueNames[offset]);
      if (pSerialized != NULL) {
        if (*pSerializedLength < sourceLength) {
          memcpy(pSerialized, pValueSet->valueNames[offset], *pSerializedLength);
          return STEC_VK_SERIALIZATION_RESULT_ERROR_INCOMPLETE;
        } else {
          // Copy full value
          memcpy(pSerialized, pValueSet->valueNames[offset], sourceLength);
        }
      }
      // In all success cases, set the length of the value string, either for how much is needed
      // or was copied.
      *pSerializedLength = sourceLength;

      return STEC_VK_SERIALIZATION_RESULT_SUCCESS;
    }

    switch (pValueSet->type) {
    case ENUM_TYPE_ENUM:
    case ENUM_TYPE_FLAG32:
      pSearchStart = ((uint32_t *)pSearchStart) + 1;
      break;
    case ENUM_TYPE_FLAG64:
      pSearchStart = ((uint64_t *)pSearchStart) + 1;
      break;
    }
  }

  return STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND;
}

static STecVkSerializationResult parseBitmask(char *pVkString,
                                              ValueSet const *pValueSet,
                                              char const *pPrefixStr,
                                              size_t prefixLength,
                                              void *pParsedValue) {
  uint64_t retVal = 0;
  char *const strEnd = pVkString + strlen(pVkString);

  char *startCh = pVkString;
  char *endCh = pVkString;
  for (; endCh != strEnd; ++endCh) {
    if (*endCh == '|') {
      char *pNewEndCh = formatString(&startCh, endCh);

      bool foundVal =
          parseValue(startCh, pNewEndCh - startCh, pPrefixStr, prefixLength, pValueSet, &retVal);
      if (!foundVal)
        return STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND;

      startCh = endCh + 1;
    }
  }
  if (startCh != endCh) {
    char *pNewEndCh = formatString(&startCh, endCh);

    bool foundVal =
        parseValue(startCh, pNewEndCh - startCh, pPrefixStr, prefixLength, pValueSet, &retVal);
    if (!foundVal)
      return STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND;
  }

  switch (pValueSet->type) {
  case ENUM_TYPE_ENUM:
    *(int32_t *)pParsedValue = *((int32_t *)&retVal);
    break;
  case ENUM_TYPE_FLAG32:
    *(uint32_t *)pParsedValue = *((uint32_t *)&retVal);
    break;
  case ENUM_TYPE_FLAG64:
    *(uint64_t *)pParsedValue = *((uint64_t *)&retVal);
    break;
  }
  return STEC_VK_SERIALIZATION_RESULT_SUCCESS;
}

static STecVkSerializationResult parseEnum(char *pVkString,
                                           ValueSet const *pValueSet,
                                           char const *pPrefixStr,
                                           size_t prefixLength,
                                           void *pParsedValue) {
  uint64_t retVal = 0;

  char *pStrEnd = formatString(&pVkString, pVkString + strlen(pVkString));
  bool found =
      parseValue(pVkString, pStrEnd - pVkString, pPrefixStr, prefixLength, pValueSet, &retVal);
  if (found) {
    switch (pValueSet->type) {
    case ENUM_TYPE_ENUM:
      *(int32_t *)pParsedValue = *((int32_t *)&retVal);
      break;
    case ENUM_TYPE_FLAG32:
      *(uint32_t *)pParsedValue = *((uint32_t *)&retVal);
      break;
    case ENUM_TYPE_FLAG64:
      *(uint64_t *)pParsedValue = *((uint64_t *)&retVal);
      break;
    }
    return STEC_VK_SERIALIZATION_RESULT_SUCCESS;
  }

  return STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND;
}

static STecVkSerializationResult vk_serialize(char const *pVkType,
                                              void const *pVkValue,
                                              size_t valueSize,
                                              uint32_t *pSerializedLength,
                                              char *pSerialized) {
  if (pVkType == NULL || strlen(pVkType) == 0) {
    return STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND;
  }

  ValueSet const *const pValueSet = getValueSet(pVkType);
  if (pValueSet == NULL) {
    return STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND;
  }

  // check type size vs value size
  switch (pValueSet->type) {
  case ENUM_TYPE_ENUM:
  case ENUM_TYPE_FLAG32:
    if (valueSize != sizeof(uint32_t))
      return STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_MISMATCH;
    break;
  case ENUM_TYPE_FLAG64:
    if (valueSize != sizeof(uint64_t))
      return STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_MISMATCH;
    break;
  }

  if (strstr(pVkType, "Flags") != NULL || strstr(pVkType, "FlagBits") != NULL) {
    return serializeBitmask(pValueSet, pVkValue, pSerializedLength, pSerialized);
  }

  return serializeEnum(pValueSet, pVkValue, pSerializedLength, pSerialized);
}

STecVkSerializationResult vk_serialize32(char const *pVkType,
                                         uint32_t vkValue,
                                         uint32_t *pSerializedLength,
                                         char *pSerialized) {
  return vk_serialize(pVkType, &vkValue, sizeof(uint32_t), pSerializedLength, pSerialized);
}

STecVkSerializationResult vk_serialize64(char const *pVkType,
                                         uint64_t vkValue,
                                         uint32_t *pSerializedLength,
                                         char *pSerialized) {
  return vk_serialize(pVkType, &vkValue, sizeof(uint64_t), pSerializedLength, pSerialized);
}

static STecVkSerializationResult vk_parse(char const *pVkType,
                                          char const *pVkString,
                                          void *pParsedValue,
                                          size_t parseValueSize) {
  if (pVkType == NULL || strlen(pVkType) == 0) {
    return STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND;
  }

  ValueSet const *const pValueSet = getValueSet(pVkType);
  if (pValueSet == NULL) {
    return STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND;
  }

  // check type size vs parse value size
  switch (pValueSet->type) {
  case ENUM_TYPE_ENUM:
  case ENUM_TYPE_FLAG32:
    if (parseValueSize != sizeof(uint32_t))
      return STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_MISMATCH;
    break;
  case ENUM_TYPE_FLAG64:
    if (parseValueSize != sizeof(uint64_t))
      return STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_MISMATCH;
    break;
  }

  size_t const strLength = strlen(pVkString);
  if (strLength == 0) {
    // Only flags/bitmasks can have no/empty values, all enum types must have *something*
    if (strstr(pVkType, "Flags") != NULL || strstr(pVkType, "FlagBits") != NULL) {
      switch (parseValueSize) {
      case sizeof(uint32_t):
        *(uint32_t *)pParsedValue = 0;
        break;
      case sizeof(uint64_t):
        *(uint64_t *)pParsedValue = 0;
        break;
      }
      return STEC_VK_SERIALIZATION_RESULT_SUCCESS;
    } else {
      return STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_HAS_NO_EMPTY_VALUE;
    }
  }

  char *mutableStr = (char *)malloc(strLength + 1);
  memcpy(mutableStr, pVkString, strLength);
  mutableStr[strLength] = '\\0';

  char const *prefixStr = generateEnumPrefix(pVkType, stripVendor(pVkType, strlen(pVkType)));

  STecVkSerializationResult result;
  if (strstr(pVkType, "Flags") != NULL || strstr(pVkType, "FlagBits") != NULL) {
    result = parseBitmask(mutableStr, pValueSet, prefixStr, strlen(prefixStr), pParsedValue);
  } else {
    result = parseEnum(mutableStr, pValueSet, prefixStr, strlen(prefixStr), pParsedValue);
  }

  free((void *)prefixStr);
  free(mutableStr);

  return result;
}

STecVkSerializationResult vk_parse32(char const *pVkType,
                                     char const *pVkString,
                                     void *pParsedValue) {
  uint32_t tempValue;
  STecVkSerializationResult result = vk_parse(pVkType, pVkString, &tempValue, sizeof(uint32_t));
  if (result == STEC_VK_SERIALIZATION_RESULT_SUCCESS) {
    memcpy(pParsedValue, &tempValue, sizeof(uint32_t));
  }
  return result;
}

STecVkSerializationResult vk_parse64(char const *pVkType,
                                     char const *pVkString,
                                     void *pParsedValue) {
  uint64_t tempValue;
  STecVkSerializationResult result = vk_parse(pVkType, pVkString, &tempValue, sizeof(uint64_t));
  if (result == STEC_VK_SERIALIZATION_RESULT_SUCCESS) {
    memcpy(pParsedValue, &tempValue, sizeof(uint64_t));
  }
  return result;
}
""")

    # endif
    outFile.write("""
#endif // VK_VALUE_SERIALIZATION_CONFIG_MAIN

#ifdef __cplusplus
}
#endif

#endif // VK_VALUE_SERIALIZATION_H
""")
    outFile.close()


if __name__ == "__main__":
    main(sys.argv[1:])
