# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_messages module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from unittest.mock import MagicMock

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

from plugins.modules.purefa_messages import (
    _create_time_window,
)


class TestCreateTimeWindow:
    """Tests for _create_time_window function"""

    def test_create_time_window_hours(self):
        """Test _create_time_window with hours"""
        result = _create_time_window("2h")
        # HOUR = 3600000 (milliseconds)
        assert result == 3600000 * 2

    def test_create_time_window_days(self):
        """Test _create_time_window with days"""
        result = _create_time_window("3d")
        # DAY = HOUR * 24 = 86400000 (milliseconds)
        assert result == 3600000 * 24 * 3

    def test_create_time_window_weeks(self):
        """Test _create_time_window with weeks"""
        result = _create_time_window("1w")
        # WEEK = DAY * 7 = 604800000 (milliseconds)
        assert result == 3600000 * 24 * 7

    def test_create_time_window_years(self):
        """Test _create_time_window with years"""
        result = _create_time_window("1y")
        # YEAR = WEEK * 52 = 31449600000 (milliseconds)
        assert result == 3600000 * 24 * 7 * 52

    def test_create_time_window_invalid(self):
        """Test _create_time_window with invalid period"""
        result = _create_time_window("5x")
        assert result is None
