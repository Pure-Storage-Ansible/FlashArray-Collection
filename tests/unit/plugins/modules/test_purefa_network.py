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
    _create_subordinates,
    _create_subinterfaces,
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
        mock_module.params = {
            "name": "ct0.fc0",
            "state": "present",
            "servicelist": None,
        }
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
        mock_module.params = {
            "name": "ct0.fc0",
            "state": "present",
            "servicelist": None,
        }
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


class TestCreateSubordinates:
    """Test cases for _create_subordinates function"""

    def test_create_subordinates_success(self):
        """Test creating subordinates with valid interfaces"""
        mock_module = Mock()
        mock_module.params = {"subordinates": ["ct0.eth0", "ct1.eth0"]}
        mock_array = Mock()
        mock_array.get_network_interfaces.return_value = Mock(status_code=200)

        v1, v2 = _create_subordinates(mock_module, mock_array)

        assert len(v1) == 2
        assert "ct0.eth0" in v1
        assert "ct1.eth0" in v1
        assert len(v2) == 2

    def test_create_subordinates_empty(self):
        """Test creating subordinates with no subordinates specified"""
        mock_module = Mock()
        mock_module.params = {"subordinates": None}
        mock_array = Mock()

        v1, v2 = _create_subordinates(mock_module, mock_array)

        assert v1 == []
        assert v2 == []

    def test_create_subordinates_not_exists(self):
        """Test creating subordinates when interface doesn't exist"""
        mock_module = Mock()
        mock_module.params = {"subordinates": ["ct0.eth0"]}
        mock_array = Mock()
        mock_array.get_network_interfaces.return_value = Mock(status_code=400)

        _create_subordinates(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()


class TestCreateSubinterfaces:
    """Test cases for _create_subinterfaces function"""

    def test_create_subinterfaces_lacp(self):
        """Test creating subinterfaces with LACP interfaces"""
        mock_module = Mock()
        mock_module.params = {"subinterfaces": ["ct0.lacp0.eth0"]}
        mock_array = Mock()
        mock_array.get_network_interfaces.return_value = Mock(status_code=200)
        mock_array.get_controllers.return_value = Mock(items=[Mock(), Mock()])

        v1, v2 = _create_subinterfaces(mock_module, mock_array)

        assert len(v1) == 1
        assert "ct0.lacp0.eth0" in v1
        assert len(v2) == 1

    def test_create_subinterfaces_empty(self):
        """Test creating subinterfaces with no subinterfaces specified"""
        mock_module = Mock()
        mock_module.params = {"subinterfaces": None}
        mock_array = Mock()
        mock_array.get_controllers.return_value = Mock(items=[Mock(), Mock()])

        v1, v2 = _create_subinterfaces(mock_module, mock_array)

        assert v1 == []
        assert v2 == []

    def test_create_subinterfaces_non_lacp(self):
        """Test creating subinterfaces with non-LACP interfaces (dual controller)"""
        mock_module = Mock()
        mock_module.params = {"subinterfaces": ["eth0"]}
        mock_array = Mock()
        mock_array.get_network_interfaces.return_value = Mock(status_code=200)
        mock_array.get_controllers.return_value = Mock(items=[Mock(), Mock()])

        v1, v2 = _create_subinterfaces(mock_module, mock_array)

        assert len(v1) == 2
        assert "ct0.eth0" in v1
        assert "ct1.eth0" in v1
        assert len(v2) == 2

    def test_create_subinterfaces_single_controller(self):
        """Test creating subinterfaces on single controller (Purity VM)"""
        mock_module = Mock()
        mock_module.params = {"subinterfaces": ["eth0"]}
        mock_array = Mock()
        mock_array.get_network_interfaces.return_value = Mock(status_code=200)
        mock_array.get_controllers.return_value = Mock(
            items=[Mock()]
        )  # Single controller

        v1, v2 = _create_subinterfaces(mock_module, mock_array)

        assert len(v1) == 1
        assert "ct0.eth0" in v1
        assert len(v2) == 1


class TestCreateInterfaceExtended:
    """Extended test cases for create_interface function"""

    @patch("plugins.modules.purefa_network._create_subinterfaces")
    def test_create_interface_vif_check_mode(self, mock_create_subinterfaces):
        """Test creating a VIF interface in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "ct0.vif0",
            "subnet": "test-subnet",
            "interface": "vif",
            "subinterfaces": None,
        }
        mock_array = Mock()
        mock_array.get_subnets.return_value = Mock(status_code=200)
        mock_create_subinterfaces.return_value = ([], [])

        create_interface(mock_module, mock_array)

        mock_array.post_network_interfaces.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_network._create_subordinates")
    def test_create_interface_lacpbond_check_mode(self, mock_create_subordinates):
        """Test creating a LACP bond interface in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "ct0.bond0",
            "subnet": "test-subnet",
            "interface": "lacpbond",
            "subordinates": ["ct0.eth0", "ct1.eth0"],
        }
        mock_array = Mock()
        mock_array.get_subnets.return_value = Mock(status_code=200)
        mock_create_subordinates.return_value = ([], [])

        create_interface(mock_module, mock_array)

        mock_array.post_network_interfaces.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestDeleteInterfaceSuccess:
    """Test cases for delete_interface success paths"""

    @patch("plugins.modules.purefa_network.check_response")
    def test_delete_interface_success(self, mock_check_response):
        """Test delete_interface successfully deletes"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "ct0.eth2.100"}
        mock_array = Mock()
        mock_array.delete_network_interfaces.return_value = Mock(status_code=200)

        delete_interface(mock_module, mock_array)

        mock_array.delete_network_interfaces.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestUpdateFcInterfaceExtended:
    """Extended test cases for update_fc_interface"""

    @patch("plugins.modules.purefa_network.check_response")
    def test_update_fc_interface_disable_success(self, mock_check_response):
        """Test disabling FC interface successfully"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "ct0.fc1", "state": "absent", "servicelist": None}
        mock_array = Mock()
        mock_array.patch_network_interfaces.return_value = Mock(status_code=200)
        mock_interface = Mock()
        mock_interface.enabled = True
        mock_interface.services = []

        update_fc_interface(mock_module, mock_array, mock_interface)

        mock_array.patch_network_interfaces.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_network.check_response")
    def test_update_fc_interface_update_services(self, mock_check_response):
        """Test updating FC interface services"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "ct0.fc1",
            "state": "present",
            "servicelist": ["replication"],
        }
        mock_array = Mock()
        mock_array.patch_network_interfaces.return_value = Mock(status_code=200)
        mock_interface = Mock()
        mock_interface.enabled = True
        mock_interface.services = ["management"]

        update_fc_interface(mock_module, mock_array, mock_interface)

        mock_array.patch_network_interfaces.assert_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_update_fc_interface_no_change(self):
        """Test update_fc_interface when no change needed"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "ct0.fc1",
            "state": "present",
            "servicelist": None,
        }
        mock_array = Mock()
        mock_interface = Mock()
        mock_interface.enabled = True
        mock_interface.services = []

        update_fc_interface(mock_module, mock_array, mock_interface)

        mock_array.patch_network_interfaces.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=False)


class TestUpdateInterfaceSuccess:
    """Test cases for update_interface success paths"""

    @patch("plugins.modules.purefa_network.check_response")
    def test_update_fc_interface_change_services(self, mock_check_response):
        """Test update_interface changes FC interface services"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.exit_json.side_effect = SystemExit(0)
        mock_module.params = {
            "name": "ct0.fc0",
            "state": "present",
            "servicelist": ["replication"],
        }
        mock_array = Mock()
        mock_interface = Mock()
        mock_interface.enabled = True
        mock_interface.services = ["management"]
        mock_array.get_network_interfaces.return_value = Mock(items=[mock_interface])
        mock_array.patch_network_interfaces.return_value = Mock(status_code=200)

        with pytest.raises(SystemExit):
            update_interface(mock_module, mock_array)

        mock_array.patch_network_interfaces.assert_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_network.check_response")
    def test_update_fc_interface_enable_and_services(self, mock_check_response):
        """Test update_interface enables FC interface and updates services"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.exit_json.side_effect = SystemExit(0)
        mock_module.params = {
            "name": "ct0.fc0",
            "state": "present",
            "servicelist": ["replication", "nvme-tcp"],
        }
        mock_array = Mock()
        mock_interface = Mock()
        mock_interface.enabled = False
        mock_interface.services = []
        mock_array.get_network_interfaces.return_value = Mock(items=[mock_interface])
        mock_array.patch_network_interfaces.return_value = Mock(status_code=200)

        with pytest.raises(SystemExit):
            update_interface(mock_module, mock_array)

        # Should be called twice - once to enable, once to change services
        assert mock_array.patch_network_interfaces.call_count == 2
        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_update_fc_interface_check_mode_enable(self):
        """Test update_interface FC interface check mode for enable"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = True
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

        with pytest.raises(SystemExit):
            update_interface(mock_module, mock_array)

        mock_array.patch_network_interfaces.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestCreateInterfaceSuccess:
    """Test cases for create_interface function success paths"""

    @patch("plugins.modules.purefa_network._create_subinterfaces")
    @patch("plugins.modules.purefa_network.check_response")
    def test_create_vif_interface_success(
        self, mock_check_response, mock_create_subinterfaces
    ):
        """Test creating a VIF interface successfully"""
        mock_create_subinterfaces.return_value = (False, ["ct0.eth8", "ct1.eth8"])
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "vif1",
            "interface": "vif",
            "subnet": None,
            "address": None,
            "gateway": None,
            "mtu": 1500,
            "enabled": True,
            "subinterfaces": ["ct0.eth8", "ct1.eth8"],
        }
        mock_array = Mock()
        mock_array.get_subnets.return_value = Mock(status_code=404)
        mock_array.post_network_interfaces.return_value = Mock(status_code=200)
        mock_array.patch_network_interfaces.return_value = Mock(status_code=200)

        create_interface(mock_module, mock_array)

        mock_array.post_network_interfaces.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_network._create_subinterfaces")
    def test_create_vif_interface_check_mode(self, mock_create_subinterfaces):
        """Test creating a VIF interface in check mode"""
        mock_create_subinterfaces.return_value = (False, [])
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "vif1",
            "interface": "vif",
            "subnet": None,
            "address": None,
            "gateway": None,
            "mtu": 1500,
            "enabled": True,
            "subinterfaces": None,
        }
        mock_array = Mock()
        mock_array.get_subnets.return_value = Mock(status_code=404)

        create_interface(mock_module, mock_array)

        mock_array.post_network_interfaces.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_create_interface_subnet_not_exists(self):
        """Test create_interface fails when subnet doesn't exist"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_module.params = {
            "name": "vif1",
            "interface": "vif",
            "subnet": "nonexistent_subnet",
            "address": None,
        }
        mock_array = Mock()
        mock_array.get_subnets.return_value = Mock(status_code=404)

        with pytest.raises(SystemExit):
            create_interface(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()


class TestDeleteInterfaceSuccess:
    """Test cases for delete_interface function success paths"""

    @patch("plugins.modules.purefa_network.check_response")
    def test_delete_interface_success(self, mock_check_response):
        """Test delete_interface successfully deletes"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "ct0.eth8"}
        mock_array = Mock()
        mock_array.delete_network_interfaces.return_value = Mock(status_code=200)

        delete_interface(mock_module, mock_array)

        mock_array.delete_network_interfaces.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_delete_interface_check_mode(self):
        """Test delete_interface in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "ct0.eth8"}
        mock_array = Mock()

        delete_interface(mock_module, mock_array)

        mock_array.delete_network_interfaces.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)
