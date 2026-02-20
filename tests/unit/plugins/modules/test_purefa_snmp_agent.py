# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_snmp_agent module."""

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

from plugins.modules.purefa_snmp_agent import (
    update_agent,
)


class TestUpdateAgent:
    """Tests for update_agent function"""

    def test_update_agent_v2c_check_mode(self):
        """Test update_agent with v2c in check mode"""
        mock_module = Mock()
        mock_module.params = {"version": "v2c", "community": "public"}
        mock_module.check_mode = True
        mock_array = Mock()

        update_agent(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.patch_snmp_agents.assert_not_called()

    @patch("plugins.modules.purefa_snmp_agent.check_response")
    def test_update_agent_v2c_success(self, mock_check_response):
        """Test update_agent with v2c successfully"""
        mock_module = Mock()
        mock_module.params = {
            "version": "v2c",
            "community": "public",
            "state": "present",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.patch_snmp_agents.return_value = Mock(status_code=200)

        update_agent(mock_module, mock_array)

        mock_array.patch_snmp_agents.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_snmp_agent.check_response")
    def test_update_agent_v2c_delete(self, mock_check_response):
        """Test update_agent with v2c delete state"""
        mock_module = Mock()
        mock_module.params = {
            "version": "v2c",
            "community": "public",
            "state": "delete",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.patch_snmp_agents.return_value = Mock(status_code=200)

        update_agent(mock_module, mock_array)

        mock_array.patch_snmp_agents.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_update_agent_v3_check_mode(self):
        """Test update_agent with v3 in check mode"""
        mock_module = Mock()
        mock_module.params = {
            "version": "v3",
            "user": "snmpuser",
            "auth_protocol": "SHA",
            "auth_passphrase": "authpass",
            "privacy_protocol": "AES",
            "privacy_passphrase": "privpass",
            "state": "present",
        }
        mock_module.check_mode = True
        mock_array = Mock()

        update_agent(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_array.patch_snmp_agents.assert_not_called()

    @patch("plugins.modules.purefa_snmp_agent.check_response")
    def test_update_agent_v3_auth_only(self, mock_check_response):
        """Test update_agent with v3 auth protocol only"""
        mock_module = Mock()
        mock_module.params = {
            "version": "v3",
            "user": "snmpuser",
            "auth_protocol": "SHA",
            "auth_passphrase": "authpass",
            "privacy_protocol": None,
            "privacy_passphrase": None,
            "state": "present",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.patch_snmp_agents.return_value = Mock(status_code=200)

        update_agent(mock_module, mock_array)

        mock_array.patch_snmp_agents.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)
