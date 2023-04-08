#!/usr/bin/env python3

# Copyright (C) 2022-2023 George Cave.
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import gen_common
import sys
import yaml
import xml.etree.ElementTree as ET


def guardStruct(struct, firstVersion, lastVersion, outFile):
    guarded = False
    # Guard check for first version
    if struct.get('first') != firstVersion:
        guarded = True
        outFile.write('#if VK_HEADER_VERSION >= {}'.format(
            struct.get('first')))
    # Guard check for last version
    if struct.get('last') != lastVersion:
        if guarded:
            # If already started, append to it
            outFile.write(
                ' && VK_HEADER_VERSION <= {}'.format(struct.get('last')))
        else:
            guarded = True
            outFile.write(
                '#if VK_HEADER_VERSION <= {}'.format(struct.get('last')))
    # Guard check for platforms
    platforms = struct.findall('platforms/')
    if platforms:
        if guarded:
            # If already started, append to it
            outFile.write(' && ')
        else:
            guarded = True
            outFile.write('\n#if ')

        if len(platforms) > 1:
            outFile.write('(')
        platformed = False
        for platform in platforms:
            defineStr = platform.tag
            subPlatforms = platform.findall('./')
            for sub in subPlatforms:
                defineStr += ' && {}'.format(sub.tag)

            if platformed:
                outFile.write(' || ({})'.format(defineStr))
            else:
                platformed = True
                outFile.write('({})'.format(defineStr))
        if len(platforms) > 1:
            outFile.write(')')

    if guarded:
        outFile.write('\n')
    return guarded


def main(argv):
    data = dict()

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input',
                        help='Input XML cache file',
                        required=True)
    parser.add_argument('-y', '--yaml',
                        help='YAML file that specifies what items to be ignored',
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

    try:
        with open(args.yaml, 'r') as file:
            yamlData = yaml.safe_load(file)
    except:
        print("Error: Could not open Yaml file: ", args.yaml)
        sys.exit(1)

    # Get first/last versions
    firstVersion = dataRoot.get('first')
    lastVersion = dataRoot.get('last')

    structs = dataRoot.findall('structs/')

    outFile = open(args.output, "w")

    # Common header
    gen_common.writeHeader(outFile)

    # Specific Header
    outFile.write("""#ifndef VK_STRUCT_COMPARE_H
#define VK_STRUCT_COMPARE_H

/*  USAGE:
    To use, include this header where the declarations for the boolean checks are required.

    On *ONE* compilation unit, include the definition of:
    #define VK_STRUCT_COMPARE_CONFIG_MAIN

    so that the definitions are compiled somewhere following the one definition rule.
*/

/*
    These compare_*(lhs, rhs) functions only check the given struct's directly held data.
    Data held externally via pointers is not compared and must be done by the caller.
*/

#ifdef __cplusplus
extern "C" {
#endif

#include <vulkan/vulkan.h>

#include <stdbool.h>
""")

    # static_asserts
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

    # Per-struct function declarations
    for struct in structs:
        structName = struct.tag

        if structName == 'VkBaseInStructure' or structName == 'VkBaseOutStructure':
            continue
        if structName in yamlData:
            continue

        outFile.write('\n')

        guarded = guardStruct(struct, firstVersion, lastVersion, outFile)
        outFile.write(
            'bool compare_{0}({0} const *s1, {0} const* s2);\n'.format(structName))
        if guarded:
            outFile.write("#endif\n")

    # Definitions
    outFile.write('\n#ifdef VK_STRUCT_COMPARE_CONFIG_MAIN\n')

    # All defined structs
    for struct in structs:
        structName = struct.tag

        if structName == 'VkBaseInStructure' or structName == 'VkBaseOutStructure':
            continue
        if structName in yamlData:
            continue

        outFile.write('\n')

        guarded = guardStruct(struct, firstVersion, lastVersion, outFile)
        outFile.write(
            'bool compare_{0}({0} const *s1, {0} const* s2) {{'.format(structName))

        # First, rule out the basic types (no pointers/sType/arrays)
        started = False
        membersNode = struct.find('members')
        members = struct.findall('members/')
        for member in members:
            memberName = member.tag
            memberType = member.find('type').text
            memberTypeSuffix = member.find('type').get('suffix')
            memberSuffix = member.get('suffix')

            if (memberTypeSuffix and '*' in memberTypeSuffix) or (memberSuffix and '[' in memberSuffix):
                continue

            if memberName == 'sType' or memberName == 'pNext':
                continue

            if not started:
                outFile.write('\n  if (\n')

            guardedMember = guardStruct(member, membersNode.get(
                'first'), membersNode.get('last'), outFile)
            memberStruct = dataRoot.findall('structs/{}/'.format(memberType))
            if memberStruct:
                outFile.write(
                    '!compare_{0}(&s1->{1}, &s2->{1}) ||\n'.format(memberType, memberName))
            else:
                outFile.write('(s1->{0} != s2->{0}) ||\n'.format(memberName))
            if guardedMember:
                outFile.write('#endif\n')
            started = True
        if started:
            outFile.write('false)\n    return false;\n\n')

        # Now for local arrays
        for member in members:
            memberName = member.tag
            memberType = member.find('type').text
            memberSuffix = member.get('suffix')

            if not memberSuffix or not '[' in memberSuffix:
                continue

            # For cases where the array is multi-dimensional
            memberSuffix = memberSuffix.replace('][', '*')

            outFile.write(
                '  for (uint32_t i = 0; i < {}; ++i) {{\n'.format(memberSuffix[1:-1]))

            if dataRoot.findall('structs/{}/'.format(memberType)):
                outFile.write(
                    '    if(compare_{0}(&s1->{1}[i], &s2->{1}[i]))\n'.format(memberType, memberName))
            else:
                outFile.write(
                    '    if(s1->{0}[i] != s2->{0}[i])\n'.format(memberName))
            outFile.write('      return false;\n')
            outFile.write('  }\n')

        outFile.write('\n  return true;\n')
        outFile.write('}\n')
        if guarded:
            outFile.write("#endif\n")

    # Footer
    outFile.write('\n#endif // VK_STRUCT_COMPARE_CONFIG_MAIN')
    outFile.write("""
#ifdef __cplusplus
}
#endif
""")
    outFile.write('\n#endif // VK_STRUCT_COMPARE_H\n')


if __name__ == "__main__":
    main(sys.argv[1:])
