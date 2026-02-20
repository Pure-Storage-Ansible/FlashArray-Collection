# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_volume_tags module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from unittest.mock import Mock, patch, MagicMock

# Mock external dependencies before importing module
sys.modules["grp"] = MagicMock()
sys.modules["pwd"] = MagicMock()
sys.modules["fcntl"] = MagicMock()
sys.modules["ansible"] = MagicMock()
sys.modules["ansible.module_utils"] = MagicMock()
sys.modules["ansible.module_utils.basic"] = MagicMock()
sys.modules["pypureclient"] = MagicMock()
sys.modules["pypureclient.flasharray"] = MagicMock()
sys.modules["ansible_collections"] = MagicMock()
sys.modules["ansible_collections.purestorage"] = MagicMock()
sys.modules["ansible_collections.purestorage.flasharray"] = MagicMock()
sys.modules["ansible_collections.purestorage.flasharray.plugins"] = MagicMock()
sys.modules["ansible_collections.purestorage.flasharray.plugins.module_utils"] = (
    MagicMock()
)
sys.modules[
    "ansible_collections.purestorage.flasharray.plugins.module_utils.purefa"
] = MagicMock()
sys.modules[
    "ansible_collections.purestorage.flasharray.plugins.module_utils.common"
] = MagicMock()
sys.modules[
    "ansible_collections.purestorage.flasharray.plugins.module_utils.api_helpers"
] = MagicMock()
sys.modules[
    "ansible_collections.purestorage.flasharray.plugins.module_utils.error_handlers"
] = MagicMock()

# Create a mock version module with real LooseVersion
mock_version_module = MagicMock()
from packaging.version import Version as LooseVersion

mock_version_module.LooseVersion = LooseVersion
sys.modules[
    "ansible_collections.purestorage.flasharray.plugins.module_utils.version"
] = mock_version_module

from plugins.modules.purefa_volume_tags import (
    get_volume,
    get_endpoint,
)


class TestGetVolume:
    """Test cases for get_volume function"""

    @patch("plugins.modules.purefa_volume_tags.get_with_context")
    def test_get_volume_exists(self, mock_get_with_context):
        """Test get_volume returns volume when it exists"""
        mock_module = Mock()
        mock_module.params = {"name": "test-vol", "context": ""}
        mock_array = Mock()
        mock_vol = Mock()
        mock_vol.name = "test-vol"
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_vol])

        result = get_volume(mock_module, mock_array)

        assert result == mock_vol

    @patch("plugins.modules.purefa_volume_tags.get_with_context")
    def test_get_volume_not_exists(self, mock_get_with_context):
        """Test get_volume returns None when volume doesn't exist"""
        mock_module = Mock()
        mock_module.params = {"name": "nonexistent", "context": ""}
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=404, items=[])

        result = get_volume(mock_module, mock_array)

        assert result is None


class TestGetEndpoint:
    """Test cases for get_endpoint function"""

    @patch("plugins.modules.purefa_volume_tags.get_with_context")
    def test_get_endpoint_exists(self, mock_get_with_context):
        """Test get_endpoint returns endpoint when it exists"""
        mock_module = Mock()
        mock_module.params = {"name": "test-endpoint", "context": ""}
        mock_array = Mock()
        mock_vol = Mock()
        mock_vol.name = "test-endpoint"
        mock_vol.subtype = "protocol_endpoint"
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_vol])

        result = get_endpoint(mock_module, mock_array)

        assert result == mock_vol

    @patch("plugins.modules.purefa_volume_tags.get_with_context")
    def test_get_endpoint_not_exists(self, mock_get_with_context):
        """Test get_endpoint returns None when endpoint doesn't exist"""
        mock_module = Mock()
        mock_module.params = {"name": "nonexistent", "context": ""}
        mock_array = Mock()
        mock_vol = Mock()
        # Not a protocol_endpoint - set container_version to None
        mock_vol.protocol_endpoint = Mock()
        mock_vol.protocol_endpoint.container_version = None
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_vol])

        result = get_endpoint(mock_module, mock_array)

        assert result is None
