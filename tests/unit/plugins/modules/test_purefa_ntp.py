# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_ntp module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

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

from plugins.modules.purefa_ntp import (
    remove,
    _is_cbs,
    delete_ntp,
    test_ntp as ntp_test_func,
    create_ntp,
)


class TestRemove:
    """Test cases for remove function"""

    def test_remove_duplicates(self):
        """Test remove function removes duplicates from list"""
        test_list = ["ntp1.example.com", "ntp2.example.com", "ntp1.example.com"]

        result = remove(test_list)

        assert result == ["ntp1.example.com", "ntp2.example.com"]

    def test_remove_no_duplicates(self):
        """Test remove function with no duplicates"""
        test_list = ["ntp1.example.com", "ntp2.example.com"]

        result = remove(test_list)

        assert result == ["ntp1.example.com", "ntp2.example.com"]


class TestIsCbs:
    """Test cases for _is_cbs function"""

    def test_is_cbs_true(self):
        """Test _is_cbs returns True for CBS model"""
        mock_array = Mock()
        mock_array.get_controllers.return_value = Mock(
            status_code=200, items=[Mock(model="CBS-S70")]
        )

        result = _is_cbs(mock_array)

        assert result is True

    def test_is_cbs_false(self):
        """Test _is_cbs returns False for non-CBS model"""
        mock_array = Mock()
        mock_array.get_controllers.return_value = Mock(
            status_code=200, items=[Mock(model="FA-X70")]
        )

        result = _is_cbs(mock_array)

        assert result is False


class TestDeleteNtp:
    """Test cases for delete_ntp function"""

    @patch("plugins.modules.purefa_ntp.get_with_context")
    def test_delete_ntp_check_mode(self, mock_get_with_context):
        """Test delete_ntp in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"context": ""}
        mock_array = Mock()
        # Mock NTP servers exist
        mock_array_obj = Mock()
        mock_array_obj.ntp_servers = ["ntp1.example.com"]
        mock_get_with_context.return_value = Mock(items=[mock_array_obj])

        delete_ntp(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_ntp.get_with_context")
    def test_delete_ntp_no_servers(self, mock_get_with_context):
        """Test delete_ntp when no NTP servers configured"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"context": ""}
        mock_array = Mock()
        # Mock empty NTP servers
        mock_array_obj = Mock()
        mock_array_obj.ntp_servers = []
        mock_get_with_context.return_value = Mock(items=[mock_array_obj])

        delete_ntp(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=False)


class TestNtpTest:
    """Test cases for test_ntp function"""

    def test_ntp_test_returns_response(self):
        """Test test_ntp returns test response"""
        mock_module = Mock()
        mock_module.params = {"context": ""}
        mock_array = Mock()

        # Create mock NTP test result
        mock_result = Mock()
        mock_result.enabled = True
        mock_result.success = True
        mock_result.component_address = "10.0.0.1"
        mock_result.component_name = "ntp1"
        mock_result.description = "NTP server test"
        mock_result.destination = "ntp.example.com"
        mock_result.result_details = "OK"
        mock_result.test_type = "connectivity"
        mock_result.resource = Mock()
        mock_result.resource.name = "array1"
        mock_array.get_arrays_ntp_test.return_value.items = [mock_result]

        ntp_test_func(mock_module, mock_array)

        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args[1]
        assert call_args["changed"] is True
        assert len(call_args["test_response"]) == 1
        assert call_args["test_response"][0]["enabled"] == "true"
        assert call_args["test_response"][0]["success"] == "true"


class TestCreateNtp:
    """Test cases for create_ntp function"""

    def test_create_ntp_check_mode(self):
        """Test create_ntp in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "context": "",
            "ntp_servers": ["ntp1.example.com", "ntp2.example.com"],
        }
        mock_array = Mock()

        create_ntp(mock_module, mock_array)

        # In check mode, always returns changed=True without making API calls
        mock_module.exit_json.assert_called_once_with(changed=True)
