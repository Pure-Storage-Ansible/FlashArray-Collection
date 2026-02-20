# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_fs module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from unittest.mock import Mock, MagicMock, patch
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

from plugins.modules.purefa_fs import (
    delete_fs,
    recover_fs,
    eradicate_fs,
    rename_fs,
    create_fs,
)


class TestDeleteFs:
    """Test cases for delete_fs function"""

    def test_delete_fs_check_mode(self):
        """Test delete_fs in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-fs", "eradicate": False}
        mock_array = Mock()

        delete_fs(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_fs.check_response")
    @patch("plugins.modules.purefa_fs.LooseVersion", side_effect=LooseVersion)
    def test_delete_fs_success(self, mock_lv, mock_check_response):
        """Test delete_fs successfully deletes file system"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "test-fs", "eradicate": False, "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        mock_array.patch_file_systems.return_value = Mock(status_code=200)

        delete_fs(mock_module, mock_array)

        mock_array.patch_file_systems.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_fs.check_response")
    @patch("plugins.modules.purefa_fs.LooseVersion", side_effect=LooseVersion)
    def test_delete_fs_with_eradicate(self, mock_lv, mock_check_response):
        """Test delete_fs with eradicate flag"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "test-fs", "eradicate": True, "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        mock_array.patch_file_systems.return_value = Mock(status_code=200)
        mock_array.delete_file_systems.return_value = Mock(status_code=200)

        delete_fs(mock_module, mock_array)

        mock_array.patch_file_systems.assert_called_once()
        mock_array.delete_file_systems.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRecoverFs:
    """Test cases for recover_fs function"""

    def test_recover_fs_check_mode(self):
        """Test recover_fs in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "deleted-fs"}
        mock_array = Mock()

        recover_fs(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_fs.check_response")
    @patch("plugins.modules.purefa_fs.LooseVersion", side_effect=LooseVersion)
    def test_recover_fs_success(self, mock_lv, mock_check_response):
        """Test recover_fs successfully recovers file system"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "deleted-fs", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        mock_array.patch_file_systems.return_value = Mock(status_code=200)

        recover_fs(mock_module, mock_array)

        mock_array.patch_file_systems.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestEradicateFs:
    """Test cases for eradicate_fs function"""

    def test_eradicate_fs_check_mode(self):
        """Test eradicate_fs in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "deleted-fs"}
        mock_array = Mock()

        eradicate_fs(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_fs.check_response")
    @patch("plugins.modules.purefa_fs.LooseVersion", side_effect=LooseVersion)
    def test_eradicate_fs_success(self, mock_lv, mock_check_response):
        """Test eradicate_fs successfully eradicates file system"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "deleted-fs", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        mock_array.delete_file_systems.return_value = Mock(status_code=200)

        eradicate_fs(mock_module, mock_array)

        mock_array.delete_file_systems.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRenameFs:
    """Test cases for rename_fs function"""

    @patch("plugins.modules.purefa_fs.LooseVersion")
    def test_rename_fs_check_mode(self, mock_loose_version):
        """Test rename_fs in check mode"""
        mock_loose_version.side_effect = LooseVersion
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "old-fs",
            "rename": "new-fs",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        # Target doesn't exist
        mock_array.get_file_systems.return_value = Mock(status_code=404)

        rename_fs(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_fs.check_response")
    @patch("plugins.modules.purefa_fs.LooseVersion", side_effect=LooseVersion)
    def test_rename_fs_success(self, mock_lv, mock_check_response):
        """Test rename_fs successfully renames file system"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "old-fs",
            "rename": "new-fs",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        mock_array.get_file_systems.return_value = Mock(status_code=404)
        mock_array.patch_file_systems.return_value = Mock(status_code=200)

        rename_fs(mock_module, mock_array)

        mock_array.patch_file_systems.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestCreateFs:
    """Test cases for create_fs function"""

    @patch("plugins.modules.purefa_fs.LooseVersion")
    def test_create_fs_check_mode(self, mock_loose_version):
        """Test create_fs in check mode"""
        mock_loose_version.side_effect = LooseVersion
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "new-fs", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"

        create_fs(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_fs.check_response")
    @patch("plugins.modules.purefa_fs.LooseVersion", side_effect=LooseVersion)
    def test_create_fs_success(self, mock_lv, mock_check_response):
        """Test create_fs successfully creates file system"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "new-fs", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        mock_array.post_file_systems.return_value = Mock(status_code=200)

        create_fs(mock_module, mock_array)

        mock_array.post_file_systems.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_fs.check_response")
    @patch("plugins.modules.purefa_fs.LooseVersion", side_effect=LooseVersion)
    def test_create_fs_in_pod_success(self, mock_lv, mock_check_response):
        """Test create_fs successfully creates file system in a pod"""
        mock_pod = Mock()
        mock_pod.promotion_status = "promoted"
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "mypod::new-fs", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        mock_array.get_pods.return_value = Mock(status_code=200, items=[mock_pod])
        mock_array.post_file_systems.return_value = Mock(status_code=200)

        create_fs(mock_module, mock_array)

        mock_array.post_file_systems.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_fs.LooseVersion", side_effect=LooseVersion)
    def test_create_fs_in_pod_not_exists(self, mock_lv):
        """Test create_fs fails when pod doesn't exist"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_module.params = {"name": "nonexistent::new-fs", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        mock_array.get_pods.return_value = Mock(status_code=404)

        with pytest.raises(SystemExit):
            create_fs(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()

    @patch("plugins.modules.purefa_fs.LooseVersion", side_effect=LooseVersion)
    def test_create_fs_in_demoted_pod_fails(self, mock_lv):
        """Test create_fs fails when pod is demoted"""
        import pytest

        mock_pod = Mock()
        mock_pod.promotion_status = "demoted"
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_module.params = {"name": "demoted-pod::new-fs", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        mock_array.get_pods.return_value = Mock(status_code=200, items=[mock_pod])

        with pytest.raises(SystemExit):
            create_fs(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()


class TestRenameFsExtended:
    """Extended test cases for rename_fs function"""

    @patch("plugins.modules.purefa_fs.LooseVersion", side_effect=LooseVersion)
    def test_rename_fs_target_exists_fails(self, mock_lv):
        """Test rename_fs fails when target exists"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_module.params = {
            "name": "old-fs",
            "rename": "existing-fs",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        # Target exists
        mock_array.get_file_systems.return_value = Mock(status_code=200, items=[Mock()])

        with pytest.raises(SystemExit):
            rename_fs(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()

    @patch("plugins.modules.purefa_fs.check_response")
    @patch("plugins.modules.purefa_fs.LooseVersion", side_effect=LooseVersion)
    def test_rename_fs_in_pod_success(self, mock_lv, mock_check_response):
        """Test rename_fs successfully renames file system in pod"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "mypod::old-fs",
            "rename": "new-fs",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        mock_array.get_file_systems.return_value = Mock(status_code=404)
        mock_array.patch_file_systems.return_value = Mock(status_code=200)

        rename_fs(mock_module, mock_array)

        mock_array.patch_file_systems.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestMoveFs:
    """Test cases for move_fs function"""

    @patch("plugins.modules.purefa_fs.LooseVersion", side_effect=LooseVersion)
    def test_move_fs_to_local_same_location_fails(self, mock_lv):
        """Test move_fs fails when source and destination are the same"""
        import pytest
        from plugins.modules.purefa_fs import move_fs

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-fs",  # Not in a pod
            "move": "local",
            "context": "",
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"

        with pytest.raises(SystemExit):
            move_fs(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()
        assert "cannot be the same" in mock_module.fail_json.call_args[1]["msg"]

    @patch("plugins.modules.purefa_fs.check_response")
    @patch("plugins.modules.purefa_fs.LooseVersion", side_effect=LooseVersion)
    def test_move_fs_to_local_success(self, mock_lv, mock_check_response):
        """Test move_fs successfully moves filesystem to local"""
        from plugins.modules.purefa_fs import move_fs

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "mypod::test-fs",  # In a pod
            "move": "local",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        mock_array.get_file_systems.return_value = Mock(status_code=404)
        mock_array.patch_file_systems.return_value = Mock(status_code=200)

        move_fs(mock_module, mock_array)

        mock_array.patch_file_systems.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_fs.check_response")
    @patch("plugins.modules.purefa_fs.LooseVersion", side_effect=LooseVersion)
    def test_move_fs_to_pod_success(self, mock_lv, mock_check_response):
        """Test move_fs successfully moves filesystem to a pod"""
        from plugins.modules.purefa_fs import move_fs

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-fs",
            "move": "target-pod",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        mock_array.get_pods.return_value = Mock(
            status_code=200,
            items=[
                Mock(
                    arrays=[Mock()],  # Single array
                    link_target_count=0,
                    promotion_status="promoted",
                )
            ],
        )
        mock_array.patch_file_systems.return_value = Mock(status_code=200)

        move_fs(mock_module, mock_array)

        mock_array.patch_file_systems.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_fs.LooseVersion", side_effect=LooseVersion)
    def test_move_fs_to_stretched_pod_fails(self, mock_lv):
        """Test move_fs fails when moving to a stretched pod"""
        import pytest
        from plugins.modules.purefa_fs import move_fs

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-fs",
            "move": "stretched-pod",
            "context": "",
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        mock_array.get_pods.return_value = Mock(
            status_code=200,
            items=[
                Mock(
                    arrays=[Mock(), Mock()],  # Multiple arrays = stretched
                    link_target_count=0,
                    promotion_status="promoted",
                )
            ],
        )

        with pytest.raises(SystemExit):
            move_fs(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()
        assert "stretched pod" in mock_module.fail_json.call_args[1]["msg"]

    @patch("plugins.modules.purefa_fs.LooseVersion", side_effect=LooseVersion)
    def test_move_fs_check_mode(self, mock_lv):
        """Test move_fs in check mode"""
        from plugins.modules.purefa_fs import move_fs

        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-fs",
            "move": "target-pod",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        mock_array.get_pods.return_value = Mock(
            status_code=200,
            items=[
                Mock(
                    arrays=[Mock()],
                    link_target_count=0,
                    promotion_status="promoted",
                )
            ],
        )

        move_fs(mock_module, mock_array)

        mock_array.patch_file_systems.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)
