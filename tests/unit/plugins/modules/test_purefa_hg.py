# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_hg module."""

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
sys.modules[
    "ansible_collections.purestorage.flasharray.plugins.module_utils.error_handlers"
] = MagicMock()

from plugins.modules.purefa_hg import (
    rename_exists,
    get_hostgroup,
    get_hostgroup_hosts,
    make_hostgroup,
)


class TestRenameExists:
    """Test cases for rename_exists function"""

    @patch("plugins.modules.purefa_hg.LooseVersion")
    def test_rename_exists_true(self, mock_loose_version):
        """Test rename_exists returns True when target exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"rename": "new-hg", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_host_groups.return_value = Mock(status_code=200)

        result = rename_exists(mock_module, mock_array)

        assert result is True

    @patch("plugins.modules.purefa_hg.LooseVersion")
    def test_rename_exists_false(self, mock_loose_version):
        """Test rename_exists returns False when target doesn't exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"rename": "new-hg", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_host_groups.return_value = Mock(status_code=404)

        result = rename_exists(mock_module, mock_array)

        assert result is False


class TestGetHostgroup:
    """Test cases for get_hostgroup function"""

    @patch("plugins.modules.purefa_hg.LooseVersion")
    def test_get_hostgroup_exists(self, mock_loose_version):
        """Test get_hostgroup returns hostgroup when it exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "test-hg", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_hg = Mock()
        mock_hg.name = "test-hg"
        mock_array.get_host_groups.return_value = Mock(status_code=200, items=[mock_hg])

        result = get_hostgroup(mock_module, mock_array)

        assert result == mock_hg

    @patch("plugins.modules.purefa_hg.LooseVersion")
    def test_get_hostgroup_not_exists(self, mock_loose_version):
        """Test get_hostgroup returns None when hostgroup doesn't exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "nonexistent", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_host_groups.return_value = Mock(status_code=404, items=[])

        result = get_hostgroup(mock_module, mock_array)

        assert result is None


class TestGetHostgroupHosts:
    """Test cases for get_hostgroup_hosts function"""

    @patch("plugins.modules.purefa_hg.LooseVersion")
    def test_get_hostgroup_hosts_exists(self, mock_loose_version):
        """Test get_hostgroup_hosts returns hostgroup hosts when they exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "test-hg", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_hg = Mock()
        mock_hg.member = Mock(name="host1")
        mock_array.get_host_groups_hosts.return_value = Mock(
            status_code=200, items=[mock_hg]
        )

        result = get_hostgroup_hosts(mock_module, mock_array)

        assert result is not None

    @patch("plugins.modules.purefa_hg.LooseVersion")
    def test_get_hostgroup_hosts_not_exists(self, mock_loose_version):
        """Test get_hostgroup_hosts returns None when no hosts exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "test-hg", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_host_groups_hosts.return_value = Mock(
            status_code=404, items=[]
        )

        result = get_hostgroup_hosts(mock_module, mock_array)

        assert result is None


class TestMakeHostgroup:
    """Test cases for make_hostgroup function"""

    @patch("plugins.modules.purefa_hg.check_response")
    @patch("plugins.modules.purefa_hg.LooseVersion")
    def test_make_hostgroup_check_mode(self, mock_loose_version, mock_check_response):
        """Test make_hostgroup in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "new-hg", "rename": None, "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        make_hostgroup(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)



