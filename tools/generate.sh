#!/usr/bin/env sh
set -e

# Variables
START=72 # Prior to v72, vk.xml was not published, so that's the default minimum.
END=

help_blurb() {
    echo " -s, --start <INT> The starting version of Vulkan to generate for (default: 72)"
    echo " -e, --end <INT>   The ending version of Vulkan to generate for (default: none)"
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
    -h | --help)
        help_blurb
        exit 0
        ;;
    esac
done

# Remove any previously generated data for a clean slate
if [ -f .gen_cache.xml ]; then
    rm .gen_cache.xml
fi

# Clone/update the Vulkan-Docs repository
if ! [ -d Vulkan-Docs ]; then
    git clone https://github.com/KhronosGroup/Vulkan-Docs
fi
pushd Vulkan-Docs >/dev/null
git fetch -p

# Collect the per-version XML data
FIRST=1
for TAG in $(git tag | grep -e "^v[0-9]*\.[0-9]*\.[0-9]*$" | sort -t '.' -k3nr); do
    EXTRA_OPTS=
    VER=$(echo $TAG | cut -d'.' -f3)
    if [[ $VER -lt $START ]]; then
        continue
    elif [ "$END" != "" ] && [[ $VER -gt $END ]]; then
        continue
    fi
    git checkout $TAG

    ../parse_vk_doc.py -i xml/vk.xml -w ../.gen_cache.xml
    FIRST=0
done
popd >/dev/null

# Generate headers
./generate_serialization_header.py -i .gen_cache.xml -o ../include/vk_value_serialization.hpp
./generate_error_code_header.py -i .gen_cache.xml -o ../include/vk_error_code.hpp
./generate_cleanup_header.py -i .gen_cache.xml -o ../include/vk_struct_cleanup.h

# Format headers
clang-format -i ../include/*.h
clang-format -i ../include/*.hpp