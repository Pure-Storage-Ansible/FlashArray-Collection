"""
Unit tests for purefa_pod_replica module

Tests for Pod Replica Link management functions
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

from plugins.modules.purefa_pod_replica import (
    get_local_pod,
    get_local_rl,
    delete_rl,
)


class TestGetLocalPod:
    """Test cases for get_local_pod function"""

    @patch("plugins.modules.purefa_pod_replica.LooseVersion")
    def test_get_local_pod_exists(self, mock_loose_version):
        """Test get_local_pod returns pod when it exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.38" else 2.38
        mock_module = Mock()
        mock_module.params = {"name": "test-pod", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_pod = Mock()
        mock_pod.name = "test-pod"
        mock_array.get_pods.return_value = Mock(status_code=200, items=[mock_pod])

        result = get_local_pod(mock_module, mock_array)

        assert result == mock_pod

    @patch("plugins.modules.purefa_pod_replica.LooseVersion")
    def test_get_local_pod_not_exists(self, mock_loose_version):
        """Test get_local_pod returns None when pod doesn't exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.38" else 2.38
        mock_module = Mock()
        mock_module.params = {"name": "nonexistent", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_pods.return_value = Mock(status_code=404, items=[])

        result = get_local_pod(mock_module, mock_array)

        assert result is None


class TestGetLocalRl:
    """Test cases for get_local_rl function"""

    @patch("plugins.modules.purefa_pod_replica.LooseVersion")
    def test_get_local_rl_not_exists(self, mock_loose_version):
        """Test get_local_rl returns None when replica link doesn't exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.38" else 2.38
        mock_module = Mock()
        mock_module.params = {"name": "test-pod", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_pod_replica_links.return_value = Mock(
            total_item_count=0, items=[]
        )

        result = get_local_rl(mock_module, mock_array)

        assert result is None


class TestDeleteRl:
    """Test cases for delete_rl function"""

    @patch("plugins.modules.purefa_pod_replica.LooseVersion")
    def test_delete_rl_check_mode(self, mock_loose_version):
        """Test delete_rl in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.38" else 2.38
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-pod", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_rl = Mock()

        delete_rl(mock_module, mock_array, mock_rl)

        mock_module.exit_json.assert_called_once_with(changed=True)
