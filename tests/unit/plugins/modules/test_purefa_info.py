# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_info module."""

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

from plugins.modules.purefa_info import (
    main,
    _is_cbs,
    generate_perf_dict,
    generate_admin_dict,
    generate_subnet_dict,
    generate_interfaces_dict,
    generate_certs_dict,
    generate_kmip_dict,
)


class TestIsCbs:
    """Test cases for _is_cbs helper function"""

    def test_is_cbs_true(self):
        """Test _is_cbs returns True for CBS model"""
        mock_array = Mock()
        mock_hw_item = Mock()
        mock_hw_item.model = "CBS-S10"
        mock_hw_response = Mock()
        mock_hw_response.items = [mock_hw_item]
        mock_array.get_hardware.return_value = mock_hw_response

        result = _is_cbs(mock_array)

        assert result is True
        mock_array.get_hardware.assert_called_once_with(filter="type='controller'")

    def test_is_cbs_false(self):
        """Test _is_cbs returns False for non-CBS model"""
        mock_array = Mock()
        mock_hw_item = Mock()
        mock_hw_item.model = "FA-X70R3"
        mock_hw_response = Mock()
        mock_hw_response.items = [mock_hw_item]
        mock_array.get_hardware.return_value = mock_hw_response

        result = _is_cbs(mock_array)

        assert result is False


class TestGeneratePerfDict:
    """Test cases for generate_perf_dict function"""

    def test_generate_perf_dict_success(self):
        """Test performance dict generation"""
        mock_array = Mock()
        mock_perf_data = Mock()
        mock_perf_data.bytes_per_mirrored_write = 4096
        mock_perf_data.bytes_per_op = 8192
        mock_perf_data.bytes_per_read = 16384
        mock_perf_data.bytes_per_write = 8192
        mock_perf_data.mirrored_write_bytes_per_sec = 1000000
        mock_perf_data.mirrored_writes_per_sec = 100
        mock_perf_data.others_per_sec = 10
        mock_perf_data.qos_rate_limit_usec_per_mirrored_write_op = 0
        mock_perf_data.qos_rate_limit_usec_per_read_op = 0
        mock_perf_data.qos_rate_limit_usec_per_write_op = 0
        mock_perf_data.queue_usec_per_mirrored_write_op = 100
        mock_perf_data.queue_usec_per_read_op = 50
        mock_perf_data.queue_usec_per_write_op = 75
        mock_perf_data.read_bytes_per_sec = 5000000
        mock_perf_data.reads_per_sec = 500
        mock_perf_data.san_usec_per_mirrored_write_op = 200
        mock_perf_data.san_usec_per_read_op = 100
        mock_perf_data.san_usec_per_write_op = 150
        mock_perf_data.service_usec_per_mirrored_write_op = 300
        mock_perf_data.service_usec_per_read_op = 150
        mock_perf_data.service_usec_per_write_op = 200
        mock_perf_data.usec_per_mirrored_write_op = 500
        mock_perf_data.usec_per_other_op = 100
        mock_perf_data.usec_per_read_op = 250
        mock_perf_data.usec_per_write_op = 350
        mock_perf_data.write_bytes_per_sec = 3000000
        mock_perf_data.writes_per_sec = 300

        mock_perf_response = Mock()
        mock_perf_response.items = [mock_perf_data]
        mock_array.get_arrays_performance.return_value = mock_perf_response

        result = generate_perf_dict(mock_array)

        assert result["bytes_per_read"] == 16384
        assert result["reads_per_sec"] == 500
        assert result["writes_per_sec"] == 300
        # Legacy values should be 0
        assert result["input_per_sec"] == 0
        assert result["output_per_sec"] == 0
        assert result["queue_depth"] == 0


class TestGenerateAdminDict:
    """Test cases for generate_admin_dict function"""

    @patch("plugins.modules.purefa_info.LooseVersion")
    def test_generate_admin_dict_success(self, mock_loose_version):
        """Test admin dict generation"""
        mock_loose_version.side_effect = float
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        mock_admin = Mock()
        mock_admin.name = "pureuser"
        mock_admin.is_local = True
        mock_admin.locked = False
        mock_role = Mock()
        mock_role.name = "array_admin"
        mock_admin.role = mock_role
        # Mock management_access_policies as a list
        mock_policy = Mock()
        mock_policy.name = "default_policy"
        mock_admin.management_access_policies = [mock_policy]

        mock_admins_response = Mock()
        mock_admins_response.items = [mock_admin]
        mock_array.get_admins.return_value = mock_admins_response

        result = generate_admin_dict(mock_array)

        assert "pureuser" in result
        assert result["pureuser"]["type"] == "local"
        assert result["pureuser"]["locked"] is False
        assert result["pureuser"]["role"] == "array_admin"

    @patch("plugins.modules.purefa_info.LooseVersion")
    def test_generate_admin_dict_remote_user(self, mock_loose_version):
        """Test admin dict generation for remote user"""
        mock_loose_version.side_effect = float
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        mock_admin = Mock()
        mock_admin.name = "ldapuser@domain.com"
        mock_admin.is_local = False
        mock_admin.locked = False
        mock_role = Mock()
        mock_role.name = "readonly"
        mock_admin.role = mock_role

        mock_admins_response = Mock()
        mock_admins_response.items = [mock_admin]
        mock_array.get_admins.return_value = mock_admins_response

        result = generate_admin_dict(mock_array)

        assert "ldapuser@domain.com" in result
        assert result["ldapuser@domain.com"]["type"] == "remote"


class TestGenerateSubnetDict:
    """Test cases for generate_subnet_dict function"""

    def test_generate_subnet_dict_success(self):
        """Test subnet dict generation"""
        mock_array = Mock()

        mock_subnet = Mock()
        mock_subnet.name = "mgmt-subnet"
        mock_subnet.enabled = True
        mock_subnet.gateway = "10.0.0.1"
        mock_subnet.mtu = 1500
        mock_subnet.vlan = 100
        mock_subnet.prefix = "10.0.0.0/24"
        mock_subnet.services = ["management", "replication"]
        mock_iface = Mock()
        mock_iface.name = "ct0.eth0"
        mock_subnet.interfaces = [mock_iface]

        mock_subnets_response = Mock()
        mock_subnets_response.items = [mock_subnet]
        mock_array.get_subnets.return_value = mock_subnets_response

        result = generate_subnet_dict(mock_array)

        assert "mgmt-subnet" in result
        assert result["mgmt-subnet"]["enabled"] is True
        assert result["mgmt-subnet"]["gateway"] == "10.0.0.1"
        assert result["mgmt-subnet"]["mtu"] == 1500
        assert result["mgmt-subnet"]["vlan"] == 100
        assert "ct0.eth0" in result["mgmt-subnet"]["interfaces"]

    def test_generate_subnet_dict_no_interfaces(self):
        """Test subnet dict generation with no interfaces"""
        mock_array = Mock()

        mock_subnet = Mock()
        mock_subnet.name = "iscsi-subnet"
        mock_subnet.enabled = False
        mock_subnet.gateway = None
        mock_subnet.mtu = 9000
        mock_subnet.vlan = None
        mock_subnet.prefix = "192.168.1.0/24"
        mock_subnet.services = ["iscsi"]
        mock_subnet.interfaces = None

        mock_subnets_response = Mock()
        mock_subnets_response.items = [mock_subnet]
        mock_array.get_subnets.return_value = mock_subnets_response

        result = generate_subnet_dict(mock_array)

        assert "iscsi-subnet" in result
        assert result["iscsi-subnet"]["interfaces"] == []


class TestGenerateInterfacesDict:
    """Test cases for generate_interfaces_dict function"""

    def test_generate_interfaces_dict_success(self):
        """Test interfaces dict generation with FC port"""
        mock_array = Mock()

        # Generate_interfaces_dict uses get_ports() and checks for wwn attribute
        mock_port = Mock()
        mock_port.name = "CT0.FC0"
        mock_port.wwn = "50:00:00:00:00:00:00:01"
        mock_port.iqn = None
        mock_port.nqn = None
        mock_port.portal = None

        mock_ports_response = Mock()
        mock_ports_response.items = [mock_port]
        mock_array.get_ports.return_value = mock_ports_response

        result = generate_interfaces_dict(mock_array)

        assert "CT0.FC0" in result
        assert result["CT0.FC0"]["wwn"] == "50:00:00:00:00:00:00:01"
        assert result["CT0.FC0"]["iqn"] is None

    def test_generate_interfaces_dict_no_wwn(self):
        """Test interfaces dict skips ports without wwn"""
        mock_array = Mock()

        # Port without wwn attribute should be skipped
        mock_port = Mock(spec=["name"])  # No wwn attribute
        mock_port.name = "ct0.eth0"

        mock_ports_response = Mock()
        mock_ports_response.items = [mock_port]
        mock_array.get_ports.return_value = mock_ports_response

        result = generate_interfaces_dict(mock_array)

        # Port without wwn should not be included
        assert "ct0.eth0" not in result


class TestGenerateCertsDict:
    """Test cases for generate_certs_dict function"""

    def test_generate_certs_dict_success(self):
        """Test certificates dict generation"""
        mock_array = Mock()

        mock_cert = Mock()
        mock_cert.name = "management"
        mock_cert.status = "valid"
        mock_cert.valid_from = 1609459200000  # 2021-01-01
        mock_cert.valid_to = 1893456000000  # 2030-01-01
        mock_cert.issued_by = "CN=Pure Storage CA"
        mock_cert.issued_to = "CN=array1.example.com"
        mock_cert.key_size = 2048
        mock_cert_type = Mock()
        mock_cert_type.type = "external"
        mock_cert.certificate_type = mock_cert_type

        mock_certs_response = Mock()
        mock_certs_response.items = [mock_cert]
        mock_array.get_certificates.return_value = mock_certs_response

        result = generate_certs_dict(mock_array)

        assert "management" in result
        assert result["management"]["status"] == "valid"
        assert result["management"]["key_size"] == 2048


class TestGenerateKmipDict:
    """Test cases for generate_kmip_dict function"""

    def test_generate_kmip_dict_success(self):
        """Test KMIP dict generation"""
        mock_array = Mock()

        mock_kmip = Mock()
        mock_kmip.name = "kmip-server"
        mock_kmip.uri = "kmip://kmip.example.com:5696"

        mock_kmip_response = Mock()
        mock_kmip_response.items = [mock_kmip]
        mock_array.get_kmip().items = [mock_kmip]

        result = generate_kmip_dict(mock_array)

        assert "kmip-server" in result

    def test_generate_kmip_dict_empty(self):
        """Test KMIP dict generation with no KMIP servers"""
        mock_array = Mock()
        mock_kmip_response = Mock()
        mock_kmip_response.items = []
        mock_array.get_kmip.return_value = mock_kmip_response

        result = generate_kmip_dict(mock_array)

        assert result == {}


class TestMain:
    """Test cases for main function"""

    @patch("plugins.modules.purefa_info.get_array")
    @patch("plugins.modules.purefa_info.AnsibleModule")
    def test_main_invalid_subset(self, mock_ansible_module, mock_get_array):
        """Test main fails with invalid subset"""
        mock_module = Mock()
        mock_module.params = {
            "gather_subset": ["invalid_subset"],
        }
        mock_module.fail_json.side_effect = SystemExit("fail_json called")
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_get_array.return_value = mock_array

        try:
            main()
        except SystemExit:
            pass

        mock_module.fail_json.assert_called_once()
        call_args = mock_module.fail_json.call_args[1]
        assert "gather_subset" in call_args["msg"]

    @patch("plugins.modules.purefa_info.LooseVersion")
    @patch("plugins.modules.purefa_info.generate_default_dict")
    @patch("plugins.modules.purefa_info.get_array")
    @patch("plugins.modules.purefa_info.AnsibleModule")
    def test_main_minimum_subset(
        self, mock_ansible_module, mock_get_array, mock_gen_default, mock_loose_version
    ):
        """Test main with minimum subset"""
        mock_loose_version.side_effect = float
        mock_module = Mock()
        mock_module.params = {
            "gather_subset": ["minimum"],
        }
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_get_array.return_value = mock_array

        mock_gen_default.return_value = {"api_versions": "2.38"}

        main()

        mock_gen_default.assert_called_once_with(mock_array)
        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args[1]
        assert call_args["changed"] is False
        assert "purefa_info" in call_args
        assert "default" in call_args["purefa_info"]

    @patch("plugins.modules.purefa_info.LooseVersion")
    @patch("plugins.modules.purefa_info.generate_perf_dict")
    @patch("plugins.modules.purefa_info.get_array")
    @patch("plugins.modules.purefa_info.AnsibleModule")
    def test_main_performance_subset(
        self, mock_ansible_module, mock_get_array, mock_gen_perf, mock_loose_version
    ):
        """Test main with performance subset"""
        mock_loose_version.side_effect = float
        mock_module = Mock()
        mock_module.params = {
            "gather_subset": ["performance"],
        }
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_get_array.return_value = mock_array

        mock_gen_perf.return_value = {"reads_per_sec": 500}

        main()

        mock_gen_perf.assert_called_once_with(mock_array)
        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args[1]
        assert "performance" in call_args["purefa_info"]

    @patch("plugins.modules.purefa_info.LooseVersion")
    @patch("plugins.modules.purefa_info.generate_admin_dict")
    @patch("plugins.modules.purefa_info.get_array")
    @patch("plugins.modules.purefa_info.AnsibleModule")
    def test_main_admins_subset(
        self, mock_ansible_module, mock_get_array, mock_gen_admin, mock_loose_version
    ):
        """Test main with admins subset"""
        mock_loose_version.side_effect = float
        mock_module = Mock()
        mock_module.params = {
            "gather_subset": ["admins"],
        }
        mock_ansible_module.return_value = mock_module

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"
        mock_get_array.return_value = mock_array

        mock_gen_admin.return_value = {"pureuser": {"type": "local"}}

        main()

        mock_gen_admin.assert_called_once_with(mock_array)
        mock_module.exit_json.assert_called_once()
        call_args = mock_module.exit_json.call_args[1]
        assert "admins" in call_args["purefa_info"]
