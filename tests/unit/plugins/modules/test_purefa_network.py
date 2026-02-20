# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_network module."""

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
    "ansible_collections.purestorage.flasharray.plugins.module_utils.version"
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

from unittest.mock import patch

from plugins.modules.purefa_network import (
    delete_interface,
    update_fc_interface,
    update_interface,
    create_interface,
    _check_subinterfaces,
)


class TestDeleteInterface:
    """Test cases for delete_interface function"""

    def test_delete_interface_check_mode(self):
        """Test delete_interface in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "ct0.eth2"}
        mock_array = Mock()

        delete_interface(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestUpdateFcInterface:
    """Test cases for update_fc_interface function"""

    @patch("plugins.modules.purefa_network.check_response")
    def test_update_fc_interface_enable_check_mode(self, mock_check_response):
        """Test enabling FC interface in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "ct0.fc0", "state": "present", "servicelist": None}
        mock_array = Mock()
        mock_interface = Mock(enabled=False, services=[])

        update_fc_interface(mock_module, mock_array, mock_interface)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_network.check_response")
    def test_update_fc_interface_disable_check_mode(self, mock_check_response):
        """Test disabling FC interface in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "ct0.fc0", "state": "absent", "servicelist": None}
        mock_array = Mock()
        mock_interface = Mock(enabled=True, services=[])

        update_fc_interface(mock_module, mock_array, mock_interface)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_network.check_response")
    def test_update_fc_interface_no_change(self, mock_check_response):
        """Test FC interface with no changes needed"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "ct0.fc0", "state": "present", "servicelist": None}
        mock_array = Mock()
        mock_interface = Mock(enabled=True, services=[])

        update_fc_interface(mock_module, mock_array, mock_interface)

        mock_module.exit_json.assert_called_once_with(changed=False)


class TestCheckSubinterfaces:
    """Test cases for _check_subinterfaces function"""

    def test_check_subinterfaces_returns_list(self):
        """Test _check_subinterfaces returns list of subinterfaces"""
        mock_module = Mock()
        mock_module.params = {"name": "ct0.eth0"}
        mock_array = Mock()
        mock_interface = Mock()
        mock_interface.eth.subinterfaces = ["sub1", "sub2"]
        mock_array.get_network_interfaces.return_value.items = [mock_interface]

        result = _check_subinterfaces(mock_module, mock_array)

        assert result == ["sub1", "sub2"]


class TestCreateInterface:
    """Test cases for create_interface function"""

    @patch("plugins.modules.purefa_network._create_subordinates")
    def test_create_interface_subnet_not_exists(self, mock_create_subordinates):
        """Test create_interface fails when subnet doesn't exist"""
        mock_create_subordinates.return_value = ([], [])
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "ct0.eth2",
            "subnet": "test-subnet",
            "interface": "lacpbond",
        }
        mock_array = Mock()
        mock_array.get_subnets.return_value.status_code = 404

        create_interface(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()

    @patch("plugins.modules.purefa_network._create_subordinates")
    def test_create_interface_check_mode(self, mock_create_subordinates):
        """Test create_interface in check mode"""
        mock_create_subordinates.return_value = ([], [])
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "ct0.eth2",
            "subnet": "test-subnet",
            "interface": "lacpbond",
        }
        mock_array = Mock()
        mock_array.get_subnets.return_value.status_code = 200

        create_interface(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestDeleteInterface:
    """Test cases for delete_interface function"""

    def test_delete_interface_success(self):
        """Test delete_interface successfully deletes"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "ct0.eth2"}
        mock_array = Mock()
        mock_array.delete_network_interfaces.return_value = Mock(status_code=200)

        delete_interface(mock_module, mock_array)

        mock_array.delete_network_interfaces.assert_called_once_with(names=["ct0.eth2"])
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestCheckSubinterfacesAdditional:
    """Additional test cases for _check_subinterfaces function"""

    def test_check_subinterfaces_multiple(self):
        """Test _check_subinterfaces returns correct list"""
        mock_module = Mock()
        mock_module.params = {"name": "eth2"}
        mock_array = Mock()

        # Create mock interface with eth.subinterfaces
        mock_interface = Mock()
        mock_interface.eth = Mock()
        mock_interface.eth.subinterfaces = ["eth2.100", "eth2.200"]
        mock_array.get_network_interfaces.return_value = Mock(items=[mock_interface])

        result = _check_subinterfaces(mock_module, mock_array)

        assert result == ["eth2.100", "eth2.200"]

    def test_check_subinterfaces_none(self):
        """Test _check_subinterfaces with no subinterfaces"""
        mock_module = Mock()
        mock_module.params = {"name": "eth2"}
        mock_array = Mock()

        # Create mock interface with empty subinterfaces
        mock_interface = Mock()
        mock_interface.eth = Mock()
        mock_interface.eth.subinterfaces = []
        mock_array.get_network_interfaces.return_value = Mock(items=[mock_interface])

        result = _check_subinterfaces(mock_module, mock_array)

        assert result == []


class TestUpdateInterface:
    """Test cases for update_interface function"""

    def test_update_interface_not_found_fails(self):
        """Test update_interface fails when interface not found"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_module.params = {"name": "eth2"}
        mock_array = Mock()
        mock_array.get_network_interfaces.return_value = Mock(items=[])

        with pytest.raises(SystemExit):
            update_interface(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()

    @patch("plugins.modules.purefa_network.check_response")
    def test_update_fc_interface_enable_success(self, mock_check_response):
        """Test update_interface enables FC interface successfully"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.exit_json.side_effect = SystemExit(0)
        mock_module.params = {
            "name": "ct0.fc0",
            "state": "present",
            "servicelist": None,
        }
        mock_array = Mock()
        mock_interface = Mock()
        mock_interface.enabled = False
        mock_array.get_network_interfaces.return_value = Mock(items=[mock_interface])
        mock_array.patch_network_interfaces.return_value = Mock(status_code=200)

        with pytest.raises(SystemExit):
            update_interface(mock_module, mock_array)

        mock_array.patch_network_interfaces.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_network.check_response")
    def test_update_fc_interface_disable_success(self, mock_check_response):
        """Test update_interface disables FC interface successfully"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.exit_json.side_effect = SystemExit(0)
        mock_module.params = {
            "name": "ct0.fc0",
            "state": "absent",
            "servicelist": None,
        }
        mock_array = Mock()
        mock_interface = Mock()
        mock_interface.enabled = True
        mock_array.get_network_interfaces.return_value = Mock(items=[mock_interface])
        mock_array.patch_network_interfaces.return_value = Mock(status_code=200)

        with pytest.raises(SystemExit):
            update_interface(mock_module, mock_array)

        mock_array.patch_network_interfaces.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_update_fc_interface_no_change(self):
        """Test update_interface with FC interface already in desired state"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.exit_json.side_effect = SystemExit(0)
        mock_module.params = {
            "name": "ct0.fc0",
            "state": "present",
            "servicelist": None,
        }
        mock_array = Mock()
        mock_interface = Mock()
        mock_interface.enabled = True  # Already enabled
        mock_array.get_network_interfaces.return_value = Mock(items=[mock_interface])

        with pytest.raises(SystemExit):
            update_interface(mock_module, mock_array)

        mock_array.patch_network_interfaces.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=False)

