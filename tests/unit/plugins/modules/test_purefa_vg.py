# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_vg module."""

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

from plugins.modules.purefa_vg import (
    rename_exists,
    get_multi_vgroups,
    get_pending_vgroup,
    get_vgroup,
    rename_vgroup,
    make_vgroup,
    make_multi_vgroups,
    update_vgroup,
    delete_vgroup,
    eradicate_vgroup,
    recover_vgroup,
)


class TestRenameExists:
    """Test cases for rename_exists function"""

    @patch("plugins.modules.purefa_vg.LooseVersion")
    def test_rename_exists_true(self, mock_loose_version):
        """Test rename_exists returns True when target exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"rename": "new-vg", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_volume_groups.return_value = Mock(status_code=200)

        result = rename_exists(mock_module, mock_array)

        assert result is True

    @patch("plugins.modules.purefa_vg.LooseVersion")
    def test_rename_exists_false(self, mock_loose_version):
        """Test rename_exists returns False when target doesn't exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"rename": "new-vg", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_volume_groups.return_value = Mock(status_code=404)

        result = rename_exists(mock_module, mock_array)

        assert result is False


class TestGetMultiVgroups:
    """Test cases for get_multi_vgroups function"""

    @patch("plugins.modules.purefa_vg.LooseVersion")
    def test_get_multi_vgroups_all_exist(self, mock_loose_version):
        """Test get_multi_vgroups returns True when all vgroups exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {
            "name": "vg",
            "start": 0,
            "count": 3,
            "digits": 2,
            "suffix": "",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_volume_groups.return_value = Mock(status_code=200)

        result = get_multi_vgroups(mock_module, mock_array)

        assert result is True


class TestGetPendingVgroup:
    """Test cases for get_pending_vgroup function"""

    @patch("plugins.modules.purefa_vg.LooseVersion")
    def test_get_pending_vgroup_exists(self, mock_loose_version):
        """Test get_pending_vgroup returns True when deleted vgroup exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "deleted-vg", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_volume_groups.return_value = Mock(status_code=200)

        result = get_pending_vgroup(mock_module, mock_array)

        assert result is True


class TestGetVgroup:
    """Test cases for get_vgroup function"""

    @patch("plugins.modules.purefa_vg.LooseVersion")
    def test_get_vgroup_exists(self, mock_loose_version):
        """Test get_vgroup returns True when it exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "test-vg", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_volume_groups.return_value = Mock(status_code=200)

        result = get_vgroup(mock_module, mock_array)

        assert result is True

    @patch("plugins.modules.purefa_vg.LooseVersion")
    def test_get_vgroup_not_exists(self, mock_loose_version):
        """Test get_vgroup returns False when vgroup doesn't exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "nonexistent", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_volume_groups.return_value = Mock(status_code=404)

        result = get_vgroup(mock_module, mock_array)

        assert result is False


class TestMakeVgroup:
    """Test cases for make_vgroup function"""

    @patch("plugins.modules.purefa_vg.LooseVersion")
    def test_make_vgroup_check_mode(self, mock_loose_version):
        """Test make_vgroup in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "new-vg", "bw_qos": None, "iops_qos": None}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        make_vgroup(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestMakeMultiVgroups:
    """Test cases for make_multi_vgroups function"""

    @patch("plugins.modules.purefa_vg.LooseVersion")
    def test_make_multi_vgroups_check_mode(self, mock_loose_version):
        """Test make_multi_vgroups in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "vg",
            "start": 0,
            "count": 3,
            "digits": 2,
            "suffix": "",
            "bw_qos": None,
            "iops_qos": None,
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        make_multi_vgroups(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestDeleteVgroup:
    """Test cases for delete_vgroup function"""

    @patch("plugins.modules.purefa_vg.LooseVersion")
    def test_delete_vgroup_check_mode(self, mock_loose_version):
        """Test delete_vgroup in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-vg", "eradicate": False}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        delete_vgroup(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestEradicateVgroup:
    """Test cases for eradicate_vgroup function"""

    @patch("plugins.modules.purefa_vg.LooseVersion")
    def test_eradicate_vgroup_check_mode(self, mock_loose_version):
        """Test eradicate_vgroup in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "deleted-vg"}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        eradicate_vgroup(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRecoverVgroup:
    """Test cases for recover_vgroup function"""

    @patch("plugins.modules.purefa_vg.LooseVersion")
    def test_recover_vgroup_check_mode(self, mock_loose_version):
        """Test recover_vgroup in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "deleted-vg"}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        recover_vgroup(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRenameVgroup:
    """Test cases for rename_vgroup function"""

    @patch("plugins.modules.purefa_vg.rename_exists")
    @patch("plugins.modules.purefa_vg.LooseVersion")
    def test_rename_vgroup_check_mode(self, mock_loose_version, mock_rename_exists):
        """Test rename_vgroup in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_rename_exists.return_value = False
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "old-vg", "rename": "new-vg", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        rename_vgroup(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_vg.rename_exists")
    @patch("plugins.modules.purefa_vg.LooseVersion")
    def test_rename_vgroup_target_exists(self, mock_loose_version, mock_rename_exists):
        """Test rename_vgroup when target already exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_rename_exists.return_value = True
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "old-vg", "rename": "existing-vg", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        rename_vgroup(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=False)


class TestUpdateVgroup:
    """Test cases for update_vgroup function"""

    @patch("plugins.modules.purefa_vg.LooseVersion")
    def test_update_vgroup_no_changes(self, mock_loose_version):
        """Test update_vgroup with no changes needed"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = False
        params = {
            "name": "test-vg",
            "context": "",
            "bw_qos": None,
            "iops_qos": None,
            "priority_operator": None,
            "priority_value": None,
        }
        mock_module.params = params
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_vg = Mock()
        mock_vg.qos = Mock(bandwidth_limit=None, iops_limit=None)
        mock_array.get_volume_groups.return_value.items = [mock_vg]

        update_vgroup(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=False)
