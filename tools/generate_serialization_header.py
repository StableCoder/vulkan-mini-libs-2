#!/usr/bin/env python3

import sys
import getopt
import xml.etree.ElementTree as ET


def processVendors(outFile, vendors):
    outFile.writelines(["\nconstexpr std::array<std::string_view, ", str(
        len(vendors)), "> vendors = {{\n"])
    for vendor in vendors:
        outFile.writelines(['  \"', vendor.tag, '\",\n'])
    outFile.write('}};\n')


def processEnumValue(outFile, enum, value):
    if not value.get('value') is None:
        # Spitting out plain values
        outFile.write(value.get('value'))
    elif not value.get('bitpos') is None:
        # Bitflag
        outFile.writelines(
            ['0x', format(1 << int(value.get('bitpos')), '08X')])
    elif not value.get('alias') is None:
        processEnumValue(outFile, enum, enum.find(value.get('alias')))


def processEnums(outFile, enums, vendors, first, last):
    for enum in enums:
        # Skip VkResult
        if enum.tag == 'VkResult':
            continue
        # Skip if there's no values, MSVC can't do zero-sized arrays
        if len(enum.findall('./')) == 0:
            continue

        outFile.writelines(
            ['\nconstexpr EnumValueSet ', enum.tag, 'Sets[] = {\n'])

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

        if strName.endswith('FlagBits'):
            strName = strName[:-8]

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
            for value in enum.findall('./'):
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

                outFile.write(valueStr)
                outFile.write("\", ")
                processEnumValue(outFile, enum, value)

                outFile.write("},\n")
            current += 1

        outFile.write('};\n')


def main(argv):
    inputFile = ''
    outputFile = ''

    try:
        opts, args = getopt.getopt(argv, 'i:o:', [])
    except getopt.GetoptError:
        print('Error parsing options')
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-i':
            inputFile = arg
        elif opt == '-o':
            outputFile = arg

    if(inputFile == ''):
        print("Error: No Vulkan XML file specified")
        sys.exit(1)
    if(outputFile == ''):
        print("Error: No output file specified")
        sys.exit(1)

    try:
        dataXml = ET.parse(inputFile)
        dataRoot = dataXml.getroot()
    except:
        print("Error: Could not open input file: ", inputFile)
        sys.exit(1)

    firstVersion = int(dataRoot.get('first'))
    lastVersion = int(dataRoot.get('last'))

    outFile = open(outputFile, "w")

    # Common Header
    with open("common_header.txt") as fd:
        outFile.write(fd.read())
        outFile.write('\n')

     #
    outFile.write("""#ifndef VK_VALUE_SERIALIZATION_HPP
#define VK_VALUE_SERIALIZATION_HPP

/*  USAGE:
    To use, include this header where the declarations for the boolean checks are required.

    On *ONE* compilation unit, include the definition of `#define VK_VALUE_SERIALIZATION_CONFIG_MAIN`
    so that the definitions are compiled somewhere following the one definition rule.
*/

#include <vulkan/vulkan.h>

#include <string>
#include <string_view>
""")

    # Static Asserts
    outFile.writelines(["\nstatic_assert(VK_HEADER_VERSION >= ", str(
        firstVersion), ", \"VK_HEADER_VERSION is from before the supported range.\");\n"])
    outFile.writelines(["static_assert(VK_HEADER_VERSION <= ", str(
        lastVersion), ", \"VK_HEADER_VERSION is from after the supported range.\");\n"])

    # Function Declarataions
    outFile.write("""
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
 * @brief Serializes a Vulkan enumerator/flag type (32-bit)
 * @param vkType Name of the Vulkan enumerator/flag type
 * @param vkValue Value being serialized
 * @param pString Pointer to a string that will be modified with the serialized value. Only modified
 * if true is returned.
 * @return True the value was successfully serialized. False otherwise.
 */
bool vk_serialize(std::string_view vkType, uint32_t vkValue, std::string *pString);

/**
 * @brief Parses a Vulkan enumerator/flag serialized string (32-bit)
 * @param vkType Name of the Vulkan enumerator/flag type
 * @param vkString String being parsed
 * @param pValue Pointer to a value that will be modified with the parsed value. Only modified if
 * true is returned.
 * @return True the value was successfully serialized. False otherwise.
 */
bool vk_parse(std::string_view vkType, std::string vkString, uint32_t *pValue);


/**
 * @brief Serializes a Vulkan enumerator/flag type (64-bit)
 * @param vkType Name of the Vulkan enumerator/flag type
 * @param vkValue Value being serialized
 * @param pString Pointer to a string that will be modified with the serialized value. Only modified
 * if true is returned.
 * @return True the value was successfully serialized. False otherwise.
 */
bool vk_serialize(std::string_view vkType, uint64_t vkValue, std::string *pString);

/**
 * @brief Parses a Vulkan enumerator/flag serialized string (64-bit)
 * @param vkType Name of the Vulkan enumerator/flag type
 * @param vkString String being parsed
 * @param pValue Pointer to a value that will be modified with the parsed value. Only modified if
 * true is returned.
 * @return True the value was successfully serialized. False otherwise.
 */
bool vk_parse(std::string_view vkType, std::string vkString, uint64_t *pValue);

/**
 * @brief Serializes a Vulkan enumerator/flag type
 * @tparam Vulkan type being serialized
 * @param vkType Name of the Vulkan enumerator/flag type
 * @param vkValue Value being serialized
 * @param pString Pointer to a string that will be modified with the serialized value. Only modified
 * if true is returned.
 * @return True the value was successfully serialized. False otherwise.
 */
template <typename T>
bool vk_serialize(std::string_view vkType, T vkValue, std::string *pString) {
    return vk_serialize(vkType, static_cast<uint32_t>(vkValue), pString);
}

/**
 * @brief Parses a Vulkan enumerator/flag serialized string
 * @tparam Vulkan type being parsed
 * @param vkType Name of the Vulkan enumerator/flag type
 * @param vkString String being parsed
 * @param pValue Pointer to a value that will be modified with the parsed value. Only modified if
 * true is returned.
 * @return True the value was successfully serialized. False otherwise.
 */
template <typename T>
bool vk_parse(std::string_view vkType, std::string vkString, T *pValue) {
    uint32_t retVal = 0;
    auto found = vk_parse(vkType, vkString, &retVal);
    if (found) {
        *pValue = static_cast<T>(retVal);
    }
    return found;
} 
""")

    # Definition Start
    outFile.write("\n#ifdef VK_VALUE_SERIALIZATION_CONFIG_MAIN\n")
    outFile.write("\n#include <algorithm>\n")
    outFile.write("#include <array>\n")
    outFile.write("#include <cstring>\n")
    outFile.write("\nnamespace {\n")

    # Vendors
    vendors = dataRoot.findall('vendors/')
    processVendors(outFile, vendors)

    # EnumSet Declaration
    outFile.write("\nstruct EnumValueSet {\n")
    outFile.write("  std::string_view name;\n")
    outFile.write("  int64_t value;\n")
    outFile.write("};\n")

    # Enums
    enums = dataRoot.findall('enums/')
    processEnums(outFile, enums, vendors, firstVersion, lastVersion)

    # Enum Type Declaration
    outFile.write("\nstruct EnumType {\n")
    outFile.write("  std::string_view name;\n")
    outFile.write("  EnumValueSet const* data;\n")
    outFile.write("  uint32_t count;\n")
    outFile.write("  bool allowEmpty;\n")
    outFile.write("};\n")

    # Enum Pointer Array
    usefulEnumCount = 0
    for enum in enums:
        if enum.tag == 'VkResult' or enum.get('alias'):
            continue
        usefulEnumCount += 1

    outFile.writelines(["\nconstexpr std::array<EnumType, ", str(
        usefulEnumCount), "> enumTypes = {{\n"])  # -1 for not doing VkResult
    for enum in enums:
        if enum.tag == 'VkResult' or enum.get('alias'):
            continue

        valueCount = len(enum.findall('./'))
        if valueCount == 0:
            outFile.writelines(
                ["  {\"", str(enum.tag), "\", nullptr, 0, true},\n"])
        else:
            allowEmpty = "true"
            for enumVal in enum.findall('./'):
                if enumVal.get('first') == enum.get('first'):
                    allowEmpty = "false"
            outFile.writelines(["  {\"", str(enum.tag), "\", ", str(
                enum.tag), "Sets, ", str(valueCount), ", ", allowEmpty, "},\n"])
    outFile.write('}};\n')

    # Function definitions
    outFile.write("""
/**
 * @brief Removes a vendor tag from the end of the given string view
 * @param view String view to remove the vendor tag from
 * @return A string_view without the vendor tag, if it was suffixed
 */
std::string_view stripVendor(std::string_view view) {
    for (auto const &it : vendors) {
        // Don't strip if it's all that's left
        if (view == it)
            break;

        if (strncmp(view.data() + view.size() - it.size(), it.data(), it.size()) == 0) {
            view = view.substr(0, view.size() - it.size());
            break;
        }
    }

    return view;
}

/**
 * @brief Strips '_BIT' from the end of a string, if there
 */
std::string_view stripBit(std::string_view view) {
    if (view.size() > strlen("_BIT")) {
        if (view.substr(view.size() - strlen("_BIT")) == "_BIT") {
            return view.substr(0, view.size() - strlen("_BIT"));
        }
    }

    return view;
}

bool getEnumType(std::string_view vkType,
                 EnumValueSet const **ppStart,
                 EnumValueSet const **ppEnd,
                 bool *pAllowEmpty) {
  // Check for a conversion from Flags -> FlagBits
  std::string localString;
  if (vkType.rfind("Flags") != std::string::npos) {
    localString = vkType;
    auto it = localString.rfind("Flags");
    localString = localString.replace(it, strlen("Flags"), "FlagBits");
    vkType = localString;
  }

  // Try the original name
  for (auto const &it : enumTypes) {
    if (vkType == std::string_view{it.name}) {
      *ppStart = it.data;
      *ppEnd = it.data + it.count;
      *pAllowEmpty = it.allowEmpty;

      return true;
    }
  }

  // Try a vendor-stripped name
  vkType = stripVendor(vkType);
  for (auto const &it : enumTypes) {
    if (vkType == std::string_view{it.name}) {
      *ppStart = it.data;
      *ppEnd = it.data + it.count;
      *pAllowEmpty = it.allowEmpty;

      return true;
    }
  }

  return false;
}

/**
 * @brief Converts a Vulkan Flag typename into the prefix that is used for it's enums
 * @param typeName Name of the type to generate the Vk enum prefix for
 * @return Generated prefix string
 *
 * Any capitalized letters except for the first has an underscore inserted before it, an underscore
 * is added to the end, and all characters are converted to upper case.
 *
 * It also removed the 'Flags' or 'FlagBits' suffixes.
 */
std::string processEnumPrefix(std::string_view typeName) {
    // Flag Bits
    std::size_t flagBitsSize = strlen("FlagBits");
    if (typeName.size() > flagBitsSize) {
        if (strncmp(typeName.data() + typeName.size() - flagBitsSize, "FlagBits", flagBitsSize) ==
            0) {
            typeName = typeName.substr(0, typeName.size() - strlen("FlagBits"));
        }
    }
    // Flags
    std::size_t flagsSize = strlen("Flags");
    if (typeName.size() > flagsSize) {
        if (strncmp(typeName.data() + typeName.size() - flagsSize, "Flags", flagsSize) == 0) {
            typeName = typeName.substr(0, typeName.size() - strlen("Flags"));
        }
    }

    std::string retStr;
    for (auto it = typeName.begin(); it != typeName.end(); ++it) {
        if (it == typeName.begin()) {
            retStr += ::toupper(*it);
        } else if (::isupper(*it)) {
            retStr += '_';
            retStr += *it;
        } else {
            retStr += toupper(*it);
        }
    }
    retStr += '_';

    return retStr;
}

bool findValue(std::string_view findValue,
               std::string_view prefix,
               uint64_t *pValue,
               EnumValueSet const *start,
               EnumValueSet const *end) {
  // Try the initial value
  for (auto const *pStart = start; pStart != end; ++pStart) {
    if (findValue == pStart->name) {
      *pValue |= pStart->value;
      return true;
    }

    std::string prefixedName{prefix};
    prefixedName += pStart->name;
    if (findValue == prefixedName) {
      *pValue |= pStart->value;
      return true;
    }
  }

  // Remove the vendor tag suffix if it's on the value
  findValue = stripVendor(findValue);
  if (findValue[findValue.size() - 1] == '_')
    findValue = findValue.substr(0, findValue.size() - 1);

  // Remove '_BIT' if it's there
  findValue = stripBit(findValue);

  for (auto const *pStart = start; pStart != end; ++pStart) {
    if (findValue == pStart->name) {
      *pValue |= pStart->value;
      return true;
    }

    std::string prefixedName{prefix};
    prefixedName += pStart->name;
    if (findValue == prefixedName) {
      *pValue |= pStart->value;
      return true;
    }
  }

  return false;
}

/**
 * @brief Takes a given string and formats it for use with parsing
 * @param str The string to format
 * @return Formatted string
 *
 * First, any non alphanumeric characters are trimmed from both ends of the string.
 * After than, any spaces are replaced with underscores, and finally all the characters are
 * capitalized. This will generate the string closest to the original ones found in the XML spec.
 */
std::string formatString(std::string str) {
    // Trim left
    std::size_t cutOffset = 0;
    for (auto c : str) {
        if (::isalnum(c))
            break;
        else
            ++cutOffset;
    }
    str = str.substr(cutOffset);

    // Trim right
    cutOffset = 0;
    for (std::size_t i = 0; i < str.size(); ++i) {
        if (::isalnum(str[i]))
            cutOffset = i + 1;
    }
    str = str.substr(0, cutOffset);

    std::replace(str.begin(), str.end(), ' ', '_');
    std::for_each(str.begin(), str.end(), [](char &c) { c = ::toupper(c); });

    return str;
}

bool serializeBitmask(EnumValueSet const *end,
                      EnumValueSet const *start,
                      bool allowEmpty,
                      uint64_t vkValue,
                      std::string *pString) {
  --end;
  --start;

    if(start == end) {
        // If this is a non-existing bitmask, then return an empty string
        *pString = {};
        return true;
    }

    std::string retStr;
    while (start != end) {
        if(vkValue == 0 && !retStr.empty()) {
            break;
        }
        if ((start->value & vkValue) == start->value) {
            // Found a compatible bit mask, add it
            if (!retStr.empty()) {
                retStr += " | ";
            }
            retStr += start->name;
            vkValue = vkValue ^ start->value;
        }

        --start;
    }

    if (vkValue != 0 || (retStr.empty() && !allowEmpty)) {
        // Failed to find a valid bitmask for the value
        return false;
    }

    *pString = retStr;
    return true;
}

bool serializeEnum(EnumValueSet const *start,
                   EnumValueSet const *end,
                   uint64_t vkValue,
                   std::string *pString) {
  while (start != end) {
    if (start->value == vkValue) {
      *pString = start->name;
      return true;
    }

        ++start;
    }

    return false;
}

bool parseBitmask(std::string_view vkString,
                  EnumValueSet const *start,
                  EnumValueSet const *end,
                  std::string_view prefix,
                  uint64_t *pValue) {
  uint64_t retVal = 0;

  auto startCh = vkString.begin();
  auto endCh = startCh;
  for (; endCh != vkString.end(); ++endCh) {
    if (*endCh == '|') {
      std::string token(startCh, endCh);
      token = formatString(token);

      bool foundVal = findValue(token, prefix, &retVal, start, end);
      if (!foundVal)
        return false;

      startCh = endCh + 1;
    }
  }
  if (startCh != endCh) {
    std::string token(startCh, endCh);
    token = formatString(token);

    bool foundVal = findValue(token, prefix, &retVal, start, end);
    if (!foundVal)
      return false;
  }

  *pValue = retVal;
  return true;
}

bool parseEnum(std::string_view vkString,
               EnumValueSet const *start,
               EnumValueSet const *end,
               std::string_view prefix,
               uint64_t *pValue) {
  uint64_t retVal = 0;

  std::string token = formatString(std::string{vkString});
  bool found = findValue(token, prefix, &retVal, start, end);
  if (found) {
    *pValue = retVal;
  }
  return found;
}

} // namespace

bool vk_serialize(std::string_view vkType, uint64_t vkValue, std::string *pString) {
    if (vkType.empty()) {
        return false;
    }

  EnumValueSet const *start, *end;
  bool allowEmpty;
  if (!getEnumType(vkType, &start, &end, &allowEmpty)) {
    return false;
  }

  if (vkType.find("Flags") != std::string::npos || vkType.find("FlagBits") != std::string::npos) {
    return serializeBitmask(start, end, allowEmpty, vkValue, pString);
  }

  return serializeEnum(start, end, vkValue, pString);
}

bool vk_serialize(std::string_view vkType, uint32_t vkValue, std::string *pString) {
  return vk_serialize(vkType, static_cast<uint64_t>(vkValue), pString);
}

bool vk_parse(std::string_view vkType, std::string vkString, uint64_t *pValue) {
  if (vkType.empty()) {
    return false;
  }

  EnumValueSet const *start, *end;
  bool allowEmpty;
  if (!getEnumType(vkType, &start, &end, &allowEmpty)) {
    return false;
  }

  if (vkString.empty()) {
    if (allowEmpty) {
      *pValue = 0;
      return true;
    } else {
      return false;
    }
  }

  std::string prefix = processEnumPrefix(stripVendor(vkType));

  if (vkType.find("Flags") != std::string::npos || vkType.find("FlagBits") != std::string::npos) {
    return parseBitmask(vkString, start, end, prefix, pValue);
  }

  return parseEnum(vkString, start, end, prefix, pValue);
}

bool vk_parse(std::string_view vkType, std::string vkString, uint32_t *pValue) {
    uint64_t tempValue;
    if (vk_parse(vkType, vkString, &tempValue)) {
        *pValue = static_cast<uint32_t>(tempValue);
        return true;
    }
    return false;
}
""")

    # endif
    outFile.write("\n#endif // VK_VALUE_SERIALIZATION_CONFIG_MAIN\n")
    outFile.write("#endif // VK_VALUE_SERIALIZATION_HPP\n")
    outFile.close()


if __name__ == "__main__":
    main(sys.argv[1:])
