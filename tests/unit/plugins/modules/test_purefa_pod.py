# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_pod module."""

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

from plugins.modules.purefa_pod import (
    get_pod,
    get_undo_pod,
    get_target,
    get_destroyed_pod,
    get_destroyed_target,
    check_arrays,
    create_pod,
    clone_pod,
    delete_pod,
    eradicate_pod,
    recover_pod,
)


class TestGetPod:
    """Test cases for get_pod function"""

    @patch("plugins.modules.purefa_pod.LooseVersion")
    def test_get_pod_exists(self, mock_loose_version):
        """Test get_pod returns True when pod exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "test-pod", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_pods.return_value = Mock(status_code=200)

        result = get_pod(mock_module, mock_array)

        assert result is True

    @patch("plugins.modules.purefa_pod.LooseVersion")
    def test_get_pod_not_exists(self, mock_loose_version):
        """Test get_pod returns False when pod doesn't exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "nonexistent-pod", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_pods.return_value = Mock(status_code=404)

        result = get_pod(mock_module, mock_array)

        assert result is False


class TestGetUndoPod:
    """Test cases for get_undo_pod function"""

    @patch("plugins.modules.purefa_pod.LooseVersion")
    def test_get_undo_pod_exists(self, mock_loose_version):
        """Test get_undo_pod returns list when undo pods exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "test-pod", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_undo_pod = Mock()
        mock_undo_pod.name = "test-pod.undo-demote.1"
        mock_array.get_pods.return_value = Mock(status_code=200, items=[mock_undo_pod])

        result = get_undo_pod(mock_module, mock_array)

        assert result == [mock_undo_pod]

    @patch("plugins.modules.purefa_pod.LooseVersion")
    def test_get_undo_pod_not_exists(self, mock_loose_version):
        """Test get_undo_pod returns None when no undo pods exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "test-pod", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_pods.return_value = Mock(status_code=404)

        result = get_undo_pod(mock_module, mock_array)

        assert result is None


class TestGetTarget:
    """Test cases for get_target function"""

    @patch("plugins.modules.purefa_pod.LooseVersion")
    def test_get_target_exists(self, mock_loose_version):
        """Test get_target returns True when target exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"target": "target-pod", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_pods.return_value = Mock(status_code=200)

        result = get_target(mock_module, mock_array)

        assert result is True


class TestGetDestroyedPod:
    """Test cases for get_destroyed_pod function"""

    @patch("plugins.modules.purefa_pod.LooseVersion")
    def test_get_destroyed_pod_exists(self, mock_loose_version):
        """Test get_destroyed_pod returns True when destroyed pod exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "deleted-pod", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_pods.return_value = Mock(status_code=200)

        result = get_destroyed_pod(mock_module, mock_array)

        assert result is True


class TestGetDestroyedTarget:
    """Test cases for get_destroyed_target function"""

    @patch("plugins.modules.purefa_pod.LooseVersion")
    def test_get_destroyed_target_exists(self, mock_loose_version):
        """Test get_destroyed_target returns True when destroyed target exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"target": "deleted-target", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_pods.return_value = Mock(status_code=200)

        result = get_destroyed_target(mock_module, mock_array)

        assert result is True


class TestCreatePod:
    """Test cases for create_pod function"""

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.LooseVersion")
    def test_create_pod_check_mode(self, mock_loose_version, mock_check_response):
        """Test create_pod in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "new-pod", "target": None}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        create_pod(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestDeletePod:
    """Test cases for delete_pod function"""

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.LooseVersion")
    def test_delete_pod_check_mode(self, mock_loose_version, mock_check_response):
        """Test delete_pod in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-pod", "eradicate": False}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        delete_pod(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestEradicatePod:
    """Test cases for eradicate_pod function"""

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.LooseVersion")
    def test_eradicate_pod_check_mode(self, mock_loose_version, mock_check_response):
        """Test eradicate_pod in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "deleted-pod", "eradicate": True}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        eradicate_pod(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRecoverPod:
    """Test cases for recover_pod function"""

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.LooseVersion")
    def test_recover_pod_check_mode(self, mock_loose_version, mock_check_response):
        """Test recover_pod in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "deleted-pod"}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        recover_pod(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestCheckArrays:
    """Test cases for check_arrays function"""

    @patch("plugins.modules.purefa_pod.LooseVersion")
    def test_check_arrays_no_stretch_no_failover(self, mock_loose_version):
        """Test check_arrays returns None when no stretch/failover specified"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"stretch": None, "failover": None, "context": None}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        # Mock array.get_arrays().items
        mock_local = Mock()
        mock_local.name = "local-array"
        mock_array.get_arrays.return_value.items = [mock_local]
        mock_array.get_array_connections.return_value.items = []

        result = check_arrays(mock_module, mock_array)

        assert result is None


class TestClonePod:
    """Test cases for clone_pod function"""

    @patch("plugins.modules.purefa_pod.get_destroyed_target")
    @patch("plugins.modules.purefa_pod.get_target")
    @patch("plugins.modules.purefa_pod.LooseVersion")
    def test_clone_pod_target_already_exists(
        self, mock_loose_version, mock_get_target, mock_get_destroyed_target
    ):
        """Test clone_pod when target already exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_get_target.return_value = True  # Target already exists
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "source-pod", "target": "existing-pod"}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        clone_pod(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=False)
