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


def getExternalDataMembers(members):
    externalMembers = []
    for member in members:
        typeSuffix = member.find('type').get('suffix')
        if not typeSuffix is None and '*' in typeSuffix:
            externalMembers.append(member)

    return externalMembers


def processMultiMember(member, suffix, dataRoot, lenSplit, availableVars, outFile):
    if len(availableVars) == 0:
        print('Error, ran out of nestable variable names, add more!')
        sys.exit(1)
    curVar = availableVars[0]
    count = lenSplit[0]
    typeName = member.find('type').text
    typeNode = dataRoot.find('structs/' + typeName)

    if len(lenSplit) > 1:
        outFile.write(
            '    for(uint32_t {0} = 0; {0} < pData->{1}{2}; ++{0}) {{\n'.format(curVar, count, suffix))
        processMultiMember(member, '[' + curVar + ']', dataRoot,
                           lenSplit[1:], availableVars[1:], outFile)
        outFile.write('    }\n')
    else:
        if not typeNode is None:
            # A Vulkan struct, cleanup first
            outFile.write(
                '    if (pData->{}{} != NULL) {{\n'.format(member.tag, suffix))
            outFile.write(
                '    for(uint32_t {0} = 0; {0} < pData->{1}{2}; ++{0})\n'.format(curVar, count, suffix))
            outFile.write(
                '            cleanup_{}(&pData->{}{}[{}]);\n'.format(typeName, member.tag, suffix, curVar))
            outFile.write('    }\n')
    outFile.write('    free((void*)pData->{}{});\n'.format(member.tag, suffix))


def main(argv):
    inputFile = ''
    yamlFile = ''
    outputFile = ''

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

    # Common Header
    with open("common_header.txt") as fd:
        outFile.write(fd.read())
        outFile.write('\n')

    # Specific Header
    outFile.write("""#ifndef VK_STRUCT_CLEANUP_H
#define VK_STRUCT_CLEANUP_H

/*  USAGE:
    To use, include this header where the declarations for the boolean checks are required.

    On *ONE* compilation unit, include the definition of:
    #define VK_STRUCT_CLEANUP_CONFIG_MAIN

    so that the definitions are compiled somewhere following the one definition rule.
*/

#ifdef __cplusplus
extern "C" {
#endif

#include <vulkan/vulkan.h>
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

    # Generic struct catchall
    outFile.write('\nvoid cleanup_vk_struct(void const* pData);\n')

    # Dynamic Declarations
    currentVersion = int(firstVersion)
    while currentVersion <= int(lastVersion):
        for struct in structs:
            if struct.get('first') != str(currentVersion):
                continue
            name = struct.tag
            if name == 'VkBaseOutStructure' or name == 'VkBaseInStructure':
                continue
            if name in yamlData:
                continue
            outFile.write('\n')
            guarded = guardStruct(struct, firstVersion, lastVersion, outFile)
            members = getExternalDataMembers(struct.findall('members/'))
            # If there's not pointer members to delete, leave an empty inlinable function instead
            if len(members) == 0:
                outFile.write(
                    'inline void cleanup_{0}({0} const* pData) {{}}\n'.format(name))
            else:
                outFile.write(
                    'void cleanup_{0}({0} const* pData);\n'.format(name))
            if guarded:
                outFile.write('#endif\n')
        currentVersion += 1

    # Definition Header
    outFile.write("""
#ifdef VK_STRUCT_CLEANUP_CONFIG_MAIN

#include <stdlib.h>
""")

    # Definitions
    outFile.write("""
void cleanup_vk_struct(void const* pData) {
    VkBaseInStructure const* pTemp = (VkBaseInStructure const*)pData;
""")
    first = True
    currentVersion = int(firstVersion)
    while currentVersion <= int(lastVersion):
        for struct in structs:
            if struct.get('first') != str(currentVersion):
                continue
            if struct.tag in yamlData:
                continue

            sTypeValue = struct.find('members/sType/value')
            # Only deal with structs that have defined sType
            if sTypeValue is None:
                continue

            outFile.write('\n')
            guarded = guardStruct(struct, firstVersion, lastVersion, outFile)
            outFile.write(
                'if (pTemp->sType =={}) {{\n'.format(sTypeValue.text))
            outFile.write(
                '        cleanup_{0}(({0} const*)pData);\n'.format(struct.tag))
            outFile.write('        return;\n    }')
            if guarded:
                outFile.write('#endif\n')
        currentVersion += 1

    outFile.write('}\n')

    # Dynamic Definitions
    currentVersion = int(firstVersion)
    while currentVersion <= int(lastVersion):
        for struct in structs:
            if struct.get('first') != str(currentVersion):
                continue

            name = struct.tag
            if name == 'VkBaseOutStructure' or name == 'VkBaseInStructure':
                continue
            if name in yamlData:
                continue
            members = getExternalDataMembers(struct.findall('members/'))

            outFile.write('\n')
            guarded = guardStruct(struct, firstVersion, lastVersion, outFile)
            if len(members) == 0:
                outFile.write(
                    'extern inline void cleanup_{0}({0} const* pData);\n'.format(name))
            else:
                outFile.write(
                    'void cleanup_{0}({0} const* pData) {{'.format(name))

                membersNode = struct.find('members')
                for member in members:
                    typeName = member.find('type').text
                    typeNode = dataRoot.find('structs/' + typeName)
                    outFile.write('\n')

                    guardedMember = guardStruct(
                        member, membersNode.get('first'), membersNode.get('last'), outFile)
                    if member.get('len') is None:
                        # Single member, no iteration or counting business here
                        outFile.write('    // {}\n'.format(member.tag))
                        if member.tag == 'pNext':
                            outFile.write('    if (pData->pNext != NULL)\n')
                            outFile.write(
                                '        cleanup_vk_struct(pData->pNext);\n')
                        elif not typeNode is None:
                            # A Vulkan struct, cleanup first
                            outFile.write(
                                '    if (pData->{0} != NULL)\n'.format(member.tag))
                            outFile.write(
                                '        cleanup_{0}(pData->{1});\n'.format(typeName, member.tag))
                        outFile.write(
                            '    free((void *)pData->{0});\n'.format(member.tag))

                    else:
                        # Multiple member or levels of indirection
                        outFile.write(
                            '    // {0} - {1}\n'.format(member.tag, member.get('len')))
                        processMultiMember(member, '', dataRoot,
                                           member.get('len').split(','), 'ijklmn', outFile)
                    if guardedMember:
                        outFile.write('#endif\n')
                outFile.write('}\n')

            if guarded:
                outFile.write('#endif\n')
        currentVersion += 1

    # Footer
    outFile.write('\n#endif // VK_STRUCT_CLEANUP_CONFIG_MAIN\n')
    outFile.write("""
#ifdef __cplusplus
}
#endif
""")
    outFile.write('\n#endif // VK_STRUCT_CLEANUP_H\n')


if __name__ == "__main__":
    main(sys.argv[1:])
