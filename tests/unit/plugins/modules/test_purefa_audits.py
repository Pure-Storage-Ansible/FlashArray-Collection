# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_audits module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from unittest.mock import Mock, MagicMock

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

from plugins.modules.purefa_audits import (
    _get_filter_string,
)


class TestGetFilterString:
    """Tests for _get_filter_string function"""

    def test_get_filter_string_no_start(self):
        """Test _get_filter_string when start is not provided"""
        mock_module = Mock()
        mock_module.params = {"start": None}

        result = _get_filter_string(mock_module, "+00:00")

        assert result == "time>=0"

    def test_get_filter_string_start_zero(self):
        """Test _get_filter_string when start is '0'"""
        mock_module = Mock()
        mock_module.params = {"start": "0"}

        result = _get_filter_string(mock_module, "+00:00")

        assert result == "time>=0"

    def test_get_filter_string_with_date(self):
        """Test _get_filter_string with a valid date"""
        mock_module = Mock()
        mock_module.params = {"start": "2026-01-15 10:30:00"}

        result = _get_filter_string(mock_module, "+00:00")

        # Should contain time>= with a non-zero timestamp
        assert result.startswith("time>=")
        assert result != "time>=0"

    def test_get_filter_string_with_timezone_offset(self):
        """Test _get_filter_string with timezone offset"""
        mock_module = Mock()
        mock_module.params = {"start": "2026-02-20 12:00:00"}

        result = _get_filter_string(mock_module, "-05:00")

        assert result.startswith("time>=")
        # The timestamp should be calculated with timezone offset


# Import main for testing
from plugins.modules.purefa_audits import main
import pytest
from unittest.mock import patch


class TestAuditsMissingDependency:
    """Test cases for missing dependency"""

    @patch("plugins.modules.purefa_audits.HAS_PYTZ", False)
    @patch("plugins.modules.purefa_audits.AnsibleModule")
    def test_missing_pytz_dependency_fails(self, mock_ansible_module):
        """Test that missing pytz dependency fails"""
        mock_module = Mock()
        mock_module.params = {
            "start": None,
            "timezone": None,
            "context": "",
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_ansible_module.return_value = mock_module

        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called_once_with(
            msg="pytz is required for this module"
        )
