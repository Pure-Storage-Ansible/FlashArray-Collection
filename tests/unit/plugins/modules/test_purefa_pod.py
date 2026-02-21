# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_pod module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from unittest.mock import Mock, patch, MagicMock
from packaging.version import Version as LooseVersion

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
    update_pod,
    stretch_pod,
    delete_pod,
    eradicate_pod,
    recover_pod,
)


class TestGetPod:
    """Test cases for get_pod function"""

    @patch("plugins.modules.purefa_pod.get_with_context")
    def test_get_pod_exists(self, mock_get_with_context):
        """Test get_pod returns True when pod exists"""
        mock_module = Mock()
        mock_module.params = {"name": "test-pod", "context": ""}
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        result = get_pod(mock_module, mock_array)

        assert result is True

    @patch("plugins.modules.purefa_pod.get_with_context")
    def test_get_pod_not_exists(self, mock_get_with_context):
        """Test get_pod returns False when pod doesn't exist"""
        mock_module = Mock()
        mock_module.params = {"name": "nonexistent-pod", "context": ""}
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=404)

        result = get_pod(mock_module, mock_array)

        assert result is False


class TestGetUndoPod:
    """Test cases for get_undo_pod function"""

    @patch("plugins.modules.purefa_pod.get_with_context")
    def test_get_undo_pod_exists(self, mock_get_with_context):
        """Test get_undo_pod returns list when undo pods exist"""
        mock_module = Mock()
        mock_module.params = {"name": "test-pod", "context": ""}
        mock_array = Mock()
        mock_undo_pod = Mock()
        mock_undo_pod.name = "test-pod.undo-demote.1"
        mock_get_with_context.return_value = Mock(
            status_code=200, items=[mock_undo_pod]
        )

        result = get_undo_pod(mock_module, mock_array)

        assert result == [mock_undo_pod]

    @patch("plugins.modules.purefa_pod.get_with_context")
    def test_get_undo_pod_not_exists(self, mock_get_with_context):
        """Test get_undo_pod returns None when no undo pods exist"""
        mock_module = Mock()
        mock_module.params = {"name": "test-pod", "context": ""}
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=404)

        result = get_undo_pod(mock_module, mock_array)

        assert result is None


class TestGetTarget:
    """Test cases for get_target function"""

    @patch("plugins.modules.purefa_pod.get_with_context")
    def test_get_target_exists(self, mock_get_with_context):
        """Test get_target returns True when target exists"""
        mock_module = Mock()
        mock_module.params = {"target": "target-pod", "context": ""}
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        result = get_target(mock_module, mock_array)

        assert result is True


class TestGetDestroyedPod:
    """Test cases for get_destroyed_pod function"""

    @patch("plugins.modules.purefa_pod.get_with_context")
    def test_get_destroyed_pod_exists(self, mock_get_with_context):
        """Test get_destroyed_pod returns True when destroyed pod exists"""
        mock_module = Mock()
        mock_module.params = {"name": "deleted-pod", "context": ""}
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        result = get_destroyed_pod(mock_module, mock_array)

        assert result is True


class TestGetDestroyedTarget:
    """Test cases for get_destroyed_target function"""

    @patch("plugins.modules.purefa_pod.get_with_context")
    def test_get_destroyed_target_exists(self, mock_get_with_context):
        """Test get_destroyed_target returns True when destroyed target exists"""
        mock_module = Mock()
        mock_module.params = {"target": "deleted-target", "context": ""}
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

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

    @patch("plugins.modules.purefa_pod.get_with_context")
    def test_check_arrays_no_stretch_no_failover(self, mock_get_with_context):
        """Test check_arrays returns None when no stretch/failover specified"""
        mock_module = Mock()
        mock_module.params = {"stretch": None, "failover": None, "context": None}
        mock_array = Mock()
        # Mock get_with_context for both get_arrays and get_array_connections
        mock_local = Mock()
        mock_local.name = "local-array"
        # First call: get_arrays, Second call: get_array_connections
        mock_get_with_context.side_effect = [
            Mock(status_code=200, items=[mock_local]),  # get_arrays
            Mock(status_code=200, items=[]),  # get_array_connections
        ]

        result = check_arrays(mock_module, mock_array)

        assert result is None


class TestClonePod:
    """Test cases for clone_pod function"""

    @patch("plugins.modules.purefa_pod.get_destroyed_target")
    @patch("plugins.modules.purefa_pod.get_target")
    def test_clone_pod_target_already_exists(
        self, mock_get_target, mock_get_destroyed_target
    ):
        """Test clone_pod when target already exists"""
        mock_get_target.return_value = True  # Target already exists
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "source-pod", "target": "existing-pod"}
        mock_array = Mock()

        clone_pod(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=False)


class TestUpdatePod:
    """Test cases for update_pod function"""

    @patch("plugins.modules.purefa_pod.get_with_context")
    def test_update_pod_no_changes(self, mock_get_with_context):
        """Test update_pod when no changes are needed"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "failover": None,
            "mediator": "purearray1",
            "stretch": None,
            "quota": None,
            "ignore_usage": False,
            "promote": None,
            "undo": None,
            "default_protection_pg": None,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        # Mock current config
        mock_config = Mock()
        mock_config.failover_preferences = []
        mock_config.mediator = "purearray1"
        mock_config.quota_limit = None
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_config])

        update_pod(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=False)

    @patch("plugins.modules.purefa_pod.get_with_context")
    def test_update_pod_check_mode_failover_change(self, mock_get_with_context):
        """Test update_pod in check mode when failover preference changes"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "failover": ["array2"],
            "mediator": "purearray1",
            "stretch": None,
            "quota": None,
            "ignore_usage": False,
            "promote": None,
            "undo": None,
            "default_protection_pg": None,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        # Mock current config with different failover
        mock_config = Mock()
        mock_config.failover_preferences = ["array1"]
        mock_config.mediator = "purearray1"
        mock_config.quota_limit = None
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_config])

        update_pod(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestStretchPod:
    """Test cases for stretch_pod function"""

    @patch("plugins.modules.purefa_pod.get_with_context")
    def test_stretch_pod_check_mode(self, mock_get_with_context):
        """Test stretch_pod in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "stretch": "remote-array",
            "quota": None,
            "state": "present",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        # Mock current config
        mock_config = Mock()
        mock_config.arrays = [{"name": "local-array"}]
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_config])

        stretch_pod(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pod.get_with_context")
    def test_stretch_pod_no_change_already_stretched(self, mock_get_with_context):
        """Test stretch_pod when pod is already stretched to target"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "stretch": "remote-array",
            "quota": None,
            "state": "present",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        # Mock current config - already stretched to remote-array
        mock_config = Mock()
        mock_config.arrays = [{"name": "local-array"}, {"name": "remote-array"}]
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_config])

        stretch_pod(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=False)


class TestCreatePodSuccess:
    """Additional test cases for create_pod function"""

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.LooseVersion")
    def test_create_pod_fail_with_target(self, mock_loose_version, mock_check_response):
        """Test create_pod fails when target is specified"""
        import pytest

        mock_loose_version.side_effect = LooseVersion
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_module.params = {
            "name": "test-pod",
            "context": "realm1",
            "target": "source-pod",
            "failover": None,
            "mediator": "purestorage",
            "stretch": None,
            "throttle": True,
            "quota": None,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        with pytest.raises(SystemExit):
            create_pod(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()


class TestDeletePodSuccess:
    """Additional test cases for delete_pod function"""

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.LooseVersion")
    def test_delete_pod_success(self, mock_loose_version, mock_check_response):
        """Test delete_pod successfully deletes a pod"""
        mock_loose_version.side_effect = LooseVersion
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "eradicate": False,
            "delete_contents": False,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.patch_pods.return_value = Mock(status_code=200)

        delete_pod(mock_module, mock_array)

        mock_array.patch_pods.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRecoverPodSuccess:
    """Additional test cases for recover_pod function"""

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.LooseVersion")
    def test_recover_pod_success(self, mock_loose_version, mock_check_response):
        """Test recover_pod successfully recovers a pod"""
        mock_loose_version.side_effect = LooseVersion
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.patch_pods.return_value = Mock(status_code=200)

        recover_pod(mock_module, mock_array)

        mock_array.patch_pods.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestEradicatePodSuccess:
    """Additional test cases for eradicate_pod function"""

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.LooseVersion")
    def test_eradicate_pod_success(self, mock_loose_version, mock_check_response):
        """Test eradicate_pod successfully eradicates a pod"""
        mock_loose_version.side_effect = LooseVersion
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "eradicate": True,
            "delete_contents": False,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.delete_pods.return_value = Mock(status_code=200)

        eradicate_pod(mock_module, mock_array)

        mock_array.delete_pods.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestCreatePodSuccess:
    """Test cases for create_pod function success scenarios"""

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.LooseVersion", side_effect=LooseVersion)
    def test_create_pod_basic(self, mock_lv, mock_check_response):
        """Test creating a basic pod without options"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "target": None,
            "failover": None,
            "stretch": None,
            "mediator": "purestorage",
            "throttle": True,
            "context": None,
            "quota": None,
            "quota_notification": None,
            "namespace": None,
            "state": "present",
        }
        mock_array = Mock()
        # Use old version to avoid DEFAULT_API_VERSION (2.24) path
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.post_pods.return_value = Mock(status_code=200)

        create_pod(mock_module, mock_array)

        mock_array.post_pods.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.LooseVersion", side_effect=LooseVersion)
    def test_create_pod_with_failover(self, mock_lv, mock_check_response):
        """Test creating a pod with failover preferences"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "target": None,
            "failover": ["array2"],
            "stretch": None,
            "mediator": "purestorage",
            "throttle": True,
            "context": None,
            "quota": None,
            "quota_notification": None,
            "namespace": None,
            "state": "present",
        }
        mock_array = Mock()
        # Use old version to avoid DEFAULT_API_VERSION (2.24) path
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.post_pods.return_value = Mock(status_code=200)

        create_pod(mock_module, mock_array)

        mock_array.post_pods.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestClonePodSuccess:
    """Test cases for clone_pod function success scenarios"""

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.LooseVersion", side_effect=LooseVersion)
    def test_clone_pod_basic(self, mock_lv, mock_check_response):
        """Test cloning a pod"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "target": "new-pod",
            "context": None,
            "throttle": True,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_pods.return_value = Mock(status_code=400)  # Target doesn't exist
        mock_array.post_pods.return_value = Mock(status_code=200)

        clone_pod(mock_module, mock_array)

        mock_array.post_pods.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestStretchPodSuccess:
    """Test cases for stretch_pod function success scenarios"""

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.post_with_context")
    @patch("plugins.modules.purefa_pod.get_with_context")
    @patch("plugins.modules.purefa_pod.LooseVersion", side_effect=LooseVersion)
    def test_stretch_pod_success(
        self,
        mock_lv,
        mock_get_with_context,
        mock_post_with_context,
        mock_check_response,
    ):
        """Test successfully stretching a pod to another array"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "stretch": "remote-array",
            "state": "present",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock current config - not yet stretched to remote
        mock_config = Mock()
        mock_config.arrays = [{"name": "local-array"}]
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_config])
        mock_post_with_context.return_value = Mock(status_code=200)

        stretch_pod(mock_module, mock_array)

        mock_post_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.delete_with_context")
    @patch("plugins.modules.purefa_pod.get_with_context")
    @patch("plugins.modules.purefa_pod.LooseVersion", side_effect=LooseVersion)
    def test_unstretch_pod_success(
        self,
        mock_lv,
        mock_get_with_context,
        mock_delete_with_context,
        mock_check_response,
    ):
        """Test successfully unstretching a pod from an array"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "stretch": "remote-array",
            "state": "absent",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock current config - stretched to remote-array
        mock_config = Mock()
        mock_config.arrays = [{"name": "local-array"}, {"name": "remote-array"}]
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_config])
        mock_delete_with_context.return_value = Mock(status_code=200)

        stretch_pod(mock_module, mock_array)

        mock_delete_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pod.get_with_context")
    def test_unstretch_pod_no_change(self, mock_get_with_context):
        """Test unstretch when pod is not stretched to target"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "stretch": "nonexistent-array",
            "state": "absent",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock current config - only local array
        mock_config = Mock()
        mock_config.arrays = [{"name": "local-array"}]
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_config])

        stretch_pod(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=False)


class TestUpdatePodSuccess:
    """Test cases for update_pod function success scenarios"""

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.patch_with_context")
    @patch("plugins.modules.purefa_pod.get_with_context")
    @patch("plugins.modules.purefa_pod.LooseVersion", side_effect=LooseVersion)
    def test_update_pod_change_failover(
        self,
        mock_lv,
        mock_get_with_context,
        mock_patch_with_context,
        mock_check_response,
    ):
        """Test update_pod changing failover preferences"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "failover": ["array1", "array2"],
            "mediator": "mediator.example.com",
            "promote": None,
            "quiesce": None,
            "undo": None,
            "priority_adjustment": None,
            "rename": None,
            "quota": None,
            "default_protection_pg": None,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        # Mock current config with different failover
        mock_config = Mock()
        mock_config.failover_preferences = ["old-array"]
        mock_config.mediator = "mediator.example.com"
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_config])
        mock_patch_with_context.return_value = Mock(status_code=200)

        update_pod(mock_module, mock_array)

        mock_patch_with_context.assert_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.patch_with_context")
    @patch("plugins.modules.purefa_pod.get_with_context")
    @patch("plugins.modules.purefa_pod.LooseVersion", side_effect=LooseVersion)
    def test_update_pod_clear_failover_auto(
        self,
        mock_lv,
        mock_get_with_context,
        mock_patch_with_context,
        mock_check_response,
    ):
        """Test update_pod clearing failover with auto"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "failover": ["auto"],
            "mediator": "mediator.example.com",
            "promote": None,
            "quiesce": None,
            "undo": None,
            "priority_adjustment": None,
            "rename": None,
            "quota": None,
            "default_protection_pg": None,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        # Mock current config with failover set
        mock_config = Mock()
        mock_config.failover_preferences = ["array1"]
        mock_config.mediator = "mediator.example.com"
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_config])
        mock_patch_with_context.return_value = Mock(status_code=200)

        update_pod(mock_module, mock_array)

        mock_patch_with_context.assert_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pod.get_with_context")
    def test_update_pod_no_changes(self, mock_get_with_context):
        """Test update_pod when no changes needed"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "failover": None,
            "mediator": "mediator.example.com",
            "promote": None,
            "quiesce": None,
            "undo": None,
            "priority_adjustment": None,
            "rename": None,
            "quota": None,
            "default_protection_pg": None,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        # Mock current config matching params
        mock_config = Mock()
        mock_config.failover_preferences = []
        mock_config.mediator = "mediator.example.com"
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_config])

        update_pod(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=False)


class TestClonePodSuccess:
    """Test cases for clone_pod success paths"""

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.LooseVersion", side_effect=LooseVersion)
    def test_clone_pod_success(self, mock_lv, mock_check_response):
        """Test clone_pod successfully clones"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "new-pod",
            "context": "",
            "target": "source-pod",
            "throttle": True,
            "quota": None,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.post_pods.return_value = Mock(status_code=200)

        clone_pod(mock_module, mock_array)

        mock_array.post_pods.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pod.get_target")
    @patch("plugins.modules.purefa_pod.LooseVersion", side_effect=LooseVersion)
    def test_clone_pod_target_already_exists(self, mock_lv, mock_get_target):
        """Test clone_pod when target already exists"""
        mock_get_target.return_value = True  # Target pod exists
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "source-pod",
            "context": "",
            "target": "existing-pod",
            "throttle": True,
            "quota": None,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        clone_pod(mock_module, mock_array)

        mock_array.post_pods.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=False)


class TestRecoverPodSuccess:
    """Test cases for recover_pod success paths"""

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.patch_with_context")
    def test_recover_pod_success(self, mock_patch_with_context, mock_check_response):
        """Test recover_pod successfully recovers"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "test-pod", "context": ""}
        mock_array = Mock()
        mock_patch_with_context.return_value = Mock(status_code=200)

        recover_pod(mock_module, mock_array)

        mock_patch_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_recover_pod_check_mode(self):
        """Test recover_pod in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-pod", "context": ""}
        mock_array = Mock()

        recover_pod(mock_module, mock_array)

        mock_array.patch_pods.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestEradicatePodSuccess:
    """Test cases for eradicate_pod success paths"""

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.delete_with_context")
    def test_eradicate_pod_success(self, mock_delete_with_context, mock_check_response):
        """Test eradicate_pod successfully eradicates"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "eradicate": True,
            "delete_contents": False,
        }
        mock_array = Mock()
        mock_delete_with_context.return_value = Mock(status_code=200)

        eradicate_pod(mock_module, mock_array)

        mock_delete_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_eradicate_pod_check_mode(self):
        """Test eradicate_pod in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "eradicate": True,
            "delete_contents": False,
        }
        mock_array = Mock()

        eradicate_pod(mock_module, mock_array)

        mock_array.delete_pods.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.delete_with_context")
    def test_eradicate_pod_with_delete_contents(
        self, mock_delete_with_context, mock_check_response
    ):
        """Test eradicate_pod with delete_contents option"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "eradicate": True,
            "delete_contents": True,
        }
        mock_array = Mock()
        mock_delete_with_context.return_value = Mock(status_code=200)

        eradicate_pod(mock_module, mock_array)

        mock_delete_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.delete_with_context")
    def test_eradicate_pod_older_api_version(
        self, mock_delete_with_context, mock_check_response
    ):
        """Test eradicate_pod with older API version"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "eradicate": True,
            "delete_contents": False,
        }
        mock_array = Mock()
        mock_delete_with_context.return_value = Mock(status_code=200)

        eradicate_pod(mock_module, mock_array)

        mock_delete_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestUpdatePodPromotion:
    """Test cases for update_pod promotion scenarios"""

    @patch("plugins.modules.purefa_pod.get_with_context")
    def test_update_pod_promote_fails_when_stretched(self, mock_get_with_context):
        """Test update_pod promotion fails when pod is stretched"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "failover": None,
            "mediator": "purestorage",
            "promote": True,
            "quiesce": None,
            "undo": None,
            "priority_adjustment": None,
            "rename": None,
            "quota": None,
            "default_protection_pg": None,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        # Mock current config with array_count > 1 (stretched)
        mock_config = Mock()
        mock_config.failover_preferences = []
        mock_config.mediator = "purestorage"
        mock_config.array_count = 2  # Stretched pod
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_config])

        update_pod(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()

    @patch("plugins.modules.purefa_pod.patch_with_context")
    @patch("plugins.modules.purefa_pod.get_with_context")
    def test_update_pod_change_mediator(
        self, mock_get_with_context, mock_patch_with_context
    ):
        """Test update_pod changing mediator"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "failover": None,
            "mediator": "new-mediator.example.com",
            "promote": None,
            "quiesce": None,
            "undo": None,
            "priority_adjustment": None,
            "rename": None,
            "quota": None,
            "default_protection_pg": None,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        # Mock current config with different mediator
        mock_config = Mock()
        mock_config.failover_preferences = []
        mock_config.mediator = "old-mediator.example.com"
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_config])
        mock_patch_with_context.return_value = Mock(status_code=200)

        update_pod(mock_module, mock_array)

        mock_patch_with_context.assert_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pod.patch_with_context")
    @patch("plugins.modules.purefa_pod.get_with_context")
    def test_update_pod_mediator_change_fails(
        self, mock_get_with_context, mock_patch_with_context
    ):
        """Test update_pod when mediator change fails"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "failover": None,
            "mediator": "unreachable-mediator.example.com",
            "promote": None,
            "quiesce": None,
            "undo": None,
            "priority_adjustment": None,
            "rename": None,
            "quota": None,
            "default_protection_pg": None,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_config = Mock()
        mock_config.failover_preferences = []
        mock_config.mediator = "old-mediator.example.com"
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_config])
        mock_error = Mock()
        mock_error.message = "Connection failed"
        mock_patch_with_context.return_value = Mock(
            status_code=400, errors=[mock_error]
        )

        update_pod(mock_module, mock_array)

        mock_module.warn.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestDeletePodSuccess:
    """Test cases for delete_pod success scenarios"""

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.patch_with_context")
    def test_delete_pod_success(self, mock_patch_with_context, mock_check_response):
        """Test delete_pod successfully deletes"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "delete_contents": False,
            "eradicate": False,
        }
        mock_array = Mock()
        mock_patch_with_context.return_value = Mock(status_code=200)

        delete_pod(mock_module, mock_array)

        mock_patch_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_delete_pod_check_mode(self):
        """Test delete_pod in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "delete_contents": False,
            "eradicate": False,
        }
        mock_array = Mock()

        delete_pod(mock_module, mock_array)

        mock_array.patch_pods.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.patch_with_context")
    def test_delete_pod_older_api(self, mock_patch_with_context, mock_check_response):
        """Test delete_pod with older API version"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "delete_contents": True,
            "eradicate": False,
        }
        mock_array = Mock()
        mock_patch_with_context.return_value = Mock(status_code=200)

        delete_pod(mock_module, mock_array)

        mock_patch_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_pod.check_response")
    @patch("plugins.modules.purefa_pod.delete_with_context")
    @patch("plugins.modules.purefa_pod.patch_with_context")
    def test_delete_pod_with_eradicate(
        self, mock_patch_with_context, mock_delete_with_context, mock_check_response
    ):
        """Test delete_pod with eradicate option"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-pod",
            "context": "",
            "delete_contents": False,
            "eradicate": True,
        }
        mock_array = Mock()
        mock_patch_with_context.return_value = Mock(status_code=200)
        mock_delete_with_context.return_value = Mock(status_code=200)

        delete_pod(mock_module, mock_array)

        mock_patch_with_context.assert_called_once()
        mock_delete_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)
