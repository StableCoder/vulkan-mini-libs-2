# Vulkan Mini Libs 2
[![pipeline status](https://git.stabletec.com/utilities/vulkan-mini-libs-2/badges/main/pipeline.svg)](https://git.stabletec.com/utilities/vulkan-mini-libs-2/commits/main)
[![coverage report](https://git.stabletec.com/utilities/vulkan-mini-libs-2/badges/main/coverage.svg)](https://git.stabletec.com/utilities/vulkan-mini-libs-2/commits/main)
[![license](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://git.stabletec.com/utilities/vulkan-mini-libs-2/blob/main/LICENSE)

A set of small header-only libraries that are of limited scope each to perform a very specific task.

Compared to the previous version of these libraries which generated header versions for each Vulkan header version, this one remains backwards and forwards compatible, serving a given whole range of header versions (typically v1.0.72 - current) through the use of Vulkan definitions

# Vulkan Value Serialization

This program builds header files for use in C++17 or newer. It
contains all Vulkan enum types/flags/values of the indicated Vulkan header spec
version, and can convert to/from strings representing those values. 

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

Also, to assist with forward and backwards compatability, all the vendor tags can 
stripped from the typenames and values, since they can be removed in later versions 
leading to incompatability issues. For example, the flag for VkToolPurposeFlagBitsEXT, 
`VK_TOOL_PURPOSE_VALIDATION_BIT_EXT`, can will output as `VALIDATION`, and can 
be read similarly, with the above rules applicable for parsing. Also removed often is
the `_BIT` suffix.

## Usage

On *ONE* compilation unit, include the definition of `#define VK_VALUE_SERIALIZATION_CONFIG_MAIN` so that the definitions are compiled somewhere following the one definition rule (ODR).

# Vulkan Error Code

Header file for C++. Contains the implementation details that allow the use of VkResult values with std::error_code and std::error_category.

## Usage

On *ONE* compilation unit, include the definition of `#define VK_ERROR_CODE_CONFIG_MAIN` so that the definitions are compiled somewhere following the one definition rule (ODR).

Then, one can implicitly convert VkResult to std::error_code:
```cpp
#include <vulkan/vulkan.h>
#include "vk_error_code.hpp"

int main(int, char **) {
  std::error_code ec = (VkResult)VK_ERROR_DEVICE_LOST;

  std::cout << ec.value() << ':' << ec.message() << std::endl;
}
```

# Vulkan Struct Cleanup

C11-compatible C header that has all available structs in the generated range, and can safely free memory held by the given struct. This operates on the principle that *all* data that the struct points to externally is *owned* by the struct and it's children, and can be safely freed.

It does follow through the `pNext` pointers to any other structs that are assumed to have `sType` members and cleans those up as well (through the `cleanup_vk_struct` function). It is also assumed that the held data are managed as separate allocations.

Structs that have no externally held data are inlined as empty functions for better compilation efficacy.

## Usage

On *ONE* compilation unit, include the definition of `#define VK_STRUCT_CLEANUP_CONFIG_MAIN` so that the definitions are compiled somewhere following the one definition rule (ODR).

Otherwise, call the appropriate function based on the Vulkan struct name, which is prefixed by `cleanup_<VK_STRUCT_NAME>(ptr)`. ie. for the `VkPipelineShaderStageCreateInfo` call `cleanup_VkPipelineShaderStageCreateInfo(pCI);`.

If a Vulkan struct is an undetermined type, but is at least of a type that contains VkStructureType/sType member, then `vk_cleanup_struct(ptr)` can be used.

# Generating Header Mini-Libs

In the root of the repository is a shell script, `tools/generate.sh` that will iterate through the range of Vulkan versions, parsing the XML files and collecting the relevant data. After that, it generates the header files using that procesed data.

## Possible Arguments

### -s, --start <INT>
The starting version of Vulkan to generate for (default: 72)

NOTE: Minimal version is 72, as that is when the XML was first published.

### -e, --end <INT>
The ending version of Vulkan to generate for (default: none)
