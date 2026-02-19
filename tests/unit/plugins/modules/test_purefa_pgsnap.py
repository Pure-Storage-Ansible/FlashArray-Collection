# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_pgsnap module."""

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

from plugins.modules.purefa_pgsnap import (
    _check_offload,
    get_pgroup,
    get_pgsnapshot,
    create_pgsnapshot,
    delete_pgsnapshot,
    eradicate_pgsnapshot,
)


class TestCheckOffload:
    """Test cases for _check_offload function"""

    @patch("plugins.modules.purefa_pgsnap.LooseVersion")
    def test_check_offload_connected(self, mock_loose_version):
        """Test _check_offload returns True when offload is connected"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"offload": "nfs-target", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_offload = Mock()
        mock_offload.status = "connected"
        mock_array.get_offloads.return_value = Mock(status_code=200, items=[mock_offload])

        result = _check_offload(mock_module, mock_array)

        assert result is True

    @patch("plugins.modules.purefa_pgsnap.LooseVersion")
    def test_check_offload_not_found(self, mock_loose_version):
        """Test _check_offload returns False when offload not found"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"offload": "nfs-target", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_offloads.return_value = Mock(status_code=404)

        result = _check_offload(mock_module, mock_array)

        assert result is False


class TestGetPgroup:
    """Test cases for get_pgroup function"""

    @patch("plugins.modules.purefa_pgsnap.LooseVersion")
    def test_get_pgroup_exists(self, mock_loose_version):
        """Test get_pgroup returns True when pgroup exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "test-pg", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_protection_groups.return_value = Mock(status_code=200)

        result = get_pgroup(mock_module, mock_array)

        assert result is True

    @patch("plugins.modules.purefa_pgsnap.LooseVersion")
    def test_get_pgroup_not_exists(self, mock_loose_version):
        """Test get_pgroup returns False when pgroup doesn't exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "nonexistent", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_protection_groups.return_value = Mock(status_code=404)

        result = get_pgroup(mock_module, mock_array)

        assert result is False


class TestGetPgsnapshot:
    """Test cases for get_pgsnapshot function"""

    @patch("plugins.modules.purefa_pgsnap.LooseVersion")
    def test_get_pgsnapshot_exists(self, mock_loose_version):
        """Test get_pgsnapshot returns snapshot when it exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "test-pg", "suffix": "snap1", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_snap = Mock()
        mock_snap.name = "test-pg.snap1"
        mock_array.get_protection_group_snapshots.return_value = Mock(
            status_code=200, items=[mock_snap]
        )

        result = get_pgsnapshot(mock_module, mock_array)

        assert result == mock_snap

    @patch("plugins.modules.purefa_pgsnap.LooseVersion")
    def test_get_pgsnapshot_not_exists(self, mock_loose_version):
        """Test get_pgsnapshot returns None when snapshot doesn't exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "test-pg", "suffix": "snap1", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_protection_group_snapshots.return_value = Mock(status_code=404)

        result = get_pgsnapshot(mock_module, mock_array)

        assert result is None


class TestCreatePgsnapshot:
    """Test cases for create_pgsnapshot function"""

    @patch("plugins.modules.purefa_pgsnap.check_response")
    @patch("plugins.modules.purefa_pgsnap.LooseVersion")
    def test_create_pgsnapshot_success(self, mock_loose_version, mock_check_response):
        """Test create_pgsnapshot creates snapshot successfully"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pg",
            "suffix": "snap1",
            "context": "",
            "now": False,
            "remote": False,
            "apply_retention": False,
            "offload": None,
            "throttle": False,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_pg = Mock()
        mock_pg.target_count = 0
        mock_array.get_protection_groups.return_value = Mock(
            status_code=200, items=[mock_pg]
        )
        mock_snap = Mock()
        mock_snap.suffix = "snap1"
        mock_array.post_protection_group_snapshots.return_value = Mock(
            status_code=200, items=[mock_snap]
        )

        create_pgsnapshot(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True, suffix="snap1")


class TestDeletePgsnapshot:
    """Test cases for delete_pgsnapshot function"""

    @patch("plugins.modules.purefa_pgsnap.LooseVersion")
    def test_delete_pgsnapshot_check_mode(self, mock_loose_version):
        """Test delete_pgsnapshot in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-pg",
            "suffix": "snap1",
            "context": "",
            "eradicate": False,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        delete_pgsnapshot(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestEradicatePgsnapshot:
    """Test cases for eradicate_pgsnapshot function"""

    @patch("plugins.modules.purefa_pgsnap.LooseVersion")
    def test_eradicate_pgsnapshot_check_mode(self, mock_loose_version):
        """Test eradicate_pgsnapshot in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-pg", "suffix": "snap1", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        eradicate_pgsnapshot(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)

