# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_policy module."""

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

from plugins.modules.purefa_policy import (
    delete_policy,
    rename_policy,
    create_policy,
    update_policy,
)


class TestDeletePolicy:
    """Tests for delete_policy function"""

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_delete_policy_check_mode(self, mock_lv):
        """Test delete_policy in check mode"""
        mock_module = Mock()
        mock_module.params = {
            "name": "policy1",
            "policy": "nfs",
            "client": None,
            "context": "",
        }
        mock_module.check_mode = True
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        delete_policy(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_delete_nfs_policy_success(self, mock_lv):
        """Test successful deletion of NFS policy"""
        mock_module = Mock()
        mock_module.params = {
            "name": "nfs_policy1",
            "policy": "nfs",
            "client": None,
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.delete_policies_nfs.return_value.status_code = 200

        delete_policy(mock_module, mock_array)

        mock_array.delete_policies_nfs.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_delete_nfs_policy_failure(self, mock_lv):
        """Test failure to delete NFS policy"""
        mock_module = Mock()
        mock_module.params = {
            "name": "nfs_policy1",
            "policy": "nfs",
            "client": None,
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_res = Mock()
        mock_res.status_code = 400
        mock_res.errors = [Mock(message="Policy in use")]
        mock_array.delete_policies_nfs.return_value = mock_res

        delete_policy(mock_module, mock_array)

        mock_module.fail_json.assert_called_once()

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_delete_smb_policy_success(self, mock_lv):
        """Test successful deletion of SMB policy"""
        mock_module = Mock()
        mock_module.params = {
            "name": "smb_policy1",
            "policy": "smb",
            "client": None,
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.delete_policies_smb.return_value.status_code = 200

        delete_policy(mock_module, mock_array)

        mock_array.delete_policies_smb.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_delete_snapshot_policy_success(self, mock_lv):
        """Test successful deletion of Snapshot policy"""
        mock_module = Mock()
        mock_module.params = {
            "name": "snap_policy1",
            "policy": "snapshot",
            "snap_client_name": None,
            "directory": None,
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.delete_policies_snapshot.return_value.status_code = 200

        delete_policy(mock_module, mock_array)

        mock_array.delete_policies_snapshot.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_delete_quota_policy_success(self, mock_lv):
        """Test successful deletion of Quota policy"""
        mock_module = Mock()
        mock_module.params = {
            "name": "quota_policy1",
            "policy": "quota",
            "context": "",
            "quota_limit": None,
            "directory": None,
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.delete_policies_quota.return_value.status_code = 200
        # Mock members and rules as empty lists
        mock_array.get_policies_quota_members.return_value.items = []
        mock_array.get_policies_quota_rules.return_value.items = []

        delete_policy(mock_module, mock_array)

        mock_array.delete_policies_quota.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_delete_autodir_policy_success(self, mock_lv):
        """Test successful deletion of Autodir policy"""
        mock_module = Mock()
        mock_module.params = {
            "name": "autodir_policy1",
            "policy": "autodir",
            "directory": None,
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.delete_policies_autodir.return_value.status_code = 200

        delete_policy(mock_module, mock_array)

        mock_array.delete_policies_autodir.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_delete_password_policy_warns(self, mock_lv):
        """Test that deleting password policy shows warning"""
        mock_module = Mock()
        mock_module.params = {
            "name": "password_policy1",
            "policy": "password",
            "context": "",
            "quota_limit": None,
            "directory": None,
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        # Password policy also falls through to quota branch due to code structure
        mock_array.get_policies_quota_members.return_value.items = []
        mock_array.get_policies_quota_rules.return_value.items = []
        mock_array.delete_policies_quota.return_value.status_code = 200

        delete_policy(mock_module, mock_array)

        mock_module.warn.assert_called_once()

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_delete_nfs_policy_with_client_rule(self, mock_lv):
        """Test deletion of NFS policy client rule"""
        mock_module = Mock()
        mock_module.params = {
            "name": "nfs_policy1",
            "policy": "nfs",
            "client": "192.168.1.0/24",
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        # Mock existing rule
        mock_rule = Mock()
        mock_rule.client = "192.168.1.0/24"
        mock_rule.name = "rule1"
        mock_array.get_policies_nfs_client_rules.return_value.items = [mock_rule]
        mock_array.delete_policies_nfs_client_rules.return_value.status_code = 200

        delete_policy(mock_module, mock_array)

        mock_array.delete_policies_nfs_client_rules.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_delete_smb_policy_with_client_rule(self, mock_lv):
        """Test deletion of SMB policy client rule"""
        mock_module = Mock()
        mock_module.params = {
            "name": "smb_policy1",
            "policy": "smb",
            "client": "client1",
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        # Mock existing rule
        mock_rule = Mock()
        mock_rule.client = "client1"
        mock_rule.name = "rule1"
        mock_array.get_policies_smb_client_rules.return_value.items = [mock_rule]
        mock_array.delete_policies_smb_client_rules.return_value.status_code = 200

        delete_policy(mock_module, mock_array)

        mock_array.delete_policies_smb_client_rules.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRenamePolicy:
    """Tests for rename_policy function"""

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    @patch("plugins.modules.purefa_policy.PolicyPatch")
    def test_rename_nfs_policy_check_mode(self, mock_policy_patch, mock_lv):
        """Test rename_policy in check mode for NFS policy"""
        mock_module = Mock()
        mock_module.params = {
            "name": "old_policy",
            "rename": "new_policy",
            "policy": "nfs",
            "context": "",
        }
        mock_module.check_mode = True
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        # status_code == 200 means target name is available (can proceed)
        mock_array.get_policies.return_value.status_code = 200

        rename_policy(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=False)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    @patch("plugins.modules.purefa_policy.PolicyPatch")
    def test_rename_nfs_policy_success(self, mock_policy_patch, mock_lv):
        """Test successful NFS policy rename"""
        mock_module = Mock()
        mock_module.params = {
            "name": "old_policy",
            "rename": "new_policy",
            "policy": "nfs",
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        # status_code == 200 means target name is available (can proceed)
        mock_array.get_policies.return_value.status_code = 200
        mock_array.patch_policies_nfs.return_value.status_code = 200

        rename_policy(mock_module, mock_array)

        mock_array.patch_policies_nfs.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    @patch("plugins.modules.purefa_policy.PolicyPatch")
    def test_rename_smb_policy_success(self, mock_policy_patch, mock_lv):
        """Test successful SMB policy rename"""
        mock_module = Mock()
        mock_module.params = {
            "name": "old_smb_policy",
            "rename": "new_smb_policy",
            "policy": "smb",
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_policies.return_value.status_code = 200
        mock_array.patch_policies_smb.return_value.status_code = 200

        rename_policy(mock_module, mock_array)

        mock_array.patch_policies_smb.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    @patch("plugins.modules.purefa_policy.PolicyPatch")
    def test_rename_snapshot_policy_success(self, mock_policy_patch, mock_lv):
        """Test successful snapshot policy rename"""
        mock_module = Mock()
        mock_module.params = {
            "name": "old_snap_policy",
            "rename": "new_snap_policy",
            "policy": "snapshot",
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_policies.return_value.status_code = 200
        mock_array.patch_policies_snapshot.return_value.status_code = 200

        rename_policy(mock_module, mock_array)

        mock_array.patch_policies_snapshot.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    @patch("plugins.modules.purefa_policy.PolicyPatch")
    def test_rename_quota_policy_success(self, mock_policy_patch, mock_lv):
        """Test successful quota policy rename"""
        mock_module = Mock()
        mock_module.params = {
            "name": "old_quota_policy",
            "rename": "new_quota_policy",
            "policy": "quota",
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_policies.return_value.status_code = 200
        mock_array.patch_policies_quota.return_value.status_code = 200

        rename_policy(mock_module, mock_array)

        mock_array.patch_policies_quota.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    @patch("plugins.modules.purefa_policy.PolicyPatch")
    def test_rename_password_policy_fails(self, mock_policy_patch, mock_lv):
        """Test that password policy rename fails with message"""
        mock_module = Mock()
        mock_module.params = {
            "name": "old_password_policy",
            "rename": "new_password_policy",
            "policy": "password",
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        # status_code == 200 means target doesn't exist (can proceed)
        mock_array.get_policies.return_value.status_code = 200

        rename_policy(mock_module, mock_array)

        # Should fail because password policy rename is not supported
        mock_module.fail_json.assert_called()

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    @patch("plugins.modules.purefa_policy.PolicyPatch")
    def test_rename_policy_target_exists(self, mock_policy_patch, mock_lv):
        """Test rename fails when target policy already exists"""
        mock_module = Mock()
        mock_module.params = {
            "name": "old_policy",
            "rename": "existing_policy",
            "policy": "nfs",
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        # status_code != 200 means target name already exists (fail)
        mock_array.get_policies.return_value.status_code = 400

        rename_policy(mock_module, mock_array)

        # May be called multiple times in error handling
        mock_module.fail_json.assert_called()


class TestCreatePolicy:
    """Tests for create_policy function"""

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    @patch("plugins.modules.purefa_policy.PolicyPost")
    @patch("plugins.modules.purefa_policy.PolicyNfsPatch")
    def test_create_nfs_policy_check_mode(self, mock_nfs_patch, mock_post, mock_lv):
        """Test create_policy in check mode"""
        mock_module = Mock()
        mock_module.params = {
            "name": "new_nfs_policy",
            "policy": "nfs",
            "enabled": True,
            "client": None,
            "context": "",
        }
        mock_module.check_mode = True
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        create_policy(mock_module, mock_array, False)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    @patch("plugins.modules.purefa_policy.PolicyPost")
    @patch("plugins.modules.purefa_policy.PolicyNfsPatch")
    def test_create_nfs_policy_success(self, mock_nfs_patch, mock_post, mock_lv):
        """Test successful NFS policy creation"""
        mock_module = Mock()
        mock_module.params = {
            "name": "new_nfs_policy",
            "policy": "nfs",
            "enabled": True,
            "client": None,
            "user_mapping": True,
            "context": "",
            "security": None,
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.post_policies_nfs.return_value.status_code = 200
        mock_array.patch_policies_nfs.return_value.status_code = 200

        create_policy(mock_module, mock_array, False)

        mock_array.post_policies_nfs.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    @patch("plugins.modules.purefa_policy.PolicyPost")
    @patch("plugins.modules.purefa_policy.PolicySmbPatch")
    def test_create_smb_policy_success(self, mock_smb_patch, mock_post, mock_lv):
        """Test successful SMB policy creation"""
        mock_module = Mock()
        mock_module.params = {
            "name": "new_smb_policy",
            "policy": "smb",
            "enabled": True,
            "client": None,
            "smb_anon_allowed": False,
            "smb_encrypt": False,
            "access_based_enumeration": False,
            "continuous_availability": False,
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.43"
        mock_array.post_policies_smb.return_value.status_code = 200
        mock_array.patch_policies_smb.return_value.status_code = 200

        create_policy(mock_module, mock_array, False)

        mock_array.post_policies_smb.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    @patch("plugins.modules.purefa_policy.PolicyPost")
    def test_create_snapshot_policy_success(self, mock_post, mock_lv):
        """Test successful Snapshot policy creation"""
        mock_module = Mock()
        mock_module.params = {
            "name": "new_snap_policy",
            "policy": "snapshot",
            "enabled": True,
            "snap_client_name": None,
            "directory": None,
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.post_policies_snapshot.return_value.status_code = 200

        create_policy(mock_module, mock_array, False)

        mock_array.post_policies_snapshot.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    @patch("plugins.modules.purefa_policy.PolicyPost")
    def test_create_quota_policy_success(self, mock_post, mock_lv):
        """Test successful Quota policy creation (no quota_limit)"""
        mock_module = Mock()
        mock_module.params = {
            "name": "new_quota_policy",
            "policy": "quota",
            "enabled": True,
            "quota_enforced": True,
            "quota_limit": None,
            "quota_notifications": "warning",
            "context": "",
            "ignore_usage": False,
            "directory": None,
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.post_policies_quota.return_value.status_code = 200

        create_policy(mock_module, mock_array, False)

        mock_array.post_policies_quota.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    @patch("plugins.modules.purefa_policy.PolicyPost")
    def test_create_autodir_policy_success(self, mock_post, mock_lv):
        """Test successful Autodir policy creation"""
        mock_module = Mock()
        mock_module.params = {
            "name": "new_autodir_policy",
            "policy": "autodir",
            "enabled": True,
            "directory": None,
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.post_policies_autodir.return_value.status_code = 200

        create_policy(mock_module, mock_array, False)

        mock_array.post_policies_autodir.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    @patch("plugins.modules.purefa_policy.PolicyPost")
    def test_create_nfs_policy_failure(self, mock_post, mock_lv):
        """Test NFS policy creation failure"""
        mock_module = Mock()
        mock_module.params = {
            "name": "new_nfs_policy",
            "policy": "nfs",
            "enabled": True,
            "client": None,
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_res = Mock()
        mock_res.status_code = 400
        mock_res.errors = [Mock(message="Creation failed")]
        mock_array.post_policies_nfs.return_value = mock_res

        create_policy(mock_module, mock_array, False)

        mock_module.fail_json.assert_called_once()


class TestUpdatePolicy:
    """Tests for update_policy function"""

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_update_nfs_policy_check_mode(self, mock_lv):
        """Test update_policy for NFS in check mode"""
        mock_module = Mock()
        mock_module.params = {
            "name": "nfs_policy1",
            "policy": "nfs",
            "enabled": True,
            "context": "",
            "nfs_version": None,
            "user_mapping": None,
            "client": None,
        }
        mock_module.check_mode = True
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock current policy
        mock_policy = Mock()
        mock_policy.enabled = False  # Different from module.params["enabled"]
        mock_policy.nfs_version = []
        mock_array.get_policies_nfs.return_value.items = [mock_policy]
        mock_array.get_policies_nfs.return_value.status_code = 200

        # Mock items for user_mapping
        mock_user_map_item = Mock()
        mock_user_map_item.user_mapping_enabled = False
        mock_array.get_policies_nfs.return_value.items = [mock_user_map_item]

        update_policy(mock_module, mock_array, "2.38", False)

        mock_module.exit_json.assert_called_once()

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    @patch("plugins.modules.purefa_policy.PolicyPatch")
    def test_update_nfs_policy_enable(self, mock_patch, mock_lv):
        """Test enabling NFS policy"""
        mock_module = Mock()
        mock_module.params = {
            "name": "nfs_policy1",
            "policy": "nfs",
            "enabled": True,
            "context": "",
            "nfs_version": None,
            "user_mapping": None,
            "client": None,
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock current policy
        mock_policy = Mock()
        mock_policy.enabled = False  # Different from module.params["enabled"]
        mock_policy.nfs_version = []
        mock_array.get_policies_nfs.return_value.items = [mock_policy]
        mock_array.get_policies_nfs.return_value.status_code = 200

        # Mock user_mapping item
        mock_user_map_item = Mock()
        mock_user_map_item.user_mapping_enabled = False
        mock_array.get_policies_nfs.return_value.items = [mock_user_map_item]

        # Mock patch response
        mock_array.patch_policies_nfs.return_value.status_code = 200

        update_policy(mock_module, mock_array, "2.38", False)

        mock_array.patch_policies_nfs.assert_called()
        mock_module.exit_json.assert_called()

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_update_smb_policy_check_mode(self, mock_lv):
        """Test update_policy for SMB in check mode"""
        mock_module = Mock()
        mock_module.params = {
            "name": "smb_policy1",
            "policy": "smb",
            "enabled": True,
            "context": "",
            "client": None,
            "smb_anon_allowed": None,
            "smb_continuous_avail": None,
            "smb_access_based_enum": None,
        }
        mock_module.check_mode = True
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock current policy
        mock_policy = Mock()
        mock_policy.enabled = False  # Different
        mock_array.get_policies_smb.return_value.items = [mock_policy]
        mock_array.get_policies_smb.return_value.status_code = 200

        update_policy(mock_module, mock_array, "2.38", False)

        mock_module.exit_json.assert_called_once()

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_update_snapshot_policy_check_mode(self, mock_lv):
        """Test update_policy for snapshot in check mode"""
        mock_module = Mock()
        mock_module.params = {
            "name": "snap_policy1",
            "policy": "snapshot",
            "enabled": True,
            "context": "",
            "directory": None,
            "snap_at": None,
            "snap_every": None,
            "snap_keep_for": None,
            "snap_client_name": None,
            "snap_suffix": None,
            "snap_timezone": None,
        }
        mock_module.check_mode = True
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock current policy
        mock_policy = Mock()
        mock_policy.enabled = False  # Different
        mock_array.get_policies_snapshot.return_value.items = [mock_policy]
        mock_array.get_policies_snapshot.return_value.status_code = 200

        update_policy(mock_module, mock_array, "2.38", False)

        mock_module.exit_json.assert_called_once()

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_update_quota_policy_check_mode(self, mock_lv):
        """Test update_policy for quota in check mode"""
        mock_module = Mock()
        mock_module.params = {
            "name": "quota_policy1",
            "policy": "quota",
            "enabled": True,
            "context": "",
            "quota_enforced": True,
            "quota_limit": None,
            "quota_notifications": "warning",
            "directory": None,
            "ignore_usage": False,
        }
        mock_module.check_mode = True
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock current policy
        mock_policy = Mock()
        mock_policy.enabled = False  # Different
        mock_array.get_policies_quota.return_value.items = [mock_policy]
        mock_array.get_policies_quota.return_value.status_code = 200

        update_policy(mock_module, mock_array, "2.38", False)

        mock_module.exit_json.assert_called_once()


class TestUpdatePolicySuccess:
    """Test cases for update_policy success paths"""

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_update_nfs_policy_success(self, mock_lv):
        """Test update_policy for NFS with actual changes"""
        mock_module = Mock()
        mock_module.params = {
            "name": "nfs_policy1",
            "policy": "nfs",
            "enabled": True,
            "context": "",
            "client": None,
            "nfs_access": None,
            "nfs_permission": None,
            "nfs_version": None,
            "user_mapping": False,
            "security": None,
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock current policy with different enabled state
        mock_policy = Mock()
        mock_policy.enabled = False
        mock_policy.user_mapping_enabled = False
        mock_policy.security = None
        mock_policy.nfs_version = None
        mock_array.get_policies_nfs.return_value.items = [mock_policy]
        mock_array.get_policies_nfs.return_value.status_code = 200
        mock_array.patch_policies_nfs.return_value = Mock(status_code=200)

        update_policy(mock_module, mock_array, "2.38", False)

        mock_array.patch_policies_nfs.assert_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_update_smb_policy_success(self, mock_lv):
        """Test update_policy for SMB with actual changes"""
        mock_module = Mock()
        mock_module.params = {
            "name": "smb_policy1",
            "policy": "smb",
            "enabled": True,
            "context": "",
            "client": None,
            "smb_access": None,
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock current policy with different enabled state
        mock_policy = Mock()
        mock_policy.enabled = False
        mock_array.get_policies_smb.return_value.items = [mock_policy]
        mock_array.get_policies_smb.return_value.status_code = 200
        mock_array.patch_policies_smb.return_value = Mock(status_code=200)

        update_policy(mock_module, mock_array, "2.38", False)

        mock_array.patch_policies_smb.assert_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_update_snapshot_policy_success(self, mock_lv):
        """Test update_policy for snapshot with actual changes"""
        mock_module = Mock()
        mock_module.params = {
            "name": "snap_policy1",
            "policy": "snapshot",
            "enabled": True,
            "context": "",
            "snap_at": None,
            "snap_every": None,
            "snap_keep_for": None,
            "snap_client_name": None,
            "directory": None,
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock current policy with different enabled state
        mock_policy = Mock()
        mock_policy.enabled = False
        mock_policy.rules = []
        mock_array.get_policies_snapshot.return_value.items = [mock_policy]
        mock_array.get_policies_snapshot.return_value.status_code = 200
        mock_array.patch_policies_snapshot.return_value = Mock(status_code=200)

        update_policy(mock_module, mock_array, "2.38", False)

        mock_array.patch_policies_snapshot.assert_called()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_update_quota_policy_success(self, mock_lv):
        """Test update_policy for quota with actual changes"""
        mock_module = Mock()
        mock_module.params = {
            "name": "quota_policy1",
            "policy": "quota",
            "enabled": True,
            "context": "",
            "quota_enforced": True,
            "quota_limit": None,
            "quota_notifications": "warning",
            "directory": None,
            "ignore_usage": False,
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock current policy with different enabled state
        mock_policy = Mock()
        mock_policy.enabled = False
        mock_array.get_policies_quota.return_value.items = [mock_policy]
        mock_array.get_policies_quota.return_value.status_code = 200
        mock_array.patch_policies_quota.return_value = Mock(status_code=200)

        update_policy(mock_module, mock_array, "2.38", False)

        mock_array.patch_policies_quota.assert_called()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestDeletePolicySuccess:
    """Test cases for delete_policy success paths"""

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_delete_nfs_policy_with_client_rule(self, mock_lv):
        """Test successful deletion of NFS client rule"""
        mock_module = Mock()
        mock_module.params = {
            "name": "nfs_policy1",
            "policy": "nfs",
            "client": "192.168.1.0/24",
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock existing rule
        mock_rule = Mock()
        mock_rule.client = "192.168.1.0/24"
        mock_rule.name = "rule1"
        mock_array.get_policies_nfs_client_rules.return_value.items = [mock_rule]
        mock_array.delete_policies_nfs_client_rules.return_value.status_code = 200

        delete_policy(mock_module, mock_array)

        mock_array.delete_policies_nfs_client_rules.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_delete_smb_policy_with_client_rule(self, mock_lv):
        """Test successful deletion of SMB client rule"""
        mock_module = Mock()
        mock_module.params = {
            "name": "smb_policy1",
            "policy": "smb",
            "client": "192.168.1.0/24",
            "context": "",
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        # Mock existing rule
        mock_rule = Mock()
        mock_rule.client = "192.168.1.0/24"
        mock_rule.name = "smb_rule1"
        mock_array.get_policies_smb_client_rules.return_value.items = [mock_rule]
        mock_array.delete_policies_smb_client_rules.return_value.status_code = 200

        delete_policy(mock_module, mock_array)

        mock_array.delete_policies_smb_client_rules.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_delete_autodir_policy_success(self, mock_lv):
        """Test successful deletion of autodir policy"""
        mock_module = Mock()
        mock_module.params = {
            "name": "autodir_policy1",
            "policy": "autodir",
            "context": "",
            "directory": None,
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.delete_policies_autodir.return_value.status_code = 200

        delete_policy(mock_module, mock_array)

        mock_array.delete_policies_autodir.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestCreatePolicySuccess:
    """Test cases for create_policy success paths"""

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_create_nfs_policy_basic(self, mock_lv):
        """Test successful creation of basic NFS policy"""
        mock_module = Mock()
        mock_module.params = {
            "name": "nfs_policy1",
            "policy": "nfs",
            "enabled": True,
            "context": "",
            "client": None,
            "user_mapping": False,
            "nfs_version": None,
            "security": None,
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.post_policies_nfs.return_value = Mock(status_code=200)
        mock_array.patch_policies_nfs.return_value = Mock(status_code=200)

        create_policy(mock_module, mock_array, False)

        mock_array.post_policies_nfs.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_policy.LooseVersion", side_effect=LooseVersion)
    def test_create_smb_policy_basic(self, mock_lv):
        """Test successful creation of basic SMB policy"""
        mock_module = Mock()
        mock_module.params = {
            "name": "smb_policy1",
            "policy": "smb",
            "enabled": True,
            "context": "",
            "client": None,
            "smb_access": None,
            "access_based_enumeration": False,
            "continuous_availability": False,
            "smb_anon_allowed": False,
            "smb_encrypt": False,
        }
        mock_module.check_mode = False
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.post_policies_smb.return_value = Mock(status_code=200)
        mock_array.patch_policies_smb.return_value = Mock(status_code=200)

        create_policy(mock_module, mock_array, False)

        mock_array.post_policies_smb.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)
