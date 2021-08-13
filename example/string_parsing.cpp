/*
    Copyright (C) 2020 George Cave - gcave@stablecoder.ca

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
*/

#include <vulkan/vulkan.h>

#define VK_VALUE_SERIALIZATION_CONFIG_MAIN
#include "vk_value_serialization.hpp"

int main() {
    { // Parsing
     {// Direct Vulkan with macro
      VkImageLayout layout = VK_IMAGE_LAYOUT_UNDEFINED;
    bool parsed = VK_PARSE(VkImageLayout, "READ_ONLY_OPTIMAL", &layout);
    // Layout will now be `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL`
}

{ // Using template function directly
    VkImageLayout layout = VK_IMAGE_LAYOUT_UNDEFINED;
    bool parsed = vk_parse<VkImageLayout>("VkImageLayout", "READ_ONLY_OPTIMAL", &layout);
    // Layout will now be `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL`
}

{ // vk_parse directly, converting against common uint32_t base type
    uint32_t tempInt;
    bool parsed = vk_parse("VkImageLayout", "READ_ONLY_OPTIMAL", &tempInt);
    VkImageLayout layout = static_cast<VkImageLayout>(tempInt);
    // Layout will now be `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL`
}
}

{     // Serializing
    { // Direct Vulkan with macro
        std::string serialized;
        bool parsed =
            VK_SERIALIZE(VkImageLayout, VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL, &serialized);
        // serialized will now be `READ_ONLY_OPTIMAL`
    }

    { // Using template function directly
        std::string serialized;
        bool parsed = vk_serialize<VkImageLayout>(
            "VkImageLayout", VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL, &serialized);
        // serialized will now be `READ_ONLY_OPTIMAL`
    }

    { // vk_parse directly, converting against common uint32_t base type
        std::string serialized;
        bool parsed = vk_serialize("VkImageLayout",
                                   static_cast<uint32_t>(VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL),
                                   &serialized);

        // serialized will now be `READ_ONLY_OPTIMAL`
    }
}

return 0;
}