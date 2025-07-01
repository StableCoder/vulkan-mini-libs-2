#!/usr/bin/env python3

# Copyright (C) 2022-2023 George Cave.
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import gen_common
import sys
import json


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input',
                        help='Input JSON cache file',
                        required=True)
    parser.add_argument('-o', '--output',
                        help='Output file to write to',
                        required=True)
    parser.add_argument('-a', '--api',
                        help='Khronos API being processed',
                        required=True)
    args = parser.parse_args()

    try:
        file = open(args.input, 'r')
        apiData = json.load(file)
    except:
        print("Error: Could not open input file: ", args.input)
        sys.exit(1)

    # Get first/last versions
    firstVersion = apiData['api']['first']
    lastVersion = apiData['api']['last']

    outFile = open(args.output, "w")

    if args.api == 'vulkan':
        apiVersionStr = 'VK_HEADER_VERSION'
        apiVersionDefine = 'VK_HEADER_VERSION'
        enumType = 'VkResult'
        header = '<vulkan/vulkan.h>'
        guard = 'VK_RESULT'
    elif args.api == 'openxr':
        apiVersionStr = '(XR_CURRENT_API_VERSION & 0xffffffffULL)'
        apiVersionDefine = 'XR_CURRENT_API_VERSION'
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

    # static asserts
    outFile.write('\n#ifdef __cplusplus\n')
    outFile.write(
        "static_assert({0} >= {1}, \"{2} is lower than the minimum supported version (v{1})\");\n".format(apiVersionStr, firstVersion, apiVersionDefine))
    outFile.write('#else\n')
    outFile.write(
        "_Static_assert({0} >= {1}, \"{2} is lower than the minimum supported version (v{1})\");\n".format(apiVersionStr, firstVersion, apiVersionDefine))
    outFile.write('#endif\n')

    # version warnings
    outFile.write('\n#if {0} > {1}\n'.format(apiVersionStr, lastVersion))
    outFile.write('#if _MSC_VER\n')
    outFile.write('#pragma message(__FILE__ ": warning: {} is higher than what the header fully supports (v{})")\n'.format(apiVersionDefine, lastVersion))
    outFile.write('#else\n')
    outFile.write('#warning "{} is higher than what the header fully supports (v{})"\n'.format(apiVersionDefine, lastVersion))
    outFile.write('#endif\n')
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

  switch (result) {{
""".format(guard, enumType))

    # Content
    doneValues = []
    for key, data in apiData['enums'][enumType]['values'].items():
        if 'alias' in data:
            continue
        if data['value'] in doneValues:
            continue

        outFile.write('  case {}:\n'.format(data['value']))
        outFile.write('    return \"{}\";\n'.format(key))
        doneValues.append(data['value'])

    # Footer
    outFile.write("""
  default:
    return NULL;
  }
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
