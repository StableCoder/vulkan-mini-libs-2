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
    for enum in enums:
        if enums[enum] is None:
            enum[enum] = dict()

    for enumSet in registryNode['enums']:
        if not '@type' in enumSet:
            continue
        enumSetName = enumSet['@name']
        if enumSetName == 'API Constants':
            continue
        if enumSetName == 'VkResult':
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

def main(argv):
    inputFile=''
    workingFile=''
    data = dict()

    try:
       opts, args =  getopt.getopt(argv, 'i:w:', [])
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

        # Output data back to the working file
        f = open(workingFile, "w")
        f.write(xmltodict.unparse(data, pretty=True))
        f.close()

if __name__ == "__main__":
    main(sys.argv[1:])