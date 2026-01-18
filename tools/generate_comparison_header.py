#!/usr/bin/env python3

# Copyright (C) 2022-2025 George Cave.
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import gen_common
import json
import re
import sys
import xml.etree.ElementTree as ET

verified_voids = []

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


def string_found(string1, string2):
    if re.search(r"\b" + re.escape(string1) + r"\b", string2):
        return True
    return False


def process_multi_member(member, member_data, struct_data, iteration, suffix, available_characters, data, out_file):
    if len(available_characters) == 0:
        print('ERROR: ran out of nestable variable names, add more!')
        sys.exit(1)
    iter_character = available_characters[0]
    this_iteration = iteration[0]

    if len(iteration) > 1:
        # more than one level of indirection
        if this_iteration.isdigit():
            out_file.write('  for (size_t {0} = 0; {0} < {1}; ++{0}) {{\n'.format(iter_character, this_iteration))
        else:
            out_file.write('  for (size_t {0} = 0; {0} < s1->{1}; ++{0}) {{\n'.format(iter_character, this_iteration))

        process_multi_member(member, member_data, struct_data, iteration[1:], '{}[{}]'.format(suffix, iter_character), available_characters[1:], data, out_file)
        out_file.write('}\n')

    else:
        # last level of indirection
        if member_data['type'] in data['structs']:
            # if an API structure...
            if this_iteration.isdigit():
                # if a specified numeric count
                out_file.write('for (size_t {0} = 0; {0} < {1}; ++{0}) {{\n'.format(iter_character, this_iteration))
            else:
                # a count specified by another member
                out_file.write('for (size_t {0} = 0; {0} < s1->{1}{2}; ++{0}) {{\n'.format(iter_character, this_iteration, suffix))

        else:
            for struct_member, struct_member_data in struct_data['members'].items():
                if string_found(struct_member, this_iteration):
                    this_iteration = this_iteration.replace(struct_member, 's1->{}'.format(struct_member))
                    if member_data['type'] != 'void':
                        this_iteration = '({}) * sizeof({})'.format(this_iteration, member_data['type'])

            if member_data['type'] == 'char':
                if this_iteration == 'null-terminated':
                    if '*' in member_data['suffix']:
                        # string is on the heap, check for null pointers
                        out_file.write('if (s1->{0}{1} != s2->{0}{1} && (s1->{0}{1} == NULL || s2->{0}{1} == NULL || strcmp(s1->{0}{1}, s2->{0}{1}) != 0))\n  return false;\n'.format(member, suffix))
                    else:
                        # string is local, check against max string length
                        max_str_len = member_data['suffix'].replace('[', '')
                        max_str_len = max_str_len.replace(']', '')
                        out_file.write('if (strncmp(s1->{0}{1}, s2->{0}{1}, {2}) != 0)\n  return false;\n'.format(member, suffix, max_str_len))
                else:
                    print('ERROR: Unsupported character comparison of {}'.format(member))
                    sys.exit(1)

            elif member_data['type'] == 'void':
                # special hardcoded items
                if struct == 'VkLayerSettingEXT' and member == 'pValues':
                    out_file.write('''\
                    if (s1->{0}{1} != s2->{0}{1}) {{
                        if (s1->{0}{1} == NULL || s2->{0}{1} == NULL)
                            return false;

                        switch (s1->type) {{
                          case VK_LAYER_SETTING_TYPE_BOOL32_EXT:
                            if (memcmp(s1->{0}{1}, s2->{0}{1}, {2} * sizeof(VkBool32)) != 0)
                                return false;
                          case VK_LAYER_SETTING_TYPE_INT32_EXT:
                            if (memcmp(s1->{0}{1}, s2->{0}{1}, {2} * sizeof(int32_t)) != 0)
                                return false;
                          case VK_LAYER_SETTING_TYPE_INT64_EXT:
                            if (memcmp(s1->{0}{1}, s2->{0}{1}, {2} * sizeof(int64_t)) != 0)
                                return false;
                          case VK_LAYER_SETTING_TYPE_UINT32_EXT:
                            if (memcmp(s1->{0}{1}, s2->{0}{1}, {2} * sizeof(uint32_t)) != 0)
                                return false;
                          case VK_LAYER_SETTING_TYPE_UINT64_EXT:
                            if (memcmp(s1->{0}{1}, s2->{0}{1}, {2} * sizeof(uint64_t)) != 0)
                                return false;
                          case VK_LAYER_SETTING_TYPE_FLOAT32_EXT:
                            if (memcmp(s1->{0}{1}, s2->{0}{1}, {2} * sizeof(float)) != 0)
                                return false;
                          case VK_LAYER_SETTING_TYPE_FLOAT64_EXT:
                            if (memcmp(s1->{0}{1}, s2->{0}{1}, {2} * sizeof(double)) != 0)
                                return false;
                          case VK_LAYER_SETTING_TYPE_STRING_EXT:
                            if (strncmp((char const *)s1->{0}{1}, (char const *) s2->{0}{1}, {2}) != 0)
                                return false;
                          default:
                            break;
                        }}
                    }}\n\n'''.format(member, suffix, this_iteration))
                    return

                # fallback to generic file-defined items
                for item in verified_voids:
                    if item['struct'] == struct and item['member'] == member:
                        out_file.write('  if (s1->{0}{1} != s2->{0}{1} && (s1->{0}{1} == NULL || s2->{0}{1} == NULL || memcmp(s1->{0}{1}, s2->{0}{1}, {2}) != 0))\n  return false;\n'.format(member, suffix, this_iteration))
                        return

                print('Error: Unverified void type, investigate {} :: {}'.format(struct, member))
                sys.exit(1)

            else:
                if '*' in member_data['suffix']:
                    out_file.write('  if (s1->{0}{1} != s2->{0}{1} && (s1->{0}{1} == NULL || s2->{0}{1} == NULL || memcmp(s1->{0}{1}, s2->{0}{1}, {2}) != 0))\n  return false;\n'.format(member, suffix, this_iteration))
                else:
                    out_file.write('  if (memcmp(&s1->{0}{1}, &s2->{0}{1}, {2}) != 0)\n  return false;\n'.format(member, suffix, this_iteration))

# main
data = dict()

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input',
                        help='Input JSON API cache file',
                        required=True)
parser.add_argument('-o', '--output',
                        help='Output file to write to',
                        required=True)
parser.add_argument('-v', '--verified-void',
                        help='File containing verified void comparisons',
                        required=True)
args = parser.parse_args()

try:
    json_file = open(args.input, 'r')
    data = json.load(json_file)
except:
    print("Error: Could not open input file: ", args.input)
    sys.exit(1)

try:
    verified_voids_file = open(args.verified_void, 'r')
    for line in verified_voids_file:
        # skip comment lines
        if line.startswith('#'):
            continue
        line_data = line.split(' ')
        if len(line_data) != 2:
            print('Error: More than two items on  a verified voids file line "{}"'.format(line))
            sys.exit(1)
        verified_voids.append({
            'struct': line_data[0],
            'member': line_data[1].strip(),
        })
except:
    print('Error: Could not open verified-voids file: ', args.verified_void)
    sys.exit(1)

# sort struct data
data['structs'] = dict(sorted(data['structs'].items()))

# Get first/last versions
first_version = data['api']['first']
last_version = data['api']['last']

out_file = open(args.output, "w")

# Common header
gen_common.writeHeader(out_file)

# Specific Header
out_file.write("""#ifndef VK_STRUCT_COMPARE_H
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

# per-struct declarations
for struct, variants in data['structs'].items():
    if struct == 'VkBaseInStructure' or struct == 'VkBaseOutStructure':
        continue

    sorted_variants = dict(sorted(variants.items(), key=lambda item: item[1]['first']))
    for variant, struct_data in sorted_variants.items():
        out_file.write('\n')
        struct_guards = get_define_guards(struct_data, first_version, last_version)
        output_define_guard(struct_guards, out_file)
        out_file.write('bool compare_{0}({0} const *s1, {0} const *s2);\n'.format(struct))
        if struct_guards:
            out_file.write('#endif\n')

# definitions
out_file.write('\n#ifdef VK_STRUCT_COMPARE_CONFIG_MAIN\n')

out_file.write('\n#include <string.h>\n')

# all structs
for struct, variants in data['structs'].items():
    if struct == 'VkBaseInStructure' or struct == 'VkBaseOutStructure':
        continue

    sorted_variants = dict(sorted(variants.items(), key=lambda item: item[1]['first']))
    for variant, struct_data in sorted_variants.items():
        out_file.write('\n')
        struct_guards = get_define_guards(struct_data, first_version, last_version)
        output_define_guard(struct_guards, out_file)
        out_file.write('bool compare_{0}({0} const *s1, {0} const *s2) {{\n'.format(struct))

        while 'alias' in struct_data:
            # swap in the alias data until reach the end of the chain
            struct_data = data['structs'][struct_data['alias']['name']][struct_data['alias']['hash']]

        if not 'members' in struct_data:
            out_file.write('  return true;\n')
            out_file.write('}\n')
            if struct_guards:
                out_file.write('#endif\n')
            continue

        # first pass, only simple/local items
        compare_started = False
        for member, member_data in struct_data['members'].items():
            if 'suffix' in member_data and ('*' in member_data['suffix'] or '[' in member_data['suffix']):
                continue
            if member == 'sType' or member == 'pNext' or member_data['type'] in data['structs'] or member_data['type'] in data['unions']:
                continue
            member_data['proccessed'] = True

            if not compare_started:
                out_file.write('  // local, simple types\n')
                out_file.write('  if (')
            else:
                out_file.write(' || ')
            compare_started = True

            out_file.write('(s1->{0} != s2 ->{0})'.format(member))
        if compare_started:
            out_file.write(')')
            out_file.write('return false;\n\n')

        # second pass, local struct types
        compare_started = False
        for member, member_data in struct_data['members'].items():
            if 'proccessed' in member_data:
                continue
            if 'suffix' in member_data and ('*' in member_data['suffix'] or '[' in member_data['suffix']):
                continue
            if member == 'sType' or member == 'pNext' or member_data['type'] in data['unions']:
                continue
            member_data['proccessed'] = True

            if not compare_started:
                out_file.write('  // local, Vulkan struct types\n')
                out_file.write('  if (')
            else:
                out_file.write(' || ')
            compare_started = True

            out_file.write('!compare_{0}(&s1->{1}, &s2->{1})'.format(member_data['type'], member))
        if compare_started:
            out_file.write(')')
            out_file.write('return false;\n\n')

        # third pass, union types with no selector
        compare_started = False
        for member, member_data in struct_data['members'].items():
            if 'proccessed' in member_data:
                continue
            if 'suffix' in member_data and ('*' in member_data['suffix'] or '[' in member_data['suffix']):
                continue
            if member == 'sType' or member == 'pNext' or member_data['type'] in data['structs'] or 'selector' in member_data:
                continue
            member_data['proccessed'] = True

            if not member_data['type'].startswith('VkDeviceOrHostAddress') and member_data['type'] != 'VkClearValue' and member_data['type'] != 'VkClearColorValue':
                print("Error: Unhandled non-selector union type {}::{}".format(struct, member))
                sys.exit(1)

            if not compare_started:
                out_file.write('  // union types (no selector)\n')
                out_file.write('  if (')
            else:
                out_file.write(' || ')
            compare_started = True

            union_type = data['unions'][member_data['type']]
            out_file.write('memcmp(&s1->{0}, &s2->{0}, sizeof({1})) != 0'.format(member, member_data['type']))
        if compare_started:
            out_file.write(')\n    return false;\n\n')

        # fourth pass, union types with selector
        compare_started = False
        for member, member_data in struct_data['members'].items():
            if 'proccessed' in member_data:
                continue
            if 'suffix' in member_data and ('*' in member_data['suffix'] or '[' in member_data['suffix']):
                continue
            if member == 'sType' or member == 'pNext' or member_data['type'] in data['structs']:
                continue
            member_data['proccessed'] = True

            if not compare_started:
                out_file.write('  // union types (with selector)\n')
            compare_started = True

            union_data = data['unions'][member_data['type']]
            enum_data = data['enums'][struct_data['members'][member_data['selector']]['type']]
            enum_value_data = enum_data['values']

            out_file.write('  switch (s1->{}) {{\n'.format(member_data['selector']))
            out_file.write('  // {}\n'.format(member_data['type']))
            for union_member, union_member_data in union_data['members'].items():
                non_guarded_cases = 0
                guarded_cases = 0
                all_guards = []
                for case in union_member_data['selection'].split(','):
                    value_guards = get_define_guards(enum_value_data[case], enum_data['first'], enum_data['last'])
                    output_define_guard(value_guards, out_file)
                    out_file.write('  case {}:\n'.format(case))
                    if value_guards:
                        out_file.write('#endif \n')
                        guarded_cases += 1
                        all_guards += value_guards
                    else:
                        non_guarded_cases += 1

                if non_guarded_cases == 0:
                    output_define_guard(all_guards, out_file)
                
                if union_member_data['type'] in data['structs'] and 'suffix' in union_member_data and '*' in union_member_data['suffix']:
                    out_file.write('    if(!compare_{0}(s1->{1}.{2}, s2->{1}.{2}))'.format(union_member_data['type'], member, union_member))
                elif union_member_data['type'] in data['structs']:
                    out_file.write('    if(!compare_{0}(&s1->{1}.{2}, &s2->{1}.{2}))'.format(union_member_data['type'], member, union_member))
                else:
                    out_file.write('    if(s1->{0}.{1} != s2->{0}.{1})'.format(member, union_member))
                out_file.write('      return false;\n')
                if non_guarded_cases == 0:
                    out_file.write('#endif\n')
                out_file.write('\n')
                
            out_file.write('  default: ;\n')
            out_file.write('  }\n\n')

        # fifth pass, local array members
        compare_started = False
        for member, member_data in struct_data['members'].items():
            if 'proccessed' in member_data:
                continue
            if 'suffix' in member_data and '*' in member_data['suffix']:
                continue
            if member == 'sType' or member == 'pNext':
                continue
            member_data['proccessed'] = True

            if not compare_started:
                out_file.write('  // local array members\n')
            compare_started = True

            max_str_len = member_data['suffix'].replace('[', '')
            max_str_len = max_str_len.replace(']', '')

            if 'len' in member_data:
                # a dynamic comparison
                if member_data['type'] == 'char':
                    if member_data['len'] == 'null-terminated':
                        out_file.write('if (strncmp(s1->{0}, s2->{0}, {1}) != 0) return false;\n'.format(member, max_str_len))
                    else:
                        print('ERROR: Non null-terminated char member {}::{}\n'.format(struct, member))
                        sys.exit(1)
                else:
                    out_file.write('if (memcmp(s1->{0}, s2->{0}, s1->{1}) != 0) return false;\n'.format(member, member_data['len']))
            else:
                out_file.write('if (memcmp(s1->{0}, s2->{0}, {1} * sizeof({2})) != 0) return false;\n'.format(member, max_str_len, member_data['type']))

        # sixth pass, heap items
        compare_started = False
        for member, member_data in struct_data['members'].items():
            if 'proccessed' in member_data:
                continue
            if member == 'sType' or member == 'pNext' or member_data['type'] in data['structs']:
                continue
            member_data['processed'] = True

            if not compare_started:
                out_file.write('  // non-local members\n')
            compare_started = True

            if 'len' in member_data:
                out_file.write('\n  // {} - {}\n'.format(member, member_data['len']))
                process_multi_member(member, member_data, struct_data, member_data['len'].split(','), '', 'ijklmn', data, out_file)
            else:
                out_file.write('  if (s1->{0} != s2->{0}) return false;\n\n'.format(member))

        # complete the comparison
        out_file.write('  return true;\n')
        out_file.write('}\n')
        if struct_guards:
            out_file.write('#endif\n')

# footer
out_file.write('\n#endif // VK_STRUCT_COMPARE_CONFIG_MAIN')
out_file.write("""
#ifdef __cplusplus
}
#endif
""")
out_file.write('\n#endif // VK_STRUCT_COMPARE_H\n')
