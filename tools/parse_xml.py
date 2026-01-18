#!/usr/bin/env python3

# Copyright (C) 2022-2025 George Cave.
#
# SPDX-License-Identifier: Apache-2.0

from os.path import exists
import argparse
import copy
import hashlib
import sys
import re
import xml.etree.ElementTree as ET
import json


def parse_dependencies(dependencies):
    outArr = []

    for item in dependencies.split('+'):
        outArr.append(item)

    return outArr



parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input',
                        help='Input API Spec XML file',
                        required=True
                        )
parser.add_argument('-c', '--cache',
                        help='Cache XML file to read/write parsed spex data',
                        required=True
                        )
parser.add_argument('-a', '--api',
                        help='Khronos API being processed',
                        required=True)
parser.add_argument('--ignore-feature', nargs='+',
                        help='Features in the spec to ignore',
                        default=[])
args = parser.parse_args()

api_xml = ET.parse(args.input)
api_data = api_xml.getroot()

# api version information
api_version = -1
for api_type in api_data.findall('./types/type'):
    category = api_type.get('category')
    if category is not None and category == 'define':
        for name in api_type.findall('name'):
            if (args.api == 'vulkan' or args.api == 'vulkan,vulkanbase') and (not api_type.get('api') or api_type.get('api') == 'vulkan' or api_type.get('api') == 'vulkan,vulkanbase') and name.text == 'VK_HEADER_VERSION':
                api_version = int(name.tail)
            elif args.api == 'vulkansc' and api_type.get('api') == 'vulkansc' and name.text == 'VK_HEADER_VERSION':
                api_version = int(name.tail)
            elif args.api == 'openxr' and name.text == 'XR_CURRENT_API_VERSION':
                verNumbers = api_type.find('type').tail
                parsedNumbers = re.findall(r'\d+', verNumbers)
                api_version = int(parsedNumbers[2])

if api_version == -1:
    print('ERROR: Failed to determine API version')
    sys.exit(1)

# prepare/load parsed data
data = {
    'api': {'first': -1, 'last': -1},
    'vendors': {},
    'enums': {},
    'structs': {},
    'unions': {},
}
if exists(args.cache):
    with open(args.cache) as f:
        data = json.load(f)

# set api version info
if data['api']['last'] == -1:
    data['api']['last'] = api_version
data['api']['first'] = api_version

# process vendors
for api_vendor in api_data.findall('./tags/tag'):
    vendor_name = api_vendor.get('name')
    if not vendor_name in data['vendors']:
        data['vendors'][vendor_name] = {'first': api_version, 'last': api_version}
    data['vendors'][vendor_name]['first'] = api_version

struct_hash_table = dict()

# pre-calculate hashes of all struct types for alias
for api_type in api_data.findall('types/type'):
    type_category = api_type.get('category')
    if type_category == 'struct':
        # check if the desired api between vulkan/vulkansc
        if api_type.get('api') and not args.api in api_type.get('api'):
            continue
        
        struct_name = api_type.get('name')
        alias = api_type.get('alias')
        
        # Structure members/layouts can change, so need creeate a hash for each to sort/split them out
        # However, we only want to do variant splits based on pertinent member/name/types, not attribute
        # or comment changes
        stripped_struct = copy.deepcopy(api_type)
        for api_member in stripped_struct.findall('./member'):
            if api_member.get('api') and not args.api in api_member.get('api'):
                stripped_struct.remove(api_member)
                continue
            for subMember in api_member.findall('./'):
                if subMember.tag != 'name' and subMember.tag != 'type':
                    api_member.remove(subMember)

        strippedTree = ET.fromstring(ET.tostring(stripped_struct, encoding='unicode'))
        strippedTree = ''.join(strippedTree.itertext())
        strippedTree = ''.join(strippedTree.split())
        strippedTree = strippedTree.replace('const','')
        if alias:
            strippedTree += alias

        struct_hash_table[struct_name] = hashlib.sha256(strippedTree.encode('utf-8')).hexdigest()

# process types
for api_type in api_data.findall('types/type'):
    # iterate through all types
    type_category = api_type.get('category')

    if type_category == 'enum' or type_category == 'bitmask':
        # limit to just enums/bitmask types
        type_name = api_type.get('name')

        # alias types have the name as an attribute, instead of as text
        if not type_name:
            # probably a regular enum
            type_name = api_type.find('name').text

        if 'FlagBits' in type_name:
            continue

        if not type_name in data['enums']:
            data['enums'][type_name] = {'first': api_version, 'last': api_version}
        data['enums'][type_name]['first'] = api_version

        if api_type.get('alias'):
            data['enums'][type_name]['alias'] = api_type.get('alias')

    elif type_category == 'struct':
        # check if the desired api between vulkan/vulkansc
        if api_type.get('api') and not args.api in api_type.get('api'):
            continue
        
        struct_name = api_type.get('name')
        alias = api_type.get('alias')
        
        # get pre-calculated hash
        struct_hash = struct_hash_table[struct_name]

        # check if a new structure
        if not struct_name in data['structs']:
            data['structs'][struct_name] = dict()

        # if not a variant captured before, add it now
        if not struct_hash in data['structs'][struct_name]:
            new_struct = {'first': api_version, 'last': api_version}

            if alias:
                new_struct['alias'] = { 'name': alias, 'hash': struct_hash_table[alias] }

            if len(api_type.findall('./member')) > 0:
                new_struct['members'] = dict()
                for api_member in api_type.findall('./member'):
                    # skip members not of the expected api
                    if api_member.get('api') and not args.api in api_member.get('api'):
                        continue

                    member_name = api_member.find('name').text
                    new_member = dict()

                    # type info
                    new_member['type'] = api_member.find('type').text
                    # type suffix
                    type_suffix = ''
                    if api_member.text:
                        type_suffix += api_member.text
                    if api_member.find('type').tail:
                        type_suffix += api_member.find('type').tail
                    if api_member.find('name').tail:
                        type_suffix += api_member.find('name').tail
                    type_suffix = type_suffix.strip()
                    if type_suffix != '':
                        new_member['suffix'] = type_suffix

                    # add any special items
                    if not api_member.get('values') is None:
                        new_member['value'] = api_member.get('values')
                    if not api_member.get('altlen') is None:
                        new_member['len'] = api_member.get('altlen')
                    elif not api_member.get('len') is None:
                        new_member['len'] = api_member.get('len')
                    if not api_member.find('enum') is None:
                        new_member['suffix'] = '[' + api_member.find('enum').text + ']'

                    if api_member.get('selector'):
                        # union types can be determined by the selector
                        new_member['selector'] = api_member.get('selector')

                    # set new member data to struct variant
                    new_struct['members'][member_name] = new_member
            # add new struct variant
            data['structs'][struct_name][struct_hash] = new_struct
        # set struct variant first api_version
        data['structs'][struct_name][struct_hash]['first'] = api_version
        data['structs'][struct_name][struct_hash]['new_require_list'] = []

    elif type_category == 'union':
        if api_type.get('api') and not args.api in api_type.get('api'):
            continue

        union_name = api_type.get('name')
        alias = api_type.get('alias')

        if alias:
            print('ERROR: Unhandled union/alis of {}'.format(union_name))
            sys.exit(1)

        if not union_name in data['unions']:
            new_union = {'first': api_version, 'last': api_version, 'members': dict()}

            for api_member in api_type.findall('./member'):
                # skip members not of the expected api
                if api_member.get('api') and not args.api in api_member.get('api'):
                    continue
                
                member_name = api_member.find('name').text
                new_member = dict()

                # type info
                new_member['type'] = api_member.find('type').text
                # type suffix
                type_suffix = ''
                if api_member.text:
                    type_suffix += api_member.text
                if api_member.find('type').tail:
                    type_suffix += api_member.find('type').tail
                type_suffix = type_suffix.strip()
                if type_suffix != '':
                    new_member['suffix'] = type_suffix

                if api_member.get('selection'):
                    # union member can be determined by this selector
                    new_member['selection'] = api_member.get('selection')

                new_union['members'][member_name] = new_member
            data['unions'][union_name] = new_union

        data['unions'][union_name]['first'] = api_version

        

# process enums / values
for api_enum in api_data.findall('enums'):
    # if no type, skip
    if api_enum.get('type') is None:
        continue
    # check to skip specific enums
    enum_name = api_enum.get('name').replace('FlagBits', 'Flags')
    if enum_name == 'API Constants':
        continue

    # shortcut
    enum_data = data['enums'][enum_name]

    # skip renamed/aliased enums
    if 'alias' in enum_data:
        continue

    # iterate through all enum values/members
    for api_enum_value in api_enum.findall('enum'):
        if not 'values' in enum_data:
            enum_data['values'] = dict()

        value_name = api_enum_value.get('name')
        if not value_name in enum_data['values']:
            enum_data['values'][value_name] = {'first': api_version, 'last': api_version}
            if api_enum_value.get('value'):
                enum_data['values'][value_name]['value'] = api_enum_value.get('value')
            elif api_enum_value.get('bitpos'):
                enum_data['values'][value_name]['bitpos'] = api_enum_value.get('bitpos')
            elif api_enum_value.get('alias'):
                enum_data['values'][value_name]['alias'] = api_enum_value.get('alias')
            else:
                print('ERROR: Unhandled enum value type of {}::{}'.format(enum_name, value_name))
                sys.exit(1)
        enum_data['values'][value_name]['first'] = api_version

# process features
for api_feature in api_data.findall('feature'):
    feature_name = api_feature.get('name')

    if feature_name in args.ignore_feature:
        continue

    # process feature enums
    for api_feature_enum in api_feature.findall('require/enum'):
        # check to see if feature is part of desired api
        if api_feature.get('api'):
            api_feature_list = api_feature.get('api').split(',')
            if not args.api in api_feature_list:
                continue

        if not api_feature_enum.get('extends'):
            continue

        extends_enum = api_feature_enum.get('extends')
        value_name = api_feature_enum.get('name')
        extended_enum_data = data['enums'][extends_enum.replace('FlagBits', 'Flags')]

        # skip alias enums
        if 'alias' in extended_enum_data:
            continue

        if not 'values' in extended_enum_data:
            extended_enum_data['values'] = dict()
        if not value_name in extended_enum_data['values']:
            new_value = {'first': api_version, 'last': api_version}
            
            # feature enums are offset
            if api_feature_enum.get('offset'):
                extension_id = int(api_feature_enum.get('extnumber'))

                new_value['value'] = 1000000000 + (extension_id - 1) * 1000 + int(api_feature_enum.get('offset'))
                if api_feature_enum.get('dir') and api_feature_enum.get('dir') == '-':
                    new_value['value'] = -new_value['value']
            elif api_feature_enum.get('value'):
                new_value['value'] = api_feature_enum.get('value')
            elif api_feature_enum.get('bitpos'):
                new_value['bitpos'] = api_feature_enum.get('bitpos')
            elif api_feature_enum.get('alias'):
                new_value['alias'] = api_feature_enum.get('alias')
            else:
                print('ERROR: Unhandled feature enum value for {}::{}'.format(extends_enum, value_name))
                sys.exit(1)
            
            extended_enum_data['values'][value_name] = new_value
        extended_enum_data['values'][value_name]['first'] = api_version

    # process feature types
    for api_feature_type in api_feature.findall('require/type'):
        type_name = api_feature_type.get('name')

        # type -> struct
        if type_name in data['structs']:
            for variant, struct_data in data['structs'][type_name].items():
                # skip variants not in this version
                if struct_data['first'] != api_version:
                    continue

                if not 'new_require_list' in struct_data:
                    struct_data['new_require_list'] = []
                if not feature_name in struct_data['new_require_list']:
                    if feature_name.startswith('VK_BASE_VERSION_') or feature_name.startswith('VK_COMPUTE_VERSION_') or feature_name.startswith('VK_GRAPHICS_VERSION_'):
                        if not feature_name.endswith('1_0'):
                            struct_data['new_require_list'].append('VK_VERSION_{}'.format(feature_name[-3:]))
                    else:
                        struct_data['new_require_list'].append(feature_name)
    
# process extensions
for api_extension in api_data.findall('extensions/extension'):
    extension_name = api_extension.get('name')
    extension_id = int(api_extension.get('number'))

    extra_extension_define = None
    if api_extension.get('platform') and api_extension.get('platform') == 'provisional':
        extra_extension_define = ['VK_ENABLE_BETA_EXTENSIONS']
    if api_extension.get('provisional') and api_extension.get('provisional') == 'true':
        extra_extension_define = ['VK_ENABLE_BETA_EXTENSIONS']

    # process extension require sets
    for api_extension_require in api_extension.findall('require'):
        # capture extra required extensions
        extra_require_define = None
        if api_extension_require.get('depends'):
            extra_require_define = parse_dependencies(api_extension_require.get('depends'))

        # enums
        for api_extension_enum in api_extension_require.findall('enum'):
            extends_enum = api_extension_enum.get('extends')
            if not extends_enum:
                continue

            value_name = api_extension_enum.get('name')
            extended_enum_data = data['enums'][extends_enum.replace('FlagBits', 'Flags')]

            # skip alias enums
            if 'alias' in extended_enum_data:
                continue

            # set values
            if not 'values' in extended_enum_data:
                extended_enum_data['values'] = dict()
            if not value_name in extended_enum_data['values']:
                new_value = {'first': api_version, 'last': api_version}

                if api_extension_enum.get('offset'):
                    temp_extension_id = extension_id

                    # sometimes there is an override
                    if api_extension_enum.get('extnumber'):
                        temp_extension_id = int(api_extension_enum.get('extnumber'))

                    new_value['value'] = 1000000000 + (temp_extension_id - 1) * 1000 + int(api_extension_enum.get('offset'))
                    if api_extension_enum.get('dir') and api_extension_enum.get('dir') == '-':
                        new_value['value'] = -new_value['value']
                elif api_extension_enum.get('value'):
                    new_value['value'] = api_extension_enum.get('value')
                elif api_extension_enum.get('bitpos'):
                    new_value['bitpos'] = api_extension_enum.get('bitpos')
                elif api_extension_enum.get('alias'):
                    new_value['alias'] = api_extension_enum.get('alias')
                else:
                    print('ERROR: Unhandled extension enum value for {}::{}'.format(extends_enum, value_name))
                    sys.exit(1)

                extended_enum_data['values'][value_name] = new_value
            value_data = extended_enum_data['values'][value_name]
            value_data['first'] = api_version

            # add the extension requirements for the value
            if not 'new_require_list' in value_data:
                value_data['new_require_list'] = []
            if not extension_name in value_data['new_require_list']:
                value_data['new_require_list'] = [extension_name]
            if extra_require_define:
                value_data['new_require_list'] = value_data['new_require_list'] + extra_require_define
            if extra_extension_define:
                value_data['new_require_list'] = value_data['new_require_list'] + extra_extension_define

        # types / requires
        for api_extension_type in api_extension_require.findall('type'):
            type_name = api_extension_type.get('name')

            # type -> struct
            if type_name in data['structs']:
                for variant, struct_data in data['structs'][type_name].items():
                    # skip variants not in this version
                    if struct_data['first'] != api_version:
                        continue

                    if not 'new_require_list' in struct_data:
                        struct_data['new_require_list'] = []
                    if not extension_name in struct_data['new_require_list']:
                        struct_data['new_require_list'].append(extension_name)
                    if extra_require_define and not extra_require_define in struct_data['new_require_list']:
                        struct_data['new_require_list'] = struct_data['new_require_list'] + extra_require_define
                        struct_data['new_require_list'] = list(dict.fromkeys(struct_data['new_require_list']))
                    if extra_extension_define and not extra_extension_define in struct_data['new_require_list']:
                        struct_data['new_require_list'] = struct_data['new_require_list'] + extra_extension_define
                        struct_data['new_require_list'] = list(dict.fromkeys(struct_data['new_require_list']))

# now need to iterate through all enums and structs, and check if the generated require list matches previous lists, or is a new one
for enum, enum_data in data['enums'].items():
    if 'values' in enum_data:
        for value, value_data in enum_data['values'].items():
            if 'new_require_list' in value_data:
                # there are struct requirements, process it
                if not 'requires' in value_data:
                    value_data['requires'] = dict()

                # sort the list and hash it
                require_hash = hashlib.sha256(''.join(sorted(value_data['new_require_list'])).encode('utf-8')).hexdigest()

                if not require_hash in value_data['requires']:
                    # add it new
                    value_data['requires'][require_hash] = {'first': api_version, 'last': api_version, 'defines': value_data['new_require_list']}
                value_data['requires'][require_hash]['first'] = api_version

                # remove the new_require_list
                value_data.pop('new_require_list')

for struct_name, struct_variants in data['structs'].items():
    for variant, struct_data in struct_variants.items():
        if 'new_require_list' in struct_data:
            # there are struct requirements, process it
            if not 'requires' in struct_data:
                struct_data['requires'] = dict()

            # sort the list and hash it
            require_hash = hashlib.sha256(''.join(sorted(struct_data['new_require_list'])).encode('utf-8')).hexdigest()

            if not require_hash in struct_data['requires']:
                # add it new
                struct_data['requires'][require_hash] = {'first': api_version, 'last': api_version, 'defines': struct_data['new_require_list']}
            struct_data['requires'][require_hash]['first'] = api_version

            # remove the new_require_list
            struct_data.pop('new_require_list')


# output to cache file
with open(args.cache, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

sys.exit(0)