# Copyright: (c) 2025, Simon Dodsley (@sdodsley)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_eradication module"""

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
from plugins.modules.purefa_eradication import main


class TestEradicationTimerValidation:
    """Test cases for eradication timer validation"""

    @patch("plugins.modules.purefa_eradication.AnsibleModule")
    def test_timer_out_of_range_fails(self, mock_ansible_module):
        """Test that timer value outside 1-30 range fails"""
        mock_module = Mock()
        mock_module.params = {
            "timer": 31,  # Out of range
            "disabled_delay": 1,
            "enabled_delay": 1,
            "context": "",
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_ansible_module.return_value = mock_module

        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once_with(
            msg="Eradication Timer must be between 1 and 30 days."
        )

    @patch("plugins.modules.purefa_eradication.AnsibleModule")
    def test_disabled_delay_out_of_range_fails(self, mock_ansible_module):
        """Test that disabled_delay value outside 1-30 range fails"""
        mock_module = Mock()
        mock_module.params = {
            "timer": None,
            "disabled_delay": 31,  # Out of range
            "enabled_delay": 1,
            "context": "",
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_ansible_module.return_value = mock_module

        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once_with(
            msg="disabled_delay must be between 1 and 30 days."
        )

    @patch("plugins.modules.purefa_eradication.AnsibleModule")
    def test_enabled_delay_out_of_range_fails(self, mock_ansible_module):
        """Test that enabled_delay value outside 1-30 range fails"""
        mock_module = Mock()
        mock_module.params = {
            "timer": None,
            "disabled_delay": 1,
            "enabled_delay": 31,  # Out of range
            "context": "",
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_ansible_module.return_value = mock_module

        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once_with(
            msg="enabled_delay must be between 1 and 30 days."
        )


class TestEradicationOldApiVersion:
    """Test cases for unsupported API version"""

    @patch("plugins.modules.purefa_eradication.LooseVersion")
    @patch("plugins.modules.purefa_eradication.get_with_context")
    @patch("plugins.modules.purefa_eradication.get_array")
    @patch("plugins.modules.purefa_eradication.AnsibleModule")
    def test_old_api_version_fails(
        self,
        mock_ansible_module,
        mock_get_array,
        mock_get_with_context,
        mock_loose_version,
    ):
        """Test that old API version fails with appropriate message"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "timer": 7,
            "disabled_delay": 1,
            "enabled_delay": 1,
            "context": "",
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.4"
        mock_get_array.return_value = mock_array

        # Make LooseVersion return comparable values - old API version
        def mock_version(v):
            versions = {"2.6": 2.6, "2.26": 2.26, "2.38": 2.38, "2.4": 2.4}
            return versions.get(v, float(v))

        mock_loose_version.side_effect = mock_version

        # Mock get_with_context for getting config
        mock_eradication_config = Mock()
        mock_eradication_config.eradication_delay = None
        mock_array_info = Mock()
        mock_array_info.eradication_config = mock_eradication_config
        mock_response = Mock()
        mock_response.items = [mock_array_info]
        mock_get_with_context.return_value = mock_response

        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once_with(
            msg="Purity version does not support changing Eradication Timer"
        )


class TestEradicationMissingDependency:
    """Test cases for missing dependency"""

    @patch("plugins.modules.purefa_eradication.HAS_PURESTORAGE", False)
    @patch("plugins.modules.purefa_eradication.AnsibleModule")
    def test_missing_purestorage_dependency_fails(self, mock_ansible_module):
        """Test that missing pypureclient dependency fails"""
        mock_module = Mock()
        mock_module.params = {
            "timer": 7,
            "disabled_delay": 1,
            "enabled_delay": 1,
            "context": "",
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_ansible_module.return_value = mock_module

        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once_with(
            msg="py-pure-client sdk is required for this module"
        )
