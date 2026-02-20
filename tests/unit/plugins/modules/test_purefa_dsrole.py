# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_dsrole module."""

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

from plugins.modules.purefa_dsrole import (
    delete_role,
    create_role,
    update_role,
)


class TestDeleteRole:
    """Tests for delete_role function"""

    @patch("plugins.modules.purefa_dsrole.LooseVersion")
    def test_delete_role_check_mode(self, mock_loose_version):
        """Test delete_role in check mode"""
        mock_module = Mock()
        mock_module.params = {"name": "role1", "context": ""}
        mock_module.check_mode = True
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_loose_version.side_effect = LooseVersion

        delete_role(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestCreateRole:
    """Tests for create_role function"""

    @patch("plugins.modules.purefa_dsrole.LooseVersion")
    def test_create_role_check_mode(self, mock_loose_version):
        """Test create_role in check mode"""
        mock_module = Mock()
        mock_module.params = {
            "name": "role1",
            "context": "",
            "group": "admins",
            "group_base": "ou=groups,dc=example,dc=com",
            "role": "array_admin",
        }
        mock_module.check_mode = True
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_loose_version.side_effect = LooseVersion

        create_role(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_dsrole.LooseVersion")
    def test_create_role_no_change(self, mock_loose_version):
        """Test create_role when group and group_base are empty"""
        mock_module = Mock()
        mock_module.params = {
            "name": "role1",
            "context": "",
            "group": "",
            "group_base": "",
            "role": "array_admin",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_loose_version.side_effect = LooseVersion

        create_role(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=False)

    @patch("plugins.modules.purefa_dsrole.check_response")
    @patch("plugins.modules.purefa_dsrole.LooseVersion")
    def test_create_role_success(self, mock_loose_version, mock_check_response):
        """Test create_role successfully creates"""
        mock_module = Mock()
        mock_module.params = {
            "name": "role1",
            "context": "",
            "group": "admins",
            "group_base": "ou=groups,dc=example,dc=com",
            "role": "array_admin",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.post_directory_services_roles.return_value = Mock(status_code=200)
        mock_loose_version.side_effect = LooseVersion

        create_role(mock_module, mock_array)

        mock_array.post_directory_services_roles.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestUpdateRole:
    """Tests for update_role function"""

    @patch("plugins.modules.purefa_dsrole.check_response")
    @patch("plugins.modules.purefa_dsrole.LooseVersion")
    def test_update_role_delete_system_defined(self, mock_loose_version, mock_check_response):
        """Test update_role deletes system-defined role"""
        import pytest

        mock_module = Mock()
        mock_module.params = {
            "name": "array_admin",
            "context": "",
            "state": "absent",
        }
        mock_module.check_mode = False
        mock_module.exit_json.side_effect = SystemExit(0)
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.patch_directory_services_roles.return_value = Mock(status_code=200)
        mock_loose_version.side_effect = LooseVersion

        with pytest.raises(SystemExit):
            update_role(mock_module, mock_array)

        mock_array.patch_directory_services_roles.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_dsrole.LooseVersion")
    def test_update_role_delete_check_mode(self, mock_loose_version):
        """Test update_role delete in check mode"""
        import pytest

        mock_module = Mock()
        mock_module.params = {
            "name": "array_admin",
            "context": "",
            "state": "absent",
        }
        mock_module.check_mode = True
        mock_module.exit_json.side_effect = SystemExit(0)
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_loose_version.side_effect = LooseVersion

        with pytest.raises(SystemExit):
            update_role(mock_module, mock_array)

        mock_array.patch_directory_services_roles.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_dsrole.LooseVersion")
    def test_update_role_system_role_no_change(self, mock_loose_version):
        """Test update_role for system role when no changes needed"""
        mock_module = Mock()
        mock_module.params = {
            "name": "array_admin",
            "context": "",
            "state": "present",
            "group": "admins",
            "group_base": "ou=groups,dc=example,dc=com",
            "role": "array_admin",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_loose_version.side_effect = LooseVersion

        # Mock current role with same values
        mock_role = Mock()
        mock_role.group = "admins"
        mock_role.group_base = "ou=groups,dc=example,dc=com"
        mock_array.get_directory_services_roles.return_value.items = [mock_role]

        update_role(mock_module, mock_array)

        mock_array.patch_directory_services_roles.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=False)

    @patch("plugins.modules.purefa_dsrole.check_response")
    @patch("plugins.modules.purefa_dsrole.LooseVersion")
    def test_update_role_custom_role_with_changes(self, mock_loose_version, mock_check_response):
        """Test update_role for custom role when changes needed"""
        mock_module = Mock()
        mock_module.params = {
            "name": "custom_role",
            "context": "",
            "state": "present",
            "group": "new-admins",
            "group_base": "ou=new-groups,dc=example,dc=com",
            "role": "storage_admin",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.patch_directory_services_roles.return_value = Mock(status_code=200)
        mock_loose_version.side_effect = LooseVersion

        # Mock current role with different values
        mock_role = Mock()
        mock_role.group = "old-admins"
        mock_role.group_base = "ou=old-groups,dc=example,dc=com"
        mock_role_ref = Mock()
        mock_role_ref.name = "array_admin"
        mock_role.role = mock_role_ref
        mock_array.get_directory_services_roles.return_value.items = [mock_role]

        update_role(mock_module, mock_array)

        mock_array.patch_directory_services_roles.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)
