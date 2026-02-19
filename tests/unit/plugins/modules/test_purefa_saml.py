"""
Unit tests for purefa_saml module

Tests for SAML2 IdP management functions
"""

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

from plugins.modules.purefa_saml import (
    delete_saml,
)


class TestDeleteSaml:
    """Tests for delete_saml function"""

    def test_delete_saml_check_mode(self):
        """Test delete_saml in check mode"""
        mock_module = Mock()
        mock_module.params = {"name": "saml1"}
        mock_module.check_mode = True
        mock_array = Mock()

        delete_saml(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.delete_sso_saml2_idps.assert_not_called()

    def test_delete_saml_success(self):
        """Test delete_saml successfully deletes"""
        mock_module = Mock()
        mock_module.params = {"name": "saml1"}
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.delete_sso_saml2_idps.return_value = Mock(status_code=200)

        delete_saml(mock_module, mock_array)

        mock_array.delete_sso_saml2_idps.assert_called_once_with(names=["saml1"])
        mock_module.exit_json.assert_called_with(changed=True)
