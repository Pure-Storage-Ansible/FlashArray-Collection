# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_ds module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from unittest.mock import Mock, MagicMock, patch

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

from plugins.modules.purefa_ds import (
    delete_ds,
    test_ds as ds_test_func,
)


class TestDeleteDs:
    """Tests for delete_ds function"""

    def test_delete_ds_check_mode(self):
        """Test delete_ds in check mode for management type"""
        mock_module = Mock()
        mock_module.params = {"dstype": "management", "context": ""}
        mock_module.check_mode = True
        mock_array = Mock()

        delete_ds(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestDsTest:
    """Tests for test_ds function"""

    @patch("plugins.modules.purefa_ds.get_with_context")
    def test_ds_test_returns_response(self, mock_get_with_context):
        """Test test_ds returns test response"""
        mock_module = Mock()
        mock_module.params = {"dstype": "management", "context": ""}
        mock_array = Mock()

        # Create mock test result
        mock_result = Mock()
        mock_result.enabled = True
        mock_result.success = True
        mock_result.component_address = "10.0.0.1"
        mock_result.component_name = "ds1"
        mock_result.description = "Directory service test"
        mock_result.destination = "ldap.example.com"
        mock_result.result_details = "OK"
        mock_result.test_type = "connectivity"
        mock_result.resource = Mock()
        mock_result.resource.name = "array1"
        mock_get_with_context.return_value = Mock(items=[mock_result])

        ds_test_func(mock_module, mock_array)

        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args[1]
        assert call_args["changed"] is False
        assert len(call_args["test_response"]) == 1
        assert call_args["test_response"][0]["enabled"] == "true"
        assert call_args["test_response"][0]["success"] == "true"


class TestDeleteDsExtended:
    """Extended tests for delete_ds function"""

    @patch("plugins.modules.purefa_ds.check_response")
    @patch("plugins.modules.purefa_ds.get_with_context")
    def test_delete_ds_management_success(
        self, mock_get_with_context, mock_check_response
    ):
        """Test deleting management directory service"""
        mock_module = Mock()
        mock_module.params = {"dstype": "management", "context": ""}
        mock_module.check_mode = False
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        delete_ds(mock_module, mock_array)

        mock_get_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_ds.check_response")
    @patch("plugins.modules.purefa_ds.get_with_context")
    def test_delete_ds_data_success(self, mock_get_with_context, mock_check_response):
        """Test deleting data directory service"""
        mock_module = Mock()
        mock_module.params = {"dstype": "data", "context": ""}
        mock_module.check_mode = False
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        delete_ds(mock_module, mock_array)

        mock_get_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_delete_ds_data_check_mode(self):
        """Test delete_ds in check mode for data type"""
        mock_module = Mock()
        mock_module.params = {"dstype": "data", "context": ""}
        mock_module.check_mode = True
        mock_array = Mock()

        delete_ds(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestUpdateDs:
    """Tests for update_ds function"""

    @patch("plugins.modules.purefa_ds.check_response")
    @patch("plugins.modules.purefa_ds.get_with_context")
    def test_update_ds_no_changes(self, mock_get_with_context, mock_check_response):
        """Test update_ds when no changes needed"""
        mock_module = Mock()
        mock_module.params = {
            "dstype": "management",
            "context": "",
            "uri": None,
            "base_dn": None,
            "enable": True,
            "bind_user": None,
            "bind_password": None,
            "force_bind_password": False,
            "certificate": None,
            "check_peer": False,
            "user_object": None,
            "user_login": None,
        }
        mock_module.check_mode = False
        mock_array = Mock()

        # Create mock current directory service
        mock_ds = Mock()
        mock_ds.name = "management"
        mock_ds.uris = ["ldap://test.example.com"]
        mock_ds.base_dn = "DC=example,DC=com"
        mock_ds.bind_user = "admin"
        mock_ds.enabled = True
        mock_ds.check_peer = False
        mock_ds.ca_certificate = None
        mock_ds.management = Mock()
        mock_ds.management.user_login_attribute = "sAMAccountName"
        mock_ds.management.user_object_class = "User"
        mock_get_with_context.return_value = Mock(items=[mock_ds])

        from plugins.modules.purefa_ds import update_ds

        update_ds(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=False)

    @patch("plugins.modules.purefa_ds.DirectoryService")
    @patch("plugins.modules.purefa_ds.DirectoryServiceManagement")
    @patch("plugins.modules.purefa_ds.check_response")
    @patch("plugins.modules.purefa_ds.get_with_context")
    def test_update_ds_uri_change(
        self,
        mock_get_with_context,
        mock_check_response,
        mock_ds_mgmt,
        mock_ds_class,
    ):
        """Test update_ds when URI changes"""
        mock_module = Mock()
        mock_module.params = {
            "dstype": "management",
            "context": "",
            "uri": ["ldap://new.example.com"],
            "base_dn": None,
            "enable": True,
            "bind_user": "admin",
            "bind_password": "newpassword",
            "force_bind_password": True,
            "certificate": None,
            "check_peer": False,
            "user_object": None,
            "user_login": None,
        }
        mock_module.check_mode = False
        mock_array = Mock()

        # Create mock current directory service
        mock_ds = Mock()
        mock_ds.name = "management"
        mock_ds.uris = ["ldap://old.example.com"]
        mock_ds.base_dn = "DC=example,DC=com"
        mock_ds.bind_user = "admin"
        mock_ds.enabled = True
        mock_ds.check_peer = False
        mock_ds.ca_certificate = None
        mock_ds.management = Mock()
        mock_ds.management.user_login_attribute = "sAMAccountName"
        mock_ds.management.user_object_class = "User"
        mock_get_with_context.return_value = Mock(items=[mock_ds], status_code=200)

        from plugins.modules.purefa_ds import update_ds

        update_ds(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_ds.DirectoryService")
    @patch("plugins.modules.purefa_ds.check_response")
    @patch("plugins.modules.purefa_ds.get_with_context")
    def test_update_ds_data_type(
        self, mock_get_with_context, mock_check_response, mock_ds_class
    ):
        """Test update_ds for data directory service type"""
        mock_module = Mock()
        mock_module.params = {
            "dstype": "data",
            "context": "",
            "uri": ["ldap://data.example.com"],
            "base_dn": "DC=data,DC=com",
            "enable": True,
            "bind_user": "dataadmin",
            "bind_password": "datapassword",
            "force_bind_password": True,
            "certificate": None,
            "check_peer": False,
            "user_object": None,
            "user_login": None,
        }
        mock_module.check_mode = False
        mock_array = Mock()

        # Create mock current directory service - data type
        mock_ds = Mock()
        mock_ds.name = "data"
        mock_ds.uris = None
        mock_ds.base_dn = None
        mock_ds.bind_user = None
        mock_ds.enabled = False
        mock_ds.check_peer = False
        mock_get_with_context.return_value = Mock(items=[mock_ds], status_code=200)

        from plugins.modules.purefa_ds import update_ds

        update_ds(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_update_ds_check_mode(self):
        """Test update_ds in check mode"""
        mock_module = Mock()
        mock_module.params = {
            "dstype": "management",
            "context": "",
            "uri": ["ldap://new.example.com"],
            "base_dn": "DC=new,DC=com",
            "enable": True,
            "bind_user": "newadmin",
            "bind_password": "newpassword",
            "force_bind_password": True,
            "certificate": None,
            "check_peer": False,
            "user_object": None,
            "user_login": None,
        }
        mock_module.check_mode = True
        mock_array = Mock()

        # Create mock current directory service
        mock_ds = Mock()
        mock_ds.name = "management"
        mock_ds.uris = ["ldap://old.example.com"]
        mock_ds.base_dn = "DC=old,DC=com"
        mock_ds.bind_user = "oldadmin"
        mock_ds.enabled = False
        mock_ds.check_peer = False
        mock_ds.ca_certificate = None
        mock_ds.management = Mock()
        mock_ds.management.user_login_attribute = "sAMAccountName"
        mock_ds.management.user_object_class = "User"

        with patch("plugins.modules.purefa_ds.get_with_context") as mock_get:
            mock_get.return_value = Mock(items=[mock_ds])
            from plugins.modules.purefa_ds import update_ds

            update_ds(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_ds.get_with_context")
    def test_update_ds_missing_bind_password(self, mock_get_with_context):
        """Test update_ds fails when bind_password is required but not provided"""
        import pytest

        mock_module = Mock()
        mock_module.params = {
            "dstype": "management",
            "context": "",
            "uri": ["ldap://new.example.com"],
            "base_dn": None,
            "enable": True,
            "bind_user": "newadmin",
            "bind_password": None,
            "force_bind_password": True,
            "certificate": None,
            "check_peer": False,
            "user_object": None,
            "user_login": None,
        }
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_array = Mock()

        mock_ds = Mock()
        mock_ds.name = "management"
        mock_ds.uris = ["ldap://old.example.com"]
        mock_ds.bind_user = "oldadmin"
        mock_ds.enabled = True
        mock_ds.check_peer = False
        mock_ds.ca_certificate = None
        mock_ds.management = Mock()
        mock_ds.management.user_login_attribute = "sAMAccountName"
        mock_ds.management.user_object_class = "User"
        mock_get_with_context.return_value = Mock(items=[mock_ds])

        from plugins.modules.purefa_ds import update_ds

        with pytest.raises(SystemExit):
            update_ds(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()
        assert "bind_password" in mock_module.fail_json.call_args[1]["msg"]
