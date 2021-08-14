#!/usr/bin/env python3

import sys, getopt
import xmltodict

def main(argv):
    inputFile=''
    outputFile=''
    data = dict()

    try:
       opts, args =  getopt.getopt(argv, 'i:o:', [])
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
        with open(inputFile) as fd:
            data = xmltodict.parse(fd.read())
    except:
        print("Error: Could not open input file: ", inputFile)
        sys.exit(1)

    outFile = open(outputFile, "w")

    root = data['root']

    with open("common_header.txt") as fd:
        outFile.write(fd.read())
        outFile.write('\n')

    outFile.write("""#ifndef VK_ERROR_CODE_HPP
#define VK_ERROR_CODE_HPP

#include <vulkan/vulkan.h>

#include <system_error>

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
""")

    # Get the start/end versions
    firstVersion = data['root']['first']
    lastVersion = data['root']['last']

    # Content
    resultSet = root['enums']['VkResult']['values']
    for resultCode in resultSet:
        if '@alias' in resultSet[resultCode]:
            continue

        guarded = False
        if resultSet[resultCode]['first'] != firstVersion:
            guarded = True
            outFile.writelines(['#if VK_HEADER_VERSION >= ', resultSet[resultCode]['first']])
        if resultSet[resultCode]['last'] != lastVersion:
            if guarded:
                # If already started, append to it
                outFile.writelines([' && VK_HEADER_VERSION <= ', resultSet[resultCode]['last']])
            else:
                guarded = True
                outFile.writelines(['#if VK_HEADER_VERSION <= ', resultSet[resultCode]['last']])

        if guarded:
            outFile.write('\n')

        outFile.writelines(['  if (vkRes == ', str(resultCode), ')\n'])
        outFile.writelines(['    return \"', str(resultCode), '\";\n'])

        if guarded:
            outFile.write('#endif\n')

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