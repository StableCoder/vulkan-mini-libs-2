#!/usr/bin/env python3


import sys
import getopt
import xml.etree.ElementTree as ET


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

    # Get first/last versions
    firstVersion = int(dataRoot.get('first'))
    lastVersion = int(dataRoot.get('last'))

    outFile = open(outputFile, "w")

    # Common Header
    with open("common_header.txt") as fd:
        outFile.write(fd.read())
        outFile.write('\n')

    outFile.write("""#ifndef VK_ERROR_CODE_HPP
#define VK_ERROR_CODE_HPP

#include <vulkan/vulkan.h>

#include <system_error>

""")

    # Static asserts
    outFile.writelines(["static_assert(VK_HEADER_VERSION >= ", str(firstVersion),
                        ", \"VK_HEADER_VERSION is from before the supported range.\");\n"])
    outFile.writelines(["static_assert(VK_HEADER_VERSION <= ", str(lastVersion),
                        ", \"VK_HEADER_VERSION is from after the supported range.\");\n"])

    outFile.write("""
/*  USAGE
    To use, include this header where the declarations for the boolean checks are required.

    On *ONE* compilation unit, include the definition of `#define VK_ERROR_CODE_CONFIG_MAIN`
    so that the definitions are compiled somewhere following the one definition rule.
*/

namespace std {
template <>
struct is_error_code_enum<VkResult> : true_type {};
} // namespace std

std::error_code make_error_code(VkResult);

#ifdef VK_ERROR_CODE_CONFIG_MAIN

namespace {

struct VulkanErrCategory : std::error_category {
  const char *name() const noexcept override;
  std::string message(int ev) const override;
};

const char *VulkanErrCategory::name() const noexcept {
  return "VkResult";
}

std::string VulkanErrCategory::message(int ev) const {
  VkResult const vkRes = static_cast<VkResult>(ev);

  // Check in descending order to get the 'latest' version of the error code text available.
  // Also, because codes have been re-used over time, can't use a switch and have to do this large set of ifs.
  // Luckily this *should* be a relatively rare call.
""")

    # Content
    currentVersion = lastVersion
    while currentVersion >= firstVersion:
        for enum in dataRoot.findall('enums/VkResult/'):
            if int(enum.get('first')) != currentVersion:
                continue

            guarded = False
            # Guard check for first version
            if int(enum.get('first')) != firstVersion:
                guarded = True
                outFile.writelines(
                    ['#if VK_HEADER_VERSION >= ', enum.get('first')])
            # Guard check for last version
            if int(enum.get('last')) != lastVersion:
                if guarded:
                    # If already started, append to it
                    outFile.writelines(
                        [' && VK_HEADER_VERSION <= ', enum.get('last')])
                else:
                    guarded = True
                    outFile.writelines(
                        ['#if VK_HEADER_VERSION <= ', enum.get('last')])
            # Guard check for platforms
            for platform in enum.findall('platforms/'):
                if guarded:
                    # If already started, append to it
                    outFile.writelines(
                        [' && ', platform.tag])
                else:
                    guarded = True
                    outFile.writelines(
                        ['#if ', platform.tag])

            if guarded:
                outFile.write('\n')

            outFile.writelines(['  if (vkRes == ', enum.tag, ')\n'])
            outFile.writelines(['    return \"', enum.tag, '\";\n'])

            if guarded:
                outFile.write('#endif\n')
        currentVersion -= 1

    # Footer
    outFile.write("""
  if (vkRes > 0)
    return "(unrecognized positive VkResult value)";
  else
    return "(unrecognized negative VkResult value)";
}

const VulkanErrCategory vulkanErrCategory{};

} // namespace

std::error_code make_error_code(VkResult e) {
  return {static_cast<int>(e), vulkanErrCategory};
}

#endif // VK_ERROR_CODE_CONFIG_MAIN
#endif // VK_ERROR_CODE_HPP
""")


if __name__ == "__main__":
    main(sys.argv[1:])
