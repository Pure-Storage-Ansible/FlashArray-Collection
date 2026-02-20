# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_vlan module."""

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

from plugins.modules.purefa_vlan import (
    _get_subnet,
    _get_interface,
    delete_vif,
)


class TestGetSubnet:
    """Test cases for _get_subnet function"""

    def test_get_subnet_exists(self):
        """Test _get_subnet returns subnet when it exists"""
        mock_module = Mock()
        mock_module.params = {"subnet": "test-subnet"}
        mock_array = Mock()
        mock_subnet = Mock()
        mock_subnet.name = "test-subnet"
        mock_array.get_subnets.return_value = Mock(status_code=200, items=[mock_subnet])

        result = _get_subnet(mock_module, mock_array)

        assert result == mock_subnet

    def test_get_subnet_not_exists(self):
        """Test _get_subnet returns None when subnet doesn't exist"""
        mock_module = Mock()
        mock_module.params = {"subnet": "nonexistent"}
        mock_array = Mock()
        mock_array.get_subnets.return_value = Mock(status_code=404, items=[])

        result = _get_subnet(mock_module, mock_array)

        assert result is None


class TestGetInterface:
    """Test cases for _get_interface function"""

    def test_get_interface_exists(self):
        """Test _get_interface returns interface when it exists"""
        mock_module = Mock()
        mock_module.params = {"name": "ct0.eth0"}
        mock_array = Mock()
        mock_interface = Mock()
        mock_interface.name = "ct0.eth0"
        mock_array.get_network_interfaces.return_value = Mock(
            status_code=200, items=[mock_interface]
        )

        result = _get_interface(mock_module, mock_array)

        assert result == mock_interface


class TestDeleteVif:
    """Test cases for delete_vif function"""

    def test_delete_vif_check_mode(self):
        """Test delete_vif in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "ct0.eth0", "subnet": "test-subnet"}
        mock_array = Mock()
        mock_subnet = Mock()
        mock_subnet.vlan = 100

        delete_vif(mock_module, mock_array, mock_subnet)

        mock_module.exit_json.assert_called_once_with(changed=True)
