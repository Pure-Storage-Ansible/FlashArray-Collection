# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_certs module."""

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
    create_cert,
    update_cert,
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

    @patch("plugins.modules.purefa_certs.check_response")
    def test_delete_cert_success(self, mock_check_response):
        """Test delete_cert successfully deletes certificate"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "test-cert"}
        mock_array = Mock()
        mock_array.delete_certificates.return_value = Mock(status_code=200)

        delete_cert(mock_module, mock_array)

        mock_array.delete_certificates.assert_called_once_with(names=["test-cert"])
        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_delete_cert_management_fails(self):
        """Test delete_cert fails for management certificate"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "management"}
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_array = Mock()

        with pytest.raises(SystemExit):
            delete_cert(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()
        mock_array.delete_certificates.assert_not_called()


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

    @patch("plugins.modules.purefa_certs.flasharray")
    @patch("plugins.modules.purefa_certs.check_response")
    def test_import_cert_success(self, mock_check_response, mock_flasharray):
        """Test import_cert successfully imports certificate"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-cert",
            "certificate": "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----",
            "intermeadiate_cert": None,
            "key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----",
            "passphrase": "secret",
        }
        mock_array = Mock()
        mock_array.post_certificates.return_value = Mock(status_code=200)

        import_cert(mock_module, mock_array, reimport=False)

        mock_array.post_certificates.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_certs.flasharray")
    @patch("plugins.modules.purefa_certs.check_response")
    def test_import_cert_reimport(self, mock_check_response, mock_flasharray):
        """Test import_cert with reimport flag"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-cert",
            "certificate": "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----",
            "intermeadiate_cert": "-----BEGIN CERTIFICATE-----\ninter\n-----END CERTIFICATE-----",
            "key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----",
            "passphrase": None,
        }
        mock_array = Mock()
        mock_array.patch_certificates.return_value = Mock(status_code=200)

        import_cert(mock_module, mock_array, reimport=True)

        mock_array.patch_certificates.assert_called_once()
        mock_array.post_certificates.assert_not_called()
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


class TestCreateCert:
    """Test cases for create_cert function"""

    @patch("plugins.modules.purefa_certs.flasharray")
    def test_create_cert_check_mode(self, mock_flasharray):
        """Test create_cert in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "new-cert",
            "common_name": "test.example.com",
            "country": "US",
            "email": "test@example.com",
            "key_size": 2048,
            "locality": "Test City",
            "organization": "Test Org",
            "org_unit": "Test Unit",
            "province": "Test State",
            "days": 365,
        }
        mock_array = Mock()

        create_cert(mock_module, mock_array)

        mock_array.post_certificates.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_certs.flasharray")
    @patch("plugins.modules.purefa_certs.check_response")
    def test_create_cert_success(self, mock_check_response, mock_flasharray):
        """Test create_cert successfully creates certificate"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "new-cert",
            "common_name": "test.example.com",
            "country": "US",
            "email": "test@example.com",
            "key_size": 4096,
            "locality": "Test City",
            "organization": "Test Org",
            "org_unit": "Test Unit",
            "province": "Test State",
            "days": 730,
        }
        mock_array = Mock()
        mock_array.post_certificates.return_value = Mock(status_code=200)

        create_cert(mock_module, mock_array)

        mock_array.post_certificates.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestUpdateCert:
    """Test cases for update_cert function"""

    @patch("plugins.modules.purefa_certs.flasharray")
    def test_update_cert_no_changes(self, mock_flasharray):
        """Test update_cert when no changes needed"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-cert",
            "common_name": "test.example.com",
            "country": "US",
            "email": "test@example.com",
            "key_size": 2048,
            "locality": "Test City",
            "organization": "Test Org",
            "org_unit": "Test Unit",
            "province": "Test State",
            "generate": False,
        }
        mock_array = Mock()

        # Current cert has same values
        mock_cert = Mock()
        mock_cert.common_name = "test.example.com"
        mock_cert.country = "US"
        mock_cert.email = "test@example.com"
        mock_cert.key_size = 2048
        mock_cert.locality = "Test City"
        mock_cert.organization = "Test Org"
        mock_cert.organizational_unit = "Test Unit"
        mock_cert.state = "Test State"
        mock_array.get_certificates.return_value = Mock(items=[mock_cert])

        update_cert(mock_module, mock_array)

        mock_array.patch_certificates.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=False)

    @patch("plugins.modules.purefa_certs.flasharray")
    @patch("plugins.modules.purefa_certs.check_response")
    def test_update_cert_common_name_change(self, mock_check_response, mock_flasharray):
        """Test update_cert when common_name changes"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-cert",
            "common_name": "new.example.com",
            "country": None,
            "email": None,
            "key_size": None,
            "locality": None,
            "organization": None,
            "org_unit": None,
            "province": None,
            "generate": True,
        }
        mock_array = Mock()

        # Current cert has different common_name
        mock_cert = Mock()
        mock_cert.common_name = "old.example.com"
        mock_cert.country = "US"
        mock_cert.email = "test@example.com"
        mock_cert.key_size = 2048
        mock_cert.locality = "Test City"
        mock_cert.organization = "Test Org"
        mock_cert.organizational_unit = "Test Unit"
        mock_cert.state = "Test State"
        mock_array.get_certificates.return_value = Mock(items=[mock_cert])
        mock_array.patch_certificates.return_value = Mock(status_code=200)

        update_cert(mock_module, mock_array)

        mock_array.patch_certificates.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_certs.flasharray")
    def test_update_cert_check_mode(self, mock_flasharray):
        """Test update_cert in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-cert",
            "common_name": "new.example.com",
            "country": None,
            "email": None,
            "key_size": None,
            "locality": None,
            "organization": None,
            "org_unit": None,
            "province": None,
            "generate": False,
        }
        mock_array = Mock()

        # Current cert has different common_name
        mock_cert = Mock()
        mock_cert.common_name = "old.example.com"
        mock_cert.country = "US"
        mock_cert.email = "test@example.com"
        mock_cert.key_size = 2048
        mock_cert.locality = "Test City"
        mock_cert.organization = "Test Org"
        mock_cert.organizational_unit = "Test Unit"
        mock_cert.state = "Test State"
        mock_array.get_certificates.return_value = Mock(items=[mock_cert])

        update_cert(mock_module, mock_array)

        mock_array.patch_certificates.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_certs.flasharray")
    @patch("plugins.modules.purefa_certs.check_response")
    def test_update_cert_multiple_field_changes(
        self, mock_check_response, mock_flasharray
    ):
        """Test update_cert when multiple fields change"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-cert",
            "common_name": "new.example.com",
            "country": "UK",
            "email": "new@example.com",
            "key_size": 4096,
            "locality": "New City",
            "organization": "New Org",
            "org_unit": "New Unit",
            "province": "New State",
            "generate": True,
        }
        mock_array = Mock()

        # Current cert has different values
        mock_cert = Mock()
        mock_cert.common_name = "old.example.com"
        mock_cert.country = "US"
        mock_cert.email = "old@example.com"
        mock_cert.key_size = 2048
        mock_cert.locality = "Old City"
        mock_cert.organization = "Old Org"
        mock_cert.organizational_unit = "Old Unit"
        mock_cert.state = "Old State"
        mock_array.get_certificates.return_value = Mock(items=[mock_cert])
        mock_array.patch_certificates.return_value = Mock(status_code=200)

        update_cert(mock_module, mock_array)

        mock_array.patch_certificates.assert_called_once()
        call_kwargs = mock_array.patch_certificates.call_args
        assert call_kwargs[1]["generate_new_key"] is True
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestImportCertReimport:
    """Test cases for import_cert reimport functionality"""

    @patch("plugins.modules.purefa_certs.flasharray")
    @patch("plugins.modules.purefa_certs.check_response")
    def test_import_cert_reimport_uses_patch(
        self, mock_check_response, mock_flasharray
    ):
        """Test import_cert with reimport=True uses patch"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "existing-cert",
            "certificate": "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----",
            "intermeadiate_cert": None,
            "key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----",
            "passphrase": None,
        }
        mock_array = Mock()
        mock_array.patch_certificates.return_value = Mock(status_code=200)

        import_cert(mock_module, mock_array, reimport=True)

        mock_array.patch_certificates.assert_called_once()
        mock_array.post_certificates.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_certs.flasharray")
    @patch("plugins.modules.purefa_certs.check_response")
    def test_import_cert_new_uses_post(self, mock_check_response, mock_flasharray):
        """Test import_cert with reimport=False uses post"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "new-cert",
            "certificate": "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----",
            "intermeadiate_cert": "-----BEGIN CERTIFICATE-----\nintermediate\n-----END CERTIFICATE-----",
            "key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----",
            "passphrase": "secret",
        }
        mock_array = Mock()
        mock_array.post_certificates.return_value = Mock(status_code=200)

        import_cert(mock_module, mock_array, reimport=False)

        mock_array.post_certificates.assert_called_once()
        mock_array.patch_certificates.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_certs.flasharray")
    def test_import_cert_check_mode(self, mock_flasharray):
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

        import_cert(mock_module, mock_array, reimport=False)

        mock_array.post_certificates.assert_not_called()
        mock_array.patch_certificates.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)
