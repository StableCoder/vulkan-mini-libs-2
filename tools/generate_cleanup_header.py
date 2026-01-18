#!/usr/bin/env python3

# Copyright (C) 2022-2025 George Cave.
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import gen_common
import json
import sys
import xml.etree.ElementTree as ET


def get_define_guards(type_data, first_version, last_version):
    guard_sets = []

    # Guard based on required definitions
    if 'requires' in type_data:
        for require_variant, require_data in type_data['requires'].items():
            guard = ''
            check_started = False

            # check version numbers first
            if require_data['first'] != first_version:
                guard += 'VK_HEADER_VERSION >= {}'.format(require_data['first'])
                check_started = True

            if require_data['last'] != last_version:
                if check_started:
                    guard += ' && '
                guard += 'VK_HEADER_VERSION <= {}'.format(require_data['last'])
                check_started = True

            # add defines
            for define in require_data['defines']:
                if check_started:
                    guard += ' && '
                # Brackets around OR defines
                if ',' in define:
                    guard += '({})'.format(define.replace(',', ' || '))
                else:
                    guard += define
                check_started = True

            if guard:
                guard_sets.append(guard)
    else:
        # do a guard based only on version numbers for the struct
        firstCheck = type_data['first']
        lastCheck = type_data['last']
        guard = ''

        # Guard check for first version
        if firstCheck != first_version:
            guard = 'VK_HEADER_VERSION >= {}'.format(firstCheck)

        # Guard check for last version
        if lastCheck != last_version:
            if guard:
                # If already started, append to it
                guard += ' && '
            guard += 'VK_HEADER_VERSION <= {}'.format(lastCheck)
        if guard:
            guard_sets.append(guard)

    return guard_sets


def output_define_guard(guard_list, out_file):
    if guard_list:
        out_file.write('#if ')
        if len(guard_list) == 1:
            out_file.write('{}'.format(guard_list[0]))
        else:
            for idx, guard in enumerate(guard_list):
                if idx > 0:
                    out_file.write(' || ')
                out_file.write('({})'.format(guard))
        out_file.write('\n')


def process_multi_member(member, member_data, iteration, suffix, available_characters, data, out_file):
    if len(available_characters) == 0:
        print('ERROR: ran out of nestable variable names, add more!')
        sys.exit(1)
    iter_character = available_characters[0]

    if len(iteration) > 1:
        # more than one level of indirection
        if iteration[0].isdigit():
            out_file.write('    for (size_t {0} = 0; {0} < {1}; ++{0}) {{\n'.format(iter_character, iteration[0]))
        else:
            out_file.write('    for (size_t {0} = 0; {0} < pData->{1}; ++{0}) {{\n'.format(iter_character, iteration[0]))

        process_multi_member(member, member_data, iteration[1:], '{}[{}]'.format(suffix, iter_character), available_characters[1:], data, out_file)
        out_file.write('    }\n')

    else:
        # last level of indirection
        if member_data['type'] in data['structs']:
            # if an API-related structure type, clean it up
            if iteration[0].isdigit():
                out_file.write('for (size_t {0} = 0; {0} < {1}; ++{0}) {{\n'.format(iter_character, iteration[0]))
            else:
                out_file.write('for (size_t {0} = 0; {0} < pData->{1}{2}; ++{0}) {{\n'.format(iter_character, iteration[0], suffix))

            out_file.write('''\
                cleanup_{2}(&pData->{3}{1}[{0}]);
            }}
            '''.format(iter_character, suffix, member_data['type'], member))

    out_file.write('    free((void *)pData->{}{});\n'.format(member, suffix))


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input',
                        help='Input JSON API cache file',
                        required=True)
    parser.add_argument('-o', '--output',
                        help='Output file to write to',
                        required=True)
    args = parser.parse_args()

    try:
        json_file = open(args.input, 'r')
        data = json.load(json_file)
    except:
        print("Error: Could not open input file: ", args.input)
        sys.exit(1)

    # sort struct data
    data['structs'] = dict(sorted(data['structs'].items()))

    # Get first/last versions
    first_version = data['api']['first']
    last_version = data['api']['last']

    out_file = open(args.output, "w")

    # Common Header
    gen_common.writeHeader(out_file)

    # Specific Header
    out_file.write("""\
#ifndef VK_STRUCT_CLEANUP_H
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

    # static asserts for minimum version
    out_file.write('''
#ifdef __cplusplus
static_assert(VK_HEADER_VERSION >= {0}, "VK_HEADER_VERSION is lower than the minimum supported version (v{0})");
#else
_Static_assert(VK_HEADER_VERSION >= {0}, "VK_HEADER_VERSION  is lower than the minimum supported version (v{0})");
#endif
'''.format(first_version))

    # warnings for above max generated version
    out_file.write('''
#if VK_HEADER_VERSION > {0}
#if _MSC_VER
#pragma message(__FILE__ ": warning: VK_HEADER_VERSION is higher than what the header fully supports (v{0})")
#else
#warning "VK_HEADER_VERSION is higher than what the header fully supports (v{0})"
#endif
#endif
'''.format(last_version))

    # Generic struct catchall
    out_file.write('\nvoid cleanup_vk_struct(void const* pData);\n')

    # Dynamic Declarations
    for struct, variants in data['structs'].items():
        if struct == 'VkBaseInStructure' or struct == 'VkBaseOutStructure':
            continue

        sorted_variants = dict(sorted(variants.items(), key=lambda item: item[1]['first']))
        for variant, struct_data in sorted_variants.items():
            out_file.write('\n')
            
            struct_guards = get_define_guards(struct_data, first_version, last_version)
            output_define_guard(struct_guards, out_file)

            # Normal function declaration
            out_file.write('void cleanup_{0}({0} const* pData);\n'.format(struct))
            if struct_guards:
                out_file.write('#endif\n')

    # Definition Header
    out_file.write("""
#ifdef VK_STRUCT_CLEANUP_CONFIG_MAIN

#include <stdlib.h>
""")

    # Definitions
    out_file.write("""
void cleanup_vk_struct(void const* pData) {
    VkBaseInStructure const* pTemp = (VkBaseInStructure const*)pData;
""")

    for struct, variants in data['structs'].items():
        if struct == 'VkBaseInStructure' or struct == 'VkBaseOutStructure':
            continue

        sorted_variants = dict(sorted(variants.items(), key=lambda item: item[1]['first']))
        for variant, struct_data in sorted_variants.items():

            # only deal with structs that have defined sType
            if not 'members' in struct_data or 'sType' not in struct_data['members']:
                continue
            sTypeValue = struct_data['members']['sType']['value']

            out_file.write('\n')
            
            struct_guards = get_define_guards(struct_data, first_version, last_version)
            output_define_guard(struct_guards, out_file)

            out_file.write(
                'if (pTemp->sType =={}) {{\n'.format(sTypeValue))
            out_file.write(
                '        cleanup_{0}(({0} const*)pData);\n'.format(struct))
            out_file.write('        return;\n    }')
            if struct_guards:
                out_file.write('\n#endif\n')

    out_file.write('}\n')


    # Dynamic Definitions
    for struct, variants in data['structs'].items():
        if struct == 'VkBaseInStructure' or struct == 'VkBaseOutStructure':
            continue

        sorted_variants = dict(sorted(variants.items(), key=lambda item: item[1]['first']))
        for variant, struct_data in sorted_variants.items():
            out_file.write('\n')
            
            struct_guards = get_define_guards(struct_data, first_version, last_version)
            output_define_guard(struct_guards, out_file)

            if 'alias' in struct_data:
                # for an alias struct, use the alias's data
                struct_data = data['structs'][struct_data['alias']['name']][struct_data['alias']['hash']]
            
            if not 'members' in struct_data:
                # if there are no members, leave an empty function
                out_file.write(
                    'void cleanup_{0}({0} const* pData) {{}}\n'.format(struct))
            else:
                # there are members, deal with them
                out_file.write(
                    'void cleanup_{0}({0} const* pData) {{'.format(struct))

                for member, member_data in struct_data['members'].items():
                    if not 'suffix' in member_data or not '*' in member_data['suffix']:
                        continue

                    member_type = member_data['type']

                    if not 'len' in member_data:
                        # single item
                        out_file.write('\n    // {}\n'.format(member))

                        if member == 'pNext':
                            # pNext could be anything, use dynamic call
                            out_file.write('''\
                                if (pData->pNext != NULL)
                                    cleanup_vk_struct(pData->pNext);
                                ''')
                            
                        elif member_type in data['structs']:
                            # a Vulkan struct type
                            out_file.write('''\
                                if (pData->{0} != NULL)
                                    cleanup_{1}(pData->{0});
                                '''.format(member, member_type))

                        out_file.write('    free((void*)pData->{});\n'.format(member))
                    else:
                        # multiple items
                        out_file.write('\n    // {} - {}\n'.format(member, member_data['len']))
                        process_multi_member(member, member_data, member_data['len'].split(','), '', 'ijklmn', data, out_file)

                out_file.write('}\n')

            if struct_guards:
                out_file.write('#endif\n')

    # Footer
    out_file.write('\n#endif // VK_STRUCT_CLEANUP_CONFIG_MAIN\n')
    out_file.write("""
#ifdef __cplusplus
}
#endif
""")
    out_file.write('\n#endif // VK_STRUCT_CLEANUP_H\n')


if __name__ == "__main__":
    main(sys.argv[1:])
