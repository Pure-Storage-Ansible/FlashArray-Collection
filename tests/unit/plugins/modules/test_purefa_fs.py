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
