# Copyright: (c) 2025, Simon Dodsley (@sdodsley)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_hardware module"""

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
from plugins.modules.purefa_hardware import main


class TestHardwareValidation:
    """Test cases for hardware validation"""

    @patch("plugins.modules.purefa_hardware.HAS_PURESTORAGE", False)
    @patch("plugins.modules.purefa_hardware.AnsibleModule")
    def test_missing_purestorage_dependency_fails(self, mock_ansible_module):
        """Test that missing pypureclient dependency fails"""
        mock_module = Mock()
        mock_module.params = {
            "name": "CH1.FB1",
            "enabled": True,
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_ansible_module.return_value = mock_module

        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once_with(
            msg="py-pure-client sdk is required for this module"
        )


class TestHardwareNoChange:
    """Test cases for no change scenarios"""

    @patch("plugins.modules.purefa_hardware.get_array")
    @patch("plugins.modules.purefa_hardware.AnsibleModule")
    def test_no_change_when_led_already_matches(
        self, mock_ansible_module, mock_get_array
    ):
        """Test no change when LED state already matches"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "CH1.FB1",
            "enabled": True,
        }
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_get_array.return_value = mock_array

        # Mock hardware get response with LED already enabled
        mock_hardware = Mock()
        mock_hardware.identify_enabled = True
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.items = [mock_hardware]
        mock_array.get_hardware.return_value = mock_response

        main()

        mock_module.exit_json.assert_called_once_with(changed=False)

    @patch("plugins.modules.purefa_hardware.get_array")
    @patch("plugins.modules.purefa_hardware.AnsibleModule")
    def test_no_change_when_identify_not_supported(
        self, mock_ansible_module, mock_get_array
    ):
        """Test no change when hardware doesn't support identify LED"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "CH1.FB1",
            "enabled": True,
        }
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_get_array.return_value = mock_array

        # Mock hardware without identify_enabled attribute
        mock_hardware = Mock(spec=[])  # Empty spec means no attributes
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.items = [mock_hardware]
        mock_array.get_hardware.return_value = mock_response

        main()

        mock_module.exit_json.assert_called_once_with(changed=False)


class TestHardwareCheckMode:
    """Test cases for check mode"""

    @patch("plugins.modules.purefa_hardware.get_array")
    @patch("plugins.modules.purefa_hardware.AnsibleModule")
    def test_check_mode_reports_change(self, mock_ansible_module, mock_get_array):
        """Test check mode reports change without making it"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "CH1.FB1",
            "enabled": True,
        }
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_get_array.return_value = mock_array

        # Mock hardware with LED disabled (different from desired)
        mock_hardware = Mock()
        mock_hardware.identify_enabled = False
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.items = [mock_hardware]
        mock_array.get_hardware.return_value = mock_response

        main()

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.patch_hardware.assert_not_called()
