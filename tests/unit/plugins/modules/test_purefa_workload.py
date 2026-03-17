# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_workload module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from unittest.mock import Mock, MagicMock, patch

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
    expand_workload,
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


class TestDeleteWorkloadSuccess:
    """Additional test cases for delete_workload function"""

    @patch("plugins.modules.purefa_workload.check_response")
    def test_delete_workload_success(self, mock_check_response):
        """Test delete_workload successfully deletes"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-workload",
            "context": "pod1",
            "eradicate": False,
        }
        mock_array = Mock()
        mock_array.patch_workloads.return_value = Mock(status_code=200)

        delete_workload(mock_module, mock_array)

        mock_array.patch_workloads.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestEradicateWorkloadSuccess:
    """Additional test cases for eradicate_workload function"""

    @patch("plugins.modules.purefa_workload.check_response")
    def test_eradicate_workload_success(self, mock_check_response):
        """Test eradicate_workload successfully eradicates"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "test-workload", "context": "pod1"}
        mock_array = Mock()
        mock_array.delete_workloads.return_value = Mock(status_code=200)

        eradicate_workload(mock_module, mock_array)

        mock_array.delete_workloads.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRecoverWorkloadSuccess:
    """Additional test cases for recover_workload function"""

    @patch("plugins.modules.purefa_workload.check_response")
    def test_recover_workload_success(self, mock_check_response):
        """Test recover_workload successfully recovers without host"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {"name": "test-workload", "context": "pod1", "host": ""}
        mock_array = Mock()
        mock_array.patch_workloads.return_value = Mock(status_code=200)

        recover_workload(mock_module, mock_array)

        mock_array.patch_workloads.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRenameWorkloadSuccess:
    """Additional test cases for rename_workload function"""

    @patch("plugins.modules.purefa_workload.check_response")
    def test_rename_workload_success(self, mock_check_response):
        """Test rename_workload successfully renames"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "old-workload",
            "rename": "new-workload",
            "context": "pod1",
        }
        mock_array = Mock()
        mock_array.patch_workloads.return_value = Mock(status_code=200)

        rename_workload(mock_module, mock_array)

        mock_array.patch_workloads.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestCreateWorkloadSuccess:
    """Test cases for create_workload function success scenarios"""

    @patch("plugins.modules.purefa_workload.check_response")
    def test_create_workload_success(self, mock_check_response):
        """Test create_workload successfully creates"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-workload",
            "preset": "test-preset",
            "context": "pod1",
            "recommendation": False,
            "host": "",
        }
        mock_array = Mock()
        mock_array.post_workloads.return_value = Mock(status_code=200)
        mock_fleet = Mock()
        mock_preset_config = Mock()
        mock_preset_config.parameters = Mock()
        mock_preset_config.periodic_replication_configurations = Mock()
        mock_preset_config.placement_configurations = Mock()
        mock_preset_config.qos_configurations = Mock()
        mock_preset_config.snapshot_configurations = Mock()
        mock_preset_config.volume_configurations = Mock()
        mock_preset_config.workload_tags = Mock()

        create_workload(mock_module, mock_array, mock_fleet, mock_preset_config)

        mock_array.post_workloads.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

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
        mock_preset_config.periodic_replication_configurations = Mock()
        mock_preset_config.placement_configurations = Mock()
        mock_preset_config.qos_configurations = Mock()
        mock_preset_config.snapshot_configurations = Mock()
        mock_preset_config.volume_configurations = Mock()
        mock_preset_config.workload_tags = Mock()

        create_workload(mock_module, mock_array, mock_fleet, mock_preset_config)

        mock_array.post_workloads.assert_not_called()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestExpandWorkloadSuccess:
    """Test cases for expand_workload function success scenarios"""

    @patch("plugins.modules.purefa_workload._connect_volumes")
    @patch("plugins.modules.purefa_workload._create_volume")
    def test_expand_workload_success(self, mock_create_vol, mock_connect_vols):
        """Test expand_workload successfully expands"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-workload",
            "preset": "test-preset",
            "context": "pod1",
            "volume_configuration": "vol-config1",
            "volume_count": 2,
            "host": "host1",
        }
        mock_array = Mock()
        mock_fleet = Mock()
        # Create volume config that matches
        mock_vol_config = Mock()
        mock_vol_config.name = "vol-config1"
        volume_configs = [mock_vol_config]

        expand_workload(mock_module, mock_array, mock_fleet, volume_configs)

        assert mock_create_vol.call_count == 2
        mock_connect_vols.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_workload._create_volume")
    def test_expand_workload_no_match_fails(self, mock_create_vol):
        """Test expand_workload fails when no volume config matches"""
        import pytest

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-workload",
            "preset": "test-preset",
            "context": "pod1",
            "volume_configuration": "nonexistent-config",
            "volume_count": 2,
            "host": "",
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_array = Mock()
        mock_fleet = Mock()
        # Create volume config with different name
        mock_vol_config = Mock()
        mock_vol_config.name = "other-config"
        volume_configs = [mock_vol_config]

        with pytest.raises(SystemExit):
            expand_workload(mock_module, mock_array, mock_fleet, volume_configs)

        mock_create_vol.assert_not_called()
        mock_module.fail_json.assert_called_once()


class TestDeleteWorkloadWithEradicate:
    """Test cases for delete_workload with eradicate option"""

    @patch("plugins.modules.purefa_workload.eradicate_workload")
    @patch("plugins.modules.purefa_workload.check_response")
    def test_delete_workload_with_eradicate(
        self, mock_check_response, mock_eradicate_workload
    ):
        """Test delete_workload with eradicate flag"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-workload",
            "context": "pod1",
            "eradicate": True,
        }
        mock_array = Mock()
        mock_array.patch_workloads.return_value = Mock(status_code=200)

        delete_workload(mock_module, mock_array)

        mock_array.patch_workloads.assert_called_once()
        mock_eradicate_workload.assert_called_once_with(mock_module, mock_array)

    @patch("plugins.modules.purefa_workload.check_response")
    def test_delete_workload_without_eradicate(self, mock_check_response):
        """Test delete_workload without eradicate flag"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-workload",
            "context": "pod1",
            "eradicate": False,
        }
        mock_array = Mock()
        mock_array.patch_workloads.return_value = Mock(status_code=200)

        delete_workload(mock_module, mock_array)

        mock_array.patch_workloads.assert_called_once()
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestRecoverWorkloadWithHost:
    """Test cases for recover_workload with host option"""

    @patch("plugins.modules.purefa_workload._connect_volumes")
    @patch("plugins.modules.purefa_workload.check_response")
    def test_recover_workload_with_host(
        self, mock_check_response, mock_connect_volumes
    ):
        """Test recover_workload with host connection"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-workload",
            "context": "pod1",
            "host": "host1",
        }
        mock_array = Mock()
        mock_array.patch_workloads.return_value = Mock(status_code=200)

        recover_workload(mock_module, mock_array)

        mock_array.patch_workloads.assert_called_once()
        mock_connect_volumes.assert_called_once_with(mock_module, mock_array)
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestConnectOrDisconnectVolumesSuccess:
    """Test cases for connect_or_disconnect_volumes success paths"""

    @patch("plugins.modules.purefa_workload._connect_volumes")
    @patch("plugins.modules.purefa_workload.check_response")
    def test_connect_volumes_success(self, mock_check_response, mock_connect_volumes):
        """Test connect_or_disconnect_volumes connects volumes"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-workload",
            "host": "host1",
            "context": "pod1",
        }
        mock_array = Mock()
        # Mock no existing connections
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.items = []
        mock_array.get_connections.return_value = mock_response
        # Mock workload volumes exist
        mock_vol_response = Mock()
        mock_vol_response.status_code = 200
        mock_vol_response.items = [Mock(name="vol1")]
        mock_array.get_volumes.return_value = mock_vol_response

        connect_or_disconnect_volumes(mock_module, mock_array, "connect")

        mock_connect_volumes.assert_called_once_with(mock_module, mock_array)
        mock_module.exit_json.assert_called_once_with(changed=True)

    @patch("plugins.modules.purefa_workload._disconnect_volumes")
    @patch("plugins.modules.purefa_workload.check_response")
    def test_disconnect_volumes_success(
        self, mock_check_response, mock_disconnect_volumes
    ):
        """Test connect_or_disconnect_volumes disconnects volumes"""
        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test-workload",
            "host": "host1",
            "context": "pod1",
        }
        mock_array = Mock()
        # Mock existing connections - volume name must be accessible via conn.volume.name
        mock_response = Mock()
        mock_response.status_code = 200
        mock_conn = Mock()
        mock_conn.volume = Mock()
        mock_conn.volume.name = "vol1"  # Set as attribute, not constructor arg
        mock_response.items = [mock_conn]
        mock_array.get_connections.return_value = mock_response
        # Mock workload volumes exist - must match connection volume name
        mock_vol_response = Mock()
        mock_vol_response.status_code = 200
        mock_vol = Mock()
        mock_vol.name = "vol1"  # Must match the connection volume name
        mock_vol_response.items = [mock_vol]
        mock_array.get_volumes.return_value = mock_vol_response

        connect_or_disconnect_volumes(mock_module, mock_array, "disconnect")

        mock_disconnect_volumes.assert_called_once_with(mock_module, mock_array)
        mock_module.exit_json.assert_called_once_with(changed=True)


class TestCreateVolume:
    """Test cases for _create_volume helper function"""

    @patch("plugins.modules.purefa_workload.check_response")
    @patch("plugins.modules.purefa_workload.VolumePost")
    @patch("plugins.modules.purefa_workload.WorkloadConfigurationReference")
    def test_create_volume_success(self, mock_workload_config, mock_volume_post, mock_check_response):
        """Test _create_volume creates a volume"""
        from plugins.modules.purefa_workload import _create_volume

        mock_module = Mock()
        mock_module.params = {
            "name": "test-workload",
            "volume_configuration": "vol-config",
            "context": "pod1",
        }
        mock_array = Mock()
        mock_array.post_volumes.return_value = Mock(status_code=200)

        _create_volume(mock_module, mock_array)

        mock_array.post_volumes.assert_called_once()
        mock_check_response.assert_called_once()


class TestDisconnectVolumes:
    """Test cases for _disconnect_volumes helper function"""

    @patch("plugins.modules.purefa_workload.check_response")
    def test_disconnect_volumes_success(self, mock_check_response):
        """Test _disconnect_volumes disconnects all workload volumes"""
        from plugins.modules.purefa_workload import _disconnect_volumes

        mock_module = Mock()
        mock_module.params = {
            "name": "test-workload",
            "host": "host1",
            "context": "pod1",
        }
        mock_array = Mock()
        mock_vol = Mock()
        mock_vol.name = "vol1"
        mock_array.get_volumes.return_value = Mock(items=[mock_vol])
        mock_array.delete_connections.return_value = Mock(status_code=200)

        _disconnect_volumes(mock_module, mock_array)

        mock_array.get_volumes.assert_called_once()
        mock_array.delete_connections.assert_called_once_with(
            host_names=["host1"],
            context_names=["pod1"],
            volume_names=["vol1"],
        )


class TestConnectVolumes:
    """Test cases for _connect_volumes helper function"""

    @patch("plugins.modules.purefa_workload.check_response")
    @patch("plugins.modules.purefa_workload.ConnectionPost")
    def test_connect_volumes_success(self, mock_connection_post, mock_check_response):
        """Test _connect_volumes connects all workload volumes"""
        from plugins.modules.purefa_workload import _connect_volumes

        mock_module = Mock()
        mock_module.params = {
            "name": "test-workload",
            "host": "host1",
            "context": "pod1",
        }
        mock_array = Mock()
        mock_vol = Mock()
        mock_vol.name = "vol1"
        mock_array.get_volumes.return_value = Mock(items=[mock_vol])
        mock_array.post_connections.return_value = Mock(status_code=200)

        _connect_volumes(mock_module, mock_array)

        mock_array.get_volumes.assert_called_once()
        mock_array.post_connections.assert_called_once()


class TestMain:
    """Test cases for main() function"""

    @patch("plugins.modules.purefa_workload.LooseVersion")
    @patch("plugins.modules.purefa_workload.get_array")
    @patch("plugins.modules.purefa_workload.AnsibleModule")
    @patch("plugins.modules.purefa_workload.HAS_PURESTORAGE", True)
    def test_main_no_purestorage_sdk(self, mock_ansible_module, mock_get_array, mock_loose_version):
        """Test main() fails when purestorage SDK not available"""
        import pytest
        from plugins.modules.purefa_workload import main

        # Need to patch at module level to override HAS_PURESTORAGE
        with patch("plugins.modules.purefa_workload.HAS_PURESTORAGE", False):
            mock_module = Mock()
            mock_module.fail_json.side_effect = SystemExit(1)
            mock_ansible_module.return_value = mock_module

            with pytest.raises(SystemExit):
                main()

            mock_module.fail_json.assert_called_once()

    @patch("plugins.modules.purefa_workload.LooseVersion")
    @patch("plugins.modules.purefa_workload.get_array")
    @patch("plugins.modules.purefa_workload.AnsibleModule")
    @patch("plugins.modules.purefa_workload.HAS_PURESTORAGE", True)
    def test_main_api_version_too_old(self, mock_ansible_module, mock_get_array, mock_loose_version):
        """Test main() fails when API version is too old"""
        import pytest
        from plugins.modules.purefa_workload import main

        mock_loose_version.side_effect = lambda x: float(x) if x else 0.0

        mock_module = Mock()
        mock_module.params = {"volume_count": None}
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_ansible_module.return_value = mock_module
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"  # Too old (needs 2.40)
        mock_get_array.return_value = mock_array

        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called()

    @patch("plugins.modules.purefa_workload.LooseVersion")
    @patch("plugins.modules.purefa_workload.get_array")
    @patch("plugins.modules.purefa_workload.AnsibleModule")
    @patch("plugins.modules.purefa_workload.HAS_PURESTORAGE", True)
    def test_main_invalid_volume_count(self, mock_ansible_module, mock_get_array, mock_loose_version):
        """Test main() fails when volume_count is not positive"""
        import pytest
        from plugins.modules.purefa_workload import main

        mock_loose_version.side_effect = lambda x: float(x) if x else 0.0

        mock_module = Mock()
        mock_module.params = {
            "volume_count": -1,
            "state": "present",
            "preset": "test-preset",
            "context": "",
            "name": "test-workload",
        }
        mock_module.fail_json.side_effect = SystemExit(1)
        mock_ansible_module.return_value = mock_module
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.40"
        mock_get_array.return_value = mock_array

        with pytest.raises(SystemExit):
            main()

        mock_module.fail_json.assert_called()

    @patch("plugins.modules.purefa_workload.create_workload")
    @patch("plugins.modules.purefa_workload.LooseVersion")
    @patch("plugins.modules.purefa_workload.check_response")
    @patch("plugins.modules.purefa_workload.get_array")
    @patch("plugins.modules.purefa_workload.AnsibleModule")
    @patch("plugins.modules.purefa_workload.HAS_PURESTORAGE", True)
    def test_main_fleet_check_fails(self, mock_ansible_module, mock_get_array, mock_check_response, mock_loose_version, mock_create_workload):
        """Test main() calls check_response for fleet"""
        from plugins.modules.purefa_workload import main

        mock_loose_version.side_effect = lambda x: float(x) if x else 0.0

        mock_module = Mock()
        mock_module.params = {
            "volume_count": None,
            "state": "present",
            "preset": "test-preset",
            "context": "",
            "name": "test-workload",
            "rename": None,
            "host": "",
            "recommendation": False,
            "placement": None,
            "eradicate": False,
        }
        mock_ansible_module.return_value = mock_module
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.40"
        mock_fleet_response = Mock(status_code=200)
        mock_fleet = Mock()
        mock_fleet.name = "test-fleet"
        mock_fleet_response.items = [mock_fleet]
        mock_array.get_fleets.return_value = mock_fleet_response
        mock_array.get_workloads.return_value = Mock(status_code=404)
        mock_preset_config = Mock()
        mock_array.get_presets_workload.return_value = Mock(status_code=200, items=[mock_preset_config])
        mock_get_array.return_value = mock_array

        main()

        mock_check_response.assert_called()

    @patch("plugins.modules.purefa_workload.delete_workload")
    @patch("plugins.modules.purefa_workload.LooseVersion")
    @patch("plugins.modules.purefa_workload.check_response")
    @patch("plugins.modules.purefa_workload.get_array")
    @patch("plugins.modules.purefa_workload.AnsibleModule")
    @patch("plugins.modules.purefa_workload.HAS_PURESTORAGE", True)
    def test_main_state_absent_delete(self, mock_ansible_module, mock_get_array, mock_check_response, mock_loose_version, mock_delete_workload):
        """Test main() calls delete_workload when state=absent"""
        from plugins.modules.purefa_workload import main

        mock_loose_version.side_effect = lambda x: float(x) if x else 0.0

        mock_module = Mock()
        mock_module.params = {
            "volume_count": None,
            "state": "absent",
            "preset": "test-preset",
            "context": "",
            "name": "test-workload",
            "host": "",
            "eradicate": False,
        }
        mock_ansible_module.return_value = mock_module
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.40"
        mock_fleet_response = Mock(status_code=200)
        mock_fleet = Mock()
        mock_fleet.name = "test-fleet"
        mock_fleet_response.items = [mock_fleet]
        mock_array.get_fleets.return_value = mock_fleet_response
        # Workload exists and not destroyed
        mock_workload = Mock()
        mock_workload.destroyed = False
        mock_array.get_workloads.return_value = Mock(status_code=200, items=[mock_workload])
        mock_get_array.return_value = mock_array

        main()

        mock_delete_workload.assert_called_once()

    @patch("plugins.modules.purefa_workload.eradicate_workload")
    @patch("plugins.modules.purefa_workload.LooseVersion")
    @patch("plugins.modules.purefa_workload.check_response")
    @patch("plugins.modules.purefa_workload.get_array")
    @patch("plugins.modules.purefa_workload.AnsibleModule")
    @patch("plugins.modules.purefa_workload.HAS_PURESTORAGE", True)
    def test_main_state_absent_eradicate(self, mock_ansible_module, mock_get_array, mock_check_response, mock_loose_version, mock_eradicate_workload):
        """Test main() calls eradicate_workload when state=absent and eradicate=true"""
        from plugins.modules.purefa_workload import main

        mock_loose_version.side_effect = lambda x: float(x) if x else 0.0

        mock_module = Mock()
        mock_module.params = {
            "volume_count": None,
            "state": "absent",
            "preset": "test-preset",
            "context": "",
            "name": "test-workload",
            "host": "",
            "eradicate": True,
        }
        mock_ansible_module.return_value = mock_module
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.40"
        mock_fleet_response = Mock(status_code=200)
        mock_fleet = Mock()
        mock_fleet.name = "test-fleet"
        mock_fleet_response.items = [mock_fleet]
        mock_array.get_fleets.return_value = mock_fleet_response
        # Workload exists and is destroyed
        mock_workload = Mock()
        mock_workload.destroyed = True
        mock_array.get_workloads.return_value = Mock(status_code=200, items=[mock_workload])
        mock_get_array.return_value = mock_array

        main()

        mock_eradicate_workload.assert_called_once()

    @patch("plugins.modules.purefa_workload.LooseVersion")
    @patch("plugins.modules.purefa_workload.check_response")
    @patch("plugins.modules.purefa_workload.get_array")
    @patch("plugins.modules.purefa_workload.AnsibleModule")
    @patch("plugins.modules.purefa_workload.HAS_PURESTORAGE", True)
    def test_main_no_change(self, mock_ansible_module, mock_get_array, mock_check_response, mock_loose_version):
        """Test main() exits with no change when no action needed"""
        from plugins.modules.purefa_workload import main

        mock_loose_version.side_effect = lambda x: float(x) if x else 0.0

        mock_module = Mock()
        mock_module.params = {
            "volume_count": None,
            "state": "absent",
            "preset": "test-preset",
            "context": "",
            "name": "test-workload",
            "host": "",
            "eradicate": False,
        }
        mock_ansible_module.return_value = mock_module
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.40"
        mock_fleet_response = Mock(status_code=200)
        mock_fleet = Mock()
        mock_fleet.name = "test-fleet"
        mock_fleet_response.items = [mock_fleet]
        mock_array.get_fleets.return_value = mock_fleet_response
        # Workload does not exist - nothing to delete
        mock_array.get_workloads.return_value = Mock(status_code=404)
        mock_get_array.return_value = mock_array

        main()

        mock_module.exit_json.assert_called_once_with(changed=False)
