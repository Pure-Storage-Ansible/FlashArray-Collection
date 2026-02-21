# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_offload module."""

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

from plugins.modules.purefa_offload import (
    get_target,
    delete_offload,
    create_offload,
    update_offload,
)


class TestGetTarget:
    """Tests for get_target function"""

    @patch("plugins.modules.purefa_offload.get_with_context")
    def test_get_target_exists(self, mock_get_with_context):
        """Test get_target returns target when it exists"""
        mock_module = Mock()
        mock_module.params = {"name": "offload1", "context": ""}
        mock_array = Mock()
        mock_target = Mock()
        mock_target.name = "offload1"
        mock_get_with_context.return_value = Mock(status_code=200, items=[mock_target])

        result = get_target(mock_module, mock_array)

        assert result == mock_target

    @patch("plugins.modules.purefa_offload.get_with_context")
    def test_get_target_not_exists(self, mock_get_with_context):
        """Test get_target returns None when target doesn't exist"""
        mock_module = Mock()
        mock_module.params = {"name": "nonexistent", "context": ""}
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=400, items=[])

        result = get_target(mock_module, mock_array)

        assert result is None


class TestDeleteOffload:
    """Tests for delete_offload function"""

    @patch("plugins.modules.purefa_offload.get_with_context")
    def test_delete_offload_check_mode(self, mock_get_with_context):
        """Test delete_offload in check mode"""
        mock_module = Mock()
        mock_module.params = {"name": "offload1", "context": ""}
        mock_module.check_mode = True
        mock_array = Mock()

        delete_offload(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
        mock_get_with_context.assert_not_called()

    @patch("plugins.modules.purefa_offload.check_response")
    @patch("plugins.modules.purefa_offload.get_with_context")
    def test_delete_offload_success(self, mock_get_with_context, mock_check_response):
        """Test delete_offload successfully deletes"""
        mock_module = Mock()
        mock_module.params = {"name": "offload1", "context": ""}
        mock_module.check_mode = False
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        delete_offload(mock_module, mock_array)

        mock_get_with_context.assert_called_once()
        mock_module.exit_json.assert_called_with(changed=True)


class TestCreateOffload:
    """Tests for create_offload function"""

    def test_create_offload_check_mode(self):
        """Test create_offload in check mode"""
        mock_module = Mock()
        mock_module.params = {"name": "offload1", "protocol": "s3"}
        mock_module.check_mode = True
        mock_array = Mock()

        create_offload(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_offload.check_response")
    @patch("plugins.modules.purefa_offload.get_with_context")
    @patch("plugins.modules.purefa_offload.OffloadS3")
    @patch("plugins.modules.purefa_offload.OffloadPost")
    def test_create_offload_s3(
        self, mock_offload_post, mock_offload_s3, mock_get_with_context, mock_check
    ):
        """Test create_offload with S3 protocol"""
        mock_module = Mock()
        mock_module.params = {
            "name": "offload1",
            "protocol": "s3",
            "access_key": "access123",
            "bucket": "mybucket",
            "secret": "secret123",
            "profile": None,
            "uri": "https://s3.example.com",
            "initialize": True,
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.30"
        mock_get_with_context.return_value = Mock(status_code=200)

        create_offload(mock_module, mock_array)

        mock_offload_s3.assert_called_once()
        mock_get_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestUpdateOffload:
    """Tests for update_offload function"""

    def test_update_offload_no_changes(self):
        """Test update_offload with no changes needed"""
        mock_module = Mock()
        mock_module.params = {"name": "offload1"}
        mock_array = Mock()

        update_offload(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=False)


class TestCreateOffloadProtocols:
    """Test cases for create_offload with different protocols"""

    @patch("plugins.modules.purefa_offload.check_response")
    @patch("plugins.modules.purefa_offload.get_with_context")
    @patch("plugins.modules.purefa_offload.OffloadGoogleCloud")
    @patch("plugins.modules.purefa_offload.OffloadPost")
    def test_create_offload_gcp(
        self, mock_offload_post, mock_offload_gcp, mock_get_with_context, mock_check
    ):
        """Test create_offload with GCP protocol"""
        mock_module = Mock()
        mock_module.params = {
            "name": "gcp-offload",
            "protocol": "gcp",
            "access_key": "access123",
            "bucket": "mybucket",
            "secret": "secret123",
            "profile": None,
            "initialize": True,
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.30"
        mock_get_with_context.return_value = Mock(status_code=200)

        create_offload(mock_module, mock_array)

        mock_offload_gcp.assert_called_once()
        mock_get_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_offload.check_response")
    @patch("plugins.modules.purefa_offload.get_with_context")
    @patch("plugins.modules.purefa_offload.OffloadAzure")
    @patch("plugins.modules.purefa_offload.OffloadPost")
    def test_create_offload_azure(
        self, mock_offload_post, mock_offload_azure, mock_get_with_context, mock_check
    ):
        """Test create_offload with Azure protocol"""
        mock_module = Mock()
        mock_module.params = {
            "name": "azure-offload",
            "protocol": "azure",
            "container": "mycontainer",
            "bucket": "mybucket",
            "secret": "secret123",
            "profile": None,
            "initialize": True,
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.30"
        mock_get_with_context.return_value = Mock(status_code=200)

        create_offload(mock_module, mock_array)

        mock_offload_azure.assert_called_once()
        mock_get_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_offload.check_response")
    @patch("plugins.modules.purefa_offload.get_with_context")
    @patch("plugins.modules.purefa_offload.OffloadNfs")
    @patch("plugins.modules.purefa_offload.OffloadPost")
    def test_create_offload_nfs(
        self, mock_offload_post, mock_offload_nfs, mock_get_with_context, mock_check
    ):
        """Test create_offload with NFS protocol"""
        mock_module = Mock()
        mock_module.params = {
            "name": "nfs-offload",
            "protocol": "nfs",
            "share": "/mnt/share",
            "address": "nfs.example.com",
            "options": "rw,no_root_squash",
            "profile": None,
            "initialize": True,
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.30"
        mock_get_with_context.return_value = Mock(status_code=200)

        create_offload(mock_module, mock_array)

        mock_offload_nfs.assert_called_once()
        mock_get_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_offload.check_response")
    @patch("plugins.modules.purefa_offload.get_with_context")
    @patch("plugins.modules.purefa_offload.OffloadS3")
    @patch("plugins.modules.purefa_offload.OffloadPost")
    def test_create_offload_s3_with_profile(
        self, mock_offload_post, mock_offload_s3, mock_get_with_context, mock_check
    ):
        """Test create_offload with S3 protocol and profile"""
        mock_module = Mock()
        mock_module.params = {
            "name": "s3-offload",
            "protocol": "s3",
            "access_key": "access123",
            "bucket": "mybucket",
            "secret": "secret123",
            "profile": "my-profile",
            "uri": "https://s3.example.com",
            "auth_region": None,
            "initialize": True,
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.25"
        mock_get_with_context.return_value = Mock(status_code=200)

        create_offload(mock_module, mock_array)

        mock_offload_s3.assert_called_once()
        mock_get_with_context.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestDeleteOffloadSuccess:
    """Test cases for delete_offload success paths"""

    @patch("plugins.modules.purefa_offload.check_response")
    @patch("plugins.modules.purefa_offload.get_with_context")
    def test_delete_offload_success(self, mock_get_with_context, mock_check_response):
        """Test successful offload deletion"""
        mock_module = Mock()
        mock_module.params = {"name": "offload1", "context": ""}
        mock_module.check_mode = False
        mock_array = Mock()
        mock_get_with_context.return_value = Mock(status_code=200)

        delete_offload(mock_module, mock_array)

        mock_get_with_context.assert_called_once()
        mock_check_response.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)
