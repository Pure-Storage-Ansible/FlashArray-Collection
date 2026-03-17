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

# Import after mocking
from plugins.modules.purefa_logging import main


class TestLoggingOldApiVersion:
    """Test cases for unsupported API version"""

    @patch("plugins.modules.purefa_logging.get_array")
    @patch("plugins.modules.purefa_logging.AnsibleModule")
    def test_old_api_version_fails(self, mock_ansible_module, mock_get_array):
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

        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once_with(
            msg="Purity version does not support audit log return"
        )


class TestLoggingCheckMode:
    """Test cases for check mode"""

    @patch("plugins.modules.purefa_logging.get_array")
    @patch("plugins.modules.purefa_logging.AnsibleModule")
    def test_audit_check_mode(self, mock_ansible_module, mock_get_array):
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

        main()

        mock_module.exit_json.assert_called_once_with(changed=True, audits=[])

    @patch("plugins.modules.purefa_logging.get_array")
    @patch("plugins.modules.purefa_logging.AnsibleModule")
    def test_session_check_mode(self, mock_ansible_module, mock_get_array):
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

        main()

        mock_module.exit_json.assert_called_once_with(changed=True, sessions=[])


class TestLoggingAuditRetrieval:
    """Test cases for audit log retrieval"""

    @patch("plugins.modules.purefa_logging.time")
    @patch("plugins.modules.purefa_logging.get_array")
    @patch("plugins.modules.purefa_logging.AnsibleModule")
    def test_audit_log_retrieval_success(
        self, mock_ansible_module, mock_get_array, mock_time
    ):
        """Test successful audit log retrieval"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "limit": 100,
            "log_type": "audit",
        }
        mock_ansible_module.return_value = mock_module

        # Mock audit entry
        mock_origin = Mock()
        mock_origin.name = "cli"
        mock_audit = Mock()
        mock_audit.time = 1700000000000  # epoch in milliseconds
        mock_audit.arguments = "arg1 arg2"
        mock_audit.command = "purearray"
        mock_audit.subcommand = "list"
        mock_audit.user = "admin"
        mock_audit.origin = mock_origin

        mock_audits_response = Mock()
        mock_audits_response.items = [mock_audit]

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.3"
        mock_array.get_audits.return_value = mock_audits_response
        mock_get_array.return_value = mock_array

        # Mock time
        mock_time.strftime.return_value = "2023-11-14 22:13:20"
        mock_time.localtime.return_value = (2023, 11, 14, 22, 13, 20, 0, 0, 0)

        main()

        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args
        assert call_args.kwargs["changed"] is True
        audits = call_args.kwargs["audits"]
        assert len(audits) == 1
        assert audits[0]["command"] == "purearray"
        assert audits[0]["user"] == "admin"
        assert audits[0]["origin"] == "cli"

    @patch("plugins.modules.purefa_logging.time")
    @patch("plugins.modules.purefa_logging.get_array")
    @patch("plugins.modules.purefa_logging.AnsibleModule")
    def test_audit_log_with_none_time(
        self, mock_ansible_module, mock_get_array, mock_time
    ):
        """Test audit log retrieval when time is None"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "limit": 100,
            "log_type": "audit",
        }
        mock_ansible_module.return_value = mock_module

        # Mock audit entry with no time
        mock_origin = Mock()
        mock_origin.name = "api"
        mock_audit = Mock(spec=["arguments", "command", "subcommand", "user", "origin"])
        mock_audit.arguments = "arg1"
        mock_audit.command = "purevol"
        mock_audit.subcommand = "create"
        mock_audit.user = "pureuser"
        mock_audit.origin = mock_origin

        # getattr will return None for 'time' since it's not in spec
        mock_audits_response = Mock()
        mock_audits_response.items = [mock_audit]

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.3"
        mock_array.get_audits.return_value = mock_audits_response
        mock_get_array.return_value = mock_array

        main()

        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args
        audits = call_args.kwargs["audits"]
        assert len(audits) == 1
        assert audits[0]["time"] is None


class TestLoggingSessionRetrieval:
    """Test cases for session log retrieval"""

    @patch("plugins.modules.purefa_logging.time")
    @patch("plugins.modules.purefa_logging.get_array")
    @patch("plugins.modules.purefa_logging.AnsibleModule")
    def test_session_log_retrieval_success(
        self, mock_ansible_module, mock_get_array, mock_time
    ):
        """Test successful session log retrieval"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "limit": 100,
            "log_type": "session",
        }
        mock_ansible_module.return_value = mock_module

        # Mock session entry
        mock_session = Mock()
        mock_session.start_time = 1700000000000
        mock_session.end_time = 1700003600000
        mock_session.location = "192.168.1.1"
        mock_session.user = "admin"
        mock_session.event = "login"
        mock_session.event_count = 1
        mock_session.user_interface = "GUI"

        mock_sessions_response = Mock()
        mock_sessions_response.items = [mock_session]

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.3"
        mock_array.get_sessions.return_value = mock_sessions_response
        mock_get_array.return_value = mock_array

        # Mock time
        mock_time.strftime.return_value = "2023-11-14 22:13:20"
        mock_time.localtime.return_value = (2023, 11, 14, 22, 13, 20, 0, 0, 0)

        main()

        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args
        assert call_args.kwargs["changed"] is True
        sessions = call_args.kwargs["sessions"]
        assert len(sessions) == 1
        assert sessions[0]["user"] == "admin"
        assert sessions[0]["event"] == "login"
        assert sessions[0]["location"] == "192.168.1.1"

    @patch("plugins.modules.purefa_logging.time")
    @patch("plugins.modules.purefa_logging.get_array")
    @patch("plugins.modules.purefa_logging.AnsibleModule")
    def test_session_log_with_none_times(
        self, mock_ansible_module, mock_get_array, mock_time
    ):
        """Test session log retrieval when times are None"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "limit": 100,
            "log_type": "session",
        }
        mock_ansible_module.return_value = mock_module

        # Mock session entry without start_time/end_time attributes
        mock_session = Mock(spec=["location", "user", "event", "event_count", "user_interface"])
        mock_session.location = "192.168.1.1"
        mock_session.user = "admin"
        mock_session.event = "logout"
        mock_session.event_count = 1
        mock_session.user_interface = "CLI"

        mock_sessions_response = Mock()
        mock_sessions_response.items = [mock_session]

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.3"
        mock_array.get_sessions.return_value = mock_sessions_response
        mock_get_array.return_value = mock_array

        main()

        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args
        sessions = call_args.kwargs["sessions"]
        assert len(sessions) == 1
        assert sessions[0]["start_time"] is None
        assert sessions[0]["end_time"] is None

    @patch("plugins.modules.purefa_logging.time")
    @patch("plugins.modules.purefa_logging.get_array")
    @patch("plugins.modules.purefa_logging.AnsibleModule")
    def test_session_log_with_only_start_time(
        self, mock_ansible_module, mock_get_array, mock_time
    ):
        """Test session log retrieval when only start_time is set"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "limit": 100,
            "log_type": "session",
        }
        mock_ansible_module.return_value = mock_module

        # Mock session entry with only start_time
        mock_session = Mock(spec=["start_time", "location", "user", "event", "event_count", "user_interface"])
        mock_session.start_time = 1700000000000
        mock_session.location = "10.0.0.1"
        mock_session.user = "pureuser"
        mock_session.event = "session_start"
        mock_session.event_count = 1
        mock_session.user_interface = "API"

        mock_sessions_response = Mock()
        mock_sessions_response.items = [mock_session]

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.3"
        mock_array.get_sessions.return_value = mock_sessions_response
        mock_get_array.return_value = mock_array

        # Mock time
        mock_time.strftime.return_value = "2023-11-14 22:13:20"
        mock_time.localtime.return_value = (2023, 11, 14, 22, 13, 20, 0, 0, 0)

        main()

        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args
        sessions = call_args.kwargs["sessions"]
        assert len(sessions) == 1
        assert sessions[0]["start_time"] == "2023-11-14 22:13:20"
        assert sessions[0]["end_time"] is None
