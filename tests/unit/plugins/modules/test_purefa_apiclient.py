# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_apiclient module."""

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

from plugins.modules.purefa_apiclient import (
    delete_client,
    update_client,
)


class TestDeleteClient:
    """Tests for delete_client function"""

    def test_delete_client_check_mode(self):
        """Test delete_client in check mode"""
        mock_module = Mock()
        mock_module.params = {"name": "client1"}
        mock_module.check_mode = True
        mock_array = Mock()

        delete_client(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.delete_api_clients.assert_not_called()

    def test_delete_client_success(self):
        """Test delete_client successfully deletes"""
        mock_module = Mock()
        mock_module.params = {"name": "client1"}
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.delete_api_clients.return_value = Mock(status_code=200)

        delete_client(mock_module, mock_array)

        mock_array.delete_api_clients.assert_called_once_with(names=["client1"])
        mock_module.exit_json.assert_called_with(changed=True)


class TestUpdateClient:
    """Tests for update_client function"""

    def test_update_client_no_change(self):
        """Test update_client when no change needed"""
        mock_module = Mock()
        mock_module.params = {"name": "client1", "enabled": True}
        mock_module.check_mode = False
        mock_array = Mock()
        mock_client = Mock()
        mock_client.enabled = True

        update_client(mock_module, mock_array, mock_client)

        mock_module.exit_json.assert_called_once_with(changed=False)
        mock_array.patch_api_clients.assert_not_called()

    def test_update_client_check_mode(self):
        """Test update_client in check mode when change needed"""
        mock_module = Mock()
        mock_module.params = {"name": "client1", "enabled": False}
        mock_module.check_mode = True
        mock_array = Mock()
        mock_client = Mock()
        mock_client.enabled = True

        update_client(mock_module, mock_array, mock_client)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.patch_api_clients.assert_not_called()

    @patch("plugins.modules.purefa_apiclient.check_response")
    def test_update_client_enable_success(self, mock_check_response):
        """Test update_client successfully enables client"""
        mock_module = Mock()
        mock_module.params = {"name": "client1", "enabled": True}
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.patch_api_clients.return_value = Mock(status_code=200)
        mock_client = Mock()
        mock_client.enabled = False

        update_client(mock_module, mock_array, mock_client)

        mock_array.patch_api_clients.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestCreateClient:
    """Tests for create_client function"""

    def test_create_client_check_mode(self):
        """Test create_client in check mode"""
        from plugins.modules.purefa_apiclient import create_client

        mock_module = Mock()
        mock_module.params = {
            "name": "new-client",
            "token_ttl": 3600,
            "issuer": "my-issuer",
            "role": "readonly",
            "public_key": "ssh-rsa AAAA...",
            "enabled": True,
        }
        mock_module.check_mode = True
        mock_array = Mock()

        create_client(mock_module, mock_array)

        mock_array.post_api_clients.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_create_client_ttl_out_of_range(self):
        """Test create_client fails when token_ttl out of range"""
        import pytest
        from plugins.modules.purefa_apiclient import create_client

        mock_module = Mock()
        mock_module.params = {
            "name": "new-client",
            "token_ttl": 100000,  # Out of range
        }
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_array = Mock()

        with pytest.raises(SystemExit):
            create_client(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()

    @patch("plugins.modules.purefa_apiclient.check_response")
    def test_create_client_success(self, mock_check_response):
        """Test create_client successfully creates client"""
        from plugins.modules.purefa_apiclient import create_client

        mock_module = Mock()
        mock_module.params = {
            "name": "new-client",
            "token_ttl": 3600,
            "issuer": None,  # Will default to name
            "role": "readonly",
            "public_key": "ssh-rsa AAAA...",
            "enabled": False,
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.post_api_clients.return_value = Mock(status_code=200)

        create_client(mock_module, mock_array)

        mock_array.post_api_clients.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)
