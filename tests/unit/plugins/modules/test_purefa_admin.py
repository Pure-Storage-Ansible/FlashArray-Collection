# Copyright: (c) 2025, Simon Dodsley (@sdodsley)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_admin module"""

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
from plugins.modules.purefa_admin import main


class TestAdminValidation:
    """Test cases for admin settings validation"""

    @patch("plugins.modules.purefa_admin.HAS_PURESTORAGE", False)
    @patch("plugins.modules.purefa_admin.AnsibleModule")
    def test_missing_purestorage_dependency_fails(self, mock_ansible_module):
        """Test that missing pypureclient dependency fails"""
        mock_module = Mock()
        mock_module.params = {
            "sso": False,
            "max_login": None,
            "min_password": 1,
            "lockout": None,
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_ansible_module.return_value = mock_module

        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once_with(
            msg="py-pure-client sdk is required for this module"
        )

    @patch("plugins.modules.purefa_admin.AnsibleModule")
    def test_lockout_out_of_range_fails(self, mock_ansible_module):
        """Test that lockout out of range fails"""
        mock_module = Mock()
        mock_module.params = {
            "sso": False,
            "max_login": None,
            "min_password": 1,
            "lockout": 8000000,  # Too large
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_ansible_module.return_value = mock_module

        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once_with(
            msg="Lockout must be between 1 and 7776000 seconds"
        )


class TestAdminOldApiVersion:
    """Test cases for unsupported API version"""

    @patch("plugins.modules.purefa_admin.LooseVersion")
    @patch("plugins.modules.purefa_admin.get_array")
    @patch("plugins.modules.purefa_admin.AnsibleModule")
    def test_old_api_version_fails(
        self, mock_ansible_module, mock_get_array, mock_loose_version
    ):
        """Test that old API version fails with appropriate message"""
        mock_module = Mock()
        mock_module.params = {
            "sso": False,
            "max_login": None,
            "min_password": 1,
            "lockout": None,
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.1"
        mock_get_array.return_value = mock_array

        # Make LooseVersion return comparable values - 2.2 > 2.1
        def mock_version(v):
            versions = {"2.2": 2.2, "2.1": 2.1}
            return versions.get(v, float(v))

        mock_loose_version.side_effect = mock_version

        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once_with(
            msg="Purity version does not support Global Admin settings"
        )


class TestAdminNoChange:
    """Test cases for no change scenarios"""

    @patch("plugins.modules.purefa_admin.LooseVersion")
    @patch("plugins.modules.purefa_admin.get_array")
    @patch("plugins.modules.purefa_admin.AnsibleModule")
    def test_no_change_when_settings_match(
        self, mock_ansible_module, mock_get_array, mock_lv
    ):
        """Test no change when settings already match"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "sso": False,
            "max_login": None,
            "min_password": 1,
            "lockout": None,
        }
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.3"
        mock_get_array.return_value = mock_array

        # Make LooseVersion comparisons work - 2.2 <= 2.3
        mock_lv.side_effect = float

        # Mock current admin settings matching desired values
        mock_current = Mock()
        mock_current.single_sign_on_enabled = False
        mock_current.min_password_length = 1
        mock_response = Mock()
        mock_response.items = [mock_current]
        mock_array.get_admins_settings.return_value = mock_response

        main()

        mock_module.exit_json.assert_called_once_with(changed=False)
