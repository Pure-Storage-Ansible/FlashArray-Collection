"""
Unit tests for purefa_syslog module

Tests for Syslog Server management functions
"""

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

from plugins.modules.purefa_syslog import (
    delete_syslog,
)


class TestDeleteSyslog:
    """Tests for delete_syslog function"""

    @patch("plugins.modules.purefa_syslog.get_with_context")
    def test_delete_syslog_check_mode(self, mock_get_with_context):
        """Test delete_syslog in check mode"""
        mock_module = Mock()
        mock_module.params = {"name": "syslog1", "context": ""}
        mock_module.check_mode = True
        mock_array = Mock()

        delete_syslog(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_get_with_context.assert_not_called()

    @patch("plugins.modules.purefa_syslog.check_response")
    @patch("plugins.modules.purefa_syslog.get_with_context")
    def test_delete_syslog_success(self, mock_get_with_context, mock_check_response):
        """Test delete_syslog successfully deletes"""
        mock_module = Mock()
        mock_module.params = {"name": "syslog1", "context": ""}
        mock_module.check_mode = False
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        delete_syslog(mock_module, mock_array)

        mock_get_with_context.assert_called_once()
        mock_module.exit_json.assert_called_with(changed=True)
