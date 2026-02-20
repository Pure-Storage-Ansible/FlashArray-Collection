# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_pg module."""

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

from plugins.modules.purefa_pg import (
    get_pod,
    get_targets,
    get_arrays,
    get_pending_pgroup,
    get_pgroup,
    make_pgroup,
    delete_pgroup,
    eradicate_pgroup,
    recover_pgroup,
)


class TestGetPod:
    """Test cases for get_pod function"""

    @patch("plugins.modules.purefa_pg.LooseVersion")
    def test_get_pod_exists(self, mock_loose_version):
        """Test get_pod returns pod when it exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "pod1::pg1", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_pod = Mock()
        mock_pod.name = "pod1"
        mock_array.get_pods.return_value = Mock(status_code=200, items=[mock_pod])

        result = get_pod(mock_module, mock_array)

        assert result == mock_pod

    @patch("plugins.modules.purefa_pg.LooseVersion")
    def test_get_pod_not_exists(self, mock_loose_version):
        """Test get_pod returns None when pod doesn't exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "pod1::pg1", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_pods.return_value = Mock(status_code=404)

        result = get_pod(mock_module, mock_array)

        assert result is None


class TestGetTargets:
    """Test cases for get_targets function"""

    @patch("plugins.modules.purefa_pg.LooseVersion")
    def test_get_targets_connected(self, mock_loose_version):
        """Test get_targets returns connected targets"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_target1 = Mock()
        mock_target1.name = "nfs-target1"
        mock_target1.status = "connected"
        mock_target2 = Mock()
        mock_target2.name = "s3-target"
        mock_target2.status = "disconnected"
        mock_array.get_offloads.return_value = Mock(items=[mock_target1, mock_target2])

        result = get_targets(mock_module, mock_array)

        assert result == ["nfs-target1"]


class TestGetArrays:
    """Test cases for get_arrays function"""

    @patch("plugins.modules.purefa_pg.LooseVersion")
    def test_get_arrays_connected(self, mock_loose_version):
        """Test get_arrays returns connected arrays"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_conn1 = Mock()
        mock_conn1.name = "array2"
        mock_conn1.status = "connected"
        mock_array.get_array_connections.return_value = Mock(items=[mock_conn1])

        result = get_arrays(mock_module, mock_array)

        assert result == ["array2"]


class TestGetPendingPgroup:
    """Test cases for get_pending_pgroup function"""

    @patch("plugins.modules.purefa_pg.LooseVersion")
    def test_get_pending_pgroup_exists(self, mock_loose_version):
        """Test get_pending_pgroup returns pgroup when deleted pgroup exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "test-pg", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_pg = Mock()
        mock_pg.name = "test-pg"
        mock_array.get_protection_groups.return_value = Mock(
            status_code=200, items=[mock_pg]
        )

        result = get_pending_pgroup(mock_module, mock_array)

        assert result == mock_pg


class TestGetPgroup:
    """Test cases for get_pgroup function"""

    @patch("plugins.modules.purefa_pg.LooseVersion")
    def test_get_pgroup_exists(self, mock_loose_version):
        """Test get_pgroup returns pgroup when it exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "test-pg", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_pg = Mock()
        mock_pg.name = "test-pg"
        mock_array.get_protection_groups.return_value = Mock(
            status_code=200, items=[mock_pg]
        )

        result = get_pgroup(mock_module, mock_array)

        assert result == mock_pg

    @patch("plugins.modules.purefa_pg.LooseVersion")
    def test_get_pgroup_not_exists(self, mock_loose_version):
        """Test get_pgroup returns None when pgroup doesn't exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"name": "nonexistent", "context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_protection_groups.return_value = Mock(status_code=404)

        result = get_pgroup(mock_module, mock_array)

        assert result is None


class TestMakePgroup:
    """Test cases for make_pgroup function"""

    @patch("plugins.modules.purefa_pg.check_response")
    @patch("plugins.modules.purefa_pg.LooseVersion")
    def test_make_pgroup_check_mode(self, mock_loose_version, mock_check_response):
        """Test make_pgroup in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "new-pg", "target": None}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        make_pgroup(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestDeletePgroup:
    """Test cases for delete_pgroup function"""

    @patch("plugins.modules.purefa_pg.check_response")
    @patch("plugins.modules.purefa_pg.LooseVersion")
    def test_delete_pgroup_check_mode(self, mock_loose_version, mock_check_response):
        """Test delete_pgroup in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-pg", "eradicate": False}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        delete_pgroup(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestEradicatePgroup:
    """Test cases for eradicate_pgroup function"""

    @patch("plugins.modules.purefa_pg.check_response")
    @patch("plugins.modules.purefa_pg.LooseVersion")
    def test_eradicate_pgroup_check_mode(self, mock_loose_version, mock_check_response):
        """Test eradicate_pgroup in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "deleted-pg"}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        eradicate_pgroup(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRecoverPgroup:
    """Test cases for recover_pgroup function"""

    @patch("plugins.modules.purefa_pg.check_response")
    @patch("plugins.modules.purefa_pg.LooseVersion")
    def test_recover_pgroup_check_mode(self, mock_loose_version, mock_check_response):
        """Test recover_pgroup in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "deleted-pg"}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"

        recover_pgroup(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)
