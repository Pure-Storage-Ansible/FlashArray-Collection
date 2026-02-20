# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_alert module."""

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

from plugins.modules.purefa_alert import (
    create_alert,
    delete_alert,
    update_alert,
)


class TestCreateAlert:
    """Tests for create_alert function"""

    def test_create_alert_check_mode(self):
        """Test create_alert in check mode"""
        mock_module = Mock()
        mock_module.params = {"address": "test@example.com", "enabled": True}
        mock_module.check_mode = True
        mock_array = Mock()

        create_alert(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.post_alert_watchers.assert_not_called()


class TestDeleteAlert:
    """Tests for delete_alert function"""

    def test_delete_alert_check_mode(self):
        """Test delete_alert in check mode"""
        mock_module = Mock()
        mock_module.params = {"address": "test@example.com"}
        mock_module.check_mode = True
        mock_array = Mock()

        delete_alert(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.delete_alert_watchers.assert_not_called()

    def test_delete_alert_builtin_fails(self):
        """Test delete_alert fails for built-in address"""
        mock_module = Mock()
        mock_module.params = {"address": "flasharray-alerts@purestorage.com"}
        mock_module.check_mode = False
        mock_array = Mock()

        delete_alert(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()


class TestUpdateAlert:
    """Tests for update_alert function"""

    def test_update_alert_no_change(self):
        """Test update_alert when no change needed"""
        mock_module = Mock()
        mock_module.params = {"address": "test@example.com", "enabled": True}
        mock_module.check_mode = False
        mock_array = Mock()

        update_alert(mock_module, mock_array, enabled=True)

        mock_module.exit_json.assert_called_once_with(changed=False)
        mock_array.patch_alert_watchers.assert_not_called()

    def test_update_alert_check_mode(self):
        """Test update_alert in check mode when change needed"""
        mock_module = Mock()
        mock_module.params = {"address": "test@example.com", "enabled": False}
        mock_module.check_mode = True
        mock_array = Mock()

        update_alert(mock_module, mock_array, enabled=True)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.patch_alert_watchers.assert_not_called()
