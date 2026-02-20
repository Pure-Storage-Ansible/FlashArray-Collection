# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_dirsnap module."""

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

from plugins.modules.purefa_dirsnap import (
    eradicate_snap,
    delete_snap,
)


class TestEradicateSnap:
    """Tests for eradicate_snap function"""

    @patch("plugins.modules.purefa_dirsnap.LooseVersion")
    def test_eradicate_snap_check_mode(self, mock_loose_version):
        """Test eradicate_snap in check mode"""
        mock_module = Mock()
        mock_module.params = {
            "name": "snap1",
            "filesystem": "fs1",
            "directory": "dir1",
            "context": "",
        }
        mock_module.check_mode = True
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        mock_loose_version.side_effect = LooseVersion

        eradicate_snap(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestDeleteSnap:
    """Tests for delete_snap function"""

    @patch("plugins.modules.purefa_dirsnap.LooseVersion")
    def test_delete_snap_check_mode(self, mock_loose_version):
        """Test delete_snap in check mode"""
        mock_module = Mock()
        mock_module.params = {
            "name": "snap1",
            "filesystem": "fs1",
            "directory": "dir1",
            "context": "",
            "eradicate": False,
        }
        mock_module.check_mode = True
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.42"
        mock_loose_version.side_effect = LooseVersion

        delete_snap(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
