#!/usr/bin/env python3

import sys, getopt
import xmltodict

def guardStruct(struct, outFile, firstVersion, lastVersion):
    guarded = False

    if struct['first'] != firstVersion:
        guarded = True
        outFile.writelines(['\n#if VK_HEADER_VERSION >= ', struct['first']])
    if struct['last'] != lastVersion:
        if guarded:
            # If already started, append to it
            outFile.writelines([' && VK_HEADER_VERSION <= ', struct['last']])
        else:
            guarded = True
            outFile.writelines(['\n#if VK_HEADER_VERSION <= ', struct['last']])
    if 'platforms' in struct:
        if isinstance(struct['platforms'], list):
            for platform in struct['platforms']:
                if guarded:
                    # If already started, append to it
                    outFile.writelines([' && ', str(platform)])
                else:
                    guarded = True
                    outFile.writelines(['\n#if ', str(platform)])
        else:
            if guarded:
                # If already started, append to it
                outFile.writelines([' && ', struct['platforms']])
            else:
                guarded = True
                outFile.writelines(['\n#if ', struct['platforms']])

    return guarded

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

    # Special comparison of unknown VkStruct
    outFile.write('\nbool compare_VkBaseStruct(void const* s1, void const*s2, bool deepCompare);\n')

    # Per-struct function declarations
    structs = root['structs']
    for it in structs:
        structName = str(it)
        guarded = guardStruct(structs[it], outFile, firstVersion, lastVersion)
        outFile.writelines(['\nbool compare_', structName, '(', structName, ' const *s1, ', structName, ' const* s2, bool deepCompare);\n'])
        if guarded:
            outFile.write("#endif\n")

    # Definitions
    outFile.write('\n//#ifdef VK_STRUCT_COMPARE_CONFIG_MAIN\n')

    # Unknown struct
    outFile.write("""\nbool compare_VkBaseStruct(void const*s1, void const*s2, bool deepCompare) {
  VkBaseInStructure const* pTemp1 = static_cast<VkBaseInStructure const*>(s1);
  VkBaseInStructure const* pTemp2 = static_cast<VkBaseInStructure const*>(s2);

  if(pTemp1->sType != pTemp2->sType)
      return false;

  switch(pTemp1->sType) {""")

    for it in structs:
        structName = str(it)
        struct = structs[it]
        if not struct['members'] is None and 'sType' in struct['members'] and 'values' in struct['members']['sType']:
            guarded = guardStruct(struct, outFile, firstVersion, lastVersion)
            outFile.writelines(['\n  case ', struct['members']['sType']['values'], ':\n'])
            outFile.writelines(['    return compare_', structName, '((', structName, ' const*)s1, (', structName, ' const*)s2, deepCompare);\n'])
            if guarded:
                outFile.write('#endif\n')

    outFile.write("""
  default:
    // Can't figure out, maybe a guarded/disabled one?
    return false;
  }
}
""")

    # All defined structs
    for it in structs:
        structName = str(it)
        guarded = guardStruct(structs[it], outFile, firstVersion, lastVersion)
        outFile.writelines(['\nbool compare_', structName, '(', structName, ' const *s1, ', structName, ' const* s2, bool deepCompare) {'])

        # First, rule out the basic types (no pointers/sType/arrays)
        started = False
        if not structs[it]['members'] is None:
            for memberIt in structs[it]['members']:
                memberName = str(memberIt)
                if memberName == 'sType':
                    continue
                member = structs[it]['members'][memberIt]
                if 'len' in member:
                    continue
                if 'text' in member:
                    if '*' in member['text']:
                        continue
                    if '[' in member['text']:
                        continue
                
                if not started:
                    outFile.write('\n  if (\n')
                    started = True
                else:
                    outFile.write(' ||\n')
                if member['type'] in structs:
                    outFile.writelines(['  (compare_', member['type'], '(&s1->', memberName, ', &s2->', memberName, ', deepCompare))'])
                else:
                    outFile.writelines(['  (s1->', memberName, ' != s2->', memberName, ')'])
        if started:
            outFile.write(')\n    return false;\n\n')

        # Now for local arrays
        if not structs[it]['members'] is None:
            for memberIt in structs[it]['members']:
                memberName = str(memberIt)
                member = structs[it]['members'][memberIt]
                if not 'text' in member:
                    continue

                if '[]' in member['text']: # Array using enum value
                    outFile.writelines(['  for(uint32_t i = 0; i < ', member['enum'], '; ++i) {\n'])
                    if member['type'] in structs:
                        outFile.writelines(['    if(compare_', member['type'], '(&s1->', memberName, '[i], &s2->', memberName, '[i], deepCompare))\n'])
                    else:
                        outFile.writelines(['    if(s1->', memberName, '[i] != s2->', memberName, '[i])\n'])
                    outFile.writelines(['      return false;\n'])
                    outFile.writelines(['  }\n'])
                elif '[' in member['text']: # 
                    outFile.writelines(['  for (uint32_t i = 0; i < ', member['text'][1:-1], '; ++i) {\n'])
                    if member['type'] in structs:
                        outFile.writelines(['    if(compare_', member['type'], '(&s1->', memberName, '[i], &s2->', memberName, '[i], deepCompare))\n'])
                    else:
                        outFile.writelines(['    if(s1->', memberName, '[i] != s2->', memberName, '[i])\n'])
                    outFile.writelines(['      return false;\n'])
                    outFile.writelines(['  }\n'])
        
        # Now for non-local data
        started = False
        if not structs[it]['members'] is None:
            for memberIt in structs[it]['members']:
                memberName = str(memberIt)
                member = structs[it]['members'][memberIt]
                if not 'text' in member or not '*' in member['text']:
                    continue

                if not started:
                    outFile.write('\n  if(deepCompare) {\n')
                    started = True

                if 'len' in member:
                    # There's a count or something for this member
                    outFile.writelines(['    for (uint32_t i = 0; i < ', member['len'], '; ++i) {\n'])
                    if member['type'] in structs:
                        outFile.writelines(['      if(compare_', member['type'], '(&s1->', memberName, '[i], &s2->', memberName, '[i], deepCompare))\n'])
                    else:
                        outFile.writelines(['      if(s1->', memberName, '[i] != s2->', memberName, '[i])\n'])
                    outFile.writelines('        return false;\n')
                    outFile.write('    }\n')
                else:
                    # Single pointer member
                    if memberName == 'pNext':
                        outFile.write("""    if(s1->pNext != s2->pNext) {
      if(s1->pNext == nullptr || s2->pNext == nullptr)
        return false;
      if(!compare_VkNextStruct(s1->pNext, s2->pNext))
        return false;
    }
""")

        if started:
            outFile.write('  }')
        
        outFile.write('\n  return true;\n')
        outFile.write('}\n')
        if guarded:
            outFile.write("#endif\n")

    # Footer
    outFile.write('\n//#endif // VK_STRUCT_COMPARE_CONFIG_MAIN')
    outFile.write('\n#endif // VK_STRUCT_COMPARE_HPP\n')
    

if __name__ == "__main__":
    main(sys.argv[1:])