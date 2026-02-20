# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_snmp module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

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

from unittest.mock import patch

from plugins.modules.purefa_snmp import (
    delete_manager,
    create_manager,
    update_manager,
    test_manager as snmp_test_manager,
)


class TestDeleteManager:
    """Tests for delete_manager function"""

    def test_delete_manager_check_mode(self):
        """Test delete_manager in check mode"""
        mock_module = Mock()
        mock_module.params = {"name": "snmp1"}
        mock_module.check_mode = True
        mock_array = Mock()

        delete_manager(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.delete_snmp_managers.assert_not_called()

    def test_delete_manager_success(self):
        """Test delete_manager successfully deletes"""
        mock_module = Mock()
        mock_module.params = {"name": "snmp1"}
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.delete_snmp_managers.return_value = Mock(status_code=200)

        delete_manager(mock_module, mock_array)

        mock_array.delete_snmp_managers.assert_called_once_with(names=["snmp1"])
        mock_module.exit_json.assert_called_with(changed=True)


class TestCreateManager:
    """Tests for create_manager function"""

    def test_create_manager_check_mode(self):
        """Test create_manager in check mode"""
        mock_module = Mock()
        mock_module.params = {
            "name": "snmp1",
            "version": "v2c",
            "host": "192.168.1.100",
            "community": "public",
            "notification": "trap",
        }
        mock_module.check_mode = True
        mock_array = Mock()

        create_manager(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.post_snmp_managers.assert_not_called()

    @patch("plugins.modules.purefa_snmp.check_response")
    def test_create_manager_v2c_success(self, mock_check_response):
        """Test create_manager with v2c version"""
        mock_module = Mock()
        mock_module.params = {
            "name": "snmp1",
            "version": "v2c",
            "host": "192.168.1.100",
            "community": "public",
            "notification": "trap",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.post_snmp_managers.return_value = Mock(status_code=200)

        create_manager(mock_module, mock_array)

        mock_array.post_snmp_managers.assert_called_once()
        mock_module.exit_json.assert_called_with(changed=True)


class TestSnmpTestManager:
    """Tests for test_manager function"""

    def test_snmp_test_manager_success(self):
        """Test test_manager returns test results"""
        mock_module = Mock()
        mock_module.params = {"name": "snmp1"}
        mock_array = Mock()

        # Create mock test response component
        mock_component = Mock()
        mock_component.enabled = True
        mock_component.success = True
        mock_component.component_address = "192.168.1.100"
        mock_component.component_name = "snmp1"
        mock_component.description = "Test description"
        mock_component.destination = "192.168.1.200"
        mock_component.result_details = "Success"
        mock_component.test_type = "trap"
        mock_component.resource = Mock()
        mock_component.resource.name = "test-resource"

        mock_array.get_snmp_managers_test.return_value.items = [mock_component]

        snmp_test_manager(mock_module, mock_array)

        mock_array.get_snmp_managers_test.assert_called_once_with(names=["snmp1"])
        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args
        assert call_args[1]["changed"] is True
        assert len(call_args[1]["test_response"]) == 1
        assert call_args[1]["test_response"][0]["enabled"] == "true"
        assert call_args[1]["test_response"][0]["success"] == "true"

    def test_snmp_test_manager_disabled_and_failed(self):
        """Test test_manager with disabled and failed component"""
        mock_module = Mock()
        mock_module.params = {"name": "snmp1"}
        mock_array = Mock()

        mock_component = Mock()
        mock_component.enabled = False
        mock_component.success = False
        mock_component.component_address = "192.168.1.100"
        mock_component.component_name = "snmp1"
        mock_component.description = "Test description"
        mock_component.destination = "192.168.1.200"
        mock_component.test_type = "trap"
        mock_component.resource = Mock()
        mock_component.resource.name = "test-resource"
        # No result_details attribute
        del mock_component.result_details

        mock_array.get_snmp_managers_test.return_value.items = [mock_component]

        snmp_test_manager(mock_module, mock_array)

        call_args = mock_module.exit_json.call_args
        assert call_args[1]["test_response"][0]["enabled"] == "false"
        assert call_args[1]["test_response"][0]["success"] == "false"


class TestUpdateManager:
    """Test cases for update_manager function"""

    @patch("plugins.modules.purefa_snmp.check_response")
    def test_update_manager_version_change_fails(self, mock_check_response):
        """Test update_manager fails when version changes"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_module.params = {
            "name": "snmp1",
            "version": "v3",
        }
        mock_array = Mock()
        mock_mgr = Mock()
        mock_mgr.version = "v2c"  # Different from params
        mock_array.get_snmp_managers.return_value = Mock(
            status_code=200, items=[mock_mgr]
        )

        with pytest.raises(SystemExit):
            update_manager(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()

    @patch("plugins.modules.purefa_snmp.check_response")
    def test_update_manager_v2c_check_mode(self, mock_check_response):
        """Test update_manager v2c in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "snmp1",
            "version": "v2c",
            "community": "public",
            "notification": "trap",
            "host": "192.168.1.100",
        }
        mock_array = Mock()
        mock_mgr = Mock()
        mock_mgr.version = "v2c"
        mock_array.get_snmp_managers.return_value = Mock(
            status_code=200, items=[mock_mgr]
        )

        update_manager(mock_module, mock_array)

        mock_array.patch_snmp_managers.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_snmp.check_response")
    def test_update_manager_v2c_success(self, mock_check_response):
        """Test update_manager v2c succeeds"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "snmp1",
            "version": "v2c",
            "community": "public",
            "notification": "trap",
            "host": "192.168.1.100",
        }
        mock_array = Mock()
        mock_mgr = Mock()
        mock_mgr.version = "v2c"
        mock_array.get_snmp_managers.return_value = Mock(
            status_code=200, items=[mock_mgr]
        )
        mock_array.patch_snmp_managers.return_value = Mock(status_code=200)

        update_manager(mock_module, mock_array)

        mock_array.patch_snmp_managers.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)
