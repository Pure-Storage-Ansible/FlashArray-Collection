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
