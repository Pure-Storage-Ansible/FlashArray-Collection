"""
Unit tests for purefa_fleet module

Tests for Fleet management functions
"""

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

from plugins.modules.purefa_fleet import (
    create_fleet,
    delete_fleet,
    rename_fleet,
)


class TestCreateFleet:
    """Test cases for create_fleet function"""

    def test_create_fleet_check_mode(self):
        """Test create_fleet in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-fleet"}
        mock_array = Mock()

        create_fleet(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.post_fleets.assert_not_called()

    @patch("plugins.modules.purefa_fleet.check_response")
    def test_create_fleet_success(self, mock_check_response):
        """Test create_fleet creates fleet"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "test-fleet"}
        mock_array = Mock()
        mock_array.post_fleets.return_value = Mock(status_code=200)

        create_fleet(mock_module, mock_array)

        mock_array.post_fleets.assert_called_once_with(names=["test-fleet"])
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestDeleteFleet:
    """Test cases for delete_fleet function"""

    def test_delete_fleet_check_mode(self):
        """Test delete_fleet in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-fleet"}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.39"

        delete_fleet(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRenameFleet:
    """Test cases for rename_fleet function"""

    def test_rename_fleet_no_change(self):
        """Test rename_fleet when name unchanged"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"rename": "current-fleet"}
        mock_array = Mock()
        mock_fleet = Mock()
        mock_fleet.name = "current-fleet"
        mock_array.get_fleets.return_value = Mock(items=[mock_fleet])

        rename_fleet(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=False)

    def test_rename_fleet_check_mode(self):
        """Test rename_fleet in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"rename": "new-fleet"}
        mock_array = Mock()
        mock_fleet = Mock()
        mock_fleet.name = "old-fleet"
        mock_array.get_fleets.return_value = Mock(items=[mock_fleet])

        rename_fleet(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
