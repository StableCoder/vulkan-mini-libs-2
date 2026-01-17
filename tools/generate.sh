# Copyright (C) 2022-2026 George Cave.
#
# SPDX-License-Identifier: Apache-2.0

#!/bin/bash
set -e

# Variables
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
START=
END=
OUTPUT="${ROOT_DIR}/include"
SKIP_PARSE=0
SKIP_FETCH=0
DOCS_REPO=""
IGNORE_FEATURES=""

# Type specific vars
API=vulkan
XML_PATH=xml/vk.xml
CACHE=.vk_cache.json
REGEX="^v[0-9]*\.[0-9]*\.[0-9]*$"

help_blurb() {
    echo " -s, --start <INT>  The starting version of Vulkan to generate for (default: 72)"
    echo " -e, --end <INT>    The ending version of Vulkan to generate for (default: none)"
    echo " -o, --output <DIR> The directory in which to generate header files (default: <repo>/include)"
    echo " --skip-parse       Skips generating new XML cache, just generate header files"
    echo " --skip-fetch       Skips fetching documentation updates from remote"
    echo " --openxr           Parse and generate for OpenXR API instead of Vulkan"
    echo " --vulkansc         Parse and generate for Vulkan SC instead of regular Vulkan"
}

# Command-line parsing
while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
    -s | --start)
        START="$2"
        shift # past argument
        shift # past value
        ;;
    -e | --end)
        END="$2"
        shift
        shift
        ;;
    -o | --output)
        OUTPUT="$(readlink -e "$2")"
        shift 2
        ;;
    --skip-parse)
        SKIP_PARSE=1
        shift
        ;;
    --skip-fetch)
        SKIP_FETCH=1
        shift
        ;;
    --openxr)
        API=openxr
        XML_PATH=specification/registry/xr.xml
        CACHE=.xr_cache.json
        REGEX="^release-[1-9].[0-9]*\.[0-9]*$"
        shift
        ;;
    --vulkansc)
        API=vulkansc
        CACHE=.vksc_cache.json
        REGEX="^vksc[1-9].[0-9]*\.[0-9]*$"
        shift
        ;;
    -h | --help)
        help_blurb
        exit 0
        ;;
    *)
        help_blurb
        exit 1
        ;;
    esac
done

if [[ "$API" == "vulkan" ]]; then
    START=${START:=72} # Prior to v72, vk.xml was not published, so that's the default minimum.
    IGNORE_FEATURES="--ignore-feature VK_VERSION_1_0"
    DOCS_REPO="Vulkan-Docs"
elif [[ "$API" == "vulkansc" ]]; then
    DOCS_REPO="VulkanSC-Docs"
elif [[ "$API" == "openxr" ]]; then
    START=${START:=0}
    DOCS_REPO="OpenXR-Docs"
fi

cd "${ROOT_DIR}/tools"

if [ $SKIP_PARSE -eq 0 ]; then
    # Remove any previously generated data for a clean slate
    if [ -f $CACHE ]; then
        rm $CACHE
    fi

    # Clone/update the Vulkan-Docs repository
    if ! [ -d $DOCS_REPO ]; then
        git clone https://github.com/KhronosGroup/$DOCS_REPO
    fi
    pushd $DOCS_REPO >/dev/null
    if [ $SKIP_FETCH -eq 0 ]; then
        git fetch -p
    fi

    # Collect the per-version XML data
    FIRST=1
    for TAG in $(git tag | grep -e "$REGEX" | sort -t '.' -k3nr); do
        EXTRA_OPTS=
        VER=$(echo $TAG | cut -d'.' -f3)
        if [[ $VER -lt $START ]]; then
            continue
        elif [ "$END" != "" ] && [[ $VER -gt $END ]]; then
            continue
        fi
        git checkout $TAG

        ../parse_xml.py --input $XML_PATH --cache ../$CACHE --api $API $IGNORE_FEATURES
        FIRST=0
    done
    popd >/dev/null
fi

# Generate headers
if [[ "$API" == "vulkan" ]]; then
    ./generate_serialization_header.py --input $CACHE --output "${OUTPUT}/vk_value_serialization.h"
    ./generate_result_string_header.py --input $CACHE --output "${OUTPUT}/vk_result_to_string.h"    --api $API
    ./generate_cleanup_header.py       --input $CACHE --output "${OUTPUT}/vk_struct_cleanup.h"
    ./generate_comparison_header.py    --input $CACHE --output "${OUTPUT}/vk_struct_compare.h"  --verified-void "${ROOT_DIR}/data/vk_verified_voids.txt"
elif [[ "$API" == "vulkansc" ]]; then
    ./generate_serialization_header.py --input $CACHE --output "${OUTPUT}/vksc_value_serialization.h"
    ./generate_result_string_header.py --input $CACHE --output "${OUTPUT}/vksc_result_to_string.h"    --api $API
    ./generate_cleanup_header.py       --input $CACHE --output "${OUTPUT}/vk_struct_cleanup.h"
    ./generate_comparison_header.py    --input $CACHE --output "${OUTPUT}/vk_struct_compare.h"
elif [[ "$API" == "openxr" ]]; then
    ./generate_result_string_header.py --input $CACHE --output "${OUTPUT}/xr_result_to_string.h"    --api $API
fi

# Format headers
cd "${OUTPUT}"
clang-format -i *.h
clang-format -i *.hpp
clang-format -i *.h
clang-format -i *.hpp
