# Copyright: (c) 2025, Simon Dodsley (@sdodsley)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_inventory module"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from unittest.mock import MagicMock, Mock, patch

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

# Import after mocking
from plugins.modules.purefa_inventory import main, generate_new_hardware_dict


class TestInventoryMain:
    """Test cases for inventory main function"""

    @patch("plugins.modules.purefa_inventory.generate_new_hardware_dict")
    @patch("plugins.modules.purefa_inventory.get_array")
    @patch("plugins.modules.purefa_inventory.AnsibleModule")
    def test_main_returns_inventory(
        self, mock_ansible_module, mock_get_array, mock_generate
    ):
        """Test main function returns inventory info"""
        mock_module = Mock()
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_get_array.return_value = mock_array

        mock_generate.return_value = {
            "fans": {},
            "controllers": {},
            "drives": {},
            "interfaces": {},
            "power": {},
            "chassis": {},
            "temperature": {},
        }

        main()

        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args
        assert call_args[1]["changed"] is False
        assert "purefa_inv" in call_args[1]


class TestGenerateHardwareDict:
    """Test cases for generate_new_hardware_dict function"""

    @patch("plugins.modules.purefa_inventory.LooseVersion")
    def test_generates_basic_hardware_dict(self, mock_lv):
        """Test generating hardware dict with basic components"""
        mock_array = Mock()

        # Mock old API version (skip SFP details)
        mock_array.get_rest_version.return_value = "2.10"
        mock_lv.side_effect = float

        # Mock hardware components
        mock_chassis = Mock()
        mock_chassis.name = "CH0"
        mock_chassis.type = "chassis"
        mock_chassis.status = "ok"
        mock_chassis.serial = "PCHFL12345"
        mock_chassis.model = "FA-X70"
        mock_chassis.identify_enabled = False

        mock_controller = Mock()
        mock_controller.name = "CT0"
        mock_controller.type = "controller"
        mock_controller.status = "ok"
        mock_controller.serial = "PCTRL001"
        mock_controller.model = "FA-X70-CT0"
        mock_controller.identify_enabled = False

        mock_fan = Mock()
        mock_fan.name = "FAN0"
        mock_fan.type = "cooling"
        mock_fan.status = "ok"

        mock_hardware_response = Mock()
        mock_hardware_response.items = [mock_chassis, mock_controller, mock_fan]
        mock_array.get_hardware.return_value = mock_hardware_response

        # Mock drives
        mock_drive = Mock()
        mock_drive.name = "CH0.BAY0"
        mock_drive.capacity = 1000000000
        mock_drive.status = "healthy"
        mock_drive.type = "SSD"
        mock_drives_response = Mock()
        mock_drives_response.items = [mock_drive]
        mock_array.get_drives.return_value = mock_drives_response

        result = generate_new_hardware_dict(mock_array)

        assert "chassis" in result
        assert "CH0" in result["chassis"]
        assert result["chassis"]["CH0"]["status"] == "ok"
        assert "controllers" in result
        assert "CT0" in result["controllers"]
        assert "fans" in result
        assert "FAN0" in result["fans"]
        assert "drives" in result
        assert "CH0.BAY0" in result["drives"]

    @patch("plugins.modules.purefa_inventory.LooseVersion")
    def test_handles_empty_hardware(self, mock_lv):
        """Test handling of empty hardware list"""
        mock_array = Mock()

        mock_array.get_rest_version.return_value = "2.10"
        mock_lv.side_effect = float

        mock_hardware_response = Mock()
        mock_hardware_response.items = []
        mock_array.get_hardware.return_value = mock_hardware_response

        mock_drives_response = Mock()
        mock_drives_response.items = []
        mock_array.get_drives.return_value = mock_drives_response

        result = generate_new_hardware_dict(mock_array)

        assert result["chassis"] == {}
        assert result["controllers"] == {}
        assert result["fans"] == {}
        assert result["drives"] == {}
        assert result["interfaces"] == {}
        assert result["power"] == {}
