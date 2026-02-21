# Copyright: (c) 2025, Simon Dodsley (@sdodsley)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_dsrole_old module"""

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
from plugins.modules.purefa_dsrole_old import main


class TestDsroleOldNewApiVersion:
    """Test cases for newer API version deprecation"""

    @patch("plugins.modules.purefa_dsrole_old.LooseVersion")
    @patch("plugins.modules.purefa_dsrole_old.get_array")
    @patch("plugins.modules.purefa_dsrole_old.AnsibleModule")
    def test_new_api_version_fails_with_deprecation(
        self, mock_ansible_module, mock_get_array, mock_loose_version
    ):
        """Test that new API version fails with deprecation message"""
        mock_module = Mock()
        mock_module.params = {
            "role": "array_admin",
            "state": "present",
            "group_base": "OU=PureGroups",
            "group": "pureadmins",
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.35"
        mock_get_array.return_value = mock_array

        # Make LooseVersion return comparable values - 2.35 > 2.30
        def mock_version(v):
            versions = {"2.35": 2.35, "2.30": 2.30}
            return versions.get(v, float(v))

        mock_loose_version.side_effect = mock_version

        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once_with(
            msg="This module is deprecated for your version of Purity//FA. "
            "Please use module ''purefa_dsrole`` instead."
        )


class TestDsroleOldNoChange:
    """Test cases for no change scenarios"""

    @patch("plugins.modules.purefa_dsrole_old.LooseVersion")
    @patch("plugins.modules.purefa_dsrole_old.get_array")
    @patch("plugins.modules.purefa_dsrole_old.AnsibleModule")
    def test_no_change_when_role_not_configured_and_absent(
        self, mock_ansible_module, mock_get_array, mock_lv
    ):
        """Test no change when role not configured and state is absent"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "role": "array_admin",
            "state": "absent",
            "group_base": None,
            "group": None,
        }
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.25"
        mock_get_array.return_value = mock_array

        # Make LooseVersion comparisons work - 2.25 <= 2.30
        mock_lv.side_effect = float

        # Mock role without group attribute (not configured)
        mock_role = Mock(spec=[])  # No attributes
        mock_response = Mock()
        mock_response.items = [mock_role]
        mock_array.get_directory_services_roles.return_value = mock_response

        main()

        mock_module.exit_json.assert_called_once_with(changed=False)


class TestDsroleOldCreateRole:
    """Test cases for create_role function"""

    @patch("plugins.modules.purefa_dsrole_old.LooseVersion")
    @patch("plugins.modules.purefa_dsrole_old.get_array")
    @patch("plugins.modules.purefa_dsrole_old.AnsibleModule")
    def test_no_change_when_empty_group_and_group_base(
        self, mock_ansible_module, mock_get_array, mock_lv
    ):
        """Test no change when group and group_base are empty"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "role": "array_admin",
            "state": "present",
            "group_base": "",
            "group": "",
        }
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.25"
        mock_get_array.return_value = mock_array

        mock_lv.side_effect = float

        # Mock role without group attribute (not configured)
        mock_role = Mock(spec=[])
        mock_response = Mock()
        mock_response.items = [mock_role]
        mock_array.get_directory_services_roles.return_value = mock_response

        main()

        mock_module.exit_json.assert_called_once_with(changed=False)
