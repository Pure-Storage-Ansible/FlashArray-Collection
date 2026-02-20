# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_host module."""

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
    "ansible_collections.purestorage.flasharray.plugins.module_utils.version"
] = MagicMock()
sys.modules[
    "ansible_collections.purestorage.flasharray.plugins.module_utils.common"
] = MagicMock()
sys.modules[
    "ansible_collections.purestorage.flasharray.plugins.module_utils.api_helpers"
] = MagicMock()

from plugins.modules.purefa_host import (
    _is_cbs,
    get_host,
    get_multi_hosts,
    rename_exists,
    make_host,
    make_multi_hosts,
    delete_host,
    update_host,
    _set_host_personality,
    _set_preferred_array,
    _set_chap_security,
    _set_vlan,
    _update_vlan,
)


class TestIsCbs:
    """Test cases for _is_cbs function"""

    def test_is_cbs_true(self):
        """Test CBS detection returns True for CBS model"""
        mock_array = Mock()
        mock_array.get_controllers.return_value = Mock(items=[Mock(model="CBS-V10")])
        result = _is_cbs(mock_array)
        assert result is True

    def test_is_cbs_false(self):
        """Test CBS detection returns False for non-CBS model"""
        mock_array = Mock()
        mock_array.get_controllers.return_value = Mock(items=[Mock(model="FA-X70R3")])
        result = _is_cbs(mock_array)
        assert result is False


class TestGetHost:
    """Test cases for get_host function"""

    @patch("plugins.modules.purefa_host.get_with_context")
    def test_get_host_exists(self, mock_get_with_context):
        """Test get_host returns host when it exists"""
        mock_module = Mock()
        mock_module.params = {"name": "test-host"}
        mock_array = Mock()

        mock_host = Mock()
        mock_host.name = "test-host"
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_host])

        result = get_host(mock_module, mock_array)

        assert result == mock_host

    @patch("plugins.modules.purefa_host.get_with_context")
    def test_get_host_not_exists(self, mock_get_with_context):
        """Test get_host returns None when host doesn't exist"""
        mock_module = Mock()
        mock_module.params = {"name": "nonexistent-host"}
        mock_array = Mock()

        mock_get_with_context.return_value = Mock(status_code=404)

        result = get_host(mock_module, mock_array)

        assert result is None


class TestGetMultiHosts:
    """Test cases for get_multi_hosts function"""

    @patch("plugins.modules.purefa_host.get_with_context")
    def test_get_multi_hosts_all_exist(self, mock_get_with_context):
        """Test get_multi_hosts returns True when all hosts exist"""
        mock_module = Mock()
        mock_module.params = {
            "name": "host",
            "start": 0,
            "count": 3,
            "digits": 2,
            "suffix": None,
        }
        mock_array = Mock()

        mock_get_with_context.return_value = Mock(status_code=200)

        result = get_multi_hosts(mock_module, mock_array)

        assert result is True

    @patch("plugins.modules.purefa_host.get_with_context")
    def test_get_multi_hosts_not_exist(self, mock_get_with_context):
        """Test get_multi_hosts returns False when hosts don't exist"""
        mock_module = Mock()
        mock_module.params = {
            "name": "host",
            "start": 0,
            "count": 3,
            "digits": 2,
            "suffix": None,
        }
        mock_array = Mock()

        mock_get_with_context.return_value = Mock(status_code=404)

        result = get_multi_hosts(mock_module, mock_array)

        assert result is False

    @patch("plugins.modules.purefa_host.get_with_context")
    def test_get_multi_hosts_with_suffix(self, mock_get_with_context):
        """Test get_multi_hosts with suffix"""
        mock_module = Mock()
        mock_module.params = {
            "name": "host",
            "start": 1,
            "count": 2,
            "digits": 3,
            "suffix": "_server",
        }
        mock_array = Mock()

        mock_get_with_context.return_value = Mock(status_code=200)

        result = get_multi_hosts(mock_module, mock_array)

        assert result is True
        # Verify the hosts list includes suffix
        call_args = mock_get_with_context.call_args
        assert "host001_server" in call_args.kwargs["names"]
        assert "host002_server" in call_args.kwargs["names"]


class TestRenameExists:
    """Test cases for rename_exists function"""

    @patch("plugins.modules.purefa_host.get_with_context")
    def test_rename_exists_true(self, mock_get_with_context):
        """Test rename_exists returns True when target exists"""
        mock_module = Mock()
        mock_module.params = {"rename": "new-host-name"}
        mock_array = Mock()

        mock_get_with_context.return_value = Mock(status_code=200)

        result = rename_exists(mock_module, mock_array)

        assert result is True

    @patch("plugins.modules.purefa_host.get_with_context")
    def test_rename_exists_false(self, mock_get_with_context):
        """Test rename_exists returns False when target doesn't exist"""
        mock_module = Mock()
        mock_module.params = {"rename": "new-host-name"}
        mock_array = Mock()

        mock_get_with_context.return_value = Mock(status_code=404)

        result = rename_exists(mock_module, mock_array)

        assert result is False


class TestMakeHost:
    """Test cases for make_host function"""

    @patch("plugins.modules.purefa_host.get_with_context")
    @patch("plugins.modules.purefa_host.check_response")
    def test_make_host_check_mode(self, mock_check_response, mock_get_with_context):
        """Test make_host in check mode doesn't make API calls"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-host"}
        mock_array = Mock()

        make_host(mock_module, mock_array)

        mock_get_with_context.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_host._set_host_initiators")
    @patch("plugins.modules.purefa_host.get_with_context")
    @patch("plugins.modules.purefa_host.check_response")
    def test_make_host_basic(
        self, mock_check_response, mock_get_with_context, mock_set_initiators
    ):
        """Test basic host creation"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-host",
            "vlan": None,
            "personality": None,
            "preferred_array": None,
            "host_user": None,
            "target_user": None,
            "volume": None,
            "nqn": None,
            "iqn": None,
            "wwns": None,
        }
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        make_host(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestMakeMultiHosts:
    """Test cases for make_multi_hosts function"""

    @patch("plugins.modules.purefa_host.get_with_context")
    @patch("plugins.modules.purefa_host.check_response")
    def test_make_multi_hosts_check_mode(
        self, mock_check_response, mock_get_with_context
    ):
        """Test make_multi_hosts in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "host",
            "start": 0,
            "count": 3,
            "digits": 2,
            "suffix": None,
        }
        mock_array = Mock()

        make_multi_hosts(mock_module, mock_array)

        mock_get_with_context.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestDeleteHost:
    """Test cases for delete_host function"""

    @patch("plugins.modules.purefa_host.get_with_context")
    @patch("plugins.modules.purefa_host.check_response")
    def test_delete_host_check_mode(self, mock_check_response, mock_get_with_context):
        """Test delete_host in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-host"}
        mock_array = Mock()

        delete_host(mock_module, mock_array)

        mock_get_with_context.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_host.get_with_context")
    @patch("plugins.modules.purefa_host.check_response")
    def test_delete_host_no_volumes(self, mock_check_response, mock_get_with_context):
        """Test delete_host with no connected volumes"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "test-host"}
        mock_array = Mock()

        # Mock host without host group
        mock_host = Mock()
        mock_host.host_group = Mock(spec=[])  # No name attribute
        mock_get_with_context.side_effect = [
            Mock(status_code=200, items=[mock_host]),  # get_hosts
            Mock(status_code=200, items=[]),  # get_connections (no volumes)
            Mock(status_code=200),  # delete_hosts
        ]

        delete_host(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestUpdateHost:
    """Test cases for update_host function"""

    @patch(
        "ansible_collections.purestorage.flasharray.plugins.module_utils.api_helpers.get_cached_api_version"
    )
    @patch("plugins.modules.purefa_host.LooseVersion")
    def test_update_host_no_changes(self, mock_loose_version, mock_get_api_version):
        """Test update_host with no changes needed"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-host",
            "state": "present",
            "vlan": None,
            "rename": None,
            "personality": None,
            "preferred_array": None,
            "host_user": None,
            "target_user": None,
            "target_password": None,
            "volume": None,
            "nqn": None,
            "iqn": None,
            "wwns": None,
        }
        mock_array = Mock()
        mock_get_api_version.return_value = "2.0"
        mock_loose_version.side_effect = float

        update_host(mock_module, mock_array)

        mock_module.exit_json.assert_called_once()


class TestSetHostPersonality:
    """Test cases for _set_host_personality function"""

    @patch(
        "plugins.modules.purefa_host.get_with_context",
    )
    @patch("plugins.modules.purefa_host.check_response")
    def test_set_host_personality_success(
        self, mock_check_response, mock_get_with_context
    ):
        """Test setting host personality"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-host",
            "personality": "hpux",
            "context": "",
        }
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)
        mock_check_response.return_value = None

        _set_host_personality(mock_module, mock_array)

        mock_get_with_context.assert_called()


class TestSetPreferredArray:
    """Test cases for _set_preferred_array function"""

    @patch(
        "plugins.modules.purefa_host.get_with_context",
    )
    @patch("plugins.modules.purefa_host.check_response")
    def test_set_preferred_array_success(
        self, mock_check_response, mock_get_with_context
    ):
        """Test setting preferred array list"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-host",
            "preferred_array": ["array1", "array2"],
            "context": "",
        }
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)
        mock_check_response.return_value = None

        _set_preferred_array(mock_module, mock_array)

        mock_get_with_context.assert_called()

    @patch(
        "plugins.modules.purefa_host.get_with_context",
    )
    @patch("plugins.modules.purefa_host.check_response")
    def test_set_preferred_array_delete(
        self, mock_check_response, mock_get_with_context
    ):
        """Test deleting preferred array list"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-host",
            "preferred_array": ["delete"],
            "context": "",
        }
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)
        mock_check_response.return_value = None

        _set_preferred_array(mock_module, mock_array)

        # When preferred_array is ["delete"], the function sets an empty list
        mock_get_with_context.assert_called()


class TestSetChapSecurity:
    """Test cases for _set_chap_security function"""

    @patch("plugins.modules.purefa_host.get_with_context")
    @patch("plugins.modules.purefa_host.check_response")
    def test_set_chap_host_user(self, mock_check_response, mock_get_with_context):
        """Test setting CHAP host user"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-host",
            "host_user": "hostuser",
            "host_password": "supersecretpassword123",  # 12+ chars
            "target_user": None,
            "target_password": None,
            "context": "",
        }
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)
        mock_check_response.return_value = None

        _set_chap_security(mock_module, mock_array)

        mock_get_with_context.assert_called()

    @patch("plugins.modules.purefa_host.get_with_context")
    @patch("plugins.modules.purefa_host.check_response")
    def test_set_chap_target_user(self, mock_check_response, mock_get_with_context):
        """Test setting CHAP target user"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-host",
            "host_user": None,
            "host_password": None,
            "target_user": "targetuser",
            "target_password": "anothersecretpassword123",  # 12+ chars
            "context": "",
        }
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)
        mock_check_response.return_value = None

        _set_chap_security(mock_module, mock_array)

        mock_get_with_context.assert_called()


class TestSetVlan:
    """Test cases for _set_vlan function"""

    @patch("plugins.modules.purefa_host.get_with_context")
    def test_set_vlan_success(self, mock_get_with_context):
        """Test setting VLAN successfully"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-host",
            "vlan": "100",
            "context": "",
        }
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        _set_vlan(mock_module, mock_array)

        mock_get_with_context.assert_called()


class TestUpdateVlan:
    """Test cases for _update_vlan function"""

    @patch("plugins.modules.purefa_host.get_with_context")
    def test_update_vlan_no_change(self, mock_get_with_context):
        """Test update_vlan when VLAN matches"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-host",
            "vlan": "100",
            "context": "",
        }
        mock_array = Mock()
        mock_host = Mock()
        mock_host.vlan = "100"
        mock_get_with_context.return_value = Mock(items=[mock_host])

        result = _update_vlan(mock_module, mock_array)

        assert result is False

    @patch("plugins.modules.purefa_host.get_with_context")
    def test_update_vlan_change_check_mode(self, mock_get_with_context):
        """Test update_vlan in check mode when VLAN differs"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-host",
            "vlan": "200",
            "context": "",
        }
        mock_array = Mock()
        mock_host = Mock()
        mock_host.vlan = "100"
        mock_get_with_context.return_value = Mock(items=[mock_host])

        result = _update_vlan(mock_module, mock_array)

        assert result is True


class TestMoveHost:
    """Test cases for move_host function"""

    @patch("plugins.modules.purefa_host.get_with_context")
    def test_move_host_fail_with_context(self, mock_get_with_context):
        """Test move_host fails when context is provided"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_module.params = {
            "name": "test-host",
            "context": "realm1",
        }
        mock_array = Mock()

        from plugins.modules.purefa_host import move_host

        with pytest.raises(SystemExit):
            move_host(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()

    @patch("plugins.modules.purefa_host.get_with_context")
    def test_move_host_with_connections_fails(self, mock_get_with_context):
        """Test move_host fails when host has connections"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_module.params = {
            "name": "test-host",
            "context": "",
            "move": ["realm1"],
        }
        mock_array = Mock()
        # Mock get_arrays
        mock_local_array = Mock()
        mock_local_array.name = "local-array"
        mock_array.get_arrays.return_value.items = [mock_local_array]

        # Mock host with connections
        mock_host = Mock()
        mock_host.connection_count = 5
        mock_get_with_context.return_value = Mock(items=[mock_host])

        from plugins.modules.purefa_host import move_host

        with pytest.raises(SystemExit):
            move_host(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()


class TestMakeHostSuccess:
    """Test cases for make_host success paths"""

    @patch("plugins.modules.purefa_host.check_response")
    @patch("plugins.modules.purefa_host.get_with_context")
    def test_make_host_success(self, mock_get_with_context, mock_check_response):
        """Test make_host creates host successfully"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-host",
            "context": "",
            "vlan": None,
            "personality": None,
            "preferred_array": None,
            "host_user": None,
            "target_user": None,
            "volume": None,
            "lun": None,
            "wwns": None,
            "iqn": None,
            "nqn": None,
        }
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        make_host(mock_module, mock_array)

        mock_get_with_context.assert_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_host.check_response")
    @patch("plugins.modules.purefa_host.get_with_context")
    @patch("plugins.modules.purefa_host._set_vlan")
    def test_make_host_with_vlan(
        self, mock_set_vlan, mock_get_with_context, mock_check_response
    ):
        """Test make_host creates host with VLAN"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-host",
            "context": "",
            "vlan": "100",
            "personality": None,
            "preferred_array": None,
            "host_user": None,
            "target_user": None,
            "volume": None,
            "lun": None,
            "wwns": None,
            "iqn": None,
            "nqn": None,
        }
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        make_host(mock_module, mock_array)

        mock_set_vlan.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestDeleteHostSuccess:
    """Test cases for delete_host success paths"""

    @patch("plugins.modules.purefa_host.get_with_context")
    def test_delete_host_success(self, mock_get_with_context):
        """Test delete_host successfully deletes host"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-host",
            "context": "",
        }
        mock_array = Mock()

        # Mock the host with no host_group
        mock_host = Mock()
        mock_host.host_group = None

        def side_effect(*args, **kwargs):
            if args[1] == "get_hosts":
                return Mock(items=[mock_host], status_code=200)
            elif args[1] == "get_connections":
                return Mock(items=[], status_code=200)
            else:
                return Mock(status_code=200)

        mock_get_with_context.side_effect = side_effect

        delete_host(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestConnectNewVolume:
    """Test cases for _connect_new_volume function"""

    @patch("plugins.modules.purefa_host.check_response")
    @patch("plugins.modules.purefa_host.get_with_context")
    def test_connect_new_volume_success(self, mock_get_with_context, mock_check_response):
        """Test connecting a new volume to a host"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "host1",
            "volume": "vol1",
            "lun": None,
        }
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        from plugins.modules.purefa_host import _connect_new_volume

        result = _connect_new_volume(mock_module, mock_array)

        assert result is True
        mock_get_with_context.assert_called_once()

    @patch("plugins.modules.purefa_host.check_response")
    @patch("plugins.modules.purefa_host.get_with_context")
    def test_connect_new_volume_with_lun(self, mock_get_with_context, mock_check_response):
        """Test connecting a volume with specific LUN"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "host1",
            "volume": "vol1",
            "lun": 10,
        }
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        from plugins.modules.purefa_host import _connect_new_volume

        result = _connect_new_volume(mock_module, mock_array)

        assert result is True
        # Verify ConnectionPost was called with LUN
        call_kwargs = mock_get_with_context.call_args[1]
        assert "connection" in call_kwargs

    @patch("plugins.modules.purefa_host.check_response")
    @patch("plugins.modules.purefa_host.get_with_context")
    def test_connect_new_volume_check_mode(
        self, mock_get_with_context, mock_check_response
    ):
        """Test connecting volume in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "host1",
            "volume": "vol1",
            "lun": None,
        }
        mock_array = Mock()

        from plugins.modules.purefa_host import _connect_new_volume

        result = _connect_new_volume(mock_module, mock_array)

        assert result is True
        mock_get_with_context.assert_not_called()


class TestDisconnectVolume:
    """Test cases for _disconnect_volume function"""

    @patch("plugins.modules.purefa_host.check_response")
    @patch("plugins.modules.purefa_host.get_with_context")
    def test_disconnect_volume_success(self, mock_get_with_context, mock_check_response):
        """Test disconnecting a volume from a host"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "host1",
            "volume": "vol1",
        }
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        from plugins.modules.purefa_host import _disconnect_volume

        result = _disconnect_volume(mock_module, mock_array)

        assert result is True
        mock_get_with_context.assert_called_once()

    @patch("plugins.modules.purefa_host.check_response")
    @patch("plugins.modules.purefa_host.get_with_context")
    def test_disconnect_volume_check_mode(
        self, mock_get_with_context, mock_check_response
    ):
        """Test disconnecting volume in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "host1",
            "volume": "vol1",
        }
        mock_array = Mock()

        from plugins.modules.purefa_host import _disconnect_volume

        result = _disconnect_volume(mock_module, mock_array)

        assert result is True
        mock_get_with_context.assert_not_called()


class TestUpdateHostInitiators:
    """Test cases for _update_host_initiators function"""

    @patch("plugins.modules.purefa_host.check_response")
    @patch("plugins.modules.purefa_host.get_with_context")
    def test_update_host_initiators_add_wwn(
        self, mock_get_with_context, mock_check_response
    ):
        """Test adding WWN initiators to a host"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "host1",
            "wwns": ["50:01:02:03:04:05:06:07"],
            "iqn": None,
            "nqn": None,
        }
        mock_array = Mock()

        # Mock get_hosts response
        mock_host = Mock()
        mock_host.wwns = []
        mock_host.iqns = []
        mock_host.nqns = []
        mock_get_with_context.return_value = Mock(items=[mock_host], status_code=200)

        from plugins.modules.purefa_host import _update_host_initiators

        result = _update_host_initiators(mock_module, mock_array)

        assert result is True

    @patch("plugins.modules.purefa_host.check_response")
    @patch("plugins.modules.purefa_host.get_with_context")
    def test_update_host_initiators_no_changes(
        self, mock_get_with_context, mock_check_response
    ):
        """Test updating host when initiators already match"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "host1",
            "wwns": None,
            "iqn": None,
            "nqn": None,
        }
        mock_array = Mock()

        # Mock get_hosts response
        mock_host = Mock()
        mock_host.wwns = []
        mock_host.iqns = []
        mock_host.nqns = []
        mock_get_with_context.return_value = Mock(items=[mock_host], status_code=200)

        from plugins.modules.purefa_host import _update_host_initiators

        result = _update_host_initiators(mock_module, mock_array)

        assert result is False
