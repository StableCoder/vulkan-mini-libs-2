#!/usr/bin/env python3

# Copyright (C) 2022-2023 George Cave.
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import gen_common
import sys
import xml.etree.ElementTree as ET


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input',
                        help='Input XML cache file',
                        required=True)
    parser.add_argument('-o', '--output',
                        help='Output file to write to',
                        required=True)
    parser.add_argument('-a', '--api',
                        help='Khronos API being processed',
                        required=True)
    args = parser.parse_args()

    try:
        dataXml = ET.parse(args.input)
        dataRoot = dataXml.getroot()
    except:
        print("Error: Could not open input file: ", args.input)
        sys.exit(1)

    # Get first/last versions
    firstVersion = int(dataRoot.get('first'))
    lastVersion = int(dataRoot.get('last'))

    outFile = open(args.output, "w")

    if args.api == 'vulkan':
        apiVersionStr = 'VK_HEADER_VERSION'
        enumType = 'VkResult'
        header = '<vulkan/vulkan.h>'
        guard = 'VK_RESULT'
    elif args.api == 'openxr':
        apiVersionStr = '(XR_CURRENT_API_VERSION & 0xffffffffULL)'
        enumType = 'XrResult'
        header = '<openxr/openxr.h>'
        guard = 'XR_RESULT'

    # Common Header
    gen_common.writeHeader(outFile)

    outFile.write("""#ifndef {0}_TO_STRING_H
#define {0}_TO_STRING_H

/*  USAGE
    To use, include this header where the declarations for the boolean checks are required.

    On *ONE* compilation unit, include the definition of:
    #define {0}_TO_STRING_CONFIG_MAIN

    so that the definitions are compiled somewhere following the one definition rule.
*/

#ifdef __cplusplus
extern "C" {{
#endif

#include {1}

""".format(guard, header))

    # Static asserts
    outFile.write('\n#ifdef __cplusplus\n')
    outFile.write(
        "static_assert({0} >= {1}, \"{2} header version is from before the minimum supported version of v{1}.\");\n".format(apiVersionStr, firstVersion, args.api))
    outFile.write(
        "static_assert({0} <= {1}, \"{2} header version is from after the maximum supported version of v{1}.\");\n".format(apiVersionStr, lastVersion, args.api))
    outFile.write('#else\n')
    outFile.write(
        "_Static_assert({0} >= {1}, \"{2} header version is from before the minimum supported version of v{1}.\");\n".format(apiVersionStr, firstVersion, args.api))
    outFile.write(
        "_Static_assert({0} <= {1}, \"{2} header version is from after the maximum supported version of v{1}.\");\n".format(apiVersionStr, lastVersion, args.api))
    outFile.write('#endif\n')

    outFile.write("""
/// Returns a string representing the given VkResult parameter. If there is no known representation,
/// returns NULL.
char const *{0}_to_string({0} result);
""".format(enumType))

    if args.api == 'vulkan':
        outFile.write("""
/// Similar to VkResult_to_string, except in the case where it is an unknown value, returns a string
/// stating '(unrecognized positive/negative VkResult value)', thus never returning NULL.
char const *vkResultToString(VkResult result);
""")

    outFile.write("""
#ifdef {0}_TO_STRING_CONFIG_MAIN

char const* {1}_to_string({1} result) {{
  // Check in descending order to get the 'latest' version of the error code text available.
  // Also, because codes have been re-used over time, can't use a switch and have to do this large set of ifs.
  // Luckily this *should* be a relatively rare call.
""".format(guard, enumType))

    # Content
    currentVersion = lastVersion
    while currentVersion >= firstVersion:
        for enum in dataRoot.findall('enums/{}/values/'.format(enumType)):
            if int(enum.get('first')) != currentVersion:
                continue

            guarded = False
            # Guard check for first version
            if int(enum.get('first')) != firstVersion:
                guarded = True
                outFile.write(
                    '#if {} >= {}'.format(apiVersionStr, enum.get('first')))
            # Guard check for last version
            if int(enum.get('last')) != lastVersion:
                if guarded:
                    # If already started, append to it
                    outFile.write(
                        ' && {} <= {}'.format(apiVersionStr, enum.get('last')))
                else:
                    guarded = True
                    outFile.write(
                        '#if {} <= {}'.format(apiVersionStr, enum.get('last')))
            # Guard check for platforms
            for platform in enum.findall('platforms/'):
                if guarded:
                    # If already started, append to it
                    outFile.write(' && {}'.format(platform.tag))
                else:
                    guarded = True
                    outFile.write('#if {}'.format(platform.tag))

            if guarded:
                outFile.write('\n')

            outFile.write('  if (result == {})\n'.format(enum.tag))
            outFile.write('    return \"{}\";\n'.format(enum.tag))

            if guarded:
                outFile.write('#endif\n')
        currentVersion -= 1

    # Footer
    outFile.write("""
  return NULL;
}
""")

    if args.api == 'vulkan':
        outFile.write("""
char const* vkResultToString(VkResult result) {
  char const* pResultString = VkResult_to_string(result);
  if(pResultString != NULL)
    return pResultString;

  if (result > 0)
    return "(unrecognized positive VkResult value)";
  else
    return "(unrecognized negative VkResult value)";
}
""")

    outFile.write("""
#endif // {0}_TO_STRING_CONFIG_MAIN

#ifdef __cplusplus
}}
#endif

#endif // {0}_TO_STRING_H
""".format(guard))


if __name__ == "__main__":
    main(sys.argv[1:])
