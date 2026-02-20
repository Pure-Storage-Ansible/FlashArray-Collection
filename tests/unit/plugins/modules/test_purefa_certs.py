# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_certs module."""

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

from plugins.modules.purefa_certs import (
    delete_cert,
    export_cert,
    import_cert,
    create_csr,
)


class TestDeleteCert:
    """Test cases for delete_cert function"""

    def test_delete_cert_check_mode(self):
        """Test delete_cert in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-cert"}
        mock_array = Mock()

        delete_cert(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestExportCert:
    """Test cases for export_cert function"""

    def test_export_cert_success(self):
        """Test export_cert returns certificate"""
        mock_module = Mock()
        mock_module.params = {"name": "test-cert"}
        mock_array = Mock()
        mock_cert = Mock()
        mock_cert.certificate = (
            "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"
        )
        mock_array.get_certificates.return_value = Mock(
            status_code=200, items=[mock_cert]
        )

        export_cert(mock_module, mock_array)

        mock_module.exit_json.assert_called_once()


class TestImportCert:
    """Test cases for import_cert function"""

    def test_import_cert_check_mode(self):
        """Test import_cert in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-cert",
            "certificate": "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----",
            "intermeadiate_cert": None,
            "key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----",
            "passphrase": None,
        }
        mock_array = Mock()

        import_cert(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestCreateCsr:
    """Test cases for create_csr function"""

    def test_create_csr_check_mode(self):
        """Test create_csr in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-cert",
            "common_name": "test.example.com",
            "country": "US",
            "email": "test@example.com",
            "locality": "Test City",
            "organization": "Test Org",
            "org_unit": "Test Unit",
            "province": "Test State",
            "csr_export_file": "/tmp/test.csr",
        }
        mock_array = Mock()
        # Mock the current certificate attributes
        mock_cert = Mock()
        mock_cert.common_name = "test.example.com"
        mock_cert.country = "US"
        mock_cert.email = "test@example.com"
        mock_cert.locality = "Test City"
        mock_cert.organization = "Test Org"
        mock_cert.organizational_unit = "Test Unit"
        mock_cert.state = "Test State"
        mock_array.get_certificates.return_value = Mock(items=[mock_cert])

        create_csr(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
