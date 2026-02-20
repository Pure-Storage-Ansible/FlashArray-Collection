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
    update_connection,
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

    @patch("plugins.modules.purefa_connect.LooseVersion", side_effect=LooseVersion)
    def test_check_connected_found(self, mock_lv):
        """Test _check_connected returns connection when found"""
        mock_module = Mock()
        mock_module.params = {
            "target_url": "192.168.1.100",
            "target_api": "api-token",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_conn = Mock()
        mock_conn.name = "array2"
        mock_conn.management_address = "192.168.1.100"
        mock_conn.status = "connected"
        mock_array.get_array_connections.return_value = Mock(
            status_code=200, items=[mock_conn]
        )

        result = _check_connected(mock_module, mock_array)

        assert result == mock_conn


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
        mock_target.management_address = "192.168.1.1"

        break_connection(mock_module, mock_array, mock_target)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_connect.check_response")
    @patch("plugins.modules.purefa_connect.LooseVersion", side_effect=LooseVersion)
    def test_break_connection_success(self, mock_lv, mock_check_response):
        """Test break_connection successfully breaks connection"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_local = Mock()
        mock_local.name = "local-array"
        mock_array.get_arrays.return_value = Mock(items=[mock_local])
        mock_array.delete_array_connections.return_value = Mock(status_code=200)
        mock_target = Mock()
        mock_target.name = "target-array"
        mock_target.management_address = "192.168.1.1"

        break_connection(mock_module, mock_array, mock_target)

        mock_array.delete_array_connections.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_connect.LooseVersion", side_effect=LooseVersion)
    def test_break_connection_wrong_array(self, mock_lv):
        """Test break_connection fails when called from wrong array"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_local = Mock()
        mock_local.name = "local-array"
        mock_array.get_arrays.return_value = Mock(items=[mock_local])
        mock_target = Mock()
        mock_target.name = "target-array"
        mock_target.management_address = None  # No management address

        break_connection(mock_module, mock_array, mock_target)

        mock_module.fail_json.assert_called_once()


class TestUpdateConnection:
    """Test cases for update_connection function"""

    @patch("plugins.modules.purefa_connect.check_response")
    @patch("plugins.modules.purefa_connect.LooseVersion", side_effect=LooseVersion)
    def test_update_connection_renew_key_check_mode(self, mock_lv, mock_check_response):
        """Test update_connection with renew_key in check mode"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.exit_json.side_effect = SystemExit(0)  # Stop at first exit_json
        mock_module.params = {
            "context": "",
            "renew_key": True,
            "refresh": False,
            "encrypted": False,
            "connection": "sync-replication",
            "target_url": "192.168.1.100",
            "target_api": "api-token",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_local = Mock()
        mock_local.name = "local-array"
        mock_array.get_arrays.return_value = Mock(items=[mock_local])
        mock_target = Mock()
        mock_target.name = "target-array"

        with pytest.raises(SystemExit):
            update_connection(mock_module, mock_array, mock_target)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_connect.check_response")
    @patch("plugins.modules.purefa_connect.LooseVersion", side_effect=LooseVersion)
    def test_update_connection_renew_key_success(self, mock_lv, mock_check_response):
        """Test update_connection with renew_key successfully renews"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.exit_json.side_effect = SystemExit(0)
        mock_module.params = {
            "context": "",
            "renew_key": True,
            "refresh": False,
            "encrypted": False,
            "connection": "sync-replication",
            "target_url": "192.168.1.100",
            "target_api": "api-token",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.patch_array_connections.return_value = Mock(status_code=200)
        mock_local = Mock()
        mock_local.name = "local-array"
        mock_array.get_arrays.return_value = Mock(items=[mock_local])
        mock_target = Mock()
        mock_target.name = "target-array"

        with pytest.raises(SystemExit):
            update_connection(mock_module, mock_array, mock_target)

        mock_array.patch_array_connections.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_connect.check_response")
    @patch("plugins.modules.purefa_connect.LooseVersion", side_effect=LooseVersion)
    def test_update_connection_refresh_success(self, mock_lv, mock_check_response):
        """Test update_connection with refresh successfully refreshes"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.exit_json.side_effect = SystemExit(0)
        mock_module.params = {
            "context": "",
            "renew_key": False,
            "refresh": True,
            "encrypted": False,
            "connection": "sync-replication",
            "target_url": "192.168.1.100",
            "target_api": "api-token",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.patch_array_connections.return_value = Mock(status_code=200)
        mock_local = Mock()
        mock_local.name = "local-array"
        mock_array.get_arrays.return_value = Mock(items=[mock_local])
        mock_target = Mock()
        mock_target.name = "target-array"

        with pytest.raises(SystemExit):
            update_connection(mock_module, mock_array, mock_target)

        mock_array.patch_array_connections.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)
