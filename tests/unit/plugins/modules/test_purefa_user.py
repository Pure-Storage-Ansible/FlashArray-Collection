"""
Unit tests for purefa_user module

Tests for Local User Account management functions
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

from plugins.modules.purefa_user import (
    get_user,
    delete_local_user,
)


class TestGetUser:
    """Test cases for get_user function"""

    def test_get_user_exists(self):
        """Test get_user returns user when it exists"""
        mock_module = Mock()
        mock_module.params = {"name": "test-user"}
        mock_array = Mock()
        mock_user = Mock()
        mock_user.name = "test-user"
        mock_array.get_admins.return_value = Mock(status_code=200, items=[mock_user])

        result = get_user(mock_module, mock_array)

        assert result == mock_user
        mock_array.get_admins.assert_called_once_with(names=["test-user"])

    def test_get_user_not_exists(self):
        """Test get_user returns None when user doesn't exist"""
        mock_module = Mock()
        mock_module.params = {"name": "nonexistent"}
        mock_array = Mock()
        mock_array.get_admins.return_value = Mock(status_code=404, items=[])

        result = get_user(mock_module, mock_array)

        assert result is None


class TestDeleteLocalUser:
    """Test cases for delete_local_user function"""

    def test_delete_local_user_check_mode(self):
        """Test delete_local_user in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-user"}
        mock_array = Mock()

        delete_local_user(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.delete_admins.assert_not_called()
