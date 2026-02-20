# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_ad module."""

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

from plugins.modules.purefa_ad import (
    delete_account,
)


class TestDeleteAccount:
    """Tests for delete_account function"""

    def test_delete_account_check_mode(self):
        """Test delete_account in check mode"""
        mock_module = Mock()
        mock_module.params = {"name": "ad-account", "local_only": False}
        mock_module.check_mode = True
        mock_array = Mock()

        delete_account(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.delete_active_directory.assert_not_called()

    @patch("plugins.modules.purefa_ad.check_response")
    def test_delete_account_success(self, mock_check_response):
        """Test delete_account successfully deletes account"""
        mock_module = Mock()
        mock_module.params = {"name": "ad-account", "local_only": False}
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.delete_active_directory.return_value = Mock(status_code=200)

        delete_account(mock_module, mock_array)

        mock_array.delete_active_directory.assert_called_once_with(
            names=["ad-account"], local_only=False
        )
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_ad.check_response")
    def test_delete_account_local_only(self, mock_check_response):
        """Test delete_account with local_only option"""
        mock_module = Mock()
        mock_module.params = {"name": "ad-account", "local_only": True}
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.delete_active_directory.return_value = Mock(status_code=200)

        delete_account(mock_module, mock_array)

        mock_array.delete_active_directory.assert_called_once_with(
            names=["ad-account"], local_only=True
        )


class TestUpdateAccount:
    """Tests for update_account function"""

    def test_update_account_no_changes(self):
        """Test update_account when no changes needed"""
        mock_module = Mock()
        mock_module.params = {"name": "ad-account", "tls": "required"}
        mock_module.check_mode = False
        mock_array = Mock()

        # Current account has same TLS setting
        mock_account = Mock()
        mock_account.tls = "required"
        mock_array.get_active_directory.return_value = Mock(items=[mock_account])

        from plugins.modules.purefa_ad import update_account

        update_account(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=False)
        mock_array.patch_active_directory.assert_not_called()

    @patch("plugins.modules.purefa_ad.ActiveDirectoryPatch")
    @patch("plugins.modules.purefa_ad.check_response")
    def test_update_account_tls_change(self, mock_check_response, mock_ad_patch_class):
        """Test update_account when TLS setting changes"""
        mock_module = Mock()
        mock_module.params = {"name": "ad-account", "tls": "optional"}
        mock_module.check_mode = False
        mock_array = Mock()

        # Current account has different TLS setting
        mock_account = Mock()
        mock_account.tls = "required"
        mock_array.get_active_directory.return_value = Mock(items=[mock_account])
        mock_array.patch_active_directory.return_value = Mock(status_code=200)

        from plugins.modules.purefa_ad import update_account

        update_account(mock_module, mock_array)

        mock_array.patch_active_directory.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_update_account_check_mode(self):
        """Test update_account in check mode"""
        mock_module = Mock()
        mock_module.params = {"name": "ad-account", "tls": "optional"}
        mock_module.check_mode = True
        mock_array = Mock()

        # Current account has different TLS setting
        mock_account = Mock()
        mock_account.tls = "required"
        mock_array.get_active_directory.return_value = Mock(items=[mock_account])

        from plugins.modules.purefa_ad import update_account

        update_account(mock_module, mock_array)

        mock_array.patch_active_directory.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestCreateAccount:
    """Tests for create_account function"""

    @patch("plugins.modules.purefa_ad.ActiveDirectoryPost")
    @patch("plugins.modules.purefa_ad.check_response")
    def test_create_account_old_api(self, mock_check_response, mock_ad_post_class):
        """Test create_account with old API version (no join_ou)"""
        mock_module = Mock()
        mock_module.params = {
            "name": "new-ad",
            "computer": "array1",
            "directory_servers": ["dc1.example.com"],
            "kerberos_servers": ["kdc1.example.com"],
            "domain": "example.com",
            "username": "admin",
            "password": "secret",
            "join_ou": None,
            "tls": "required",
            "join_existing": False,
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.post_active_directory.return_value = Mock(status_code=200)

        from plugins.modules.purefa_ad import create_account

        # Test with API version older than MIN_JOIN_OU_API_VERSION (2.8)
        create_account(mock_module, mock_array, "2.5")

        mock_ad_post_class.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_ad.ActiveDirectoryPost")
    @patch("plugins.modules.purefa_ad.check_response")
    def test_create_account_new_api_with_tls(
        self, mock_check_response, mock_ad_post_class
    ):
        """Test create_account with new API version (with TLS support)"""
        mock_module = Mock()
        mock_module.params = {
            "name": "new-ad",
            "computer": "array1",
            "directory_servers": ["dc1.example.com"],
            "kerberos_servers": ["kdc1.example.com"],
            "domain": "example.com",
            "username": "admin",
            "password": "secret",
            "join_ou": "OU=Arrays",
            "tls": "optional",
            "join_existing": True,
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.post_active_directory.return_value = Mock(status_code=200)

        from plugins.modules.purefa_ad import create_account

        # Test with API version >= MIN_TLS_API_VERSION (2.15)
        create_account(mock_module, mock_array, "2.15")

        mock_ad_post_class.assert_called_once()
        mock_array.post_active_directory.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_ad.ActiveDirectoryPost")
    def test_create_account_check_mode(self, mock_ad_post_class):
        """Test create_account in check mode"""
        mock_module = Mock()
        mock_module.params = {
            "name": "new-ad",
            "computer": "array1",
            "directory_servers": ["dc1.example.com"],
            "kerberos_servers": ["kdc1.example.com"],
            "domain": "example.com",
            "username": "admin",
            "password": "secret",
            "join_ou": None,
            "tls": "required",
            "join_existing": False,
        }
        mock_module.check_mode = True
        mock_array = Mock()

        from plugins.modules.purefa_ad import create_account

        create_account(mock_module, mock_array, "2.5")

        mock_array.post_active_directory.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_ad.ActiveDirectoryPost")
    @patch("plugins.modules.purefa_ad.check_response")
    def test_create_account_middle_api_version(
        self, mock_check_response, mock_ad_post_class
    ):
        """Test create_account with middle API version (join_ou but no TLS)"""
        mock_module = Mock()
        mock_module.params = {
            "name": "new-ad",
            "computer": "array1",
            "directory_servers": ["dc1.example.com"],
            "kerberos_servers": ["kdc1.example.com"],
            "domain": "example.com",
            "username": "admin",
            "password": "secret",
            "join_ou": "OU=Arrays",
            "tls": "required",
            "join_existing": False,
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.post_active_directory.return_value = Mock(status_code=200)

        from plugins.modules.purefa_ad import create_account

        # Test with API version >= MIN_JOIN_OU_API_VERSION but < MIN_TLS_API_VERSION
        create_account(mock_module, mock_array, "2.10")

        mock_ad_post_class.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)
