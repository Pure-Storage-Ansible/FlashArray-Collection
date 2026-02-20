# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_directory module."""

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

from plugins.modules.purefa_directory import (
    delete_dir,
    rename_dir,
    create_dir,
)


class TestDeleteDir:
    """Tests for delete_dir function"""

    @patch("plugins.modules.purefa_directory.LooseVersion")
    def test_delete_dir_check_mode(self, mock_loose_version):
        """Test delete_dir in check mode"""
        mock_module = Mock()
        mock_module.params = {"name": "dir1", "filesystem": "fs1", "context": ""}
        mock_module.check_mode = True
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_loose_version.side_effect = LooseVersion

        delete_dir(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.delete_directories.assert_not_called()

    @patch("plugins.modules.purefa_directory.check_response")
    @patch("plugins.modules.purefa_directory.LooseVersion", side_effect=LooseVersion)
    def test_delete_dir_success(self, mock_lv, mock_check_response):
        """Test delete_dir successfully deletes directory"""
        mock_module = Mock()
        mock_module.params = {"name": "dir1", "filesystem": "fs1", "context": ""}
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.delete_directories.return_value = Mock(status_code=200)

        delete_dir(mock_module, mock_array)

        mock_array.delete_directories.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRenameDir:
    """Tests for rename_dir function"""

    @patch("plugins.modules.purefa_directory.check_response")
    @patch("plugins.modules.purefa_directory.LooseVersion", side_effect=LooseVersion)
    def test_rename_dir_success(self, mock_lv, mock_check_response):
        """Test rename_dir successfully renames directory"""
        mock_module = Mock()
        mock_module.params = {
            "name": "dir1",
            "filesystem": "fs1",
            "rename": "dir2",
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_directories.return_value = Mock(status_code=400)  # Target not exists
        mock_array.patch_directories.return_value = Mock(status_code=200)

        rename_dir(mock_module, mock_array)

        mock_array.patch_directories.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_directory.LooseVersion", side_effect=LooseVersion)
    def test_rename_dir_target_exists(self, mock_lv):
        """Test rename_dir fails when target exists"""
        mock_module = Mock()
        mock_module.params = {
            "name": "dir1",
            "filesystem": "fs1",
            "rename": "dir2",
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_directories.return_value = Mock(status_code=200)  # Target exists

        rename_dir(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()


class TestCreateDir:
    """Tests for create_dir function"""

    @patch("plugins.modules.purefa_directory.LooseVersion", side_effect=LooseVersion)
    def test_create_dir_check_mode(self, mock_lv):
        """Test create_dir in check mode"""
        mock_module = Mock()
        mock_module.params = {
            "name": "dir1",
            "filesystem": "fs1",
            "path": None,
            "context": "",
        }
        mock_module.check_mode = True
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_directories.return_value = Mock(items=[])

        create_dir(mock_module, mock_array)

        mock_array.post_directories.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_directory.check_response")
    @patch("plugins.modules.purefa_directory.LooseVersion", side_effect=LooseVersion)
    def test_create_dir_success(self, mock_lv, mock_check_response):
        """Test create_dir successfully creates directory"""
        mock_module = Mock()
        mock_module.params = {
            "name": "dir1",
            "filesystem": "fs1",
            "path": "/dir1",
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_directories.return_value = Mock(items=[])
        mock_array.post_directories.return_value = Mock(status_code=200)

        create_dir(mock_module, mock_array)

        mock_array.post_directories.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_directory.LooseVersion", side_effect=LooseVersion)
    def test_create_dir_path_exists(self, mock_lv):
        """Test create_dir fails when path exists"""
        mock_module = Mock()
        mock_module.params = {
            "name": "dir1",
            "filesystem": "fs1",
            "path": "dir1",
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock existing directory with same path
        mock_existing_dir = Mock()
        mock_existing_dir.path = "/dir1"
        mock_array.get_directories.return_value = Mock(items=[mock_existing_dir])

        create_dir(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()
