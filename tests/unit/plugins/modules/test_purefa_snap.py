# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_snap module."""

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

from plugins.modules.purefa_snap import (
    _check_offload,
    _check_target,
    get_volume,
    get_target,
    get_snapshot,
    get_deleted_snapshot,
    create_snapshot,
    delete_snapshot,
    eradicate_snapshot,
    recover_snapshot,
)


class TestCheckOffload:
    """Test cases for _check_offload function"""

    @patch("plugins.modules.purefa_snap.LooseVersion")
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

    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_check_offload_not_connected(self, mock_loose_version):
        """Test _check_offload returns False when offload is not connected"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"offload": "nfs-target", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_offloads.return_value = Mock(status_code=404)

        result = _check_offload(mock_module, mock_array)

        assert result is False


class TestCheckTarget:
    """Test cases for _check_target function"""

    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_check_target_connected(self, mock_loose_version):
        """Test _check_target returns True when target is connected"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"offload": "array-target", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_conn = Mock()
        mock_conn.status = "connected"
        mock_array.get_array_connections.return_value = Mock(
            status_code=200, items=[mock_conn]
        )

        result = _check_target(mock_module, mock_array)

        assert result is True


class TestGetVolume:
    """Test cases for get_volume function"""

    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_get_volume_exists(self, mock_loose_version):
        """Test get_volume returns volume when it exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "test-vol", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_vol = Mock()
        mock_vol.name = "test-vol"
        mock_array.get_volumes.return_value = Mock(status_code=200, items=[mock_vol])

        result = get_volume(mock_module, mock_array)

        assert result == mock_vol

    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_get_volume_not_exists(self, mock_loose_version):
        """Test get_volume returns None when volume doesn't exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "nonexistent", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_volumes.return_value = Mock(status_code=404)

        result = get_volume(mock_module, mock_array)

        assert result is None


class TestGetTarget:
    """Test cases for get_target function"""

    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_get_target_exists(self, mock_loose_version):
        """Test get_target returns target when it exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"target": "target-vol", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_vol = Mock()
        mock_vol.name = "target-vol"
        mock_array.get_volumes.return_value = Mock(status_code=200, items=[mock_vol])

        result = get_target(mock_module, mock_array)

        assert result == mock_vol


class TestGetSnapshot:
    """Test cases for get_snapshot function"""

    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_get_snapshot_exists(self, mock_loose_version):
        """Test get_snapshot returns True when snapshot exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "test-vol", "suffix": "snap1", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_volume_snapshots.return_value = Mock(status_code=200)

        result = get_snapshot(mock_module, mock_array)

        assert result is True

    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_get_snapshot_not_exists(self, mock_loose_version):
        """Test get_snapshot returns False when snapshot doesn't exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "test-vol", "suffix": "snap1", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_volume_snapshots.return_value = Mock(status_code=404)

        result = get_snapshot(mock_module, mock_array)

        assert result is False


class TestCreateSnapshot:
    """Test cases for create_snapshot function"""

    @patch("plugins.modules.purefa_snap.check_response")
    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_create_snapshot_check_mode(self, mock_loose_version, mock_check_response):
        """Test create_snapshot in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-vol", "suffix": "snap1", "offload": None}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        create_snapshot(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True, suffix="snap1")


class TestDeleteSnapshot:
    """Test cases for delete_snapshot function"""

    @patch("plugins.modules.purefa_snap.check_response")
    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_delete_snapshot_check_mode(self, mock_loose_version, mock_check_response):
        """Test delete_snapshot in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-vol",
            "suffix": "snap1",
            "eradicate": False,
            "offload": None,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        delete_snapshot(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestEradicateSnapshot:
    """Test cases for eradicate_snapshot function"""

    @patch("plugins.modules.purefa_snap.check_response")
    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_eradicate_snapshot_check_mode(
        self, mock_loose_version, mock_check_response
    ):
        """Test eradicate_snapshot in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-vol", "suffix": "snap1"}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        eradicate_snapshot(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRecoverSnapshot:
    """Test cases for recover_snapshot function"""

    @patch("plugins.modules.purefa_snap.check_response")
    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_recover_snapshot_check_mode(self, mock_loose_version, mock_check_response):
        """Test recover_snapshot in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-vol",
            "suffix": "snap1",
            "overwrite": False,
            "target": None,
            "offload": None,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        recover_snapshot(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)

