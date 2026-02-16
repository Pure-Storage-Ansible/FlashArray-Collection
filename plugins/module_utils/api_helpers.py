# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Pure Storage Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Centralized API helper functions for FlashArray modules.

This module provides utilities to reduce code duplication across modules,
particularly for context-aware API calls and version checking.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.purestorage.flasharray.plugins.module_utils.version import (
    LooseVersion,
)


def get_cached_api_version(array):
    """Get API version with caching to avoid repeated calls.

    Args:
        array: FlashArray client instance

    Returns:
        str: API version string (e.g., "2.38")
    """
    if not hasattr(array, "_cached_api_version"):
        array._cached_api_version = array.get_rest_version()
    return array._cached_api_version


def check_api_version(array, min_version, module, feature_name=None):
    """Check if array API version meets minimum requirement.

    Args:
        array: FlashArray client instance
        min_version: Minimum required API version string
        module: AnsibleModule instance
        feature_name: Optional name of feature for error message

    Returns:
        bool: True if API version is sufficient, False otherwise

    Raises:
        Fails module if API version is insufficient and feature_name is provided
    """
    api_version = get_cached_api_version(array)
    version_ok = LooseVersion(min_version) <= LooseVersion(api_version)

    if not version_ok and feature_name:
        module.fail_json(
            msg=f"{feature_name} requires API version {min_version} or higher. "
            f"Current version: {api_version}. Please upgrade Purity."
        )

    return version_ok


def get_with_context(array, method_name, context_version, module, **kwargs):
    """Call array API method with context support if API version allows.

    This is the primary helper to eliminate duplicated context-aware API calls.
    Automatically adds context_names parameter if:
    1. API version supports it (>= context_version)
    2. Module has a 'context' parameter
    3. Context parameter is not None/empty

    Args:
        array: FlashArray client instance
        method_name: Name of method to call (e.g., 'get_protection_groups')
        context_version: Minimum API version for context support (e.g., "2.38")
        module: AnsibleModule instance
        **kwargs: Arguments to pass to the method

    Returns:
        API response object

    Example:
        # Instead of:
        api_version = array.get_rest_version()
        if LooseVersion("2.38") <= LooseVersion(api_version):
            res = array.get_protection_groups(
                names=[name],
                context_names=[module.params["context"]]
            )
        else:
            res = array.get_protection_groups(names=[name])

        # Use:
        res = get_with_context(
            array, 'get_protection_groups', "2.38", module,
            names=[name]
        )
    """
    api_version = get_cached_api_version(array)
    method = getattr(array, method_name)

    # Add context if API version supports it and context is provided
    if LooseVersion(context_version) <= LooseVersion(api_version) and module.params.get(
        "context"
    ):
        kwargs["context_names"] = [module.params["context"]]

    return method(**kwargs)


def post_with_context(array, method_name, context_version, module, **kwargs):
    """Alias for get_with_context for POST operations.

    Identical to get_with_context but named for clarity when doing POST operations.
    """
    return get_with_context(array, method_name, context_version, module, **kwargs)


def patch_with_context(array, method_name, context_version, module, **kwargs):
    """Alias for get_with_context for PATCH operations.

    Identical to get_with_context but named for clarity when doing PATCH operations.
    """
    return get_with_context(array, method_name, context_version, module, **kwargs)


def delete_with_context(array, method_name, context_version, module, **kwargs):
    """Alias for get_with_context for DELETE operations.

    Identical to get_with_context but named for clarity when doing DELETE operations.
    """
    return get_with_context(array, method_name, context_version, module, **kwargs)


def check_response(response, module, operation="Operation"):
    """Check API response and fail module if error occurred.

    Args:
        response: API response object
        module: AnsibleModule instance
        operation: Description of operation for error message

    Raises:
        Fails module with appropriate error message if response indicates error
    """
    if hasattr(response, "status_code") and response.status_code != 200:
        error_detail = (
            response.errors[0].message
            if hasattr(response, "errors") and response.errors
            else "Unknown error"
        )
        module.fail_json(
            msg=f"{operation} failed. Error: {error_detail}",
            status_code=response.status_code,
            changed=False,
        )
