# Vulkan (and OpenXR) Mini Libs 2  <!-- omit in toc -->
[![pipeline status](https://git.stabletec.com/utilities/vulkan-mini-libs-2/badges/main/pipeline.svg)](https://git.stabletec.com/utilities/vulkan-mini-libs-2/commits/main)
[![coverage report](https://git.stabletec.com/utilities/vulkan-mini-libs-2/badges/main/coverage.svg)](https://git.stabletec.com/utilities/vulkan-mini-libs-2/commits/main)
[![license](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://git.stabletec.com/utilities/vulkan-mini-libs-2/blob/main/LICENSE)

- [Vulkan Value Serialization (C/C++)](#vulkan-value-serialization-cc)
  - [Serialization](#serialization)
  - [Parsing](#parsing)
- [Vulkan Result to String (C)](#vulkan-result-to-string-c)
- [OpenXR Result to String (C)](#openxr-result-to-string-c)
- [Vulkan Error Code (C++)](#vulkan-error-code-c)
- [Vulkan Struct Cleanup (C)](#vulkan-struct-cleanup-c)
- [Generating fresh Mini-Libs](#generating-fresh-mini-libs)

A set of small header-only libraries that are of limited scope each to perform a very specific task.

Compared to the previous version of these libraries which generated header versions for each Vulkan header version, this one remains backwards and forwards compatible, serving a given whole range of header versions (typically v1.0.72 - current for Vulkan, all of OpenXR) through the use of the provided XML registry specficiations.

# Vulkan Value Serialization (C/C++)

This program builds header files for use in C11/C++17 or newer. It
contains all Vulkan enum types/flags/values of the indicated Vulkan header spec
version range, and can convert to/from strings representing those values.

Supports both plain enums and the bitmasks.

When converting values to strings, where possible a shorter version of the
enum string is used, where the verbose type prefix is removed:
- VK_IMAGE_LAYOUT_GENERAL => GENERAL
- VK_CULL_MODE_FRONT_BIT | VK_CULL_MODE_BACK_BIT => FRONT | BACK

When converting from strings into values, either the short OR full string can
be used where strings are case insensitive, and underscores can be replaced
with spaces, and addition whitespace can be added to either side of the first/
last alphanumeric character, as these are trimmed off.

For example, all of the following convert to VK_IMAGE_LAYOUT_GENERAL:
`vk imAGE_LayOut GenerAL`, `VK_IMAGE_LAYOUT_GENERAL`,`GENERAL`, `   General `

Also, to assist with forward and backwards compatibility, all the vendor tags can 
stripped from the typenames and values, since they can be removed in later versions 
leading to incompatibility issues. For example, the flag for VkToolPurposeFlagBitsEXT, 
`VK_TOOL_PURPOSE_VALIDATION_BIT_EXT`, can will output as `VALIDATION`, and can 
be read similarly, with the above rules applicable for parsing. Also removed often is
the `_BIT` suffix.

## Usage <!-- omit in toc -->

On *ONE* compilation unit, include the definition of `#define VK_VALUE_SERIALIZATION_CONFIG_MAIN` before the header is included so that the definitions are compiled somewhere following the one definition rule (ODR).

### C <!-- omit in toc -->

For C, there are the simple functions for parsing and serializing:
- vk_parse32
- vk_parse64
- vk_serialize32
- vk_serialize64
```c
#define VK_VALUE_SERIALIZATION_CONFIG_MAIN
#include <vk_value_serialization.h>
```

### C++ <!-- omit in toc -->

Using the HPP header in C++ also grants the use of a few templated functions and macros to make usage just a tad easier, no longer having to deal with the casting to uint types, and can be included similarly, and does include the original C functions as well:
```c
#define VK_VALUE_SERIALIZATION_CONFIG_MAIN
#include <vk_value_serialization.hpp>
```
## Serialization

```c
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
STecVkSerializationResult vk_serialize32(char const *pVkType,
                                         uint32_t vkValue,
                                         uint32_t *pSerializedLength,
                                         char *pSerialized);
```

### Usage <!-- omit in toc -->

```c
char testStr[20];
uint32_t serializedLength = 20;
STecVkSerializationResult result;
result = vk_serialize32("VkDebugReportFlagsEXT",
                        VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT,
                        &serializedLength, testStr);
  // result is STEC_VK_SERIALIZATION_RESULT_SUCCESS
  // testStr's first 13 characters is now "DEBUG | ERROR"
  // serializedLength is now 13
```

```c
char testStr[20];
uint32_t serializedLength = 8;
STecVkSerializationResult result;
result = vk_serialize32("VkDebugReportFlagsEXT",
                        VK_DEBUG_REPORT_DEBUG_BIT_EXT | VK_DEBUG_REPORT_ERROR_BIT_EXT,
                        &serializedLength, testStr);
  // result is STEC_VK_SERIALIZATION_RESULT_ERROR_INCOMPLETE
  // testStr's first 8 characters is now "DEBUG | "
  // serializedLength is now 8
```

## Parsing

```c
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
STecVkSerializationResult vk_parse32(char const *pVkType,
                                     char const *pVkString,
                                     uint32_t *pParsedValue);
```

### Usage <!-- omit in toc -->

```c
VkImageLayout parsedLayout;
STecVkSerializationResult result;
result = vk_parse32("VkImageLayout", "TRANSFER_DST_OPTIMAL", (uint32_t *)&parsedLayout);
  // parsedLayout is now VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL

VkPipelineStageFlags2 parsedStagsFlags;
result = vk_parse64("VkPipelineStageFlagBits2",
           "INVOCATION_MASK_BIT_HUAWEI | VK_PIPELINE_STAGE_2_TOP_OF_PIPE_BIT",
           (uint64_t *)&parsedStagsFlags);
  // parsedStagsFlags is now VK_PIPELINE_STAGE_2_TOP_OF_PIPE_BIT | VK_PIPELINE_STAGE_2_INVOCATION_MASK_BIT_HUAWEI
```

# Vulkan Result to String (C)

C-compatible header file with functions which will convert a VkResult to the corresponding string representation, or as close as possible in the case with shared values.

## Usage <!-- omit in toc -->

On *ONE* compilation unit, include the definition of `#define VK_RESULT_TO_STRING_CONFIG_MAIN` before the header is included so that the definitions are compiled somewhere following the one definition rule (ODR).

There are two functions that can be called:
- `char const *VkResult_to_string(VkResult)` which returns NULL if there is no compiled string representation for the given VkResult.
- `char const *vkResultToString(VkResult)` which returns a string of '(unrecognized positive VkResult value)' or '(unrecognized negative VkResult value)' if there is no compiled string representation for the given VkResult.

```cpp
#define VK_RESULT_TO_STRING_CONFIG_MAIN
#include "vk_result_to_string.h"
#include <iostream>

int main(int, char **) {
  char const* resStr = vkResultToString(VK_ERROR_DEVICE_LOST);
  std::cout << resStr << std::endl;
}
```

# OpenXR Result to String (C)

C-compatible header file with a single function, `XrResult_to_string`, which will convert a given XrResult to a string representation, or as close as possible in the case with shared values. If the given value doesn't have a corresponding string, it returns `NULL`.

## Usage <!-- omit in toc -->

On *ONE* compilation unit, include the definition of `#define XR_RESULT_TO_STRING_CONFIG_MAIN` before the header is included so that the definitions are compiled somewhere following the one definition rule (ODR).

```cpp
#define XR_RESULT_TO_STRING_CONFIG_MAIN
#include "xr_result_to_string.h"
#include <iostream>

int main(int, char **) {
  char const* resStr = XrResult_to_string(XR_ERROR_TIME_INVALID);
  if(resStr != nullptr)
    std::cout << resStr << std::endl;
}
```

# Vulkan Error Code (C++)

Header file for C++. Contains the implementation details that allow the use of VkResult values with std::error_code and std::error_category.

## Usage <!-- omit in toc -->

On *ONE* compilation unit, include the definition of `#define VK_ERROR_CODE_CONFIG_MAIN` **AND** ensure that `#define VK_RESULT_TO_STRING_CONFIG_MAIN` is defined somewhere before the header is included, not necessarily in the same compilation unit, so that the definitions are compiled somewhere following the one definition rule (ODR).

Then, one can implicitly convert VkResult to std::error_code:
```cpp
#define VK_RESULT_TO_STRING_CONFIG_MAIN
#define VK_ERROR_CODE_CONFIG_MAIN
#include "vk_error_code.hpp"
#include <iostream>

int main(int, char **) {
  std::error_code ec = (VkResult)VK_ERROR_DEVICE_LOST;

  std::cout << ec.value() << ':' << ec.message() << std::endl;
}
```

# Vulkan Struct Cleanup (C)

C11-compatible C header that has all available structs in the generated range, and can safely free memory held by the given struct. This operates on the principle that *all* data that the struct points to externally is *owned* by the struct and it's children, and can be safely freed.

It does follow through the `pNext` pointers to any other structs that are assumed to have `sType` members and cleans those up as well (through the `cleanup_vk_struct` function). It is also assumed that the held data are managed as separate allocations.

Structs that have no externally held data are inlined as empty functions for better compilation efficacy.

## Usage <!-- omit in toc -->

On *ONE* compilation unit, include the definition of `#define VK_STRUCT_CLEANUP_CONFIG_MAIN` so that the definitions are compiled somewhere following the one definition rule (ODR).

Otherwise, call the appropriate function based on the Vulkan struct name, which is prefixed by `cleanup_<VK_STRUCT_NAME>(ptr)`. ie. for the `VkPipelineShaderStageCreateInfo` call `cleanup_VkPipelineShaderStageCreateInfo(pCI);`.

If a Vulkan struct is an undetermined type, but is at least of a type that contains VkStructureType/sType member, then `vk_cleanup_struct(ptr)` can be used.

# Generating fresh Mini-Libs

In the root of the repository is a shell script, `tools/generate.sh` that will iterate through the range of Vulkan versions, parsing the XML files and collecting the relevant data. After that, it generates the header files using that procesed data.


## Possible Arguments <!-- omit in toc -->

### -s, --start \<INT> <!-- omit in toc -->
The starting version of Vulkan to generate for (default: 72 for Vulkan, 0 for OpenXR)

NOTE: Minimal version is 72, as that is when the XML was first published.

### -e, --end \<INT> <!-- omit in toc -->
The ending version of Vulkan to generate for (default: none)

### -o, --output \<DIR> <!-- omit in toc -->

The directory in which to generate header files (default: <repo>/include)

### --openxr <!-- omit in toc -->

Parses then generates files for OpenXR instead of the Vulkan default.

### --skip-parse <!-- omit in toc -->
Skips parsing the XML doc and re-generating the cache file. Use this if the cache has been previously generated and you're just re-generating the headers from that cache.
