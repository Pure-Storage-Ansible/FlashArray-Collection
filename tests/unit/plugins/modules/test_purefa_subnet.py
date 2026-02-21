# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_subnet module."""

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

from plugins.modules.purefa_subnet import (
    _get_subnet,
    delete_subnet,
    create_subnet,
    update_subnet,
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


class TestCreateSubnet:
    """Test cases for create_subnet function"""

    @patch("plugins.modules.purefa_subnet.check_response")
    def test_create_subnet_no_prefix_fails(self, mock_check_response):
        """Test create_subnet fails without prefix"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_module.params = {
            "name": "subnet1",
            "prefix": None,
        }
        mock_array = Mock()

        with pytest.raises(SystemExit):
            create_subnet(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()

    @patch("plugins.modules.purefa_subnet.check_response")
    def test_create_subnet_check_mode(self, mock_check_response):
        """Test create_subnet in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "subnet1",
            "prefix": "10.0.0.0/24",
            "gateway": None,
            "vlan": None,
            "mtu": None,
            "enabled": True,
        }
        mock_array = Mock()

        create_subnet(mock_module, mock_array)

        mock_array.post_subnets.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_subnet.check_response")
    def test_create_subnet_success(self, mock_check_response):
        """Test create_subnet successfully creates"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "subnet1",
            "prefix": "10.0.0.0/24",
            "gateway": None,
            "vlan": None,
            "mtu": None,
            "enabled": True,
        }
        mock_array = Mock()
        mock_array.post_subnets.return_value = Mock(status_code=200)

        create_subnet(mock_module, mock_array)

        mock_array.post_subnets.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_subnet.check_response")
    def test_create_subnet_vlan_out_of_range(self, mock_check_response):
        """Test create_subnet fails with invalid VLAN"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_module.params = {
            "name": "subnet1",
            "prefix": "10.0.0.0/24",
            "gateway": None,
            "vlan": 5000,  # Out of range
            "mtu": None,
            "enabled": True,
        }
        mock_array = Mock()

        with pytest.raises(SystemExit):
            create_subnet(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()

    @patch("plugins.modules.purefa_subnet.check_response")
    def test_create_subnet_mtu_out_of_range(self, mock_check_response):
        """Test create_subnet fails with invalid MTU"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_module.params = {
            "name": "subnet1",
            "prefix": "10.0.0.0/24",
            "gateway": None,
            "vlan": None,
            "mtu": 10000,  # Out of range
            "enabled": True,
        }
        mock_array = Mock()

        with pytest.raises(SystemExit):
            create_subnet(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()


class TestUpdateSubnet:
    """Tests for update_subnet function"""

    @patch("plugins.modules.purefa_subnet.check_response")
    def test_update_subnet_no_change(self, mock_check_response):
        """Test update_subnet when no changes needed"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "prefix": None,
            "vlan": None,
            "mtu": None,
            "gateway": None,
            "enabled": True,
        }

        # Use dict for subnet because function accesses subnet["gateway"]
        mock_subnet = Mock()
        mock_subnet.name = "subnet1"
        mock_subnet.prefix = "10.0.0.0/24"
        mock_subnet.mtu = 1500
        mock_subnet.vlan = 100
        mock_subnet.gateway = "10.0.0.1"
        mock_subnet.enabled = True
        # Make subnet subscriptable for subnet["gateway"]
        mock_subnet.__getitem__ = Mock(return_value="10.0.0.1")

        mock_array = Mock()

        update_subnet(mock_module, mock_array, mock_subnet)

        mock_module.exit_json.assert_called_once_with(changed=False)
        mock_array.patch_subnets.assert_not_called()

    @patch("plugins.modules.purefa_subnet.check_response")
    def test_update_subnet_change_mtu(self, mock_check_response):
        """Test update_subnet with MTU change"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "prefix": None,
            "vlan": None,
            "mtu": 9000,  # Change MTU
            "gateway": None,
            "enabled": True,
        }

        mock_subnet = Mock()
        mock_subnet.name = "subnet1"
        mock_subnet.prefix = "10.0.0.0/24"
        mock_subnet.mtu = 1500
        mock_subnet.vlan = 100
        mock_subnet.gateway = "10.0.0.1"
        mock_subnet.enabled = True
        # Make subnet subscriptable for subnet["gateway"]
        mock_subnet.__getitem__ = Mock(return_value="10.0.0.1")

        mock_array = Mock()
        mock_array.patch_subnets.return_value = Mock(status_code=200)

        update_subnet(mock_module, mock_array, mock_subnet)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.patch_subnets.assert_called_once()

    @patch("plugins.modules.purefa_subnet.check_response")
    def test_update_subnet_check_mode(self, mock_check_response):
        """Test update_subnet in check mode with changes"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "prefix": None,
            "vlan": 200,  # Change VLAN
            "mtu": None,
            "gateway": None,
            "enabled": True,
        }

        mock_subnet = Mock()
        mock_subnet.name = "subnet1"
        mock_subnet.prefix = "10.0.0.0/24"
        mock_subnet.mtu = 1500
        mock_subnet.vlan = 100
        mock_subnet.gateway = "10.0.0.1"
        mock_subnet.enabled = True
        # Make subnet subscriptable for subnet["gateway"]
        mock_subnet.__getitem__ = Mock(return_value="10.0.0.1")

        mock_array = Mock()

        update_subnet(mock_module, mock_array, mock_subnet)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.patch_subnets.assert_not_called()

    @patch("plugins.modules.purefa_subnet.check_response")
    def test_update_subnet_vlan_out_of_range(self, mock_check_response):
        """Test update_subnet fails with invalid VLAN"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_module.params = {
            "prefix": None,
            "vlan": 5000,  # Out of range
            "mtu": None,
            "gateway": None,
            "enabled": True,
        }

        mock_subnet = Mock()
        mock_subnet.name = "subnet1"
        mock_subnet.prefix = "10.0.0.0/24"
        mock_subnet.mtu = 1500
        mock_subnet.vlan = 100
        mock_subnet.gateway = "10.0.0.1"
        mock_subnet.enabled = True

        mock_array = Mock()

        with pytest.raises(SystemExit):
            update_subnet(mock_module, mock_array, mock_subnet)

        mock_module.fail_json.assert_called_once()

    @patch("plugins.modules.purefa_subnet.check_response")
    def test_update_subnet_mtu_out_of_range(self, mock_check_response):
        """Test update_subnet fails with invalid MTU"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_module.params = {
            "prefix": None,
            "vlan": None,
            "mtu": 500,  # Out of range - minimum is 568
            "gateway": None,
            "enabled": True,
        }

        mock_subnet = Mock()
        mock_subnet.name = "subnet1"
        mock_subnet.prefix = "10.0.0.0/24"
        mock_subnet.mtu = 1500
        mock_subnet.vlan = 100
        mock_subnet.gateway = "10.0.0.1"
        mock_subnet.enabled = True

        mock_array = Mock()

        with pytest.raises(SystemExit):
            update_subnet(mock_module, mock_array, mock_subnet)

        mock_module.fail_json.assert_called_once()

    @patch("plugins.modules.purefa_subnet.check_response")
    def test_update_subnet_change_enabled(self, mock_check_response):
        """Test update_subnet changes enabled state"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "prefix": None,
            "vlan": None,
            "mtu": None,
            "gateway": None,
            "enabled": False,  # Change from True to False
        }

        mock_subnet = Mock()
        mock_subnet.name = "subnet1"
        mock_subnet.prefix = "10.0.0.0/24"
        mock_subnet.mtu = 1500
        mock_subnet.vlan = 100
        mock_subnet.gateway = "10.0.0.1"
        mock_subnet.enabled = True
        mock_subnet.__getitem__ = Mock(return_value="10.0.0.1")

        mock_array = Mock()
        mock_array.patch_subnets.return_value = Mock(status_code=200)

        update_subnet(mock_module, mock_array, mock_subnet)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.patch_subnets.assert_called()

    @patch("plugins.modules.purefa_subnet.check_response")
    def test_update_subnet_change_mtu(self, mock_check_response):
        """Test update_subnet changes MTU"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "prefix": None,
            "vlan": None,
            "mtu": 9000,  # Change MTU
            "gateway": None,
            "enabled": True,
        }

        mock_subnet = Mock()
        mock_subnet.name = "subnet1"
        mock_subnet.prefix = "10.0.0.0/24"
        mock_subnet.mtu = 1500
        mock_subnet.vlan = 100
        mock_subnet.gateway = "10.0.0.1"
        mock_subnet.enabled = True
        mock_subnet.__getitem__ = Mock(return_value="10.0.0.1")

        mock_array = Mock()
        mock_array.patch_subnets.return_value = Mock(status_code=200)

        update_subnet(mock_module, mock_array, mock_subnet)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.patch_subnets.assert_called()
