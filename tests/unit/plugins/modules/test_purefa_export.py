# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_export module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from unittest.mock import Mock, MagicMock, patch

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

from plugins.modules.purefa_export import (
    create_export,
    delete_export,
)


class TestCreateExport:
    """Tests for create_export function"""

    def test_create_export_no_policy(self):
        """Test create_export when no policy is provided"""
        mock_module = Mock()
        mock_module.params = {
            "filesystem": "fs1",
            "directory": "dir1",
            "nfs_policy": None,
            "smb_policy": None,
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"

        create_export(mock_module, mock_array)

        mock_module.fail_json.assert_called_once_with(
            msg="At least one policy must be provided"
        )


class TestDeleteExport:
    """Tests for delete_export function"""

    def test_delete_export_no_policy(self):
        """Test delete_export when no policy is provided"""
        mock_module = Mock()
        mock_module.params = {
            "name": "export1",
            "filesystem": "fs1",
            "directory": "dir1",
            "nfs_policy": None,
            "smb_policy": None,
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"

        delete_export(mock_module, mock_array)

        mock_module.fail_json.assert_called_once_with(
            msg="At least one policy must be provided"
        )

    @patch("plugins.modules.purefa_export.check_response")
    @patch("plugins.modules.purefa_export.LooseVersion", side_effect=LooseVersion)
    def test_delete_export_nfs_policy_success(self, mock_lv, mock_check_response):
        """Test delete_export with NFS policy"""
        mock_module = Mock()
        mock_module.params = {
            "name": "export1",
            "filesystem": "fs1",
            "directory": "dir1",
            "nfs_policy": "nfs_policy1",
            "smb_policy": None,
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        mock_array.get_directory_exports.return_value = Mock(status_code=200)
        mock_array.delete_directory_exports.return_value = Mock(status_code=200)

        delete_export(mock_module, mock_array)

        mock_array.delete_directory_exports.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_export.LooseVersion", side_effect=LooseVersion)
    def test_delete_export_check_mode(self, mock_lv):
        """Test delete_export in check mode"""
        mock_module = Mock()
        mock_module.params = {
            "name": "export1",
            "filesystem": "fs1",
            "directory": "dir1",
            "nfs_policy": "nfs_policy1",
            "smb_policy": None,
            "context": "",
        }
        mock_module.check_mode = True
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        mock_array.get_directory_exports.return_value = Mock(status_code=200)

        delete_export(mock_module, mock_array)

        mock_array.delete_directory_exports.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_export.LooseVersion", side_effect=LooseVersion)
    def test_delete_export_policy_not_exists(self, mock_lv):
        """Test delete_export when policy doesn't exist"""
        mock_module = Mock()
        mock_module.params = {
            "name": "export1",
            "filesystem": "fs1",
            "directory": "dir1",
            "nfs_policy": "nfs_policy1",
            "smb_policy": None,
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        mock_array.get_directory_exports.return_value = Mock(status_code=400)

        delete_export(mock_module, mock_array)

        mock_array.delete_directory_exports.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=False)
