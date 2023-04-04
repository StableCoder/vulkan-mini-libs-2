#!/usr/bin/env python3

# Copyright (C) 2022-2023 George Cave.
#
# SPDX-License-Identifier: Apache-2.0

from os.path import exists
import argparse
import sys
import re
import xml.etree.ElementTree as ET


def findVkVersion(rootNode):
    for type in rootNode.findall('./types/type'):
        category = type.get('category')
        if category is not None and category == 'define':
            for name in type.findall('name'):
                if name.text == 'VK_HEADER_VERSION':
                    return str(int(name.tail))

    return ''


def findXrVersion(rootNode):
    for type in rootNode.findall('./types/type'):
        category = type.get('category')
        if category is not None and category == 'define':
            for name in type.findall('name'):
                if name.text == 'XR_CURRENT_API_VERSION':
                    verNumbers = type.find('type').tail
                    parsedNumbers = re.findall(r'\d+', verNumbers)
                    return parsedNumbers[2]


def processVendors(inVendor, outVendors, apiVersion):
    name = inVendor.get('name')
    vendor = outVendors.find(name)
    if vendor is None:
        vendor = ET.SubElement(
            outVendors, name, {'first': apiVersion, 'last': apiVersion})
    else:
        vendor.set('first', apiVersion)


def processEnum(inEnum, outEnum, apiVersion):
    # If the enum has no type, just return
    if inEnum.get('type') is None:
        return
    # Skip certain named enums
    enumName = inEnum.get('name').replace('FlagBits', 'Flags')
    if enumName == 'API Constants' or enumName == 'VkStructureType':
        return

    # Add or edit
    enum = outEnum.find(enumName)
    if enum.get('alias'):
        # Skip renamed/aliased enums
        return

    enumValues = enum.find('values')
    for value in inEnum.findall('enum'):
        valName = value.get('name')
        enumVal = enumValues.find(valName)
        if enumVal is None:
            enumVal = ET.SubElement(
                enumValues, valName, {'first': apiVersion, 'last': apiVersion})
            ET.SubElement(enumVal, 'platforms')
            if not value.get('value') is None:
                enumVal.set('value', value.get('value'))
            elif not value.get('bitpos') is None:
                enumVal.set('bitpos', value.get('bitpos'))
            elif not value.get('alias') is None:
                enumVal.set('alias', value.get('alias'))
            else:
                print("Could not determine enum value for ", valName)
                sys.exit(1)
        else:
            enumVal.set('first', apiVersion)


def processFeatureEnum(featureEnum, outEnum, apiVersion):
    extends = featureEnum.get('extends')
    valName = featureEnum.get('name')
    if extends is None or extends == 'VkStructureType':
        return

    # Get the enum
    enum = outEnum.find(extends.replace('FlagBits', 'Flags'))
    if enum.get('alias'):
        # Skip renamed/aliased enums
        return

    # Value
    enumValues = enum.find('values')
    value = enumValues.find(valName)
    if value is None:
        value = ET.SubElement(
            enumValues, valName, {'first': apiVersion, 'last': apiVersion})
        ET.SubElement(value, 'platforms')
        if not featureEnum.get('offset') is None:
            extNum = int(featureEnum.get('extnumber'))
            if not featureEnum.get('dir') is None and featureEnum.get('dir') == '-':
                value.set('value', str(-(1000000000 + (extNum - 1)
                                         * 1000 + int(featureEnum.get('offset')))))
            else:
                value.set('value', str(1000000000 + (extNum - 1)
                                       * 1000 + int(featureEnum.get('offset'))))
        elif not featureEnum.get('value') is None:
            value.set('value', featureEnum.get('value'))
        elif not featureEnum.get('bitpos') is None:
            value.set('bitpos', featureEnum.get('bitpos'))
        elif not featureEnum.get('alias') is None:
            value.set('alias', featureEnum.get('alias'))
        else:
            print("Could not determine enum value for ", valName)
            sys.exit(1)
    else:
        value.set('first', apiVersion)


def processExtensionEnums(extension, outEnum, apiVersion):
    extName = extension.get('name')
    extNum = int(extension.get('number'))

    for extEnum in extension.findall('require/enum'):
        extends = extEnum.get('extends')
        valName = extEnum.get('name')
        if extends is None or extends == 'VkStructureType':
            continue

        # Enum
        enum = outEnum.find(extends.replace('FlagBits', 'Flags'))
        if enum.get('alias'):
            # Skip renamed/aliased enums
            continue

        # Value
        enumValues = enum.find('values')
        value = enumValues.find(valName)
        if value is None:
            value = ET.SubElement(
                enumValues, valName, {'first': apiVersion, 'last': apiVersion})
            ET.SubElement(value, 'platforms')
            if not extEnum.get('offset') is None:
                tempExtNum = extNum
                if not extEnum.get('extnumber') is None:
                    tempExtNum = int(extEnum.get('extnumber'))
                if not extEnum.get('dir') is None and extEnum.get('dir') == '-':
                    value.set('value', str(-(1000000000 + (tempExtNum - 1)
                                             * 1000 + int(extEnum.get('offset')))))
                else:
                    value.set('value', str(1000000000 + (tempExtNum - 1)
                                           * 1000 + int(extEnum.get('offset'))))
            elif not extEnum.get('value') is None:
                value.set('value', extEnum.get('value'))
            elif not extEnum.get('bitpos') is None:
                value.set('bitpos', extEnum.get('bitpos'))
            elif not extEnum.get('alias') is None:
                value.set('alias', extEnum.get('alias'))
            else:
                print("Could not determine enum value for ", valName)
                sys.exit(1)
        else:
            value.set('first', apiVersion)

        if value.find('platforms/' + extName) is None:
            ET.SubElement(value.find('platforms'), extName)

    for extType in extension.findall('require/type'):
        typeName = extType.get('name')
        enum = outEnum.find(typeName)
        if enum is None:
            continue

        if enum.find('platforms/' + extName) is None:
            ET.SubElement(enum.find('platforms'), extName)


def processStruct(structNode, structData, api, apiVersion):
    category = structNode.get('category')
    if category is None or category != 'struct':
        return

    # If specified, make sure it is the correct API
    if structNode.get('api') and structNode.get('api') != api:
        return

    structName = structNode.get('name')
    alias = structNode.get('alias')

    struct = structData.find(structName)
    if struct is None:
        struct = ET.SubElement(structData, structName, {
                               'first': apiVersion, 'last': apiVersion})
        ET.SubElement(struct, 'platforms')

        if alias:
            struct.set('alias', alias)
        if len(structNode.findall('./member')) != 0:
            members = ET.SubElement(struct, 'members', {
                'first': apiVersion, 'last': apiVersion})
            for member in structNode.findall('./member'):
                if member.get('api') and member.get('api') != api:
                    continue
                nameNode = member.find('name')
                node = ET.SubElement(members, nameNode.text, {
                    'first': apiVersion, 'last': apiVersion})
                if not member.get('values') is None:
                    value = ET.SubElement(node, 'value')
                    value.text = member.get('values')
                if not member.get('altlen') is None:
                    node.set('len', member.get('altlen'))
                elif not member.get('len') is None:
                    node.set('len', member.get('len'))
                if not member.find('enum') is None:
                    node.set('suffix', '[' + member.find('enum').text + ']')

                # Type Info
                type = ET.SubElement(node, 'type')
                type.text = member.find('type').text
                # Type Suffix
                typeSuffix = ''
                if not member.text is None:
                    typeSuffix += member.text
                if not member.find('type').tail is None:
                    typeSuffix += member.find('type').tail
                typeSuffix = typeSuffix.strip()
                if typeSuffix != '':
                    type.set('suffix', typeSuffix)

                # Array Stuff
                if not nameNode.tail is None and nameNode.tail != '[':
                    node.set('suffix', nameNode.tail)

    else:
        struct.set('first', apiVersion)

        if len(structNode.findall('./member')) != 0:
            members = struct.find('members')
            if members:
                members.set('first', apiVersion)
            else:
                members = ET.SubElement(struct, 'members', {
                    'first': apiVersion, 'last': apiVersion})

            for member in structNode.findall('./member'):
                nameNode = member.find('name')
                node = members.find(nameNode.text)
                if node:
                    node.set('first', apiVersion)
                    continue

                node = ET.SubElement(members, nameNode.text, {
                    'first': apiVersion, 'last': apiVersion})
                if not member.get('values') is None:
                    value = ET.SubElement(node, 'value')
                    value.text = member.get('values')
                if not member.get('altlen') is None:
                    node.set('len', member.get('altlen'))
                elif not member.get('len') is None:
                    node.set('len', member.get('len'))
                if not member.find('enum') is None:
                    node.set('suffix', '[' + member.find('enum').text + ']')

                # Type Info
                type = ET.SubElement(node, 'type')
                type.text = member.find('type').text
                # Type Suffix
                typeSuffix = ''
                if not member.text is None:
                    typeSuffix += member.text
                if not member.find('type').tail is None:
                    typeSuffix += member.find('type').tail
                typeSuffix = typeSuffix.strip()
                if typeSuffix != '':
                    type.set('suffix', typeSuffix)

                # Array Stuff
                if not nameNode.tail is None and nameNode.tail != '[':
                    node.set('suffix', nameNode.tail)


def processFeatureStruct(featureName, featureType, structData, apiVersion):
    name = featureType.get('name')

    struct = structData.find(name)
    if not struct is None:
        platforms = struct.find('platforms')
        platform = platforms.find(featureName)
        if platform is None:
            ET.SubElement(platforms, featureName, {
                'first': apiVersion, 'last': apiVersion})
        else:
            platform.set('first', apiVersion)


def processExtensionStruct(extension, structData, apiVersion):
    extName = extension.get('name')

    for require in extension.findall('require'):
        for type in require.findall('type'):
            typeName = type.get('name')
            struct = structData.find(typeName)
            if not struct is None:
                platforms = struct.find('platforms')
                platform = platforms.find(extName)
                if platform is None:
                    ET.SubElement(platforms, extName, {
                                  'first': apiVersion, 'last': apiVersion})
                else:
                    platform.set('first', apiVersion)

                platform = platforms.find(extName)
                if require.get('depends'):
                    dependencies = require.get('depends').split(',')
                    for dependency in dependencies:
                        depend = platform.find(dependency)
                        if depend is None:
                            ET.SubElement(platform, dependency, {'first': apiVersion,
                                                                 'last': apiVersion})
                        else:
                            depend.set('first', apiVersion)


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input',
                        help='Input Spec XML file',
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

    dataRoot = ET.Element('root')
    if exists(args.cache):
        dataXml = ET.parse(args.cache)
        dataRoot = dataXml.getroot()

    vkXml = ET.parse(args.input)
    vkRoot = vkXml.getroot()

    # Version
    apiVersion = ''
    if args.api == 'vulkan':
        apiVersion = findVkVersion(vkRoot)
    elif args.api == 'openxr':
        apiVersion = findXrVersion(vkRoot)
    if apiVersion == '':
        print("Error: Failed to determine API version")
        sys.exit(1)

    dataRoot.set('first', apiVersion)
    if dataRoot.get('last') is None:
        dataRoot.set('last', apiVersion)

    # Process Vendors
    if dataRoot.find('vendors') is None:
        ET.SubElement(dataRoot, 'vendors')
    vendorData = dataRoot.find('vendors')

    for vendor in vkRoot.findall('./tags/tag'):
        processVendors(vendor, vendorData, apiVersion)

    # Process Enums
    if dataRoot.find('enums') is None:
        ET.SubElement(dataRoot, 'enums')
    enumData = dataRoot.find('enums')

    for typeData in vkRoot.findall('types/type'):
        typeCategory = typeData.get('category')
        if typeCategory == 'enum' or typeCategory == 'bitmask':
            name = typeData.get('name')
            if name:
                if 'FlagBits' in name or name == 'VkStructureType':
                    continue
                enum = enumData.find(name)
                if enum is None:
                    if typeData.get('alias'):
                        enum = ET.SubElement(enumData, name, {
                            'first': apiVersion, 'last': apiVersion, 'alias': typeData.get('alias')})
                    else:
                        enum = ET.SubElement(enumData, name, {
                            'first': apiVersion, 'last': apiVersion})
                    ET.SubElement(enum, 'values', {})
                    ET.SubElement(enum, 'platforms', {})
                else:
                    enum.set('first', apiVersion)
            else:
                name = typeData.find('name').text
                if 'FlagBits' in name:
                    continue

                enum = enumData.find(name)
                if enum is None:
                    enum = ET.SubElement(enumData, name, {
                        'first': apiVersion, 'last': apiVersion})
                    ET.SubElement(enum, 'values', {})
                    ET.SubElement(enum, 'platforms', {})
                else:
                    enum.set('first', apiVersion)

    for enum in vkRoot.findall('enums'):
        processEnum(enum, enumData, apiVersion)

    for feature in vkRoot.findall('feature'):
        # If specified, make sure that the feature is for the desired API
        if feature.get('api'):
            apiList = feature.get('api').split(',')
            if not args.api in apiList:
                continue
        for featureEnum in feature.findall('require/enum'):
            processFeatureEnum(featureEnum, enumData, apiVersion)
    for extension in vkRoot.findall('extensions/extension'):
        # If specified, make sure that the feature is for the desired API
        if extension.get('supported'):
            apiList = extension.get('supported').split(',')
            if not args.api in apiList:
                continue
        processExtensionEnums(extension, enumData, apiVersion)

    # Process Structs
    if dataRoot.find('structs') is None:
        ET.SubElement(dataRoot, 'structs')
    structData = dataRoot.find('structs')

    for struct in vkRoot.findall('types/type'):
        processStruct(struct, structData, args.api, apiVersion)

    for feature in vkRoot.findall('feature'):
        featureName = feature.get('name')
        # Check to see if the feature is supposed to be ignored
        if featureName in args.ignore_feature:
            continue
        for featureType in feature.findall('require/type'):
            processFeatureStruct(featureName, featureType,
                                 structData, apiVersion)

    for extension in vkRoot.findall('extensions/extension'):
        processExtensionStruct(extension, structData, apiVersion)

    # Output XML
    tree = ET.ElementTree(dataRoot)
    tree.write(args.cache)


if __name__ == "__main__":
    main(sys.argv[1:])
