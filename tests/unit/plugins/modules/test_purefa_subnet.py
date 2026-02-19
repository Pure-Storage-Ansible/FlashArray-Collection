"""
Unit tests for purefa_subnet module

Tests for Subnet management functions
"""

import sys
from unittest.mock import Mock, MagicMock

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

from plugins.modules.purefa_subnet import (
    _get_subnet,
    delete_subnet,
)


class TestGetSubnet:
    """Tests for _get_subnet function"""

    def test_get_subnet_exists(self):
        """Test _get_subnet returns subnet when it exists"""
        mock_module = Mock()
        mock_module.params = {"name": "subnet1"}
        mock_array = Mock()
        mock_subnet = Mock()
        mock_subnet.name = "subnet1"
        mock_array.get_subnets.return_value = Mock(status_code=200, items=[mock_subnet])

        result = _get_subnet(mock_module, mock_array)

        assert result == mock_subnet
        mock_array.get_subnets.assert_called_once_with(names=["subnet1"])

    def test_get_subnet_not_exists(self):
        """Test _get_subnet returns None when subnet doesn't exist"""
        mock_module = Mock()
        mock_module.params = {"name": "nonexistent"}
        mock_array = Mock()
        mock_array.get_subnets.return_value = Mock(status_code=400, items=[])

        result = _get_subnet(mock_module, mock_array)

        assert result is None


class TestDeleteSubnet:
    """Tests for delete_subnet function"""

    def test_delete_subnet_check_mode(self):
        """Test delete_subnet in check mode"""
        mock_module = Mock()
        mock_module.params = {"name": "subnet1"}
        mock_module.check_mode = True
        mock_array = Mock()

        delete_subnet(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.delete_subnets.assert_not_called()

    def test_delete_subnet_success(self):
        """Test delete_subnet successfully deletes"""
        mock_module = Mock()
        mock_module.params = {"name": "subnet1"}
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.delete_subnets.return_value = Mock(status_code=200)

        delete_subnet(mock_module, mock_array)

        mock_array.delete_subnets.assert_called_once_with(names=["subnet1"])
        mock_module.exit_json.assert_called_with(changed=True)
