# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_smtp module."""

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

from plugins.modules.purefa_smtp import (
    delete_smtp,
    create_smtp,
)


class TestDeleteSmtp:
    """Tests for delete_smtp function"""

    def test_delete_smtp_check_mode(self):
        """Test delete_smtp in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_array = Mock()

        delete_smtp(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.patch_smtp_servers.assert_not_called()


class TestCreateSmtp:
    """Tests for create_smtp function"""

    def test_create_smtp_no_change(self):
        """Test create_smtp when settings already match"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "sender_domain": "example.com",
            "relay_host": "smtp.example.com",
            "user": None,
            "user_name": None,
            "password": None,
            "encryption_mode": "tls",
            "sender": None,
            "subject_prefix": "[Alert]",
            "body_prefix": "FlashArray:",
        }
        mock_array = Mock()
        # Current settings match
        mock_smtp = Mock()
        mock_smtp.sender_domain = "example.com"
        mock_smtp.relay_host = "smtp.example.com"
        mock_smtp.user_name = None
        mock_smtp.encryption_mode = "tls"
        mock_smtp.sender_username = None
        mock_smtp.subject_prefix = "[Alert]"
        mock_smtp.body_prefix = "FlashArray:"
        mock_array.get_smtp_servers.return_value.items = [mock_smtp]

        create_smtp(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=False)
