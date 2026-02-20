# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_dns module."""

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

from plugins.modules.purefa_dns import (
    remove,
    delete_dns,
    create_dns,
    _get_source,
    update_multi_dns,
    delete_multi_dns,
    create_multi_dns,
)


class TestRemove:
    """Test cases for remove function"""

    def test_remove_duplicates(self):
        """Test remove function removes duplicates from list"""
        test_list = ["ns1.example.com", "ns2.example.com", "ns1.example.com"]

        result = remove(test_list)

        assert result == ["ns1.example.com", "ns2.example.com"]

    def test_remove_no_duplicates(self):
        """Test remove function with no duplicates"""
        test_list = ["ns1.example.com", "ns2.example.com"]

        result = remove(test_list)

        assert result == ["ns1.example.com", "ns2.example.com"]


class TestDeleteDns:
    """Test cases for delete_dns function"""

    @patch("plugins.modules.purefa_dns.get_with_context")
    def test_delete_dns_already_empty(self, mock_get_with_context):
        """Test delete_dns when DNS already empty"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"state": "absent", "context": ""}
        mock_array = Mock()
        # DNS already empty
        mock_dns = Mock()
        mock_dns.domain = ""
        mock_dns.nameservers = [""]
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_dns])

        delete_dns(mock_module, mock_array)

        # Note: Module calls exit_json twice when already empty (first at line 166, then at line 178)
        mock_module.exit_json.assert_called_with(changed=False)


class TestCreateDns:
    """Test cases for create_dns function"""

    def test_create_dns_no_change(self):
        """Test create_dns when config matches"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "domain": "example.com",
            "nameservers": ["ns1.example.com", "ns2.example.com"],
        }
        mock_array = Mock()
        # DNS already matches
        mock_dns = {
            "domain": "example.com",
            "nameservers": ["ns1.example.com", "ns2.example.com"],
        }
        mock_array.get_dns.return_value = Mock(items=[mock_dns])

        create_dns(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=False)


class TestGetSource:
    """Test cases for _get_source function"""

    @patch("plugins.modules.purefa_dns.get_with_context")
    def test_get_source_exists(self, mock_get_with_context):
        """Test _get_source returns True when source interface exists"""
        mock_module = Mock()
        mock_module.params = {"source": "ct0.eth0"}
        mock_array = Mock()
        mock_get_with_context.return_value.status_code = 200

        result = _get_source(mock_module, mock_array)

        assert result is True

    @patch("plugins.modules.purefa_dns.get_with_context")
    def test_get_source_not_exists(self, mock_get_with_context):
        """Test _get_source returns False when source interface doesn't exist"""
        mock_module = Mock()
        mock_module.params = {"source": "ct0.eth0"}
        mock_array = Mock()
        mock_get_with_context.return_value.status_code = 404

        result = _get_source(mock_module, mock_array)

        assert result is False


class TestDeleteDnsExtended:
    """Extended test cases for delete_dns function"""

    @patch("plugins.modules.purefa_dns.check_response")
    @patch("plugins.modules.purefa_dns.get_with_context")
    def test_delete_dns_success(self, mock_get_with_context, mock_check_response):
        """Test delete_dns successfully deletes DNS config"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"state": "absent", "context": ""}
        mock_array = Mock()
        # DNS has existing config
        mock_dns = Mock()
        mock_dns.domain = "example.com"
        mock_dns.nameservers = ["ns1.example.com"]
        mock_get_with_context.side_effect = [
            Mock(status_code=200, items=[mock_dns]),  # get_dns
            Mock(status_code=200),  # delete_dns
        ]

        delete_dns(mock_module, mock_array)

        mock_module.exit_json.assert_called_with(changed=True)

    @patch("plugins.modules.purefa_dns.get_with_context")
    def test_delete_dns_check_mode(self, mock_get_with_context):
        """Test delete_dns in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"state": "absent", "context": ""}
        mock_array = Mock()
        # DNS has existing config
        mock_dns = Mock()
        mock_dns.domain = "example.com"
        mock_dns.nameservers = ["ns1.example.com"]
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_dns])

        delete_dns(mock_module, mock_array)

        # Should not call delete_dns in check mode
        assert mock_get_with_context.call_count == 1
        mock_module.exit_json.assert_called_with(changed=True)


class TestCreateDnsExtended:
    """Extended test cases for create_dns function"""

    @patch("plugins.modules.purefa_dns.check_response")
    def test_create_dns_success(self, mock_check_response):
        """Test create_dns successfully creates DNS config"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "domain": "example.com",
            "nameservers": ["ns1.example.com", "ns2.example.com"],
        }
        mock_array = Mock()
        # DNS is different - will trigger change
        mock_dns = {
            "domain": "olddomain.com",
            "nameservers": ["old.example.com"],
        }
        mock_array.get_dns.return_value = Mock(items=[mock_dns])
        mock_array.patch_dns.return_value = Mock(status_code=200)

        create_dns(mock_module, mock_array)

        mock_array.patch_dns.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_create_dns_check_mode(self):
        """Test create_dns in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "domain": "example.com",
            "nameservers": ["ns1.example.com", "ns2.example.com"],
        }
        mock_array = Mock()
        # DNS is different - would trigger change
        mock_dns = {
            "domain": "olddomain.com",
            "nameservers": ["old.example.com"],
        }
        mock_array.get_dns.return_value = Mock(items=[mock_dns])

        create_dns(mock_module, mock_array)

        mock_array.patch_dns.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestUpdateMultiDns:
    """Test cases for update_multi_dns function"""

    @patch("plugins.modules.purefa_dns.get_with_context")
    def test_update_multi_dns_no_changes(self, mock_get_with_context):
        """Test update_multi_dns when no changes needed"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "file-dns",
            "domain": "example.com",
            "nameservers": ["ns1.example.com"],
            "service": None,
            "source": None,
            "context": "",
        }
        mock_array = Mock()
        mock_dns = Mock()
        mock_dns.domain = "example.com"
        mock_dns.nameservers = ["ns1.example.com"]
        mock_dns.services = ["file"]
        mock_dns.source = Mock()
        mock_dns.source.name = ""
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_dns])

        update_multi_dns(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=False)

    @patch("plugins.modules.purefa_dns.check_response")
    @patch("plugins.modules.purefa_dns.get_with_context")
    def test_update_multi_dns_domain_change(
        self, mock_get_with_context, mock_check_response
    ):
        """Test update_multi_dns when domain changes"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "file-dns",
            "domain": "newdomain.com",
            "nameservers": None,
            "service": None,
            "source": "",
            "context": "",
        }
        mock_array = Mock()
        mock_dns = Mock()
        mock_dns.domain = "olddomain.com"
        mock_dns.nameservers = ["ns1.example.com"]
        mock_dns.services = ["file"]
        mock_dns.source = Mock()
        mock_dns.source.name = ""
        mock_get_with_context.side_effect = [
            Mock(status_code=200, items=[mock_dns]),
            Mock(status_code=200),
        ]

        update_multi_dns(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_dns.get_with_context")
    def test_update_multi_dns_check_mode(self, mock_get_with_context):
        """Test update_multi_dns in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "file-dns",
            "domain": "newdomain.com",
            "nameservers": None,
            "service": None,
            "source": None,
            "context": "",
        }
        mock_array = Mock()
        mock_dns = Mock()
        mock_dns.domain = "olddomain.com"
        mock_dns.nameservers = ["ns1.example.com"]
        mock_dns.services = ["file"]
        mock_dns.source = Mock()
        mock_dns.source.name = ""
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_dns])

        update_multi_dns(mock_module, mock_array)

        # Should not call patch in check mode
        assert mock_get_with_context.call_count == 1
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_dns.get_with_context")
    def test_update_multi_dns_service_change_fails(self, mock_get_with_context):
        """Test update_multi_dns fails when trying to change service type"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_module.params = {
            "name": "file-dns",
            "domain": None,
            "nameservers": None,
            "service": "management",  # Trying to change service type
            "source": None,
            "context": "",
        }
        mock_array = Mock()
        mock_dns = Mock()
        mock_dns.domain = "example.com"
        mock_dns.nameservers = ["ns1.example.com"]
        mock_dns.services = ["file"]  # Current service is file
        mock_dns.source = Mock()
        mock_dns.source.name = ""
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_dns])

        with pytest.raises(SystemExit):
            update_multi_dns(mock_module, mock_array)

        mock_module.fail_json.assert_called_once_with(
            msg="Changing service type is not permitted"
        )


class TestDeleteMultiDns:
    """Test cases for delete_multi_dns function"""

    @patch("plugins.modules.purefa_dns.check_response")
    @patch("plugins.modules.purefa_dns.get_with_context")
    def test_delete_multi_dns_file_success(
        self, mock_get_with_context, mock_check_response
    ):
        """Test delete_multi_dns successfully deletes file DNS"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "file-dns", "context": ""}
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        delete_multi_dns(mock_module, mock_array)

        mock_get_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_dns.check_response")
    @patch("plugins.modules.purefa_dns.get_with_context")
    def test_delete_multi_dns_management(
        self, mock_get_with_context, mock_check_response
    ):
        """Test delete_multi_dns clears management DNS (can't delete)"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "management", "context": ""}
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        delete_multi_dns(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_dns.get_with_context")
    def test_delete_multi_dns_check_mode(self, mock_get_with_context):
        """Test delete_multi_dns in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "file-dns", "context": ""}
        mock_array = Mock()

        delete_multi_dns(mock_module, mock_array)

        # Should not call delete in check mode for non-management
        mock_get_with_context.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestCreateMultiDns:
    """Test cases for create_multi_dns function"""

    @patch("plugins.modules.purefa_dns.check_response")
    @patch("plugins.modules.purefa_dns.get_with_context")
    def test_create_multi_dns_file_success(
        self, mock_get_with_context, mock_check_response
    ):
        """Test create_multi_dns successfully creates file DNS"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "file-dns",
            "domain": "example.com",
            "nameservers": ["ns1.example.com"],
            "service": "file",
            "source": None,
            "context": "",
        }
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        create_multi_dns(mock_module, mock_array)

        mock_get_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_dns.check_response")
    @patch("plugins.modules.purefa_dns.get_with_context")
    def test_create_multi_dns_file_with_source(
        self, mock_get_with_context, mock_check_response
    ):
        """Test create_multi_dns with source interface"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "file-dns",
            "domain": "example.com",
            "nameservers": ["ns1.example.com"],
            "service": "file",
            "source": "ct0.eth0",
            "context": "",
        }
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        create_multi_dns(mock_module, mock_array)

        mock_get_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_dns.check_response")
    @patch("plugins.modules.purefa_dns.get_with_context")
    def test_create_multi_dns_management(
        self, mock_get_with_context, mock_check_response
    ):
        """Test create_multi_dns for management service"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "management",
            "domain": "example.com",
            "nameservers": ["ns1.example.com"],
            "service": "management",
            "source": None,
            "context": "",
        }
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        create_multi_dns(mock_module, mock_array)

        mock_get_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_create_multi_dns_check_mode(self):
        """Test create_multi_dns in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "file-dns",
            "domain": "example.com",
            "nameservers": ["ns1.example.com"],
            "service": "file",
            "source": None,
            "context": "",
        }
        mock_array = Mock()

        create_multi_dns(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
