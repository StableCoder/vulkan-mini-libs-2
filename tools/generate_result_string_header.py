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

    outFile.write("""#ifndef VK_RESULT_TO_STRING_H
#define VK_RESULT_TO_STRING_H

/*  USAGE
    To use, include this header where the declarations for the boolean checks are required.

    On *ONE* compilation unit, include the definition of `#define VK_RESULT_TO_STRING_CONFIG_MAIN`
    so that the definitions are compiled somewhere following the one definition rule.
*/

#ifdef __cplusplus
extern "C" {
#endif

#include <vulkan/vulkan.h>

""")

    # Static asserts
    outFile.writelines(["static_assert(VK_HEADER_VERSION >= ", str(firstVersion),
                        ", \"VK_HEADER_VERSION is from before the supported range.\");\n"])
    outFile.writelines(["static_assert(VK_HEADER_VERSION <= ", str(lastVersion),
                        ", \"VK_HEADER_VERSION is from after the supported range.\");\n"])

    outFile.write("""
// This is effectively a cheap approximation of OpenXR's useful `xrResultToString` function but for Vulkan
char const* vkResultToString(VkResult res);

#ifdef VK_RESULT_TO_STRING_CONFIG_MAIN

char const* vkResultToString(VkResult vkRes) {
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

#endif // VK_RESULT_TO_STRING_CONFIG_MAIN

#ifdef __cplusplus
}
#endif

#endif // VK_RESULT_TO_STRING_H
""")


if __name__ == "__main__":
    main(sys.argv[1:])