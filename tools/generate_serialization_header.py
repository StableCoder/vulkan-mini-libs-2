#!/usr/bin/env python3

# Copyright (C) 2022-2023 George Cave.
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import gen_common
import sys
import xml.etree.ElementTree as ET


def processVendors(outFile, vendors):
    outFile.write(
        '#define cVendorCount sizeof(cVendorList) / sizeof(char const*)')
    outFile.write('\nchar const *cVendorList[{}] = {{\n'.format(len(vendors)))
    for vendor in vendors:
        outFile.write('  "{}",\n'.format(vendor.tag))
    outFile.write('};\n')


def processEnumValue(outFile, enum, value):
    if not value.get('value') is None:
        # Spitting out plain values
        outFile.write(value.get('value'))
    elif not value.get('bitpos') is None:
        # Bitflag
        outFile.write('0x{}'.format(
            format(1 << int(value.get('bitpos')), '08X')))
    elif not value.get('alias') is None:
        processEnumValue(outFile, enum, enum.find(
            './values/{}'.format(value.get('alias'))))


def processEnums(outFile, enums, vendors, first, last):
    for enum in enums:
        # Skip VkResult
        if enum.tag == 'VkResult':
            continue
        # Skip if there's no values, MSVC can't do zero-sized arrays
        if len(enum.findall('./values/')) == 0:
            continue

        outFile.write(
            '\nEnumValueSet const {}Sets[] = {{\n'.format(enum.tag))

        # Determine how much to chop off the front
        strName = enum.tag
        typeDigit = ''
        # Determine if type ends with vendor tag
        vendorName = ''
        for vendor in vendors:
            if strName.endswith(vendor.tag):
                vendorName = vendor.tag
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

        current = first
        while current <= last:
            for value in enum.findall('./values/'):
                if int(value.get('first')) != current:
                    continue
                outFile.write("  {\"")

                valueStr = value.tag
                if valueStr.startswith(mainPrefix):
                    valueStr = valueStr[len(mainPrefix):]
                if vendorName != '' and valueStr.endswith(vendorName):
                    valueStr = valueStr[:-len(vendorName)-1]
                if valueStr.endswith('_BIT'):
                    valueStr = valueStr[:-4]

                # Name
                outFile.write(valueStr)
                outFile.write("\", ")
                # Value
                processEnumValue(outFile, enum, value)
                # Alias
                if value.get('alias'):
                    outFile.write(', true')
                else:
                    outFile.write(', false')

                outFile.write("},\n")
            current += 1

        outFile.write('};\n')


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input',
                        help='Input XML cache file',
                        required=True)
    parser.add_argument('-o', '--output',
                        help='Output file to write to',
                        required=True)
    args = parser.parse_args()

    try:
        dataXml = ET.parse(args.input)
        dataRoot = dataXml.getroot()
    except:
        print("Error: Could not open input file: ", args.input)
        sys.exit(1)

    firstVersion = int(dataRoot.get('first'))
    lastVersion = int(dataRoot.get('last'))

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

    # Static Asserts
    outFile.write('\n#ifdef __cplusplus\n')
    outFile.write(
        "static_assert(VK_HEADER_VERSION >= {0}, \"VK_HEADER_VERSION is from before the minimum supported version of v{0}.\");\n".format(firstVersion))
    outFile.write(
        "static_assert(VK_HEADER_VERSION <= {0}, \"VK_HEADER_VERSION is from after the maximum supported version of v{0}.\");\n".format(lastVersion))
    outFile.write('#else\n')
    outFile.write(
        "_Static_assert(VK_HEADER_VERSION >= {0}, \"VK_HEADER_VERSION is from before the minimum supported version of v{0}.\");\n".format(firstVersion))
    outFile.write(
        "_Static_assert(VK_HEADER_VERSION <= {0}, \"VK_HEADER_VERSION is from after the maximum supported version of v{0}.\");\n".format(lastVersion))
    outFile.write('#endif\n')

    # Function Declarataions
    outFile.write("""

typedef enum STecVkSerializationResult {
    STEC_VK_SERIALIZATION_RESULT_SUCCESS = 0,
    STEC_VK_SERIALIZATION_RESULT_ERROR_INCOMPLETE,
    STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND,
    STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_HAS_NO_EMPTY_VALUE,
    STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND,
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
 */
STecVkSerializationResult vk_serialize32(char const *pVkType, uint32_t vkValue, uint32_t *pSerializedLength, char* pSerialized);

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
 */
STecVkSerializationResult vk_serialize64(char const *pVkType, uint64_t vkValue, uint32_t *pSerializedLength, char* pSerialized);

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
 */
STecVkSerializationResult vk_parse32(char const *pVkType, char const *pVkString, uint32_t *pParsedValue);

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
 */
STecVkSerializationResult vk_parse64(char const* pVkType, char const *pVkString, uint64_t *pParsedValue);

""")

    # Definition Start
    outFile.write("\n#ifdef VK_VALUE_SERIALIZATION_CONFIG_MAIN\n")
    outFile.write("#include <assert.h>\n")
    outFile.write("#include <ctype.h>\n")
    outFile.write("#include <stdbool.h>\n")
    outFile.write("#include <stdlib.h>\n")
    outFile.write("#include <string.h>\n\n")

    # Vendors
    vendors = dataRoot.findall('vendors/')
    processVendors(outFile, vendors)

    # EnumSet Declaration
    outFile.write("\ntypedef struct EnumValueSet {\n")
    outFile.write("  char const *name;\n")
    outFile.write("  int64_t value;\n")
    outFile.write("  bool alias;\n")
    outFile.write("} EnumValueSet;\n")

    # Enums
    enums = dataRoot.findall('enums/')
    processEnums(outFile, enums, vendors, firstVersion, lastVersion)

    # Enum Type Declaration
    outFile.write("\ntypedef struct EnumType {\n")
    outFile.write("  char const *name;\n")
    outFile.write("  EnumValueSet const* data;\n")
    outFile.write("  uint32_t count;\n")
    outFile.write("} EnumType;\n")

    # Enum Pointer Array
    usefulEnumCount = 0
    for enum in enums:
        if enum.tag == 'VkResult' or enum.get('alias'):
            continue
        usefulEnumCount += 1

    outFile.write(
        '\n#define cEnumTypeCount sizeof(cEnumTypes) / sizeof(EnumType)\n')
    outFile.write('EnumType const cEnumTypes[{}] = {{\n'.format(
        usefulEnumCount))  # -1 for not doing VkResult
    for enum in enums:
        if enum.tag == 'VkResult' or enum.get('alias'):
            continue

        valueCount = len(enum.findall('./values/'))
        if valueCount == 0:
            outFile.write('  {{"{}", NULL, 0}},\n'.format(enum.tag))
        else:
            outFile.write('  {{"{0}", {0}Sets, {1}}},\n'.format(
                enum.tag, valueCount))
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
size_t stripVendor(char const *str, size_t len) {
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
size_t stripBit(char const *str, size_t len) {
  if (len > strlen("_BIT")) {
    if (strncmp(str + len - strlen("_BIT"), "_BIT", strlen("_BIT")) == 0) {
      len -= strlen("_BIT");
    }
  }

  return len;
}

/**
 * @brief Iterates through and finds the corresponding type's EnumValueSet
 * @param pVkType is a pointer to the string name of the Vulkan type
 * @param ppStart is a double-pointer that will point to the start of any found set
 * @param ppEnd is a double-pointer that will point to the end of any found set
 * values
 * @return True if a matching type value set is found, false otherwise.
 *
 * This iterates through the big cEnumTypes array, attempting to find a matching type and returning
 * data about it.
 */
bool getEnumType(char const *pVkType,
                 EnumValueSet const **ppStart,
                 EnumValueSet const **ppEnd) {
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
  for (size_t i = 0; i < cEnumTypeCount; ++i) {
    EnumType const *it = &cEnumTypes[i];
    if (strcmp(localStr, it->name) == 0) {
      *ppStart = it->data;
      *ppEnd = it->data + it->count;

      return true;
    }
  }

  // Try a vendor-stripped name
  localStr[stripVendor(localStr, localLen)] = '\\0';
  for (size_t i = 0; i < cEnumTypeCount; ++i) {
    EnumType const *it = &cEnumTypes[i];
    if (strcmp(localStr, it->name) == 0) {
      *ppStart = it->data;
      *ppEnd = it->data + it->count;

      return true;
    }
  }

  return false;
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
char const *generateEnumPrefix(char const *pTypeName, size_t nameLength) {
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
bool parseValue(char const *pValueStr,
                size_t valueLength,
                char const *pPrefixStr,
                size_t prefixLength,
                EnumValueSet const *pSearchStart,
                EnumValueSet const *pSearchEnd,
                uint64_t *pParsedValue) {
  // Check if there's a matching prefix
  if (valueLength >= prefixLength && strncmp(pValueStr, pPrefixStr, prefixLength) == 0) {
    // There is, limit the searching scope to the part *after* the prefix
    pValueStr += prefixLength;
    valueLength -= prefixLength;
  }

  // Try the initial value
  for (EnumValueSet const *pStart = pSearchStart; pStart != pSearchEnd; ++pStart) {
    if (valueLength == strlen(pStart->name) && strncmp(pValueStr, pStart->name, valueLength) == 0) {
      *pParsedValue |= pStart->value;
      return true;
    }
  }

  // Remove the vendor tag suffix if it's on the value
  valueLength = stripVendor(pValueStr, valueLength);
  if (valueLength > 0 && pValueStr[valueLength - 1] == '_')
    --valueLength;

  // Remove '_BIT' if it's there
  valueLength = stripBit(pValueStr, valueLength);

  for (EnumValueSet const *pStart = pSearchStart; pStart != pSearchEnd; ++pStart) {
    if (valueLength == strlen(pStart->name) && strncmp(pValueStr, pStart->name, valueLength) == 0) {
      *pParsedValue |= pStart->value;
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
char *formatString(char **ppStart, char *pEnd) {
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

STecVkSerializationResult serializeBitmask(EnumValueSet const *pSearchStart,
                                           EnumValueSet const *pSearchEnd,
                                           uint64_t vkValue,
                                           uint32_t *pSerializedLength,
                                           char *pSerialized) {
  if (pSearchStart == pSearchEnd) {
    // If this is a non-existing bitmask, then return an empty string
    *pSerializedLength = 0;
    return STEC_VK_SERIALIZATION_RESULT_SUCCESS;
  }

  // As we want to search in reverse order (to possible catch values that encompass multiple bits)
  // we decrement both items here, so the 'end' is at a valid value and 'start' is now one 'beyond
  // the end'
  EnumValueSet const* pSwap = pSearchStart;
  pSearchStart = pSearchEnd - 1;
  pSearchEnd = pSwap - 1;

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

  while (pSearchStart != pSearchEnd) {
    if (vkValue == 0 && serializedLength > 0) {
      // No more non-zero values to serialize, and we've serialized something,
      // so we can skip any possible zero-values
      break;
    }

    if (!pSearchStart->alias && (pSearchStart->value & vkValue) == pSearchStart->value) {
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
        serializedLength += strlen(pSearchStart->name);
      } else {
        uint32_t toCopy = serializeMin(*pSerializedLength - serializedLength, strlen(pSearchStart->name));
        memcpy(pSrcStr, pSearchStart->name, toCopy);
        pSrcStr += toCopy;
        serializedLength += toCopy;
        if (toCopy != strlen(pSearchStart->name)) {
          incomplete = true;
          break;
        }
      }
      vkValue = vkValue ^ pSearchStart->value;
    }

    --pSearchStart;
  }

  if (!incomplete && vkValue != 0) {
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

STecVkSerializationResult serializeEnum(EnumValueSet const *pSearchStart,
                                        EnumValueSet const *pSearchEnd,
                                        uint64_t vkValue,
                                        uint32_t *pSerializedLength,
                                        char *pSerialized) {
  while (pSearchStart != pSearchEnd) {
    if (!pSearchStart->alias && pSearchStart->value == vkValue) {
      uint32_t const sourceLength = strlen(pSearchStart->name);
      if (pSerialized != NULL) {
        if (*pSerializedLength < sourceLength) {
          memcpy(pSerialized, pSearchStart->name, *pSerializedLength);
          return STEC_VK_SERIALIZATION_RESULT_ERROR_INCOMPLETE;
        } else {
          // Copy full value
          memcpy(pSerialized, pSearchStart->name, sourceLength);
        }
      }
      // In all success cases, set the length of the value string, either for how much is needed or
      // was copied.
      *pSerializedLength = sourceLength;

      return STEC_VK_SERIALIZATION_RESULT_SUCCESS;
    }

    ++pSearchStart;
  }

  return STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND;
}

STecVkSerializationResult parseBitmask(char *pVkString,
                                       EnumValueSet const *pSearchStart,
                                       EnumValueSet const *pSearchEnd,
                                       char const *pPrefixStr,
                                       size_t prefixLength,
                                       uint64_t *pParsedValue) {
  uint64_t retVal = 0;
  char *const strEnd = pVkString + strlen(pVkString);

  char *startCh = pVkString;
  char *endCh = pVkString;
  for (; endCh != strEnd; ++endCh) {
    if (*endCh == '|') {
      char *pNewEndCh = formatString(&startCh, endCh);

      bool foundVal =
          parseValue(startCh, pNewEndCh - startCh, pPrefixStr, prefixLength, pSearchStart, pSearchEnd, &retVal);
      if (!foundVal)
        return STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND;

      startCh = endCh + 1;
    }
  }
  if (startCh != endCh) {
    char *pNewEndCh = formatString(&startCh, endCh);

    bool foundVal =
        parseValue(startCh, pNewEndCh - startCh, pPrefixStr, prefixLength, pSearchStart, pSearchEnd, &retVal);
    if (!foundVal)
      return STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND;
  }

  *pParsedValue = retVal;
  return STEC_VK_SERIALIZATION_RESULT_SUCCESS;
}

STecVkSerializationResult parseEnum(char *pVkString,
                                    EnumValueSet const *pSearchStart,
                                    EnumValueSet const *pSearchEnd,
                                    char const *pPrefixStr,
                                    size_t prefixLength,
                                    uint64_t *pParsedValue) {
  uint64_t retVal = 0;

  char *pStrEnd = formatString(&pVkString, pVkString + strlen(pVkString));
  bool found =
      parseValue(pVkString, pStrEnd - pVkString, pPrefixStr, prefixLength, pSearchStart, pSearchEnd, &retVal);
  if (found) {
    *pParsedValue = retVal;
    return STEC_VK_SERIALIZATION_RESULT_SUCCESS;
  }

  return STEC_VK_SERIALIZATION_RESULT_ERROR_VALUE_NOT_FOUND;
}

STecVkSerializationResult vk_serialize32(char const *pVkType,
                                         uint32_t vkValue,
                                         uint32_t *pSerializedLength,
                                         char *pSerialized) {
  return vk_serialize64(pVkType, (uint64_t)vkValue, pSerializedLength, pSerialized);
}

STecVkSerializationResult vk_serialize64(char const *pVkType,
                                         uint64_t vkValue,
                                         uint32_t *pSerializedLength,
                                         char *pSerialized) {
  if (pVkType == NULL || strlen(pVkType) == 0) {
    return STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND;
  }

  EnumValueSet const *pSearchStart, *pSearchEnd;
  if (!getEnumType(pVkType, &pSearchStart, &pSearchEnd)) {
    return STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND;
  }

  if (strstr(pVkType, "Flags") != NULL || strstr(pVkType, "FlagBits") != NULL) {
    return serializeBitmask(pSearchStart, pSearchEnd, vkValue, pSerializedLength, pSerialized);
  }

  return serializeEnum(pSearchStart, pSearchEnd, vkValue, pSerializedLength, pSerialized);
}

STecVkSerializationResult vk_parse32(char const *pVkType,
                                     char const *pVkString,
                                     uint32_t *pParsedValue) {
  uint64_t tempValue;
  STecVkSerializationResult result = vk_parse64(pVkType, pVkString, &tempValue);
  if (result == STEC_VK_SERIALIZATION_RESULT_SUCCESS) {
    *pParsedValue = (uint32_t)tempValue;
  }
  return result;
}

STecVkSerializationResult vk_parse64(char const *pVkType,
                                     char const *pVkString,
                                     uint64_t *pParsedValue) {
  if (pVkType == NULL || strlen(pVkType) == 0) {
    return STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND;
  }

  EnumValueSet const *pSearchStart, *pSearchEnd;
  if (!getEnumType(pVkType, &pSearchStart, &pSearchEnd)) {
    return STEC_VK_SERIALIZATION_RESULT_ERROR_TYPE_NOT_FOUND;
  }

  size_t const strLength = strlen(pVkString);
  if (strLength == 0) {
    // Only bitmasks can have empty values, all enum types must have *something*
    if (strstr(pVkType, "Flags") != NULL || strstr(pVkType, "FlagBits") != NULL) {
      *pParsedValue = 0;
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
    result = parseBitmask(mutableStr, pSearchStart, pSearchEnd, prefixStr, strlen(prefixStr), pParsedValue);
  } else {
    result = parseEnum(mutableStr, pSearchStart, pSearchEnd, prefixStr, strlen(prefixStr), pParsedValue);
  }

  free((void *)prefixStr);
  free(mutableStr);

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
