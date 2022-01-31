#!/usr/bin/env python3

import sys
import getopt
import yaml
import xml.etree.ElementTree as ET


def guardStruct(struct, firstVersion, lastVersion, outFile):
    guarded = False
    # Guard check for first version
    if struct.get('first') != firstVersion:
        guarded = True
        outFile.writelines(
            ['#if VK_HEADER_VERSION >= ', struct.get('first')])
    # Guard check for last version
    if struct.get('last') != lastVersion:
        if guarded:
            # If already started, append to it
            outFile.writelines(
                [' && VK_HEADER_VERSION <= ', struct.get('last')])
        else:
            guarded = True
            outFile.writelines(
                ['#if VK_HEADER_VERSION <= ', struct.get('last')])
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
            if platformed:
                outFile.write(' || {}'.format(platform.tag))
            else:
                platformed = True
                outFile.write(platform.tag)
        if len(platforms) > 1:
            outFile.write(')')

    if guarded:
        outFile.write('\n')
    return guarded


def main(argv):
    inputFile = ''
    yamlFile = ''
    outputFile = ''
    data = dict()

    try:
        opts, args = getopt.getopt(argv, 'i:y:o:', [])
    except getopt.GetoptError:
        print('Error parsing options')
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-i':
            inputFile = arg
        elif opt == '-y':
            yamlFile = arg
        elif opt == '-o':
            outputFile = arg

    if(inputFile == ''):
        print("Error: No Vulkan XML file specified")
        sys.exit(1)
    if(yamlFile == ''):
        print("Error: No Yaml exclude file specified")
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

    try:
        with open(yamlFile, 'r') as file:
            yamlData = yaml.safe_load(file)
    except:
        print("Error: Could not open Yaml file: ", yamlFile)
        sys.exit(1)

    # Get first/last versions
    firstVersion = dataRoot.get('first')
    lastVersion = dataRoot.get('last')

    structs = dataRoot.findall('structs/')

    outFile = open(outputFile, "w")

    # Common header
    with open("common_header.txt") as fd:
        outFile.write(fd.read())
        outFile.write('\n')

    # Specific Header
    outFile.write("""#ifndef VK_STRUCT_COMPARE_H
#define VK_STRUCT_COMPARE_H

/*  USAGE:
    To use, include this header where the declarations for the boolean checks are required.

    #define VK_STRUCT_COMPARE_CONFIG_MAIN`
    On *ONE* compilation unit, include the definition of `
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
    outFile.writelines(["static_assert(VK_HEADER_VERSION >= ", firstVersion,
                        ", \"VK_HEADER_VERSION is from before the supported range.\");\n"])
    outFile.writelines(["static_assert(VK_HEADER_VERSION <= ", lastVersion,
                        ", \"VK_HEADER_VERSION is from after the supported range.\");\n"])
    outFile.write('#else\n')
    outFile.writelines(["_Static_assert(VK_HEADER_VERSION >= ", firstVersion,
                        ", \"VK_HEADER_VERSION is from before the supported range.\");\n"])
    outFile.writelines(["_Static_assert(VK_HEADER_VERSION <= ", lastVersion,
                        ", \"VK_HEADER_VERSION is from after the supported range.\");\n"])
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
        outFile.writelines(['bool compare_', structName, '(', structName,
                           ' const *s1, ', structName, ' const* s2);\n'])
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
        outFile.writelines(['bool compare_', structName, '(', structName,
                           ' const *s1, ', structName, ' const* s2) {'])

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
                outFile.writelines(
                    ['!compare_', memberType, '(&s1->', memberName, ', &s2->', memberName, ') ||\n'])
            else:
                outFile.writelines(
                    ['(s1->', memberName, ' != s2->', memberName, ') ||\n'])
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

            outFile.writelines(
                ['  for (uint32_t i = 0; i < ', memberSuffix[1:-1], '; ++i) {\n'])

            if dataRoot.findall('structs/{}/'.format(memberType)):
                outFile.writelines(
                    ['    if(compare_', memberType, '(&s1->', memberName, '[i], &s2->', memberName, '[i]))\n'])
            else:
                outFile.writelines(
                    ['    if(s1->', memberName, '[i] != s2->', memberName, '[i])\n'])
            outFile.writelines(['      return false;\n'])
            outFile.writelines(['  }\n'])

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
