# Copyright: (c) 2025, Simon Dodsley (@sdodsley)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_logging module"""

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
from plugins.modules.purefa_logging import main


class TestLoggingOldApiVersion:
    """Test cases for unsupported API version"""

    @patch("plugins.modules.purefa_logging.LooseVersion")
    @patch("plugins.modules.purefa_logging.get_array")
    @patch("plugins.modules.purefa_logging.AnsibleModule")
    def test_old_api_version_fails(
        self, mock_ansible_module, mock_get_array, mock_loose_version
    ):
        """Test that old API version fails with appropriate message"""
        mock_module = Mock()
        mock_module.params = {
            "limit": 100,
            "log_type": "audit",
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
            msg="Purity version does not support audit log return"
        )


class TestLoggingCheckMode:
    """Test cases for check mode"""

    @patch("plugins.modules.purefa_logging.LooseVersion")
    @patch("plugins.modules.purefa_logging.get_array")
    @patch("plugins.modules.purefa_logging.AnsibleModule")
    def test_audit_check_mode(self, mock_ansible_module, mock_get_array, mock_lv):
        """Test audit log check mode returns changed=True with empty list"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "limit": 100,
            "log_type": "audit",
        }
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.3"
        mock_get_array.return_value = mock_array

        # Make LooseVersion comparisons work - 2.2 <= 2.3
        mock_lv.side_effect = lambda x: float(x)

        main()

        mock_module.exit_json.assert_called_once_with(changed=True, audits=[])

    @patch("plugins.modules.purefa_logging.LooseVersion")
    @patch("plugins.modules.purefa_logging.get_array")
    @patch("plugins.modules.purefa_logging.AnsibleModule")
    def test_session_check_mode(self, mock_ansible_module, mock_get_array, mock_lv):
        """Test session log check mode returns changed=True with empty list"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "limit": 100,
            "log_type": "session",
        }
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.3"
        mock_get_array.return_value = mock_array

        # Make LooseVersion comparisons work - 2.2 <= 2.3
        mock_lv.side_effect = lambda x: float(x)

        main()

        mock_module.exit_json.assert_called_once_with(changed=True, sessions=[])
