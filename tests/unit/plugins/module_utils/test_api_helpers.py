# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for api_helpers module utilities."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from unittest.mock import Mock, MagicMock

# Mock external dependencies before importing api_helpers
sys.modules["pypureclient"] = MagicMock()
sys.modules["pypureclient.flasharray"] = MagicMock()
sys.modules["ansible_collections"] = MagicMock()
sys.modules["ansible_collections.purestorage"] = MagicMock()
sys.modules["ansible_collections.purestorage.flasharray"] = MagicMock()
sys.modules["ansible_collections.purestorage.flasharray.plugins"] = MagicMock()
sys.modules[
    "ansible_collections.purestorage.flasharray.plugins.module_utils"
] = MagicMock()

# Mock the LooseVersion class needed by api_helpers
mock_version = MagicMock()


class MockLooseVersion:
    """Mock LooseVersion that supports comparison."""

    def __init__(self, version):
        self.version = version
        self.parts = [int(p) for p in version.split(".")]

    def __le__(self, other):
        return self.parts <= other.parts

    def __lt__(self, other):
        return self.parts < other.parts

    def __ge__(self, other):
        return self.parts >= other.parts

    def __gt__(self, other):
        return self.parts > other.parts

    def __eq__(self, other):
        return self.parts == other.parts


sys.modules[
    "ansible_collections.purestorage.flasharray.plugins.module_utils.version"
] = MagicMock()
sys.modules[
    "ansible_collections.purestorage.flasharray.plugins.module_utils.version"
].LooseVersion = MockLooseVersion

from plugins.module_utils.api_helpers import (
    check_response,
    get_cached_api_version,
    check_api_version,
    get_with_context,
)


class TestCheckResponse:
    """Tests for check_response function."""

    def test_success_response(self, mock_module, mock_success_response):
        """Test that success response does not raise."""
        # Should not raise - no return value expected
        check_response(mock_success_response, mock_module, "Test operation")
        # Verify fail_json was NOT called
        mock_module.fail_json.assert_not_called()

    def test_error_response_with_message(
        self, mock_module, mock_error_response
    ):
        """Test that error response calls fail_json with error message."""
        try:
            check_response(mock_error_response, mock_module, "Test operation")
        except Exception:
            pass

        mock_module.fail_json.assert_called_once()
        call_kwargs = mock_module.fail_json.call_args[1]
        assert "Test operation failed" in call_kwargs["msg"]
        assert "Test error message" in call_kwargs["msg"]
        assert call_kwargs["status_code"] == 400
        assert call_kwargs["changed"] is False

    def test_error_response_empty_errors(
        self, mock_module, mock_empty_error_response
    ):
        """Test that error response with no errors uses 'Unknown error'."""
        try:
            check_response(
                mock_empty_error_response, mock_module, "Test operation"
            )
        except Exception:
            pass

        mock_module.fail_json.assert_called_once()
        call_kwargs = mock_module.fail_json.call_args[1]
        assert "Unknown error" in call_kwargs["msg"]

    def test_response_without_status_code(self, mock_module):
        """Test that response without status_code attribute is ignored."""
        response = Mock(spec=[])  # No attributes
        # Should not raise
        check_response(response, mock_module, "Test operation")
        mock_module.fail_json.assert_not_called()

    def test_custom_operation_message(self, mock_module, mock_error_response):
        """Test that custom operation message is included in error."""
        try:
            check_response(
                mock_error_response, mock_module, "Create volume 'test-vol'"
            )
        except Exception:
            pass

        call_kwargs = mock_module.fail_json.call_args[1]
        assert "Create volume 'test-vol' failed" in call_kwargs["msg"]


class TestGetCachedApiVersion:
    """Tests for get_cached_api_version function."""

    def test_returns_version(self):
        """Test that function returns API version."""
        # Create a fresh mock without _cached_api_version
        array = Mock(spec=["get_rest_version"])
        array.get_rest_version.return_value = "2.38"

        result = get_cached_api_version(array)
        assert result == "2.38"

    def test_caches_version(self):
        """Test that version is cached after first call."""
        # Create a fresh mock without _cached_api_version
        array = Mock(spec=["get_rest_version"])
        array.get_rest_version.return_value = "2.38"

        # First call
        result1 = get_cached_api_version(array)
        # Second call
        result2 = get_cached_api_version(array)

        # Should only call get_rest_version once
        array.get_rest_version.assert_called_once()
        assert result1 == result2 == "2.38"

    def test_uses_cached_value(self):
        """Test that cached value is used if available."""
        # Create a mock WITH _cached_api_version already set
        array = Mock(spec=["get_rest_version", "_cached_api_version"])
        array._cached_api_version = "2.40"

        result = get_cached_api_version(array)

        # Should not call get_rest_version
        array.get_rest_version.assert_not_called()
        assert result == "2.40"


class TestCheckApiVersion:
    """Tests for check_api_version function."""

    def test_version_sufficient(self, mock_module):
        """Test that True is returned when version is sufficient."""
        # Create fresh mock without cached version
        array = Mock(spec=["get_rest_version"])
        array.get_rest_version.return_value = "2.38"

        result = check_api_version(array, "2.30", mock_module)
        assert result is True

    def test_version_exact_match(self, mock_module):
        """Test that True is returned when version exactly matches."""
        # Create fresh mock without cached version
        array = Mock(spec=["get_rest_version"])
        array.get_rest_version.return_value = "2.38"

        result = check_api_version(array, "2.38", mock_module)
        assert result is True

    def test_version_insufficient(self, mock_module):
        """Test that False is returned when version is insufficient."""
        # Create fresh mock without cached version
        array = Mock(spec=["get_rest_version"])
        array.get_rest_version.return_value = "2.38"

        result = check_api_version(array, "2.40", mock_module)
        assert result is False

    def test_version_insufficient_with_feature_name_fails(self, mock_module):
        """Test that module fails when version is insufficient and feature_name is provided."""
        # Create fresh mock without cached version
        array = Mock(spec=["get_rest_version"])
        array.get_rest_version.return_value = "2.38"

        try:
            check_api_version(
                array, "2.40", mock_module, feature_name="SafeMode"
            )
        except Exception:
            pass

        mock_module.fail_json.assert_called_once()
        call_kwargs = mock_module.fail_json.call_args[1]
        assert "SafeMode" in call_kwargs["msg"]
        assert "2.40" in call_kwargs["msg"]
        assert "2.38" in call_kwargs["msg"]


class TestGetWithContext:
    """Tests for get_with_context function."""

    def test_calls_method_without_context(self, mock_module, mock_array):
        """Test that method is called without context_names when context is None."""
        get_with_context(
            mock_array,
            "get_volumes",
            "2.38",
            mock_module,
            names=["test-vol"],
        )

        mock_array.get_volumes.assert_called_once_with(names=["test-vol"])

    def test_calls_method_with_context(self, mock_module):
        """Test that method is called with context_names when context is provided."""
        # Create fresh mock without cached version
        array = Mock(spec=["get_rest_version", "get_volumes"])
        array.get_rest_version.return_value = "2.38"
        mock_module.params["context"] = "pod1"

        get_with_context(
            array,
            "get_volumes",
            "2.38",
            mock_module,
            names=["test-vol"],
        )

        array.get_volumes.assert_called_once_with(
            names=["test-vol"], context_names=["pod1"]
        )

    def test_no_context_when_api_version_insufficient(
        self, mock_module, mock_array
    ):
        """Test that context is not added when API version is too old."""
        mock_module.params["context"] = "pod1"
        mock_array.get_rest_version.return_value = "2.30"

        get_with_context(
            mock_array,
            "get_volumes",
            "2.38",
            mock_module,
            names=["test-vol"],
        )

        # Context should NOT be included since API version is too old
        mock_array.get_volumes.assert_called_once_with(names=["test-vol"])

    def test_returns_api_response(self, mock_module, mock_array):
        """Test that function returns the API response."""
        expected_response = Mock()
        mock_array.get_volumes.return_value = expected_response

        result = get_with_context(
            mock_array,
            "get_volumes",
            "2.38",
            mock_module,
            names=["test-vol"],
        )

        assert result == expected_response

    def test_passes_all_kwargs(self, mock_module, mock_array):
        """Test that all kwargs are passed to the API method."""
        mock_module.params["context"] = None

        get_with_context(
            mock_array,
            "get_volumes",
            "2.38",
            mock_module,
            names=["vol1", "vol2"],
            destroyed=False,
            filter="name='vol*'",
        )

        mock_array.get_volumes.assert_called_once_with(
            names=["vol1", "vol2"],
            destroyed=False,
            filter="name='vol*'",
        )
