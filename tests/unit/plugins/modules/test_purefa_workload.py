# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_workload module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from unittest.mock import Mock, MagicMock

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

from plugins.modules.purefa_workload import (
    delete_workload,
    eradicate_workload,
    recover_workload,
    rename_workload,
)


class TestDeleteWorkload:
    """Test cases for delete_workload function"""

    def test_delete_workload_check_mode(self):
        """Test delete_workload in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-workload",
            "context": "",
            "eradicate": False,
        }
        mock_array = Mock()

        delete_workload(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestEradicateWorkload:
    """Test cases for eradicate_workload function"""

    def test_eradicate_workload_check_mode(self):
        """Test eradicate_workload in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-workload", "context": ""}
        mock_array = Mock()

        eradicate_workload(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRecoverWorkload:
    """Test cases for recover_workload function"""

    def test_recover_workload_check_mode(self):
        """Test recover_workload in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-workload", "context": "", "host": ""}
        mock_array = Mock()

        recover_workload(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRenameWorkload:
    """Test cases for rename_workload function"""

    def test_rename_workload_check_mode(self):
        """Test rename_workload in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "old-workload",
            "rename": "new-workload",
            "context": "",
        }
        mock_array = Mock()

        rename_workload(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)