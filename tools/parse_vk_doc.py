#!/usr/bin/env python3

from os.path import exists
import sys
import getopt
import xml.etree.ElementTree as ET


def findVersion(rootNode):
    for type in rootNode.findall('./types/type'):
        category = type.get('category')
        if category is not None and category == 'define':
            for name in type.findall('name'):
                if name.text == 'VK_HEADER_VERSION':
                    return str(int(name.tail))

    return ''


def processVendors(inVendor, outVendors, vkVersion):
    name = inVendor.get('name')
    vendor = outVendors.find(name)
    if vendor is None:
        vendor = ET.SubElement(
            outVendors, name, {'first': vkVersion, 'last': vkVersion})
    else:
        vendor.set('first', vkVersion)


def processEnum(inEnum, outEnum, vkVersion):
    # If the enum has no type, just return
    if inEnum.get('type') is None:
        return
    # Skip certain named enums
    enumName = inEnum.get('name')
    if enumName == 'API Constants' or enumName == 'VkStructureType':
        return

    # Add or edit
    enum = outEnum.find(enumName)
    if enum is None:
        enum = ET.SubElement(outEnum, enumName,  {
                             'first': vkVersion, 'last': vkVersion})
    else:
        enum.set('first', vkVersion)

    for value in inEnum.findall('enum'):
        valName = value.get('name')
        enumVal = enum.find(valName)
        if enumVal is None:
            enumVal = ET.SubElement(
                enum, valName, {'first': vkVersion, 'last': vkVersion})
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
            enumVal.set('first', vkVersion)


def processFeatureEnum(featureEnum, outEnum, vkVersion):
    extends = featureEnum.get('extends')
    valName = featureEnum.get('name')
    if extends is None or extends == 'VkStructureType':
        return

    # Get the enum
    enum = outEnum.find(extends)
    value = enum.find(valName)
    if value is None:
        value = ET.SubElement(
            enum, valName, {'first': vkVersion, 'last': vkVersion})
        ET.SubElement(value, 'platforms')
        if not featureEnum.get('offset') is None:
            extNum = int(featureEnum.get('extnumber'))
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
        value.set('first', vkVersion)


def processExtensionEnums(extension, outEnum, vkVersion):
    extName = extension.get('name')
    extNum = int(extension.get('number'))

    for extEnum in extension.findall('require/enum'):
        extends = extEnum.get('extends')
        valName = extEnum.get('name')
        if extends is None or extends == 'VkStructureType':
            continue

        enum = outEnum.find(extends)
        value = enum.find(valName)
        if value is None:
            value = ET.SubElement(
                enum, valName, {'first': vkVersion, 'last': vkVersion})
            ET.SubElement(value, 'platforms')
            if not extEnum.get('offset') is None:
                value.set('value', str(1000000000 + (extNum - 1)
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
            value.set('first', vkVersion)

        if value.find('platforms/' + extName) is None:
            ET.SubElement(value.find('platforms'), extName)


def processStruct(structNode, structData, vkVersion):
    category = structNode.get('category')
    if category is None or category != 'struct':
        return
    structName = structNode.get('name')

    struct = structData.find(structName)
    if struct is None:
        struct = ET.SubElement(structData, structName, {
                               'first': vkVersion, 'last': vkVersion})
        members = ET.SubElement(struct, 'members')
        ET.SubElement(struct, 'platforms')

        # Only need to process the members the first time it appears, as they don't change through time
        for member in structNode.findall('./member'):
            nameNode = member.find('name')
            node = ET.SubElement(members, nameNode.text)
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
        struct.set('first', vkVersion)


def processFeatureStruct(featureName, featureType, structData):
    name = featureType.get('name')

    struct = structData.find(name)
    if not struct is None:
        platforms = struct.find('platforms')
        if platforms.find(featureName) is None:
            ET.SubElement(platforms, featureName)


def processExtensionStruct(extension, structData):
    extName = extension.get('name')

    for type in extension.findall('require/type'):
        typeName = type.get('name')
        struct = structData.find(typeName)
        if not struct is None:
            platforms = struct.find('platforms')
            if platforms.find(extName) is None:
                ET.SubElement(platforms, extName)


def main(argv):
    inputFile = ''
    workingFile = ''

    try:
        opts, args = getopt.getopt(argv, 'i:w:a', [])
    except getopt.GetoptError:
        print('Error parsing options')
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-i':
            inputFile = arg
        elif opt == '-w':
            workingFile = arg

    if(inputFile == ''):
        print("Error: No Vulkan XML file specified")
        sys.exit(1)
    if(workingFile == ''):
        print("Error: No working file specified")
        sys.exit(1)

    dataRoot = ET.Element('root')
    if exists(workingFile):
        dataXml = ET.parse(workingFile)
        dataRoot = dataXml.getroot()

    vkXml = ET.parse(inputFile)
    vkRoot = vkXml.getroot()

    # Find current version
    vkVersion = findVersion(vkRoot)
    if vkVersion == '':
        print("Error: Failed to determine Vulkan Header Version")
        sys.exit(1)

    dataRoot.set('first', vkVersion)
    if dataRoot.get('last') is None:
        dataRoot.set('last', vkVersion)

    # Process Vendors
    if dataRoot.find('vendors') is None:
        ET.SubElement(dataRoot, 'vendors')
    vendorData = dataRoot.find('vendors')

    for vendor in vkRoot.findall('./tags/tag'):
        processVendors(vendor, vendorData, vkVersion)

    # Process Enums
    if dataRoot.find('enums') is None:
        ET.SubElement(dataRoot, 'enums')
    enumData = dataRoot.find('enums')

    for enum in vkRoot.findall('enums'):
        processEnum(enum, enumData, vkVersion)

    for feature in vkRoot.findall('feature/require/enum'):
        processFeatureEnum(feature, enumData, vkVersion)
    for extension in vkRoot.findall('extensions/extension'):
        processExtensionEnums(extension, enumData, vkVersion)

    # Process Structs
    if dataRoot.find('structs') is None:
        ET.SubElement(dataRoot, 'structs')
    structData = dataRoot.find('structs')

    for struct in vkRoot.findall('types/type'):
        processStruct(struct, structData, vkVersion)

    for feature in vkRoot.findall('feature'):
        featureName = feature.get('name')
        # Skip the core set
        if featureName == 'VK_VERSION_1_0':
            continue
        for featureType in feature.findall('require/type'):
            processFeatureStruct(featureName, featureType, structData)

    for extension in vkRoot.findall('extensions/extension'):
        processExtensionStruct(extension, structData)

    # Output XML
    tree = ET.ElementTree(dataRoot)
    tree.write(workingFile)


if __name__ == "__main__":
    main(sys.argv[1:])
