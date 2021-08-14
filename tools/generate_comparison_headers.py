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

    # Get the start/end versions
    firstVersion = data['root']['first']
    lastVersion = data['root']['last']

    # Common header
    with open("common_header.txt") as fd:
        outFile.write(fd.read())
        outFile.write('\n')
    
    # Specific Header
    outFile.write("""#ifndef VK_STRUCT_COMPARE_HPP
#define VK_STRUCT_COMPARE_HPP

/*  USAGE:
    To use, include this header where the declarations for the boolean checks are required.

    On *ONE* compilation unit, include the definition of `#define VK_STRUCT_COMPARE_CONFIG_MAIN`
    so that the definitions are compiled somewhere following the one definition rule.
*/

#include <vulkan/vulkan.h>
""")

    # static_asserts
    outFile.writelines(["\nstatic_assert(VK_HEADER_VERSION >= ", root['first'], ", \"VK_HEADER_VERSION is from before the supported range.\");\n"])
    outFile.writelines(["static_assert(VK_HEADER_VERSION <= ", root['last'], ", \"VK_HEADER_VERSION is from after the supported range.\");\n"])

    # Per-struct function declarations
    structs = root['structs']
    for it in structs:
        structName = str(it)
        guarded = False
        if structs[it]['first'] != firstVersion:
            guarded = True
            outFile.writelines(['\n#if VK_HEADER_VERSION >= ', structs[it]['first']])
        if structs[it]['last'] != lastVersion:
            if guarded:
                # If already started, append to it
                outFile.writelines([' && VK_HEADER_VERSION <= ', structs[it]['last']])
            else:
                guarded = True
                outFile.writelines(['\n#if VK_HEADER_VERSION <= ', structs[it]['last']])
        if 'platforms' in structs[it]:
            if isinstance(structs[it]['platforms'], list):
                for platform in structs[it]['platforms']:
                    if guarded:
                        # If already started, append to it
                        outFile.writelines([' && ', str(platform)])
                    else:
                        guarded = True
                        outFile.writelines(['\n#if ', str(platform)])
            else:
                if guarded:
                    # If already started, append to it
                    outFile.writelines([' && ', structs[it]['platforms']])
                else:
                    guarded = True
                    outFile.writelines(['\n#if ', structs[it]['platforms']])
        outFile.writelines(['\nbool compare_', structName, '(', structName, ' const *s1, ', structName, ' const* s2);\n'])
        if guarded:
            outFile.write("#endif\n")

    # Definitions
    outFile.write('\n#ifdef VK_STRUCT_COMPARE_CONFIG_MAIN\n')

    for it in structs:
        structName = str(it)
        guarded = False
        if structs[it]['first'] != firstVersion:
            guarded = True
            outFile.writelines(['\n#if VK_HEADER_VERSION >= ', structs[it]['first']])
        if structs[it]['last'] != lastVersion:
            if guarded:
                # If already started, append to it
                outFile.writelines([' && VK_HEADER_VERSION <= ', structs[it]['last']])
            else:
                guarded = True
                outFile.writelines(['\n#if VK_HEADER_VERSION <= ', structs[it]['last']])
        if 'platforms' in structs[it]:
            if isinstance(structs[it]['platforms'], list):
                for platform in structs[it]['platforms']:
                    if guarded:
                        # If already started, append to it
                        outFile.writelines([' && ', str(platform)])
                    else:
                        guarded = True
                        outFile.writelines(['\n#if ', str(platform)])
            else:
                if guarded:
                    # If already started, append to it
                    outFile.writelines([' && ', structs[it]['platforms']])
                else:
                    guarded = True
                    outFile.writelines(['\n#if ', structs[it]['platforms']])
        outFile.writelines(['\nbool compare_', structName, '(', structName, ' const *s1, ', structName, ' const* s2) {\n'])

        if not structs[it]['members'] is None:
            for member in structs[it]['members']:
                print(member)
        
        outFile.write('  return true;\n')
        outFile.write('}\n')
        if guarded:
            outFile.write("#endif\n")

    # Footer
    outFile.write('\n#endif // VK_STRUCT_COMPARE_CONFIG_MAIN')
    outFile.write('\n#endif // VK_STRUCT_COMPARE_HPP\n')
    

if __name__ == "__main__":
    main(sys.argv[1:])