# Copyright: (c) 2026, Pure Storage Ansible Team <pure-ansible-team@purestorage.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for purefa_endpoint module."""

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

from plugins.modules.purefa_endpoint import (
    get_volume,
    delete_endpoint,
    eradicate_endpoint,
    recover_endpoint,
    rename_endpoint,
    _volfact,
)


class TestGetVolume:
    """Test cases for get_volume function"""

    @patch("plugins.modules.purefa_endpoint.LooseVersion")
    def test_get_volume_exists(self, mock_loose_version):
        """Test get_volume returns volume when it exists"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_vol = Mock()
        mock_vol.name = "vol1"
        mock_array.get_volumes.return_value = Mock(status_code=200, items=[mock_vol])

        result = get_volume(mock_module, "vol1", mock_array)

        assert result == mock_vol

    @patch("plugins.modules.purefa_endpoint.LooseVersion")
    def test_get_volume_not_exists(self, mock_loose_version):
        """Test get_volume returns None when volume doesn't exist"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.params = {"context": ""}
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        mock_array.get_volumes.return_value = Mock(status_code=404)

        result = get_volume(mock_module, "nonexistent", mock_array)

        assert result is None


class TestDeleteEndpoint:
    """Test cases for delete_endpoint function"""

    def test_delete_endpoint_check_mode(self):
        """Test delete_endpoint in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-endpoint",
            "eradicate": False,
            "hgroup": None,
            "host": None,
            "pgroup": None,
        }
        mock_array = Mock()

        delete_endpoint(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True, volume={})


class TestEradicateEndpoint:
    """Test cases for eradicate_endpoint function"""

    def test_eradicate_endpoint_check_mode(self):
        """Test eradicate_endpoint in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "deleted-endpoint"}
        mock_array = Mock()

        eradicate_endpoint(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True, volume=[])


class TestRecoverEndpoint:
    """Test cases for recover_endpoint function"""

    def test_recover_endpoint_check_mode(self):
        """Test recover_endpoint in check mode"""
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {"name": "deleted-endpoint", "pgroup": None}
        mock_array = Mock()

        recover_endpoint(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True, volume={})


class TestVolfact:
    """Test cases for _volfact function"""

    @patch("plugins.modules.purefa_endpoint.LooseVersion")
    def test_volfact_check_mode_returns_empty(self, mock_loose_version):
        """Test _volfact returns empty dict in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_array = Mock()

        result = _volfact(mock_module, mock_array, "test-vol")

        assert result == {}


class TestRenameEndpoint:
    """Test cases for rename_endpoint function"""

    @patch("plugins.modules.purefa_endpoint.LooseVersion")
    @patch("plugins.modules.purefa_endpoint.get_volume")
    def test_rename_endpoint_check_mode(self, mock_get_volume, mock_loose_version):
        """Test rename_endpoint in check mode"""
        mock_loose_version.side_effect = lambda x: float(x) if x != "2.0" else 2.0
        mock_module = Mock()
        mock_module.check_mode = True
        mock_module.params = {
            "name": "test-endpoint",
            "rename": "new-name",
            "context": "",
        }
        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.0"
        # Target does not exist
        mock_get_volume.return_value = None

        rename_endpoint(mock_module, mock_array)

        mock_module.exit_json.assert_called_once_with(changed=True, volume={})
