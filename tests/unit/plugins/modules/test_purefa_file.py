# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_file module."""

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

from plugins.modules.purefa_file import (
    _check_dirs,
)


class TestCheckDirs:
    """Tests for _check_dirs function"""

    def test_check_dirs_success(self):
        """Test _check_dirs when both directories exist"""
        mock_module = Mock()
        mock_module.params = {"source_dir": "src_dir", "target_dir": "tgt_dir"}
        mock_array = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_array.get_directories.return_value = mock_response

        # Should not raise any errors
        _check_dirs(mock_module, mock_array)

        assert mock_array.get_directories.call_count == 2

    @patch("plugins.modules.purefa_file.check_response")
    def test_check_dirs_source_not_found(self, mock_check_response):
        """Test _check_dirs when source directory doesn't exist"""
        mock_module = Mock()
        mock_module.params = {"source_dir": "missing_src", "target_dir": "tgt_dir"}
        mock_array = Mock()
        mock_response = Mock()
        mock_response.status_code = 400
        mock_array.get_directories.return_value = mock_response

        _check_dirs(mock_module, mock_array)

        mock_check_response.assert_called()

    @patch("plugins.modules.purefa_file.check_response")
    def test_check_dirs_target_not_found(self, mock_check_response):
        """Test _check_dirs when target directory doesn't exist"""
        mock_module = Mock()
        mock_module.params = {"source_dir": "src_dir", "target_dir": "missing_tgt"}
        mock_array = Mock()
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response2 = Mock()
        mock_response2.status_code = 400
        mock_array.get_directories.side_effect = [mock_response1, mock_response2]

        _check_dirs(mock_module, mock_array)

        assert mock_array.get_directories.call_count == 2
        mock_check_response.assert_called()
