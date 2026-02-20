# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_snap module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from unittest.mock import Mock, patch, MagicMock
from packaging.version import Version as LooseVersion

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
    _check_offload_snapshot,
    get_volume,
    get_target,
    get_snapshot,
    get_deleted_snapshot,
    create_snapshot,
    create_from_snapshot,
    update_snapshot,
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
        mock_array.get_offloads.return_value = Mock(
            status_code=200, items=[mock_offload]
        )

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


class TestCheckOffloadSnapshot:
    """Test cases for _check_offload_snapshot function"""

    @patch("plugins.modules.purefa_snap._check_offload")
    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_check_offload_snapshot_exists(
        self, mock_loose_version, mock_check_offload
    ):
        """Test _check_offload_snapshot returns snapshot when it exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_check_offload.return_value = True
        mock_module = Mock()
        mock_module.params = {
            "name": "test-vol",
            "suffix": "snap1",
            "offload": "offload-target",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        # Mock array.get_arrays().items
        mock_local_array = Mock()
        mock_local_array.name = "local-array"
        mock_array.get_arrays.return_value.items = [mock_local_array]
        mock_snap = Mock()
        mock_snap.name = "offload-target:test-vol.snap1"
        mock_array.get_remote_volume_snapshots.return_value.status_code = 200
        mock_array.get_remote_volume_snapshots.return_value.items = [mock_snap]

        result = _check_offload_snapshot(mock_module, mock_array)

        assert result is not None

    @patch("plugins.modules.purefa_snap._check_offload")
    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_check_offload_snapshot_not_exists(
        self, mock_loose_version, mock_check_offload
    ):
        """Test _check_offload_snapshot returns None when snapshot doesn't exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_check_offload.return_value = True
        mock_module = Mock()
        mock_module.params = {
            "name": "test-vol",
            "suffix": "snap1",
            "offload": "offload-target",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        # Mock array.get_arrays().items
        mock_local_array = Mock()
        mock_local_array.name = "local-array"
        mock_array.get_arrays.return_value.items = [mock_local_array]
        mock_array.get_remote_volume_snapshots.return_value.status_code = 404

        result = _check_offload_snapshot(mock_module, mock_array)

        assert result is None


class TestGetDeletedSnapshot:
    """Test cases for get_deleted_snapshot function"""

    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_get_deleted_snapshot_exists(self, mock_loose_version):
        """Test get_deleted_snapshot returns snapshot when it exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "test-vol", "suffix": "snap1", "offload": None}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_snap = Mock()
        mock_array.get_volume_snapshots.return_value.status_code = 200
        mock_array.get_volume_snapshots.return_value.items = [mock_snap]

        result = get_deleted_snapshot(mock_module, mock_array)

        assert result is not None

    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_get_deleted_snapshot_not_exists(self, mock_loose_version):
        """Test get_deleted_snapshot returns False when snapshot doesn't exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "test-vol", "suffix": "snap1", "offload": None}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_volume_snapshots.return_value.status_code = 404

        result = get_deleted_snapshot(mock_module, mock_array)

        # get_deleted_snapshot returns bool, not None
        assert result is False


class TestCreateFromSnapshot:
    """Test cases for create_from_snapshot function"""

    @patch("plugins.modules.purefa_snap.check_response")
    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_create_from_snapshot_check_mode(
        self, mock_loose_version, mock_check_response
    ):
        """Test create_from_snapshot in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-vol",
            "suffix": "snap1",
            "target": "new-vol",
            "overwrite": False,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        create_from_snapshot(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestUpdateSnapshot:
    """Test cases for update_snapshot function"""

    @patch("plugins.modules.purefa_snap.check_response")
    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_update_snapshot_check_mode(self, mock_loose_version, mock_check_response):
        """Test update_snapshot in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-vol",
            "suffix": "snap1",
            "rename": "new-suffix",
            "target": None,
            "offload": None,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        update_snapshot(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestCreateSnapshotSuccess:
    """Additional test cases for create_snapshot function"""

    @patch("plugins.modules.purefa_snap.check_response")
    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_create_snapshot_success(self, mock_loose_version, mock_check_response):
        """Test create_snapshot successfully creates"""
        mock_loose_version.side_effect = LooseVersion
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-vol",
            "suffix": "snap1",
            "offload": None,
            "throttle": True,
            "context": "pod1",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.post_volume_snapshots.return_value = Mock(status_code=200)

        create_snapshot(mock_module, mock_array)

        mock_array.post_volume_snapshots.assert_called_once()
        # exit_json is called with changed=True and suffix
        mock_module.exit_json.assert_called_once()


class TestDeleteSnapshotSuccess:
    """Additional test cases for delete_snapshot function"""

    @patch("plugins.modules.purefa_snap.check_response")
    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_delete_snapshot_success(self, mock_loose_version, mock_check_response):
        """Test delete_snapshot successfully deletes"""
        mock_loose_version.side_effect = LooseVersion
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-vol",
            "suffix": "snap1",
            "target": None,
            "offload": None,
            "context": "",
            "eradicate": False,
            "ignore_repl": True,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.patch_volume_snapshots.return_value = Mock(status_code=200)

        delete_snapshot(mock_module, mock_array)

        mock_array.patch_volume_snapshots.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestEradicateSnapshotSuccess:
    """Test cases for eradicate_snapshot success paths"""

    @patch("plugins.modules.purefa_snap.check_response")
    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_eradicate_snapshot_success(self, mock_loose_version, mock_check_response):
        """Test eradicate_snapshot successfully eradicates"""
        mock_loose_version.side_effect = LooseVersion
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-vol",
            "suffix": "snap1",
            "offload": None,
            "context": "",
            "ignore_repl": True,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.delete_volume_snapshots.return_value = Mock(status_code=200)

        eradicate_snapshot(mock_module, mock_array)

        mock_array.delete_volume_snapshots.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRecoverSnapshotSuccess:
    """Test cases for recover_snapshot success paths"""

    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_recover_snapshot_success(self, mock_loose_version):
        """Test recover_snapshot successfully recovers"""
        mock_loose_version.side_effect = LooseVersion
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-vol",
            "suffix": "snap1",
            "offload": None,
            "target": None,
            "context": "",
            "ignore_repl": True,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.patch_volume_snapshot.return_value = Mock(status_code=200)

        recover_snapshot(mock_module, mock_array)

        mock_array.patch_volume_snapshot.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestUpdateSnapshotSuccess:
    """Test cases for update_snapshot success paths"""

    @patch("plugins.modules.purefa_snap.check_response")
    @patch("plugins.modules.purefa_snap.LooseVersion")
    def test_update_snapshot_success(self, mock_loose_version, mock_check_response):
        """Test update_snapshot successfully updates"""
        mock_loose_version.side_effect = LooseVersion
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-vol",
            "suffix": "old-suffix",
            "target": "new-suffix",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.patch_volume_snapshots.return_value = Mock(status_code=200)

        update_snapshot(mock_module, mock_array)

        mock_array.patch_volume_snapshots.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestCreateFromSnapshotSuccess:
    """Test cases for create_from_snapshot success paths"""

    @patch("plugins.modules.purefa_snap.check_response")
    @patch("plugins.modules.purefa_snap.get_target")
    @patch("plugins.modules.purefa_snap.LooseVersion", side_effect=LooseVersion)
    def test_create_from_snapshot_new_volume(
        self, mock_lv, mock_get_target, mock_check_response
    ):
        """Test creating new volume from snapshot"""
        mock_get_target.return_value = None  # Target doesn't exist
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "source-vol",
            "suffix": "snap1",
            "target": "new-vol",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.post_volumes.return_value = Mock(status_code=200)

        create_from_snapshot(mock_module, mock_array)

        mock_array.post_volumes.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_snap.check_response")
    @patch("plugins.modules.purefa_snap.get_target")
    @patch("plugins.modules.purefa_snap.LooseVersion", side_effect=LooseVersion)
    def test_create_from_snapshot_overwrite(
        self, mock_lv, mock_get_target, mock_check_response
    ):
        """Test creating volume from snapshot with overwrite"""
        mock_get_target.return_value = Mock()  # Target exists
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "source-vol",
            "suffix": "snap1",
            "target": "existing-vol",
            "overwrite": True,
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.post_volumes.return_value = Mock(status_code=200)

        create_from_snapshot(mock_module, mock_array)

        mock_array.post_volumes.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_snap.get_target")
    @patch("plugins.modules.purefa_snap.LooseVersion", side_effect=LooseVersion)
    def test_create_from_snapshot_no_overwrite(self, mock_lv, mock_get_target):
        """Test creating volume from snapshot when target exists and no overwrite"""
        mock_get_target.return_value = Mock()  # Target exists
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "source-vol",
            "suffix": "snap1",
            "target": "existing-vol",
            "overwrite": False,
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        create_from_snapshot(mock_module, mock_array)

        mock_array.post_volumes.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=False)


class TestDeleteSnapshotOffload:
    """Test cases for delete_snapshot with offload scenarios"""

    @patch("plugins.modules.purefa_snap.check_response")
    @patch("plugins.modules.purefa_snap._check_offload")
    @patch("plugins.modules.purefa_snap.LooseVersion", side_effect=LooseVersion)
    def test_delete_snapshot_offload_with_eradicate(
        self, mock_lv, mock_check_offload, mock_check_response
    ):
        """Test deleting snapshot from offload with eradicate"""
        mock_check_offload.return_value = True
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "vol1",
            "suffix": "snap1",
            "offload": "nfs-target",
            "context": "",
            "eradicate": True,
            "ignore_repl": False,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_local_array = Mock()
        mock_local_array.name = "local-array"
        mock_array.get_arrays.return_value = Mock(items=[mock_local_array])
        mock_array.patch_remote_volume_snapshots.return_value = Mock(status_code=200)
        mock_array.delete_remote_volume_snapshots.return_value = Mock(status_code=200)

        delete_snapshot(mock_module, mock_array)

        mock_array.patch_remote_volume_snapshots.assert_called_once()
        mock_array.delete_remote_volume_snapshots.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_snap.check_response")
    @patch("plugins.modules.purefa_snap._check_offload")
    @patch("plugins.modules.purefa_snap._check_target")
    @patch("plugins.modules.purefa_snap.LooseVersion", side_effect=LooseVersion)
    def test_delete_snapshot_local_with_eradicate(
        self, mock_lv, mock_check_target, mock_check_offload, mock_check_response
    ):
        """Test deleting local snapshot with eradicate"""
        mock_check_offload.return_value = False
        mock_check_target.return_value = False
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "vol1",
            "suffix": "snap1",
            "offload": None,
            "context": "",
            "eradicate": True,
            "ignore_repl": False,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.patch_volume_snapshots.return_value = Mock(status_code=200)
        mock_array.delete_volume_snapshots.return_value = Mock(status_code=200)

        delete_snapshot(mock_module, mock_array)

        mock_array.patch_volume_snapshots.assert_called_once()
        mock_array.delete_volume_snapshots.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestUpdateSnapshotExtended:
    """Extended test cases for update_snapshot function"""

    @patch("plugins.modules.purefa_snap.check_response")
    @patch("plugins.modules.purefa_snap.LooseVersion", side_effect=LooseVersion)
    def test_update_snapshot_older_api(self, mock_lv, mock_check_response):
        """Test renaming snapshot with older API version"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "vol1",
            "suffix": "snap1",
            "target": "snap2",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.16"
        mock_array.patch_volume_snapshots.return_value = Mock(status_code=200)

        update_snapshot(mock_module, mock_array)

        mock_array.patch_volume_snapshots.assert_called_once()
        call_kwargs = mock_array.patch_volume_snapshots.call_args[1]
        assert "context_names" not in call_kwargs
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRecoverSnapshotExtended:
    """Extended test cases for recover_snapshot function"""

    @patch("plugins.modules.purefa_snap._check_offload")
    @patch("plugins.modules.purefa_snap.LooseVersion", side_effect=LooseVersion)
    def test_recover_snapshot_local_success(self, mock_lv, mock_check_offload):
        """Test recovering local snapshot"""
        mock_check_offload.return_value = False
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "vol1",
            "suffix": "snap1",
            "offload": None,
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.patch_volume_snapshot.return_value = Mock(status_code=200)

        recover_snapshot(mock_module, mock_array)

        mock_array.patch_volume_snapshot.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestEradicateSnapshotExtended:
    """Extended test cases for eradicate_snapshot function"""

    @patch("plugins.modules.purefa_snap.check_response")
    @patch("plugins.modules.purefa_snap._check_offload")
    @patch("plugins.modules.purefa_snap.LooseVersion", side_effect=LooseVersion)
    def test_eradicate_snapshot_local_success(
        self, mock_lv, mock_check_offload, mock_check_response
    ):
        """Test eradicating local snapshot"""
        mock_check_offload.return_value = False
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "vol1",
            "suffix": "snap1",
            "offload": None,
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.delete_volume_snapshots.return_value = Mock(status_code=200)

        eradicate_snapshot(mock_module, mock_array)

        mock_array.delete_volume_snapshots.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)
