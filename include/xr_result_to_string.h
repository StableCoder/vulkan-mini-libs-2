/*
    Copyright (C) 2021-2023 George Cave - gcave@stablecoder.ca

    SPDX-License-Identifier: Apache-2.0

    This file was auto-generated by the Vulkan Mini Libs 2 utility:
    https://github.com/stablecoder/vulkan-mini-libs-2.git
    or
    https://git.stabletec.com/utilities/vulkan-mini-libs-2.git

    Check for an updated version anytime, or state concerns/bugs.
*/

#ifndef XR_RESULT_TO_STRING_H
#define XR_RESULT_TO_STRING_H

/*  USAGE
    To use, include this header where the declarations for the boolean checks are required.

    On *ONE* compilation unit, include the definition of:
    #define XR_RESULT_TO_STRING_CONFIG_MAIN

    so that the definitions are compiled somewhere following the one definition rule.
*/

#ifdef __cplusplus
extern "C" {
#endif

#include <openxr/openxr.h>

#ifdef __cplusplus
static_assert((XR_CURRENT_API_VERSION & 0xffffffffULL) >= 0,
              "openxr header version is from before the minimum supported version of v0.");
static_assert((XR_CURRENT_API_VERSION & 0xffffffffULL) <= 28,
              "openxr header version is from after the maximum supported version of v28.");
#else
_Static_assert((XR_CURRENT_API_VERSION & 0xffffffffULL) >= 0,
               "openxr header version is from before the minimum supported version of v0.");
_Static_assert((XR_CURRENT_API_VERSION & 0xffffffffULL) <= 28,
               "openxr header version is from after the maximum supported version of v28.");
#endif

/// Returns a string representing the given VkResult parameter. If there is no known representation,
/// returns NULL.
char const *XrResult_to_string(XrResult result);

#ifdef XR_RESULT_TO_STRING_CONFIG_MAIN

char const *XrResult_to_string(XrResult result) {
  // Check in descending order to get the 'latest' version of the error code text available.
  // Also, because codes have been re-used over time, can't use a switch and have to do this large
  // set of ifs. Luckily this *should* be a relatively rare call.
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 28 && XR_META_passthrough_color_lut
  if (result == XR_ERROR_PASSTHROUGH_COLOR_LUT_BUFFER_SIZE_MISMATCH_META)
    return "XR_ERROR_PASSTHROUGH_COLOR_LUT_BUFFER_SIZE_MISMATCH_META";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 28 && XR_EXT_plane_detection
  if (result == XR_ERROR_SPACE_NOT_LOCATABLE_EXT)
    return "XR_ERROR_SPACE_NOT_LOCATABLE_EXT";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 28 && XR_EXT_plane_detection
  if (result == XR_ERROR_PLANE_DETECTION_PERMISSION_DENIED_EXT)
    return "XR_ERROR_PLANE_DETECTION_PERMISSION_DENIED_EXT";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 27 && XR_FB_spatial_entity_sharing
  if (result == XR_ERROR_SPACE_MAPPING_INSUFFICIENT_FB)
    return "XR_ERROR_SPACE_MAPPING_INSUFFICIENT_FB";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 27 && XR_FB_spatial_entity_sharing
  if (result == XR_ERROR_SPACE_LOCALIZATION_FAILED_FB)
    return "XR_ERROR_SPACE_LOCALIZATION_FAILED_FB";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 27 && XR_FB_spatial_entity_sharing
  if (result == XR_ERROR_SPACE_NETWORK_TIMEOUT_FB)
    return "XR_ERROR_SPACE_NETWORK_TIMEOUT_FB";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 27 && XR_FB_spatial_entity_sharing
  if (result == XR_ERROR_SPACE_NETWORK_REQUEST_FAILED_FB)
    return "XR_ERROR_SPACE_NETWORK_REQUEST_FAILED_FB";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 27 && XR_FB_spatial_entity_sharing
  if (result == XR_ERROR_SPACE_CLOUD_STORAGE_DISABLED_FB)
    return "XR_ERROR_SPACE_CLOUD_STORAGE_DISABLED_FB";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 27 && XR_QCOM_tracking_optimization_settings
  if (result == XR_ERROR_HINT_ALREADY_SET_QCOM)
    return "XR_ERROR_HINT_ALREADY_SET_QCOM";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 23 && XR_FB_spatial_entity
  if (result == XR_ERROR_SPACE_COMPONENT_NOT_SUPPORTED_FB)
    return "XR_ERROR_SPACE_COMPONENT_NOT_SUPPORTED_FB";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 23 && XR_FB_spatial_entity
  if (result == XR_ERROR_SPACE_COMPONENT_NOT_ENABLED_FB)
    return "XR_ERROR_SPACE_COMPONENT_NOT_ENABLED_FB";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 23 && XR_FB_spatial_entity
  if (result == XR_ERROR_SPACE_COMPONENT_STATUS_PENDING_FB)
    return "XR_ERROR_SPACE_COMPONENT_STATUS_PENDING_FB";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 23 && XR_FB_spatial_entity
  if (result == XR_ERROR_SPACE_COMPONENT_STATUS_ALREADY_SET_FB)
    return "XR_ERROR_SPACE_COMPONENT_STATUS_ALREADY_SET_FB";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 21 && XR_FB_render_model
  if (result == XR_ERROR_RENDER_MODEL_KEY_INVALID_FB)
    return "XR_ERROR_RENDER_MODEL_KEY_INVALID_FB";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 21 && XR_FB_render_model
  if (result == XR_RENDER_MODEL_UNAVAILABLE_FB)
    return "XR_RENDER_MODEL_UNAVAILABLE_FB";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 20 && XR_FB_passthrough
  if (result == XR_ERROR_UNEXPECTED_STATE_PASSTHROUGH_FB)
    return "XR_ERROR_UNEXPECTED_STATE_PASSTHROUGH_FB";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 20 && XR_FB_passthrough
  if (result == XR_ERROR_FEATURE_ALREADY_CREATED_PASSTHROUGH_FB)
    return "XR_ERROR_FEATURE_ALREADY_CREATED_PASSTHROUGH_FB";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 20 && XR_FB_passthrough
  if (result == XR_ERROR_FEATURE_REQUIRED_PASSTHROUGH_FB)
    return "XR_ERROR_FEATURE_REQUIRED_PASSTHROUGH_FB";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 20 && XR_FB_passthrough
  if (result == XR_ERROR_NOT_PERMITTED_PASSTHROUGH_FB)
    return "XR_ERROR_NOT_PERMITTED_PASSTHROUGH_FB";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 20 && XR_FB_passthrough
  if (result == XR_ERROR_INSUFFICIENT_RESOURCES_PASSTHROUGH_FB)
    return "XR_ERROR_INSUFFICIENT_RESOURCES_PASSTHROUGH_FB";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 20 && XR_FB_passthrough
  if (result == XR_ERROR_UNKNOWN_PASSTHROUGH_FB)
    return "XR_ERROR_UNKNOWN_PASSTHROUGH_FB";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 20 && XR_VARJO_marker_tracking
  if (result == XR_ERROR_MARKER_NOT_TRACKED_VARJO)
    return "XR_ERROR_MARKER_NOT_TRACKED_VARJO";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 20 && XR_VARJO_marker_tracking
  if (result == XR_ERROR_MARKER_ID_INVALID_VARJO)
    return "XR_ERROR_MARKER_ID_INVALID_VARJO";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 18 && XR_MSFT_spatial_anchor_persistence
  if (result == XR_ERROR_SPATIAL_ANCHOR_NAME_NOT_FOUND_MSFT)
    return "XR_ERROR_SPATIAL_ANCHOR_NAME_NOT_FOUND_MSFT";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 18 && XR_MSFT_spatial_anchor_persistence
  if (result == XR_ERROR_SPATIAL_ANCHOR_NAME_INVALID_MSFT)
    return "XR_ERROR_SPATIAL_ANCHOR_NAME_INVALID_MSFT";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 17 && XR_MSFT_composition_layer_reprojection
  if (result == XR_ERROR_REPROJECTION_MODE_UNSUPPORTED_MSFT)
    return "XR_ERROR_REPROJECTION_MODE_UNSUPPORTED_MSFT";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 17 && XR_MSFT_scene_understanding
  if (result == XR_ERROR_COMPUTE_NEW_SCENE_NOT_COMPLETED_MSFT)
    return "XR_ERROR_COMPUTE_NEW_SCENE_NOT_COMPLETED_MSFT";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 17 && XR_MSFT_scene_understanding
  if (result == XR_ERROR_SCENE_COMPONENT_ID_INVALID_MSFT)
    return "XR_ERROR_SCENE_COMPONENT_ID_INVALID_MSFT";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 17 && XR_MSFT_scene_understanding
  if (result == XR_ERROR_SCENE_COMPONENT_TYPE_MISMATCH_MSFT)
    return "XR_ERROR_SCENE_COMPONENT_TYPE_MISMATCH_MSFT";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 17 && XR_MSFT_scene_understanding
  if (result == XR_ERROR_SCENE_MESH_BUFFER_ID_INVALID_MSFT)
    return "XR_ERROR_SCENE_MESH_BUFFER_ID_INVALID_MSFT";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 17 && XR_MSFT_scene_understanding
  if (result == XR_ERROR_SCENE_COMPUTE_FEATURE_INCOMPATIBLE_MSFT)
    return "XR_ERROR_SCENE_COMPUTE_FEATURE_INCOMPATIBLE_MSFT";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 17 && XR_MSFT_scene_understanding
  if (result == XR_ERROR_SCENE_COMPUTE_CONSISTENCY_MISMATCH_MSFT)
    return "XR_ERROR_SCENE_COMPUTE_CONSISTENCY_MISMATCH_MSFT";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 16
  if (result == XR_ERROR_RUNTIME_UNAVAILABLE)
    return "XR_ERROR_RUNTIME_UNAVAILABLE";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 13 && XR_FB_display_refresh_rate
  if (result == XR_ERROR_DISPLAY_REFRESH_RATE_UNSUPPORTED_FB)
    return "XR_ERROR_DISPLAY_REFRESH_RATE_UNSUPPORTED_FB";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 13 && XR_FB_color_space
  if (result == XR_ERROR_COLOR_SPACE_UNSUPPORTED_FB)
    return "XR_ERROR_COLOR_SPACE_UNSUPPORTED_FB";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 12 && XR_MSFT_controller_model
  if (result == XR_ERROR_CONTROLLER_MODEL_KEY_INVALID_MSFT)
    return "XR_ERROR_CONTROLLER_MODEL_KEY_INVALID_MSFT";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 11
  if (result == XR_ERROR_GRAPHICS_REQUIREMENTS_CALL_MISSING)
    return "XR_ERROR_GRAPHICS_REQUIREMENTS_CALL_MISSING";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 9 && XR_MSFT_secondary_view_configuration
  if (result == XR_ERROR_SECONDARY_VIEW_CONFIGURATION_TYPE_NOT_ENABLED_MSFT)
    return "XR_ERROR_SECONDARY_VIEW_CONFIGURATION_TYPE_NOT_ENABLED_MSFT";
#endif
#if (XR_CURRENT_API_VERSION & 0xffffffffULL) >= 1 && XR_MSFT_spatial_anchor
  if (result == XR_ERROR_CREATE_SPATIAL_ANCHOR_FAILED_MSFT)
    return "XR_ERROR_CREATE_SPATIAL_ANCHOR_FAILED_MSFT";
#endif
  if (result == XR_SUCCESS)
    return "XR_SUCCESS";
  if (result == XR_TIMEOUT_EXPIRED)
    return "XR_TIMEOUT_EXPIRED";
  if (result == XR_SESSION_LOSS_PENDING)
    return "XR_SESSION_LOSS_PENDING";
  if (result == XR_EVENT_UNAVAILABLE)
    return "XR_EVENT_UNAVAILABLE";
  if (result == XR_SPACE_BOUNDS_UNAVAILABLE)
    return "XR_SPACE_BOUNDS_UNAVAILABLE";
  if (result == XR_SESSION_NOT_FOCUSED)
    return "XR_SESSION_NOT_FOCUSED";
  if (result == XR_FRAME_DISCARDED)
    return "XR_FRAME_DISCARDED";
  if (result == XR_ERROR_VALIDATION_FAILURE)
    return "XR_ERROR_VALIDATION_FAILURE";
  if (result == XR_ERROR_RUNTIME_FAILURE)
    return "XR_ERROR_RUNTIME_FAILURE";
  if (result == XR_ERROR_OUT_OF_MEMORY)
    return "XR_ERROR_OUT_OF_MEMORY";
  if (result == XR_ERROR_API_VERSION_UNSUPPORTED)
    return "XR_ERROR_API_VERSION_UNSUPPORTED";
  if (result == XR_ERROR_INITIALIZATION_FAILED)
    return "XR_ERROR_INITIALIZATION_FAILED";
  if (result == XR_ERROR_FUNCTION_UNSUPPORTED)
    return "XR_ERROR_FUNCTION_UNSUPPORTED";
  if (result == XR_ERROR_FEATURE_UNSUPPORTED)
    return "XR_ERROR_FEATURE_UNSUPPORTED";
  if (result == XR_ERROR_EXTENSION_NOT_PRESENT)
    return "XR_ERROR_EXTENSION_NOT_PRESENT";
  if (result == XR_ERROR_LIMIT_REACHED)
    return "XR_ERROR_LIMIT_REACHED";
  if (result == XR_ERROR_SIZE_INSUFFICIENT)
    return "XR_ERROR_SIZE_INSUFFICIENT";
  if (result == XR_ERROR_HANDLE_INVALID)
    return "XR_ERROR_HANDLE_INVALID";
  if (result == XR_ERROR_INSTANCE_LOST)
    return "XR_ERROR_INSTANCE_LOST";
  if (result == XR_ERROR_SESSION_RUNNING)
    return "XR_ERROR_SESSION_RUNNING";
  if (result == XR_ERROR_SESSION_NOT_RUNNING)
    return "XR_ERROR_SESSION_NOT_RUNNING";
  if (result == XR_ERROR_SESSION_LOST)
    return "XR_ERROR_SESSION_LOST";
  if (result == XR_ERROR_SYSTEM_INVALID)
    return "XR_ERROR_SYSTEM_INVALID";
  if (result == XR_ERROR_PATH_INVALID)
    return "XR_ERROR_PATH_INVALID";
  if (result == XR_ERROR_PATH_COUNT_EXCEEDED)
    return "XR_ERROR_PATH_COUNT_EXCEEDED";
  if (result == XR_ERROR_PATH_FORMAT_INVALID)
    return "XR_ERROR_PATH_FORMAT_INVALID";
  if (result == XR_ERROR_PATH_UNSUPPORTED)
    return "XR_ERROR_PATH_UNSUPPORTED";
  if (result == XR_ERROR_LAYER_INVALID)
    return "XR_ERROR_LAYER_INVALID";
  if (result == XR_ERROR_LAYER_LIMIT_EXCEEDED)
    return "XR_ERROR_LAYER_LIMIT_EXCEEDED";
  if (result == XR_ERROR_SWAPCHAIN_RECT_INVALID)
    return "XR_ERROR_SWAPCHAIN_RECT_INVALID";
  if (result == XR_ERROR_SWAPCHAIN_FORMAT_UNSUPPORTED)
    return "XR_ERROR_SWAPCHAIN_FORMAT_UNSUPPORTED";
  if (result == XR_ERROR_ACTION_TYPE_MISMATCH)
    return "XR_ERROR_ACTION_TYPE_MISMATCH";
  if (result == XR_ERROR_SESSION_NOT_READY)
    return "XR_ERROR_SESSION_NOT_READY";
  if (result == XR_ERROR_SESSION_NOT_STOPPING)
    return "XR_ERROR_SESSION_NOT_STOPPING";
  if (result == XR_ERROR_TIME_INVALID)
    return "XR_ERROR_TIME_INVALID";
  if (result == XR_ERROR_REFERENCE_SPACE_UNSUPPORTED)
    return "XR_ERROR_REFERENCE_SPACE_UNSUPPORTED";
  if (result == XR_ERROR_FILE_ACCESS_ERROR)
    return "XR_ERROR_FILE_ACCESS_ERROR";
  if (result == XR_ERROR_FILE_CONTENTS_INVALID)
    return "XR_ERROR_FILE_CONTENTS_INVALID";
  if (result == XR_ERROR_FORM_FACTOR_UNSUPPORTED)
    return "XR_ERROR_FORM_FACTOR_UNSUPPORTED";
  if (result == XR_ERROR_FORM_FACTOR_UNAVAILABLE)
    return "XR_ERROR_FORM_FACTOR_UNAVAILABLE";
  if (result == XR_ERROR_API_LAYER_NOT_PRESENT)
    return "XR_ERROR_API_LAYER_NOT_PRESENT";
  if (result == XR_ERROR_CALL_ORDER_INVALID)
    return "XR_ERROR_CALL_ORDER_INVALID";
  if (result == XR_ERROR_GRAPHICS_DEVICE_INVALID)
    return "XR_ERROR_GRAPHICS_DEVICE_INVALID";
  if (result == XR_ERROR_POSE_INVALID)
    return "XR_ERROR_POSE_INVALID";
  if (result == XR_ERROR_INDEX_OUT_OF_RANGE)
    return "XR_ERROR_INDEX_OUT_OF_RANGE";
  if (result == XR_ERROR_VIEW_CONFIGURATION_TYPE_UNSUPPORTED)
    return "XR_ERROR_VIEW_CONFIGURATION_TYPE_UNSUPPORTED";
  if (result == XR_ERROR_ENVIRONMENT_BLEND_MODE_UNSUPPORTED)
    return "XR_ERROR_ENVIRONMENT_BLEND_MODE_UNSUPPORTED";
  if (result == XR_ERROR_NAME_DUPLICATED)
    return "XR_ERROR_NAME_DUPLICATED";
  if (result == XR_ERROR_NAME_INVALID)
    return "XR_ERROR_NAME_INVALID";
  if (result == XR_ERROR_ACTIONSET_NOT_ATTACHED)
    return "XR_ERROR_ACTIONSET_NOT_ATTACHED";
  if (result == XR_ERROR_ACTIONSETS_ALREADY_ATTACHED)
    return "XR_ERROR_ACTIONSETS_ALREADY_ATTACHED";
  if (result == XR_ERROR_LOCALIZED_NAME_DUPLICATED)
    return "XR_ERROR_LOCALIZED_NAME_DUPLICATED";
  if (result == XR_ERROR_LOCALIZED_NAME_INVALID)
    return "XR_ERROR_LOCALIZED_NAME_INVALID";
#if XR_KHR_android_thread_settings
  if (result == XR_ERROR_ANDROID_THREAD_SETTINGS_ID_INVALID_KHR)
    return "XR_ERROR_ANDROID_THREAD_SETTINGS_ID_INVALID_KHR";
#endif
#if XR_KHR_android_thread_settings
  if (result == XR_ERROR_ANDROID_THREAD_SETTINGS_FAILURE_KHR)
    return "XR_ERROR_ANDROID_THREAD_SETTINGS_FAILURE_KHR";
#endif

  return NULL;
}

#endif // XR_RESULT_TO_STRING_CONFIG_MAIN

#ifdef __cplusplus
}
#endif

#endif // XR_RESULT_TO_STRING_H
