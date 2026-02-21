# Copyright: (c) 2025, Simon Dodsley (@sdodsley)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_syslog_settings module"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

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

# Import after mocking
from plugins.modules.purefa_syslog_settings import main


class TestSyslogSettingsValidation:
    """Test cases for syslog settings validation"""

    @patch("plugins.modules.purefa_syslog_settings.AnsibleModule")
    def test_certificate_too_long_fails(self, mock_ansible_module):
        """Test that certificate over 3000 chars fails"""
        mock_module = Mock()
        mock_module.params = {
            "severity": "info",
            "tls_audit": True,
            "ca_certificate": "x" * 3001,  # Too long
            "context": "",
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_ansible_module.return_value = mock_module

        # Need to mock other dependencies
        with patch(
            "plugins.modules.purefa_syslog_settings.get_array"
        ) as mock_get_array:
            with patch(
                "plugins.modules.purefa_syslog_settings.LooseVersion"
            ) as mock_lv:
                mock_lv.side_effect = lambda x: float(x.replace(".", ""))
                mock_array = Mock()
                mock_array.get_rest_version.return_value = "2.10"
                mock_get_array.return_value = mock_array

                with pytest.raises(SystemExit):
                    main()

        mock_module.fail_json.assert_called_once_with(
            msg="Certificate exceeds 3000 characters"
        )

    @patch("plugins.modules.purefa_syslog_settings.HAS_PURESTORAGE", False)
    @patch("plugins.modules.purefa_syslog_settings.AnsibleModule")
    def test_missing_purestorage_dependency_fails(self, mock_ansible_module):
        """Test that missing pypureclient dependency fails"""
        mock_module = Mock()
        mock_module.params = {
            "severity": "info",
            "tls_audit": True,
            "ca_certificate": None,
            "context": "",
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_ansible_module.return_value = mock_module

        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once_with(
            msg="py-pure-client sdk is required for this module"
        )


class TestSyslogSettingsOldApiVersion:
    """Test cases for unsupported API version"""

    @patch("plugins.modules.purefa_syslog_settings.LooseVersion")
    @patch("plugins.modules.purefa_syslog_settings.get_array")
    @patch("plugins.modules.purefa_syslog_settings.AnsibleModule")
    def test_old_api_version_fails(
        self, mock_ansible_module, mock_get_array, mock_loose_version
    ):
        """Test that old API version fails with appropriate message"""
        mock_module = Mock()
        mock_module.params = {
            "severity": "info",
            "tls_audit": True,
            "ca_certificate": None,
            "context": "",
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.5"
        mock_get_array.return_value = mock_array

        # Make LooseVersion return comparable values - 2.9 > 2.5
        def mock_version(v):
            versions = {"2.9": 2.9, "2.38": 2.38, "2.5": 2.5}
            return versions.get(v, float(v))

        mock_loose_version.side_effect = mock_version

        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once_with(
            msg="Purity//FA version not supported. Minimum version required: 6.2.0"
        )


class TestSyslogSettingsNoChange:
    """Test cases for no change scenarios"""

    @patch("plugins.modules.purefa_syslog_settings.LooseVersion")
    @patch("plugins.modules.purefa_syslog_settings.get_with_context")
    @patch("plugins.modules.purefa_syslog_settings.get_array")
    @patch("plugins.modules.purefa_syslog_settings.AnsibleModule")
    def test_no_change_when_settings_match(
        self, mock_ansible_module, mock_get_array, mock_get_with_context, mock_lv
    ):
        """Test no change when settings already match"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "severity": "info",
            "tls_audit": True,
            "ca_certificate": None,
            "context": "",
        }
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.10"
        mock_get_array.return_value = mock_array

        # Make LooseVersion comparisons work correctly
        mock_lv.side_effect = lambda x: float(x.replace(".", "")) / 100

        # Mock current syslog settings matching desired values
        mock_current = Mock()
        mock_current.tls_audit_enabled = True
        mock_current.logging_severity = "info"
        mock_current.ca_certificate = None
        mock_response = Mock()
        mock_response.items = [mock_current]
        mock_get_with_context.return_value = mock_response

        main()

        mock_module.exit_json.assert_called_once_with(changed=False)
