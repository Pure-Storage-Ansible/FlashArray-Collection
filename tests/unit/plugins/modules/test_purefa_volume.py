# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_volume module."""

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

from plugins.modules.purefa_volume import (
    main,
    get_volume,
    get_destroyed_volume,
    get_target,
    create_volume,
    create_multi_volume,
    update_volume,
    delete_volume,
    eradicate_volume,
    recover_volume,
    copy_from_volume,
    rename_volume,
    _create_nguid,
)


class TestCreateNguid:
    """Test cases for _create_nguid helper function"""

    def test_create_nguid_valid_serial(self):
        """Test NGUID creation from valid serial"""
        serial = "361019ecace43d83000120a4"
        result = _create_nguid(serial)
        assert result.startswith("eui.00")
        assert "24a937" in result

    def test_create_nguid_format(self):
        """Test NGUID format is correct"""
        serial = "abcdef12345678901234"
        result = _create_nguid(serial)
        # Should be: eui.00 + first 14 chars + 24a937 + last 10 chars
        # serial[0:14] = "abcdef12345678"
        # serial[-10:] = "5678901234"
        assert result == "eui.00abcdef1234567824a9375678901234"


class TestGetVolume:
    """Test cases for get_volume function"""

    @patch("plugins.modules.purefa_volume.LooseVersion")
    def test_get_volume_exists(self, mock_loose_version):
        """Test get_volume returns volume when it exists"""
        mock_loose_version.side_effect = float
        mock_module = Mock()
        mock_module.params = {"name": "test_volume", "context": "array1"}

        mock_volume = Mock()
        mock_volume.name = "test_volume"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.items = [mock_volume]

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_volumes.return_value = mock_response

        result = get_volume(mock_module, mock_array)

        assert result == mock_volume
        mock_array.get_volumes.assert_called_once()

    @patch("plugins.modules.purefa_volume.LooseVersion")
    def test_get_volume_not_exists(self, mock_loose_version):
        """Test get_volume returns None when volume doesn't exist"""
        mock_loose_version.side_effect = float
        mock_module = Mock()
        mock_module.params = {"name": "nonexistent_volume", "context": "array1"}

        mock_response = Mock()
        mock_response.status_code = 400

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_volumes.return_value = mock_response

        result = get_volume(mock_module, mock_array)

        assert result is None


class TestGetDestroyedVolume:
    """Test cases for get_destroyed_volume function"""

    @patch("plugins.modules.purefa_volume.LooseVersion")
    def test_get_destroyed_volume_exists(self, mock_loose_version):
        """Test get_destroyed_volume returns destroyed volume"""
        mock_loose_version.side_effect = float
        mock_module = Mock()
        mock_module.params = {"name": "deleted_volume", "context": "array1"}

        mock_volume = Mock()
        mock_volume.destroyed = True
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.items = [mock_volume]

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_volumes.return_value = mock_response

        result = get_destroyed_volume(mock_module, mock_array)

        assert result == mock_volume
        mock_array.get_volumes.assert_called_once()


class TestGetTarget:
    """Test cases for get_target function"""

    @patch("plugins.modules.purefa_volume.LooseVersion")
    def test_get_target_exists(self, mock_loose_version):
        """Test get_target returns target volume"""
        mock_loose_version.side_effect = float
        mock_module = Mock()
        mock_module.params = {"target": "target_volume", "context": "array1"}

        mock_volume = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.items = [mock_volume]

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_volumes.return_value = mock_response

        result = get_target(mock_module, mock_array)

        assert result == mock_volume


class TestCreateVolume:
    """Test cases for create_volume function"""

    @patch("plugins.modules.purefa_volume._volfact")
    @patch("plugins.modules.purefa_volume.check_response")
    @patch("plugins.modules.purefa_volume.human_to_bytes")
    @patch("plugins.modules.purefa_volume.check_vgroup")
    @patch("plugins.modules.purefa_volume.check_pod")
    @patch("plugins.modules.purefa_volume.LooseVersion")
    @patch("plugins.modules.purefa_volume.VolumePost")
    def test_create_volume_basic(
        self,
        mock_volume_post,
        mock_loose_version,
        mock_check_pod,
        mock_check_vgroup,
        mock_human_to_bytes,
        mock_check_response,
        mock_volfact,
    ):
        """Test basic volume creation without QoS"""
        mock_loose_version.side_effect = float
        mock_human_to_bytes.return_value = 1073741824  # 1GB
        mock_check_vgroup.return_value = True
        mock_check_pod.return_value = True
        mock_volfact.return_value = {"test_volume": {"size": 1073741824}}

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test_volume",
            "size": "1G",
            "bw_qos": None,
            "iops_qos": None,
            "add_to_pgs": None,
            "promotion_state": None,
            "priority_operator": None,
            "pgroup": None,
            "context": "array1",
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.post_volumes.return_value = mock_response

        create_volume(mock_module, mock_array)

        mock_array.post_volumes.assert_called_once()
        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args[1]
        assert call_args["changed"] is True

    @patch("plugins.modules.purefa_volume.LooseVersion")
    def test_create_volume_missing_size(self, mock_loose_version):
        """Test volume creation fails without size"""
        mock_loose_version.side_effect = float

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test_volume",
            "size": None,
            "bw_qos": None,
            "iops_qos": None,
            "add_to_pgs": None,
            "context": "array1",
        }
        mock_module.fail_json.side_effect = SystemExit("fail_json called")

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        try:
            create_volume(mock_module, mock_array)
        except SystemExit:
            pass

        mock_module.fail_json.assert_called_once()
        call_args = mock_module.fail_json.call_args[1]
        assert "Size for a new volume must be specified" in call_args["msg"]

    @patch("plugins.modules.purefa_volume._volfact")
    @patch("plugins.modules.purefa_volume.check_response")
    @patch("plugins.modules.purefa_volume.human_to_bytes")
    @patch("plugins.modules.purefa_volume.LooseVersion")
    @patch("plugins.modules.purefa_volume.VolumePost")
    @patch("plugins.modules.purefa_volume.Qos")
    def test_create_volume_check_mode(
        self,
        mock_qos,
        mock_volume_post,
        mock_loose_version,
        mock_human_to_bytes,
        mock_check_response,
        mock_volfact,
    ):
        """Test volume creation in check mode"""
        mock_loose_version.side_effect = float
        mock_human_to_bytes.return_value = 1073741824
        mock_volfact.return_value = {}

        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test_volume",
            "size": "1G",
            "bw_qos": None,
            "iops_qos": None,
            "add_to_pgs": None,
            "promotion_state": None,
            "priority_operator": None,
            "pgroup": None,
            "context": "array1",
        }

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        create_volume(mock_module, mock_array)

        # In check mode, post_volumes should NOT be called
        mock_array.post_volumes.assert_not_called()
        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args[1]
        assert call_args["changed"] is True


class TestUpdateVolume:
    """Test cases for update_volume function"""

    @patch("plugins.modules.purefa_volume._volfact")
    @patch("plugins.modules.purefa_volume.check_response")
    @patch("plugins.modules.purefa_volume.human_to_bytes")
    @patch("plugins.modules.purefa_volume.LooseVersion")
    @patch("plugins.modules.purefa_volume.VolumePatch")
    def test_update_volume_size_increase(
        self,
        mock_volume_patch,
        mock_loose_version,
        mock_human_to_bytes,
        mock_check_response,
        mock_volfact,
    ):
        """Test volume size increase"""
        mock_loose_version.side_effect = float
        mock_human_to_bytes.return_value = 2147483648  # 2GB
        mock_volfact.return_value = {"test_volume": {"size": 2147483648}}

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test_volume",
            "size": "2G",
            "bw_qos": None,
            "iops_qos": None,
            "add_to_pgs": None,
            "pgroup": None,
            "promotion_state": None,
            "priority_operator": None,
            "context": "array1",
        }

        # Mock existing volume with 1GB
        mock_vol = Mock()
        mock_vol.provisioned = 1073741824  # 1GB
        mock_qos = Mock(spec=[])
        mock_vol.qos = mock_qos

        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.items = [mock_vol]

        mock_patch_response = Mock()
        mock_patch_response.status_code = 200

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_volumes.return_value = mock_get_response
        mock_array.patch_volumes.return_value = mock_patch_response

        update_volume(mock_module, mock_array)

        mock_array.patch_volumes.assert_called_once()
        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args[1]
        assert call_args["changed"] is True


class TestDeleteVolume:
    """Test cases for delete_volume function"""

    @patch("plugins.modules.purefa_volume._volfact")
    @patch("plugins.modules.purefa_volume.check_response")
    @patch("plugins.modules.purefa_volume.LooseVersion")
    @patch("plugins.modules.purefa_volume.VolumePatch")
    def test_delete_volume_success(
        self,
        mock_volume_patch,
        mock_loose_version,
        mock_check_response,
        mock_volfact,
    ):
        """Test successful volume deletion"""
        mock_loose_version.side_effect = float
        mock_volfact.return_value = {"test_volume": {"destroyed": True}}

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test_volume",
            "add_to_pgs": None,
            "eradicate": False,
            "context": "array1",
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.patch_volumes.return_value = mock_response

        delete_volume(mock_module, mock_array)

        mock_array.patch_volumes.assert_called_once()
        mock_module.exit_json.assert_called_once()

    @patch("plugins.modules.purefa_volume._volfact")
    @patch("plugins.modules.purefa_volume.LooseVersion")
    @patch("plugins.modules.purefa_volume.VolumePatch")
    def test_delete_volume_check_mode(
        self,
        mock_volume_patch,
        mock_loose_version,
        mock_volfact,
    ):
        """Test volume deletion in check mode"""
        mock_loose_version.side_effect = float
        mock_volfact.return_value = {}

        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test_volume",
            "add_to_pgs": None,
            "eradicate": False,
            "context": "array1",
        }

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        delete_volume(mock_module, mock_array)

        # In check mode, patch_volumes should NOT be called
        mock_array.patch_volumes.assert_not_called()
        mock_module.exit_json.assert_called_once()


class TestEradicateVolume:
    """Test cases for eradicate_volume function"""

    @patch("plugins.modules.purefa_volume._volfact")
    @patch("plugins.modules.purefa_volume.check_response")
    @patch("plugins.modules.purefa_volume.LooseVersion")
    def test_eradicate_volume_success(
        self,
        mock_loose_version,
        mock_check_response,
        mock_volfact,
    ):
        """Test successful volume eradication"""
        mock_loose_version.side_effect = float
        mock_volfact.return_value = []

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test_volume",
            "eradicate": True,
            "context": "array1",
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.delete_volumes.return_value = mock_response

        eradicate_volume(mock_module, mock_array)

        mock_array.delete_volumes.assert_called_once()
        mock_module.exit_json.assert_called_once()

    @patch("plugins.modules.purefa_volume._volfact")
    @patch("plugins.modules.purefa_volume.LooseVersion")
    def test_eradicate_volume_no_eradicate_flag(
        self,
        mock_loose_version,
        mock_volfact,
    ):
        """Test eradicate_volume when eradicate flag is False"""
        mock_loose_version.side_effect = float
        mock_volfact.return_value = {"test_volume": {"destroyed": True}}

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test_volume",
            "eradicate": False,
            "context": "array1",
        }

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        eradicate_volume(mock_module, mock_array)

        # Should not call delete_volumes when eradicate is False
        mock_array.delete_volumes.assert_not_called()
        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args[1]
        assert call_args["changed"] is False


class TestRecoverVolume:
    """Test cases for recover_volume function"""

    @patch("plugins.modules.purefa_volume._volfact")
    @patch("plugins.modules.purefa_volume.check_response")
    @patch("plugins.modules.purefa_volume.LooseVersion")
    @patch("plugins.modules.purefa_volume.VolumePatch")
    def test_recover_volume_success(
        self,
        mock_volume_patch,
        mock_loose_version,
        mock_check_response,
        mock_volfact,
    ):
        """Test successful volume recovery"""
        mock_loose_version.side_effect = float
        mock_volfact.return_value = {"test_volume": {"destroyed": False}}

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "test_volume",
            "context": "array1",
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.patch_volumes.return_value = mock_response

        recover_volume(mock_module, mock_array)

        mock_array.patch_volumes.assert_called_once()
        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args[1]
        assert call_args["changed"] is True

    @patch("plugins.modules.purefa_volume._volfact")
    @patch("plugins.modules.purefa_volume.LooseVersion")
    @patch("plugins.modules.purefa_volume.VolumePatch")
    def test_recover_volume_check_mode(
        self,
        mock_volume_patch,
        mock_loose_version,
        mock_volfact,
    ):
        """Test volume recovery in check mode"""
        mock_loose_version.side_effect = float
        mock_volfact.return_value = {}

        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test_volume",
            "context": "array1",
        }

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        recover_volume(mock_module, mock_array)

        # In check mode, patch_volumes should NOT be called
        mock_array.patch_volumes.assert_not_called()
        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args[1]
        assert call_args["changed"] is True


class TestCopyFromVolume:
    """Test cases for copy_from_volume function"""

    @patch("plugins.modules.purefa_volume._volfact")
    @patch("plugins.modules.purefa_volume.check_response")
    @patch("plugins.modules.purefa_volume.get_target")
    @patch("plugins.modules.purefa_volume.LooseVersion")
    @patch("plugins.modules.purefa_volume.VolumePost")
    @patch("plugins.modules.purefa_volume.Reference")
    def test_copy_volume_success(
        self,
        mock_reference,
        mock_volume_post,
        mock_loose_version,
        mock_get_target,
        mock_check_response,
        mock_volfact,
    ):
        """Test successful volume copy"""
        mock_loose_version.side_effect = float
        mock_get_target.return_value = None  # Target doesn't exist
        mock_volfact.return_value = {"target_volume": {"size": 1073741824}}

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "source_volume",
            "target": "target_volume",
            "overwrite": False,
            "add_to_pgs": None,
            "with_default_protection": True,
            "context": "array1",
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.post_volumes.return_value = mock_response

        copy_from_volume(mock_module, mock_array)

        mock_array.post_volumes.assert_called_once()
        mock_module.exit_json.assert_called_once()


class TestRenameVolume:
    """Test cases for rename_volume function"""

    @patch("plugins.modules.purefa_volume._volfact")
    @patch("plugins.modules.purefa_volume.check_response")
    @patch("plugins.modules.purefa_volume.LooseVersion")
    @patch("plugins.modules.purefa_volume.VolumePatch")
    def test_rename_volume_success(
        self,
        mock_volume_patch,
        mock_loose_version,
        mock_check_response,
        mock_volfact,
    ):
        """Test successful volume rename"""
        mock_loose_version.side_effect = float
        mock_volfact.return_value = {"new_volume": {"size": 1073741824}}

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "old_volume",
            "rename": "new_volume",
            "context": "array1",
        }

        # Mock target doesn't exist check
        mock_get_response = Mock()
        mock_get_response.status_code = 400
        mock_patch_response = Mock()
        mock_patch_response.status_code = 200

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_volumes.return_value = mock_get_response
        mock_array.patch_volumes.return_value = mock_patch_response

        rename_volume(mock_module, mock_array)

        mock_array.patch_volumes.assert_called_once()
        mock_module.exit_json.assert_called_once()

    @patch("plugins.modules.purefa_volume.LooseVersion")
    def test_rename_volume_target_exists(self, mock_loose_version):
        """Test rename fails when target exists"""
        mock_loose_version.side_effect = float

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "old_volume",
            "rename": "existing_volume",
            "context": "array1",
        }
        mock_module.fail_json.side_effect = SystemExit("fail_json called")

        mock_response = Mock()
        mock_response.status_code = 200  # Target exists

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array.get_volumes.return_value = mock_response

        try:
            rename_volume(mock_module, mock_array)
        except SystemExit:
            pass

        mock_module.fail_json.assert_called_once()
        call_args = mock_module.fail_json.call_args[1]
        assert "already exists" in call_args["msg"]


class TestMain:
    """Test cases for main function"""

    @patch("plugins.modules.purefa_volume.get_array")
    @patch("plugins.modules.purefa_volume.AnsibleModule")
    @patch("plugins.modules.purefa_volume.HAS_PURESTORAGE", False)
    def test_main_missing_sdk(self, mock_ansible_module, mock_get_array):
        """Test main when pypureclient SDK is missing"""
        mock_module = Mock()
        mock_module.params = {
            "name": "test_volume",
            "state": "present",
            "size": "1G",
            "target": None,
            "move": None,
            "rename": None,
            "eradicate": False,
            "bw_qos": None,
            "iops_qos": None,
            "pgroup": None,
            "count": None,
            "context": "",
        }
        mock_module.fail_json.side_effect = SystemExit("fail_json called")
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_get_array.return_value = mock_array

        # Mock get_volume and get_endpoint
        with patch("plugins.modules.purefa_volume.get_volume") as mock_get_vol:
            with patch("plugins.modules.purefa_volume.get_endpoint") as mock_get_ep:
                mock_get_vol.return_value = None
                mock_get_ep.return_value = None

                try:
                    main()
                except SystemExit:
                    pass

        mock_module.fail_json.assert_called_once()
        call_args = mock_module.fail_json.call_args[1]
        assert "py-pure-client sdk is required" in call_args["msg"]

    @patch("plugins.modules.purefa_volume.get_endpoint")
    @patch("plugins.modules.purefa_volume.get_volume")
    @patch("plugins.modules.purefa_volume.LooseVersion")
    @patch("plugins.modules.purefa_volume.get_array")
    @patch("plugins.modules.purefa_volume.AnsibleModule")
    @patch("plugins.modules.purefa_volume.HAS_PURESTORAGE", True)
    def test_main_volume_is_endpoint(
        self,
        mock_ansible_module,
        mock_get_array,
        mock_loose_version,
        mock_get_volume,
        mock_get_endpoint,
    ):
        """Test main fails when volume is a protocol endpoint"""
        mock_loose_version.side_effect = float
        mock_module = Mock()
        mock_module.params = {
            "name": "endpoint_volume",
            "state": "present",
            "size": "1G",
            "target": None,
            "move": None,
            "rename": None,
            "eradicate": False,
            "bw_qos": None,
            "iops_qos": None,
            "pgroup": None,
            "count": None,
            "context": "",
        }
        mock_module.fail_json.side_effect = SystemExit("fail_json called")
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array_item = Mock()
        mock_array_item.name = "array1"
        mock_arrays_response = Mock()
        mock_arrays_response.items = [mock_array_item]
        mock_array.get_arrays.return_value = mock_arrays_response
        mock_get_array.return_value = mock_array

        mock_get_volume.return_value = None
        mock_endpoint = Mock()
        mock_endpoint.subtype = "protocol_endpoint"
        mock_get_endpoint.return_value = mock_endpoint

        try:
            main()
        except SystemExit:
            pass

        mock_module.fail_json.assert_called_once()
        call_args = mock_module.fail_json.call_args[1]
        assert "is an endpoint" in call_args["msg"]

    @patch("plugins.modules.purefa_volume.human_to_bytes")
    @patch("plugins.modules.purefa_volume.get_endpoint")
    @patch("plugins.modules.purefa_volume.get_volume")
    @patch("plugins.modules.purefa_volume.LooseVersion")
    @patch("plugins.modules.purefa_volume.get_array")
    @patch("plugins.modules.purefa_volume.AnsibleModule")
    @patch("plugins.modules.purefa_volume.HAS_PURESTORAGE", True)
    def test_main_bw_qos_out_of_range(
        self,
        mock_ansible_module,
        mock_get_array,
        mock_loose_version,
        mock_get_volume,
        mock_get_endpoint,
        mock_human_to_bytes,
    ):
        """Test main fails when bandwidth QoS is out of range"""
        mock_loose_version.side_effect = float
        mock_human_to_bytes.return_value = 100  # Too low

        mock_module = Mock()
        mock_module.params = {
            "name": "test_volume",
            "state": "present",
            "size": "1G",
            "target": None,
            "move": None,
            "rename": None,
            "eradicate": False,
            "bw_qos": "100B",  # Too low
            "iops_qos": None,
            "pgroup": None,
            "count": None,
            "context": "",
        }
        mock_module.fail_json.side_effect = SystemExit("fail_json called")
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array_item = Mock()
        mock_array_item.name = "array1"
        mock_arrays_response = Mock()
        mock_arrays_response.items = [mock_array_item]
        mock_array.get_arrays.return_value = mock_arrays_response
        mock_get_array.return_value = mock_array

        mock_get_volume.return_value = None
        mock_get_endpoint.return_value = None

        try:
            main()
        except SystemExit:
            pass

        mock_module.fail_json.assert_called_once()
        call_args = mock_module.fail_json.call_args[1]
        assert "Bandwidth QoS value out of range" in call_args["msg"]

    @patch("plugins.modules.purefa_volume.human_to_real")
    @patch("plugins.modules.purefa_volume.human_to_bytes")
    @patch("plugins.modules.purefa_volume.get_endpoint")
    @patch("plugins.modules.purefa_volume.get_volume")
    @patch("plugins.modules.purefa_volume.LooseVersion")
    @patch("plugins.modules.purefa_volume.get_array")
    @patch("plugins.modules.purefa_volume.AnsibleModule")
    @patch("plugins.modules.purefa_volume.HAS_PURESTORAGE", True)
    def test_main_iops_qos_out_of_range(
        self,
        mock_ansible_module,
        mock_get_array,
        mock_loose_version,
        mock_get_volume,
        mock_get_endpoint,
        mock_human_to_bytes,
        mock_human_to_real,
    ):
        """Test main fails when IOPs QoS is out of range"""
        mock_loose_version.side_effect = float
        mock_human_to_bytes.return_value = 0
        mock_human_to_real.return_value = 10  # Too low (min is 100)

        mock_module = Mock()
        mock_module.params = {
            "name": "test_volume",
            "state": "present",
            "size": "1G",
            "target": None,
            "move": None,
            "rename": None,
            "eradicate": False,
            "bw_qos": None,
            "iops_qos": "10",  # Too low
            "pgroup": None,
            "count": None,
            "context": "",
        }
        mock_module.fail_json.side_effect = SystemExit("fail_json called")
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array_item = Mock()
        mock_array_item.name = "array1"
        mock_arrays_response = Mock()
        mock_arrays_response.items = [mock_array_item]
        mock_array.get_arrays.return_value = mock_arrays_response
        mock_get_array.return_value = mock_array

        mock_get_volume.return_value = None
        mock_get_endpoint.return_value = None

        try:
            main()
        except SystemExit:
            pass

        mock_module.fail_json.assert_called_once()
        call_args = mock_module.fail_json.call_args[1]
        assert "IOPs QoS value out of range" in call_args["msg"]


class TestCreateMultiVolume:
    """Test cases for create_multi_volume function"""

    @patch("plugins.modules.purefa_volume.check_response")
    @patch("plugins.modules.purefa_volume.human_to_bytes")
    @patch("plugins.modules.purefa_volume.check_vgroup")
    @patch("plugins.modules.purefa_volume.check_pod")
    @patch("plugins.modules.purefa_volume.LooseVersion")
    @patch("plugins.modules.purefa_volume.VolumePost")
    def test_create_multi_volume_basic(
        self,
        mock_volume_post,
        mock_loose_version,
        mock_check_pod,
        mock_check_vgroup,
        mock_human_to_bytes,
        mock_check_response,
    ):
        """Test basic multi-volume creation with count, start, digits, suffix"""
        mock_loose_version.side_effect = float
        mock_human_to_bytes.return_value = 1073741824  # 1GB
        mock_check_vgroup.return_value = True
        mock_check_pod.return_value = True

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "vol",
            "size": "1G",
            "count": 5,
            "start": 0,
            "digits": 2,
            "suffix": "",
            "bw_qos": None,
            "iops_qos": None,
            "pgroup": None,
            "add_to_pgs": None,
            "promotion_state": None,
            "priority_operator": None,
            "priority_value": None,
            "with_default_protection": True,
            "context": "",
        }

        mock_vol_post = Mock()
        mock_volume_post.return_value = mock_vol_post

        # Create mock volume items for the response
        mock_vol_items = []
        for i in range(5):
            mock_item = Mock()
            mock_item.name = f"vol0{i}"
            mock_item.provisioned = 1073741824
            mock_item.serial = f"SERIAL000{i}"
            mock_item.created = 1700000000000
            mock_vol_items.append(mock_item)

        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.items = mock_vol_items

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array_item = Mock()
        mock_array_item.name = "array1"
        mock_arrays_response = Mock()
        mock_arrays_response.items = [mock_array_item]
        mock_array.get_arrays.return_value = mock_arrays_response
        mock_array.post_volumes.return_value = mock_post_response

        create_multi_volume(mock_module, mock_array)

        # Verify post_volumes was called with correct names
        mock_array.post_volumes.assert_called_once()
        call_kwargs = mock_array.post_volumes.call_args[1]
        # Volume names should be vol00, vol01, vol02, vol03, vol04
        expected_names = ["vol00", "vol01", "vol02", "vol03", "vol04"]
        assert call_kwargs["names"] == expected_names
        mock_module.exit_json.assert_called_once()

    @patch("plugins.modules.purefa_volume.check_response")
    @patch("plugins.modules.purefa_volume.human_to_bytes")
    @patch("plugins.modules.purefa_volume.check_vgroup")
    @patch("plugins.modules.purefa_volume.check_pod")
    @patch("plugins.modules.purefa_volume.LooseVersion")
    @patch("plugins.modules.purefa_volume.VolumePost")
    def test_create_multi_volume_with_suffix(
        self,
        mock_volume_post,
        mock_loose_version,
        mock_check_pod,
        mock_check_vgroup,
        mock_human_to_bytes,
        mock_check_response,
    ):
        """Test multi-volume creation with custom suffix and start"""
        mock_loose_version.side_effect = float
        mock_human_to_bytes.return_value = 2147483648  # 2GB
        mock_check_vgroup.return_value = True
        mock_check_pod.return_value = True

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "data",
            "size": "2G",
            "count": 3,
            "start": 10,
            "digits": 3,
            "suffix": "_disk",
            "bw_qos": None,
            "iops_qos": None,
            "pgroup": None,
            "add_to_pgs": None,
            "promotion_state": None,
            "priority_operator": None,
            "priority_value": None,
            "with_default_protection": True,
            "context": "",
        }

        mock_vol_post = Mock()
        mock_volume_post.return_value = mock_vol_post

        # Create mock volume items for the response
        mock_vol_items = []
        for i, name in enumerate(["data010_disk", "data011_disk", "data012_disk"]):
            mock_item = Mock()
            mock_item.name = name
            mock_item.provisioned = 2147483648
            mock_item.serial = f"SERIAL001{i}"
            mock_item.created = 1700000000000
            mock_vol_items.append(mock_item)

        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.items = mock_vol_items

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_array_item = Mock()
        mock_array_item.name = "array1"
        mock_arrays_response = Mock()
        mock_arrays_response.items = [mock_array_item]
        mock_array.get_arrays.return_value = mock_arrays_response
        mock_array.post_volumes.return_value = mock_post_response

        create_multi_volume(mock_module, mock_array)

        # Verify post_volumes was called with correct names
        mock_array.post_volumes.assert_called_once()
        call_kwargs = mock_array.post_volumes.call_args[1]
        # Volume names should be data010_disk, data011_disk, data012_disk
        expected_names = ["data010_disk", "data011_disk", "data012_disk"]
        assert call_kwargs["names"] == expected_names
        mock_module.exit_json.assert_called_once()

    @patch("plugins.modules.purefa_volume.check_response")
    @patch("plugins.modules.purefa_volume.human_to_bytes")
    @patch("plugins.modules.purefa_volume.check_vgroup")
    @patch("plugins.modules.purefa_volume.check_pod")
    @patch("plugins.modules.purefa_volume.LooseVersion")
    @patch("plugins.modules.purefa_volume.VolumePost")
    def test_create_multi_volume_check_mode(
        self,
        mock_volume_post,
        mock_loose_version,
        mock_check_pod,
        mock_check_vgroup,
        mock_human_to_bytes,
        mock_check_response,
    ):
        """Test multi-volume creation in check mode"""
        mock_loose_version.side_effect = float
        mock_human_to_bytes.return_value = 1073741824
        mock_check_vgroup.return_value = True
        mock_check_pod.return_value = True

        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "vol",
            "size": "1G",
            "count": 3,
            "start": 0,
            "digits": 1,
            "suffix": "",
            "bw_qos": None,
            "iops_qos": None,
            "pgroup": None,
            "add_to_pgs": None,
            "promotion_state": None,
            "with_default_protection": True,
            "context": "",
        }

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        create_multi_volume(mock_module, mock_array)

        # In check mode, post_volumes should NOT be called
        mock_array.post_volumes.assert_not_called()
        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args[1]
        assert call_args["changed"] is True

    @patch("plugins.modules.purefa_volume.check_vgroup")
    def test_create_multi_volume_vgroup_not_exists(self, mock_check_vgroup):
        """Test multi-volume creation fails when volume group doesn't exist"""
        mock_check_vgroup.return_value = False

        mock_module = Mock()
        mock_module.check_mode = False
        mock_module.params = {
            "name": "vgroup/vol",
            "size": "1G",
            "count": 5,
            "start": 0,
            "digits": 1,
            "suffix": "",
            "bw_qos": None,
            "iops_qos": None,
            "pgroup": None,
        }
        mock_module.fail_json.side_effect = SystemExit("fail_json called")

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        try:
            create_multi_volume(mock_module, mock_array)
        except SystemExit:
            pass

        mock_module.fail_json.assert_called_once()
        call_args = mock_module.fail_json.call_args[1]
        assert "Volume Group" in call_args["msg"]
        assert "does not exist" in call_args["msg"]
