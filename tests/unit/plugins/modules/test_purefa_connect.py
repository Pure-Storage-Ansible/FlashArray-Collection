# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_connect module."""

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

from plugins.modules.purefa_connect import (
    _lookup,
    _check_connected,
    break_connection,
)


class TestLookup:
    """Test cases for _lookup function"""

    @patch("plugins.modules.purefa_connect.socket")
    def test_lookup_success(self, mock_socket):
        """Test _lookup returns shortname and fqdn"""
        mock_socket.getnameinfo.return_value = ("host.example.com", "")

        shortname, fqdn = _lookup("192.168.1.1")

        assert shortname == "host"
        assert fqdn == "host.example.com"


class TestCheckConnected:
    """Test cases for _check_connected function"""

    @patch("plugins.modules.purefa_connect.LooseVersion")
    def test_check_connected_not_connected(self, mock_loose_version):
        """Test _check_connected returns None when not connected"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.38" else 2.38
        mock_module = Mock()
        mock_module.params = {
            "target_url": "array2",
            "target_api": "api-token",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_array_connections.return_value = Mock(items=[])

        result = _check_connected(mock_module, mock_array)

        assert result is None


class TestBreakConnection:
    """Test cases for break_connection function"""

    @patch("plugins.modules.purefa_connect.LooseVersion")
    def test_break_connection_check_mode(self, mock_loose_version):
        """Test break_connection in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.38" else 2.38
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_local = Mock()
        mock_local.name = "local-array"
        mock_array.get_arrays.return_value = Mock(items=[mock_local])
        mock_target = Mock()
        mock_target.name = "target-array"

        break_connection(mock_module, mock_array, mock_target)

        mock_module.exit_json.assert_called_once_with(changed=True)
