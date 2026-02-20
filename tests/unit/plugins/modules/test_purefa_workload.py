# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_workload module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from unittest.mock import Mock, MagicMock

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

from plugins.modules.purefa_workload import (
    delete_workload,
    eradicate_workload,
    recover_workload,
    rename_workload,
    create_workload,
    connect_or_disconnect_volumes,
)


class TestDeleteWorkload:
    """Test cases for delete_workload function"""

    def test_delete_workload_check_mode(self):
        """Test delete_workload in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-workload",
            "context": "",
            "eradicate": False,
        }
        mock_array = Mock()

        delete_workload(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestEradicateWorkload:
    """Test cases for eradicate_workload function"""

    def test_eradicate_workload_check_mode(self):
        """Test eradicate_workload in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-workload", "context": ""}
        mock_array = Mock()

        eradicate_workload(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRecoverWorkload:
    """Test cases for recover_workload function"""

    def test_recover_workload_check_mode(self):
        """Test recover_workload in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "test-workload", "context": "", "host": ""}
        mock_array = Mock()

        recover_workload(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRenameWorkload:
    """Test cases for rename_workload function"""

    def test_rename_workload_check_mode(self):
        """Test rename_workload in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "old-workload",
            "rename": "new-workload",
            "context": "",
        }
        mock_array = Mock()

        rename_workload(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestCreateWorkload:
    """Test cases for create_workload function"""

    def test_create_workload_check_mode(self):
        """Test create_workload in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-workload",
            "preset": "test-preset",
            "context": "pod1",
            "recommendation": False,
            "host": "",
        }
        mock_array = Mock()
        mock_fleet = Mock()
        mock_preset_config = Mock()
        mock_preset_config.parameters = Mock()
        mock_preset_config.periodic_replication_configurations = []
        mock_preset_config.placement_configurations = []
        mock_preset_config.qos_configurations = []
        mock_preset_config.snapshot_configurations = []
        mock_preset_config.volume_configurations = []
        mock_preset_config.workload_tags = []

        create_workload(mock_module, mock_array, mock_fleet, mock_preset_config)

        mock_module.exit_json.assert_called_once_with(changed=True)


class TestConnectOrDisconnectVolumes:
    """Test cases for connect_or_disconnect_volumes function"""

    def test_connect_volumes_check_mode(self):
        """Test connect_or_disconnect_volumes in connect mode with check_mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-workload",
            "context": "pod1",
            "host": "host1",
        }
        mock_array = Mock()

        # Mock get_connections - no existing connections
        mock_array.get_connections.return_value = Mock(status_code=200, items=[])

        # Mock get_volumes - workload has volumes
        mock_volume = Mock()
        mock_volume.name = "test-volume"
        mock_array.get_volumes.return_value = Mock(status_code=200, items=[mock_volume])

        connect_or_disconnect_volumes(mock_module, mock_array, "connect")

        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_disconnect_volumes_check_mode(self):
        """Test connect_or_disconnect_volumes in disconnect mode with check_mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-workload",
            "context": "pod1",
            "host": "host1",
        }
        mock_array = Mock()

        # Mock get_connections - volume is connected
        mock_conn = Mock()
        mock_conn.volume = Mock()
        mock_conn.volume.name = "test-volume"
        mock_array.get_connections.return_value = Mock(
            status_code=200, items=[mock_conn]
        )

        # Mock get_volumes - workload has the connected volume
        mock_volume = Mock()
        mock_volume.name = "test-volume"
        mock_array.get_volumes.return_value = Mock(status_code=200, items=[mock_volume])

        connect_or_disconnect_volumes(mock_module, mock_array, "disconnect")

        mock_module.exit_json.assert_called_once_with(changed=True)

    def test_connect_volumes_no_change(self):
        """Test connect_or_disconnect_volumes when volume is already connected"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-workload",
            "context": "pod1",
            "host": "host1",
        }
        mock_array = Mock()

        # Mock get_connections - volume is already connected
        mock_conn = Mock()
        mock_conn.volume = Mock()
        mock_conn.volume.name = "test-volume"
        mock_array.get_connections.return_value = Mock(
            status_code=200, items=[mock_conn]
        )

        # Mock get_volumes - workload has the same volume
        mock_volume = Mock()
        mock_volume.name = "test-volume"
        mock_array.get_volumes.return_value = Mock(status_code=200, items=[mock_volume])

        connect_or_disconnect_volumes(mock_module, mock_array, "connect")

        mock_module.exit_json.assert_called_once_with(changed=False)
