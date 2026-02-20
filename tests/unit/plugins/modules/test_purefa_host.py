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
