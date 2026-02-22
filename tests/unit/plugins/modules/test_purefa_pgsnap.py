# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_pgsnap module."""

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

import pytest  # pylint: disable=unused-import

from plugins.modules.purefa_pgsnap import (
    _check_offload,
    get_pgroup,
    get_pgsnapshot,
    get_rpgsnapshot,
    create_pgsnapshot,
    update_pgsnapshot,
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
        mock_array.get_offloads.return_value = Mock(
            status_code=200, items=[mock_offload]
        )

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


class TestGetRpgsnapshot:
    """Test cases for get_rpgsnapshot function"""

    @patch("plugins.modules.purefa_pgsnap.LooseVersion")
    def test_get_rpgsnapshot_exists(self, mock_loose_version):
        """Test get_rpgsnapshot returns snapshot name when it exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {
            "name": "test-pg",
            "suffix": "snap1",
            "restore": "source-vol",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_volume_snapshots.return_value.status_code = 200

        result = get_rpgsnapshot(mock_module, mock_array)

        assert result == "test-pg.snap1.source-vol"

    @patch("plugins.modules.purefa_pgsnap.LooseVersion")
    def test_get_rpgsnapshot_not_exists(self, mock_loose_version):
        """Test get_rpgsnapshot returns None when snapshot doesn't exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {
            "name": "test-pg",
            "suffix": "snap1",
            "restore": "source-vol",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_volume_snapshots.return_value.status_code = 404

        result = get_rpgsnapshot(mock_module, mock_array)

        assert result is None


class TestUpdatePgsnapshot:
    """Test cases for update_pgsnapshot function"""

    @patch("plugins.modules.purefa_pgsnap.LooseVersion")
    def test_update_pgsnapshot_check_mode(self, mock_loose_version):
        """Test update_pgsnapshot in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-pg",
            "suffix": "snap1",
            "rename": "new-suffix",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        update_pgsnapshot(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pgsnap.check_response")
    @patch("plugins.modules.purefa_pgsnap.LooseVersion")
    def test_update_pgsnapshot_success(self, mock_loose_version, mock_check_response):
        """Test update_pgsnapshot successfully renames"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pg",
            "suffix": "snap1",
            "target": "snap2",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.patch_protection_group_snapshots.return_value = Mock(status_code=200)

        update_pgsnapshot(mock_module, mock_array)

        mock_array.patch_protection_group_snapshots.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestDeletePgsnapshotSuccess:
    """Test cases for delete_pgsnapshot success paths"""

    @patch("plugins.modules.purefa_pgsnap.check_response")
    @patch("plugins.modules.purefa_pgsnap.LooseVersion")
    def test_delete_pgsnapshot_success(self, mock_loose_version, mock_check_response):
        """Test delete_pgsnapshot successfully deletes"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pg",
            "suffix": "snap1",
            "context": "",
            "eradicate": False,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.patch_protection_group_snapshots.return_value = Mock(status_code=200)

        delete_pgsnapshot(mock_module, mock_array)

        mock_array.patch_protection_group_snapshots.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pgsnap.check_response")
    @patch("plugins.modules.purefa_pgsnap.LooseVersion")
    def test_delete_pgsnapshot_with_eradicate(
        self, mock_loose_version, mock_check_response
    ):
        """Test delete_pgsnapshot with eradicate=True"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pg",
            "suffix": "snap1",
            "context": "",
            "eradicate": True,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.patch_protection_group_snapshots.return_value = Mock(status_code=200)
        mock_array.delete_protection_group_snapshots.return_value = Mock(
            status_code=200
        )

        delete_pgsnapshot(mock_module, mock_array)

        mock_array.patch_protection_group_snapshots.assert_called_once()
        mock_array.delete_protection_group_snapshots.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestEradicatePgsnapshotSuccess:
    """Test cases for eradicate_pgsnapshot success paths"""

    @patch("plugins.modules.purefa_pgsnap.check_response")
    @patch("plugins.modules.purefa_pgsnap.LooseVersion")
    def test_eradicate_pgsnapshot_success(
        self, mock_loose_version, mock_check_response
    ):
        """Test eradicate_pgsnapshot successfully eradicates"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pg",
            "suffix": "snap1",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.delete_protection_group_snapshots.return_value = Mock(
            status_code=200
        )

        eradicate_pgsnapshot(mock_module, mock_array)

        mock_array.delete_protection_group_snapshots.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRestorePgsnapvolume:
    """Test cases for restore_pgsnapvolume function"""

    @patch("plugins.modules.purefa_pgsnap.check_response")
    @patch("plugins.modules.purefa_pgsnap.LooseVersion")
    @patch("plugins.modules.purefa_pgsnap.get_pgroupvolume")
    def test_restore_pgsnapvolume_check_mode(
        self, mock_get_pgroupvolume, mock_loose_version, mock_check_response
    ):
        """Test restore_pgsnapvolume in check mode"""
        mock_loose_version.side_effect = LooseVersion
        mock_get_pgroupvolume.return_value = Mock()  # Volume exists
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-pg",
            "suffix": "snap1",
            "restore": "vol1",
            "target": "new-vol1",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        from plugins.modules.purefa_pgsnap import restore_pgsnapvolume

        restore_pgsnapvolume(mock_module, mock_array)

        mock_array.post_volumes.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pgsnap.check_response")
    @patch("plugins.modules.purefa_pgsnap.LooseVersion")
    @patch("plugins.modules.purefa_pgsnap.get_pgroupvolume")
    def test_restore_pgsnapvolume_volume_not_in_pgroup(
        self, mock_get_pgroupvolume, mock_loose_version, mock_check_response
    ):
        """Test restore_pgsnapvolume fails when volume not in pgroup"""
        import pytest

        mock_loose_version.side_effect = LooseVersion
        mock_get_pgroupvolume.return_value = None  # Volume doesn't exist
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_module.params = {
            "name": "test-pg",
            "suffix": "snap1",
            "restore": "nonexistent-vol",
            "target": "new-vol",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        from plugins.modules.purefa_pgsnap import restore_pgsnapvolume

        with pytest.raises(SystemExit):
            restore_pgsnapvolume(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()

    @patch("plugins.modules.purefa_pgsnap.check_response")
    @patch("plugins.modules.purefa_pgsnap.LooseVersion")
    @patch("plugins.modules.purefa_pgsnap.get_pgroupvolume")
    def test_restore_pgsnapvolume_success(
        self, mock_get_pgroupvolume, mock_loose_version, mock_check_response
    ):
        """Test restore_pgsnapvolume successfully restores volume"""
        mock_loose_version.side_effect = LooseVersion
        mock_get_pgroupvolume.return_value = Mock()  # Volume exists
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pg",
            "suffix": "snap1",
            "restore": "vol1",
            "target": "new-vol1",
            "context": "",
            "overwrite": False,
            "with_default_protection": False,
            "add_to_pgs": None,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.post_volumes.return_value = Mock(status_code=200)

        from plugins.modules.purefa_pgsnap import restore_pgsnapvolume

        restore_pgsnapvolume(mock_module, mock_array)

        mock_array.post_volumes.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestCreatePgsnapshotSuccess:
    """Test cases for create_pgsnapshot success paths"""

    @patch("plugins.modules.purefa_pgsnap.check_response")
    @patch("plugins.modules.purefa_pgsnap.ProtectionGroupSnapshot")
    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_create_pgsnapshot_with_target(
        self, mock_lv, mock_pgs, mock_check_response
    ):
        """Test create_pgsnapshot with remote target"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pg",
            "suffix": "snap1",
            "apply_retention": False,
            "now": False,
            "remote": True,
            "context": "",
            "throttle": False,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_pg = Mock()
        mock_pg.target_count = 1
        mock_array.get_protection_groups.return_value = Mock(
            status_code=200, items=[mock_pg]
        )
        mock_snap = Mock()
        mock_snap.name = "test-pg.snap1"
        mock_array.post_protection_group_snapshots.return_value = Mock(
            status_code=200, items=[mock_snap]
        )

        from plugins.modules.purefa_pgsnap import create_pgsnapshot

        create_pgsnapshot(mock_module, mock_array)

        mock_array.post_protection_group_snapshots.assert_called_once()
        mock_module.exit_json.assert_called()


class TestDeletePgsnapshotSuccess:
    """Test cases for delete_pgsnapshot success paths"""

    @patch("plugins.modules.purefa_pgsnap.check_response")
    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_delete_pgsnapshot_success(self, mock_lv, mock_check_response):
        """Test delete_pgsnapshot deletes successfully"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pg",
            "suffix": "snap1",
            "context": "",
            "eradicate": False,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.patch_protection_group_snapshots.return_value = Mock(status_code=200)

        delete_pgsnapshot(mock_module, mock_array)

        mock_array.patch_protection_group_snapshots.assert_called_once()
        mock_check_response.assert_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_delete_pgsnapshot_check_mode(self):
        """Test delete_pgsnapshot in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-pg",
            "suffix": "snap1",
            "context": "",
            "eradicate": False,
        }
        mock_array = Mock()

        delete_pgsnapshot(mock_module, mock_array)

        mock_array.patch_protection_group_snapshots.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestEradicatePgsnapshotSuccess:
    """Test cases for eradicate_pgsnapshot success paths"""

    @patch("plugins.modules.purefa_pgsnap.check_response")
    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_eradicate_pgsnapshot_success(self, mock_lv, mock_check_response):
        """Test eradicate_pgsnapshot eradicates successfully"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "test-pg", "suffix": "snap1", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.delete_protection_group_snapshots.return_value = Mock(
            status_code=200
        )

        eradicate_pgsnapshot(mock_module, mock_array)

        mock_array.delete_protection_group_snapshots.assert_called_once()
        mock_check_response.assert_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_eradicate_pgsnapshot_check_mode(self):
        """Test eradicate_pgsnapshot in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-pg", "suffix": "snap1", "context": ""}
        mock_array = Mock()

        eradicate_pgsnapshot(mock_module, mock_array)

        mock_array.delete_protection_group_snapshots.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestUpdatePgsnapshotExtended:
    """Extended test cases for update_pgsnapshot"""

    @patch("plugins.modules.purefa_pgsnap.check_response")
    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_update_pgsnapshot_rename(self, mock_lv, mock_check_response):
        """Test update_pgsnapshot with rename"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pg",
            "suffix": "snap1",
            "context": "",
            "target": "snap2",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.patch_protection_group_snapshots.return_value = Mock(status_code=200)

        update_pgsnapshot(mock_module, mock_array)

        mock_array.patch_protection_group_snapshots.assert_called_once()
        mock_check_response.assert_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_update_pgsnapshot_check_mode(self):
        """Test update_pgsnapshot in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-pg",
            "suffix": "snap1",
            "context": "",
            "target": "snap2",
        }
        mock_array = Mock()

        update_pgsnapshot(mock_module, mock_array)

        mock_array.patch_protection_group_snapshots.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestDeleteOffloadSnapshot:
    """Test cases for delete_offload_snapshot function"""

    @patch("plugins.modules.purefa_pgsnap.check_response")
    @patch("plugins.modules.purefa_pgsnap._check_offload")
    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_delete_offload_snapshot_success(
        self, mock_lv, mock_check_offload, mock_check_response
    ):
        """Test successful deletion of offload snapshot"""
        from plugins.modules.purefa_pgsnap import delete_offload_snapshot

        mock_check_offload.return_value = True
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "array2:pg1",
            "suffix": "snap1",
            "offload": "s3target",
            "context": "",
            "eradicate": False,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_remote_protection_group_snapshots.return_value = Mock(
            status_code=200, items=[Mock(destroyed=False)]
        )
        mock_array.patch_remote_protection_group_snapshots.return_value = Mock(
            status_code=200
        )

        delete_offload_snapshot(mock_module, mock_array)

        mock_array.patch_remote_protection_group_snapshots.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pgsnap._check_offload")
    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_delete_offload_snapshot_offload_not_connected(
        self, mock_lv, mock_check_offload
    ):
        """Test delete_offload_snapshot fails when offload not connected"""
        import pytest
        from plugins.modules.purefa_pgsnap import delete_offload_snapshot

        mock_check_offload.return_value = False
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "array2:pg1",
            "suffix": "snap1",
            "offload": "s3target",
            "context": "",
            "eradicate": False,
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        with pytest.raises(SystemExit):
            delete_offload_snapshot(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()
        assert "not exist or not connected" in mock_module.fail_json.call_args[1]["msg"]

    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_delete_offload_snapshot_bad_name_format(self, mock_lv):
        """Test delete_offload_snapshot fails with bad name format"""
        import pytest
        from plugins.modules.purefa_pgsnap import delete_offload_snapshot

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "pg1",  # No colon - bad format
            "suffix": "snap1",
            "offload": "s3target",
            "context": "",
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        with pytest.raises(SystemExit):
            delete_offload_snapshot(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()
        assert "not in the correct format" in mock_module.fail_json.call_args[1]["msg"]

    @patch("plugins.modules.purefa_pgsnap.check_response")
    @patch("plugins.modules.purefa_pgsnap._check_offload")
    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_delete_offload_snapshot_with_eradicate(
        self, mock_lv, mock_check_offload, mock_check_response
    ):
        """Test deletion of offload snapshot with eradicate"""
        from plugins.modules.purefa_pgsnap import delete_offload_snapshot

        mock_check_offload.return_value = True
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "array2:pg1",
            "suffix": "snap1",
            "offload": "s3target",
            "context": "",
            "eradicate": True,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_remote_protection_group_snapshots.return_value = Mock(
            status_code=200, items=[Mock(destroyed=False)]
        )
        mock_array.patch_remote_protection_group_snapshots.return_value = Mock(
            status_code=200
        )
        mock_array.delete_remote_protection_group_snapshots.return_value = Mock(
            status_code=200
        )

        delete_offload_snapshot(mock_module, mock_array)

        mock_array.patch_remote_protection_group_snapshots.assert_called_once()
        mock_array.delete_remote_protection_group_snapshots.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestUpdatePgSnapshot:
    """Test cases for update_pgsnapshot function"""

    @patch("plugins.modules.purefa_pgsnap.check_response")
    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_update_pgsnapshot_success(self, mock_lv, mock_check_response):
        """Test updating/renaming a protection group snapshot"""
        from plugins.modules.purefa_pgsnap import update_pgsnapshot

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "pg1",
            "suffix": "snap1",
            "target": "snap2",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.patch_protection_group_snapshots.return_value = Mock(status_code=200)

        update_pgsnapshot(mock_module, mock_array)

        mock_array.patch_protection_group_snapshots.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_update_pgsnapshot_check_mode(self, mock_lv):
        """Test updating snapshot in check mode"""
        from plugins.modules.purefa_pgsnap import update_pgsnapshot

        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "pg1",
            "suffix": "snap1",
            "target": "snap2",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        update_pgsnapshot(mock_module, mock_array)

        mock_array.patch_protection_group_snapshots.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pgsnap.check_response")
    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_update_pgsnapshot_older_api(self, mock_lv, mock_check_response):
        """Test updating snapshot with older API version"""
        from plugins.modules.purefa_pgsnap import update_pgsnapshot

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "pg1",
            "suffix": "snap1",
            "target": "snap2",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.16"
        mock_array.patch_protection_group_snapshots.return_value = Mock(status_code=200)

        update_pgsnapshot(mock_module, mock_array)

        mock_array.patch_protection_group_snapshots.assert_called_once()
        # Verify no context_names kwarg in call
        call_kwargs = mock_array.patch_protection_group_snapshots.call_args[1]
        assert "context_names" not in call_kwargs
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestEradicatePgSnapshot:
    """Test cases for eradicate_pgsnapshot function"""

    @patch("plugins.modules.purefa_pgsnap.check_response")
    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_eradicate_pgsnapshot_success(self, mock_lv, mock_check_response):
        """Test eradicating a protection group snapshot"""
        from plugins.modules.purefa_pgsnap import eradicate_pgsnapshot

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "pg1",
            "suffix": "snap1",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.delete_protection_group_snapshots.return_value = Mock(
            status_code=200
        )

        eradicate_pgsnapshot(mock_module, mock_array)

        mock_array.delete_protection_group_snapshots.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_eradicate_pgsnapshot_check_mode(self, mock_lv):
        """Test eradicating snapshot in check mode"""
        from plugins.modules.purefa_pgsnap import eradicate_pgsnapshot

        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "pg1",
            "suffix": "snap1",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        eradicate_pgsnapshot(mock_module, mock_array)

        mock_array.delete_protection_group_snapshots.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pgsnap.check_response")
    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_eradicate_pgsnapshot_older_api(self, mock_lv, mock_check_response):
        """Test eradicating snapshot with older API version"""
        from plugins.modules.purefa_pgsnap import eradicate_pgsnapshot

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "pg1",
            "suffix": "snap1",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.16"
        mock_array.delete_protection_group_snapshots.return_value = Mock(
            status_code=200
        )

        eradicate_pgsnapshot(mock_module, mock_array)

        mock_array.delete_protection_group_snapshots.assert_called_once()
        # Verify no context_names kwarg in call
        call_kwargs = mock_array.delete_protection_group_snapshots.call_args[1]
        assert "context_names" not in call_kwargs
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestGetPgroupvolume:
    """Test cases for get_pgroupvolume function"""

    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_get_pgroupvolume_host_pg_context_api(self, mock_lv):
        """Test get_pgroupvolume with host PG and context API"""
        from plugins.modules.purefa_pgsnap import get_pgroupvolume

        mock_module = Mock()
        mock_module.params = {
            "name": "pg1",
            "context": "",
            "restore": "vol1",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock pgroup with host_count > 0
        mock_pgroup = Mock()
        mock_pgroup.host_count = 1
        mock_pgroup.host_group_count = 0
        mock_array.get_protection_groups.return_value = Mock(
            status_code=200, items=[mock_pgroup]
        )

        # Mock hosts in protection group
        mock_host = Mock()
        mock_host.member = Mock()
        mock_host.member.name = "host1"
        mock_array.get_protection_groups_hosts.return_value = Mock(
            status_code=200, items=[mock_host]
        )

        # Mock volumes connected to host
        mock_connection = Mock()
        mock_connection.volume = Mock()
        mock_connection.volume.name = "vol1"
        mock_array.get_connections.return_value = Mock(
            status_code=200, items=[mock_connection]
        )

        result = get_pgroupvolume(mock_module, mock_array)

        assert result == "vol1"
        mock_array.get_protection_groups.assert_called_once()
        mock_array.get_protection_groups_hosts.assert_called_once()
        mock_array.get_connections.assert_called_once()

    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_get_pgroupvolume_hostgroup_pg_context_api(self, mock_lv):
        """Test get_pgroupvolume with hostgroup PG and context API"""
        from plugins.modules.purefa_pgsnap import get_pgroupvolume

        mock_module = Mock()
        mock_module.params = {
            "name": "pg1",
            "context": "",
            "restore": "vol2",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock pgroup with host_group_count > 0
        mock_pgroup = Mock()
        mock_pgroup.host_count = 0
        mock_pgroup.host_group_count = 1
        mock_array.get_protection_groups.return_value = Mock(
            status_code=200, items=[mock_pgroup]
        )

        # Mock hostgroups in protection group
        mock_hgroup = Mock()
        mock_hgroup.member = Mock()
        mock_hgroup.member.name = "hg1"
        mock_array.get_protection_groups_host_groups.return_value = Mock(
            status_code=200, items=[mock_hgroup]
        )

        # Mock volumes connected to hostgroup
        mock_connection = Mock()
        mock_connection.volume = Mock()
        mock_connection.volume.name = "vol2"
        mock_array.get_connections.return_value = Mock(
            status_code=200, items=[mock_connection]
        )

        # Mock hosts in hostgroup
        mock_hg_host = Mock()
        mock_hg_host.member = Mock()
        mock_hg_host.member.name = "host_in_hg"
        mock_array.get_host_groups_hosts.return_value = Mock(
            status_code=200, items=[mock_hg_host]
        )

        result = get_pgroupvolume(mock_module, mock_array)

        assert result == "vol2"

    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_get_pgroupvolume_volume_pg_context_api(self, mock_lv):
        """Test get_pgroupvolume with volume PG and context API"""
        from plugins.modules.purefa_pgsnap import get_pgroupvolume

        mock_module = Mock()
        mock_module.params = {
            "name": "pg1",
            "context": "",
            "restore": "vol3",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock pgroup with no hosts or hostgroups (volume PG)
        mock_pgroup = Mock()
        mock_pgroup.host_count = 0
        mock_pgroup.host_group_count = 0
        mock_array.get_protection_groups.return_value = Mock(
            status_code=200, items=[mock_pgroup]
        )

        # Mock volumes in protection group
        mock_vol_entry = Mock()
        mock_vol_entry.member = Mock()
        mock_vol_entry.member.name = "vol3"
        mock_array.get_protection_groups_volumes.return_value = Mock(
            status_code=200, items=[mock_vol_entry]
        )

        result = get_pgroupvolume(mock_module, mock_array)

        assert result == "vol3"
        mock_array.get_protection_groups_volumes.assert_called_once()

    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_get_pgroupvolume_volume_not_found(self, mock_lv):
        """Test get_pgroupvolume when volume is not found"""
        from plugins.modules.purefa_pgsnap import get_pgroupvolume

        mock_module = Mock()
        mock_module.params = {
            "name": "pg1",
            "context": "",
            "restore": "nonexistent_vol",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock pgroup with no hosts or hostgroups (volume PG)
        mock_pgroup = Mock()
        mock_pgroup.host_count = 0
        mock_pgroup.host_group_count = 0
        mock_array.get_protection_groups.return_value = Mock(
            status_code=200, items=[mock_pgroup]
        )

        # Mock volumes in protection group - different volume
        mock_vol_entry = Mock()
        mock_vol_entry.member = Mock()
        mock_vol_entry.member.name = "other_vol"
        mock_array.get_protection_groups_volumes.return_value = Mock(
            status_code=200, items=[mock_vol_entry]
        )

        result = get_pgroupvolume(mock_module, mock_array)

        assert result is None

    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_get_pgroupvolume_exception_returns_none(self, mock_lv):
        """Test get_pgroupvolume returns None on exception"""
        from plugins.modules.purefa_pgsnap import get_pgroupvolume

        mock_module = Mock()
        mock_module.params = {
            "name": "pg1",
            "context": "",
            "restore": "vol1",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_protection_groups.side_effect = Exception("API error")

        result = get_pgroupvolume(mock_module, mock_array)

        assert result is None

    @patch("plugins.modules.purefa_pgsnap.LooseVersion", side_effect=LooseVersion)
    def test_get_pgroupvolume_pod_volume(self, mock_lv):
        """Test get_pgroupvolume with pod volume (:: in name)"""
        from plugins.modules.purefa_pgsnap import get_pgroupvolume

        mock_module = Mock()
        mock_module.params = {
            "name": "pod1::pg1",
            "context": "",
            "restore": "vol1",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock pgroup with no hosts or hostgroups (volume PG)
        mock_pgroup = Mock()
        mock_pgroup.host_count = 0
        mock_pgroup.host_group_count = 0
        mock_array.get_protection_groups.return_value = Mock(
            status_code=200, items=[mock_pgroup]
        )

        # Mock volumes in protection group - pod volume
        mock_vol_entry = Mock()
        mock_vol_entry.member = Mock()
        mock_vol_entry.member.name = "pod1::vol1"
        mock_array.get_protection_groups_volumes.return_value = Mock(
            status_code=200, items=[mock_vol_entry]
        )

        result = get_pgroupvolume(mock_module, mock_array)

        assert result == "pod1::vol1"
