"""
Unit tests for purefa_pgsched module

Tests for Protection Group Schedule management functions
"""

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

from plugins.modules.purefa_pgsched import (
    get_pending_pgroup,
    get_pgroup,
    _convert_to_minutes,
)


class TestGetPendingPgroup:
    """Test cases for get_pending_pgroup function"""

    @patch("plugins.modules.purefa_pgsched.get_with_context")
    def test_get_pending_pgroup_exists(self, mock_get_with_context):
        """Test get_pending_pgroup returns pgroup when it exists"""
        mock_module = Mock()
        mock_module.params = {"name": "test-pg", "context": ""}
        mock_array = Mock()
        mock_pgroup = Mock()
        mock_pgroup.name = "test-pg"
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_pgroup])

        result = get_pending_pgroup(mock_module, mock_array)

        assert result == mock_pgroup

    @patch("plugins.modules.purefa_pgsched.get_with_context")
    def test_get_pending_pgroup_not_exists(self, mock_get_with_context):
        """Test get_pending_pgroup returns None when pgroup doesn't exist"""
        mock_module = Mock()
        mock_module.params = {"name": "nonexistent", "context": ""}
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=404, items=[])

        result = get_pending_pgroup(mock_module, mock_array)

        assert result is None


class TestGetPgroup:
    """Test cases for get_pgroup function"""

    @patch("plugins.modules.purefa_pgsched.get_with_context")
    def test_get_pgroup_exists(self, mock_get_with_context):
        """Test get_pgroup returns pgroup when it exists"""
        mock_module = Mock()
        mock_module.params = {"name": "test-pg", "context": ""}
        mock_array = Mock()
        mock_pgroup = Mock()
        mock_pgroup.name = "test-pg"
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_pgroup])

        result = get_pgroup(mock_module, mock_array)

        assert result == mock_pgroup

    @patch("plugins.modules.purefa_pgsched.get_with_context")
    def test_get_pgroup_not_exists(self, mock_get_with_context):
        """Test get_pgroup returns None when pgroup doesn't exist"""
        mock_module = Mock()
        mock_module.params = {"name": "nonexistent", "context": ""}
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=404, items=[])

        result = get_pgroup(mock_module, mock_array)

        assert result is None


class TestConvertToMinutes:
    """Test cases for _convert_to_minutes function"""

    def test_convert_to_minutes_12am(self):
        """Test conversion of 12AM to seconds"""
        result = _convert_to_minutes("12AM")
        assert result == 0

    def test_convert_to_minutes_12pm(self):
        """Test conversion of 12PM to seconds"""
        result = _convert_to_minutes("12PM")
        assert result == 43200

    def test_convert_to_minutes_6am(self):
        """Test conversion of 6AM to seconds"""
        result = _convert_to_minutes("6AM")
        assert result == 21600  # 6 * 3600

    def test_convert_to_minutes_6pm(self):
        """Test conversion of 6PM to seconds"""
        result = _convert_to_minutes("6PM")
        assert result == 64800  # (6 + 12) * 3600
