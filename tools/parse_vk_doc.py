#!/usr/bin/env python3

# WARNING! THIS APPLICATION ASSUMES OPERATING ON DECREASING VERSIONS

import sys, getopt
import xmltodict

def getVersion(registryNode):
    for type in registryNode['types']['type']:
            if 'name' in type and type['name'] == 'VK_HEADER_VERSION':
                splitStr = type['#text'].split(' ')
                return splitStr[-1]

    return -1

def processVendors(registryNode, version, vendors):
    for tag in registryNode['tags']['tag']:
        if tag['@name'] in vendors:
            vendors[tag['@name']]['first'] = version
        else:
            vendors[tag['@name']] = {
                "first": version,
                "last": version,
            }
    return vendors

def processPlatforms(registryNode, version, platforms):
    for platform in registryNode['platforms']['platform']:
        if platform['@name'] in platforms:
            platforms[platform['@name']]['first'] = version
        else:
            platforms[platform['@name']] = {
                "first": version,
                "last": version,
                "guard": platform['@protect']
            }
    return platforms

def processEnumValue(enum, values, version):
    name = enum['@name']
    if name in values:
        values[name]['first'] = version
    else:
        values[name] = {
            "first": version,
            "last": version,
        }
        if '@value' in enum:
            values[name]['value'] = enum['@value']
        elif '@bitpos' in enum:
            values[name]['bitpos'] = enum['@bitpos']
        elif '@alias' in enum:
            values[name]['alias'] = enum['@alias']
        else:
            print("Could not determine enum value for ", name)
            sys.exit(1)

    return values

def processEnums(registryNode, version, enums):
    for enumSet in registryNode['enums']:
        if not '@type' in enumSet:
            continue
        enumSetName = enumSet['@name']
        if enumSetName == 'API Constants':
            continue
        if enumSetName == 'VkStructureType':
            continue

        if enumSetName in enums:
            enums[enumSetName]['first'] = version
        else:
            enums[enumSetName] = {
                "first": version,
                "last": version,
                "values": dict(),
            }
        
        values = enums[enumSetName]['values']

        # If it's an empty enum set, continue
        if not 'enum' in enumSet:
            continue

        # If a list need to iterate, otherwise pass plainly
        if isinstance(enumSet['enum'], list):
            for enum in enumSet['enum']:
                values = processEnumValue(enum, values, version)
        else:
            values = processEnumValue(enumSet['enum'], values, version)

    return enums

def processFeatureEnum(enum, version, enums):
    if '@extends' in enum:
        enumSetName = enum['@extends']
        if enumSetName == 'VkStructureType':
            return enums

        if enumSetName in enums:
            enums[enumSetName]['first'] = version
        else:
            enums[enumSetName] = {
                "first": version,
                "last": version,
                "values": dict(),
            }

        enumName = enum['@name']
        if enumName in enums[enumSetName]['values']:
            # Found previously
            enums[enumSetName]['values'][enumName]['first'] = version
        else:
            enums[enumSetName]['values'][enumName] = {
                "first": version,
                "last": version,
            }
            if '@value' in enum:
                enums[enumSetName]['values'][enumName]['value'] = enum['@value']
            elif '@offset' in enum:
                enums[enumSetName]['values'][enumName]['value'] = 1000000000 + (int(enum['@extnumber'])-1) * (1000) + int(enum['@offset'])
                if '@dir' in enum and enum['@dir'] == '-':
                    enums[enumSetName]['values'][enumName]['value'] = -enums[enumSetName]['values'][enumName]['value']
            elif '@bitpos' in enum:
                enums[enumSetName]['values'][enumName]['bitpos'] = enum['@bitpos']
            elif '@alias' in enum:
                enums[enumSetName]['values'][enumName]['alias'] = enum['@alias']
            else:
                print('FFF')
                sys.exit(1)

    return enums

def processFeatures(registryNode, version, enums):
    for feature in registryNode['feature']:
        # Ignore the base spec feature set
        featureName = feature['@name']
        if featureName == 'VK_VERSION_1_0':
            continue

        for require in feature['require']:
            if 'enum' in require:
                if isinstance(require['enum'], list):
                    for enum in require['enum']:
                        enums = processFeatureEnum(enum, version, enums)
                else:
                    enums = processFeatureEnum(require['enum'], version, enums)

    return enums

def processExtensions(registryNode, version, enums):
    for extension in registryNode['extensions']['extension']:
        if extension['@supported'] == 'disabled':
            continue
        extName = extension['@name']
        extNumber = int(extension['@number'])

        if 'require' in extension:
            if 'enum' in extension['require']:
                for enum in extension['require']['enum']:
                    if '@extends' in enum:
                        enumSetName = enum['@extends']
                        if enumSetName == 'VkStructureType':
                            continue

                        if enumSetName in enums:
                            enums[enumSetName]['first'] = version
                        else:
                            enums[enumSetName] = {
                                "first": version,
                                "last": version,
                                "values": dict(),
                            }

                        enumName = enum['@name']
                        if enumName in enums[enumSetName]['values']:
                            # Found previously
                            enums[enumSetName]['values'][enumName]['first'] = version
                        else:
                            enums[enumSetName]['values'][enumName] = {
                                "first": version,
                                "last": version,
                            }
                            if '@value' in enum:
                                enums[enumSetName]['values'][enumName]['value'] = enum['@value']
                            elif '@offset' in enum:
                                enums[enumSetName]['values'][enumName]['value'] = 1000000000 + (extNumber-1) * (1000) + int(enum['@offset'])
                            elif '@bitpos' in enum:
                                enums[enumSetName]['values'][enumName]['bitpos'] = enum['@bitpos']
                            elif '@alias' in enum:
                                enums[enumSetName]['values'][enumName]['alias'] = enum['@alias']
                            else:
                                print('FFF')
                                sys.exit(1)

    return enums

def processStructMember(newMember, memberList):
    member = {
        "type": newMember['type'],
    }
    if '#text' in newMember:
        member['text'] = newMember['#text']
    if '@len' in newMember:
        member['len'] = newMember['@len']
    if '@values' in newMember:
        member['values'] = newMember['@values']
    if 'enum' in newMember:
        member['enum'] = newMember['enum']

    memberList[newMember['name']] = member

def processStructs(registryNode, version, structs):
    for type in registryNode['types']['type']:
        if not '@category' in type:
            continue
        if type['@category'] != 'struct':
            continue

        structName = type['@name']
        if structName in structs:
            structs[structName]['first'] = version
        else:

            structs[structName] = {
                "first": version,
                "last": version,
                "members": dict(),
                "platforms": []
            }
            if '@alias' in type:
                structs[structName]['alias'] = type['@alias']
            if 'member' in type:
                if isinstance(type['member'], list):
                    for member in type['member']:
                        processStructMember(member, structs[structName]['members'])
                else:
                    processStructMember(type['member'], structs[structName]['members'])

    return structs

def processFeatureStructs(feature, structs):
    featureName = feature['@name']
    # Skip the original feature set
    if featureName == 'VK_VERSION_1_0':
        return structs
    
    for require in feature['require']:
        if 'type' in require:
            if isinstance(require['type'], list):
                for type in require['type']:
                    if type['@name'] in structs:
                        structs[type['@name']]['platforms'].append(featureName)
            elif not require['type']['@name'].startswith('VK_API_VERSION'):
                if require['type']['@name'] in structs:
                    structs[require['type']['@name']]['platforms'].append(featureName)

    return structs

def processExtensionStructs(extension, structs):
    if extension['@supported'] == 'disabled':
        return structs
    extName = extension['@name']
    require = extension['require']

    if 'type' in require:
        if isinstance(require['type'], list):
            for type in require['type']:
                if type['@name'] in structs:
                    structs[type['@name']]['platforms'].append(extName)
        else:
            if require['type']['@name'] in structs:
                structs[require['type']['@name']]['platforms'].append(extName)

    return structs

def main(argv):
    inputFile=''
    workingFile=''
    processExtra=False
    data = dict()

    try:
       opts, args =  getopt.getopt(argv, 'i:w:a', [])
    except getopt.GetoptError:
        print('Error parsing options')
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-i':
            inputFile = arg
        elif opt == '-w':
            workingFile = arg
        elif opt == '-a':
            processExtra = True


    if(inputFile == ''):
        print("Error: No Vulkan XML file specified")
        sys.exit(1)
    if(workingFile == ''):
        print("Error: No working file specified")
        sys.exit(1)

    try:
        with open(workingFile) as fd:
            data = xmltodict.parse(fd.read())
    except:
        print("No working file to read, assuming clean slate")

    if not 'root' in data:
        data['root'] = dict()

    with open(inputFile) as fd:
        doc = xmltodict.parse(fd.read())
        registryNode = doc['registry']

        version = getVersion(registryNode)
        if version == -1:
            print("Error: Failed to parse header version")
            sys.exit(1)

        # Update the first version we're operating with
        data['root']['first'] = version
        if not 'last' in data['root']:
            data['root']['last'] = version
        
        # Vendors
        if 'vendors' in data['root']:
            data['root']['vendors'] = processVendors(registryNode, version, data['root']['vendors'])
        else:
            data['root']['vendors'] = processVendors(registryNode, version, dict())
        
        # Platforms
        if 'platforms' in data['root']:
            data['root']['platforms'] = processPlatforms(registryNode, version, data['root']['platforms'])
        else:
            data['root']['platforms'] = processPlatforms(registryNode, version, dict())

        # Enums
        if 'enums' in data['root']:
            data['root']['enums'] = processEnums(registryNode, version, data['root']['enums'])
        else:
            data['root']['enums'] = processEnums(registryNode, version, dict())

        # Enum features/extensions
        data['root']['enums'] = processFeatures(registryNode, version, data['root']['enums'])
        data['root']['enums'] = processExtensions(registryNode, version, data['root']['enums'])

        # Structs
        if 'structs' in data['root']:
            data['root']['structs'] = processStructs(registryNode, version, data['root']['structs'])
        else:
            data['root']['structs'] = processStructs(registryNode, version, dict())

        if processExtra:
            for feature in registryNode['feature']:
                data['root']['structs'] = processFeatureStructs(feature, data['root']['structs'])
            for extension in registryNode['extensions']['extension']:
                data['root']['structs'] = processExtensionStructs(extension, data['root']['structs'])

        # Output data back to the working file
        f = open(workingFile, "w")
        f.write(xmltodict.unparse(data, pretty=True))
        f.close()

if __name__ == "__main__":
    main(sys.argv[1:])