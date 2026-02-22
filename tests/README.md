# FlashArray Collection - Test Suite

This directory contains the test suite for the Pure Storage FlashArray Ansible Collection.

## Test Statistics

| Metric | Value |
|--------|-------|
| **Total Tests** | 1,150 |
| **Code Coverage** | 62% |
| **Test Files** | 68 |
| **Modules Tested** | 66 |

## Directory Structure

```
tests/
├── unit/                           # Unit tests
│   └── plugins/
│       ├── modules/                # Module unit tests (66 test files)
│       └── module_utils/           # Utility function unit tests
│           ├── test_api_helpers.py # API helper tests
│           └── test_common.py      # Common utilities tests
├── conftest.py                     # Shared pytest fixtures
├── requirements.txt                # Test dependencies
└── README.md                       # This file
```

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install -r tests/requirements.txt
```

### Run All Tests

```bash
# Standard run
pytest tests/unit/

# Quiet mode with no traceback
pytest tests/unit/ -p no:sugar --tb=no -q
```

### Run Specific Test Files

```bash
# Run api_helpers tests
pytest tests/unit/plugins/module_utils/test_api_helpers.py

# Run a specific module's tests
pytest tests/unit/plugins/modules/test_purefa_volume.py
```

### Run with Coverage

```bash
# Generate coverage report
pytest tests/unit/ --cov=plugins --cov-report=term

# Generate HTML coverage report
pytest tests/unit/ --cov=plugins --cov-report=html
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS/Linux

# Coverage for a specific module
pytest tests/unit/plugins/modules/test_purefa_host.py --cov=plugins.modules.purefa_host --cov-report=term
```

### Run Specific Test Classes or Methods

```bash
# Run specific test class
pytest tests/unit/plugins/modules/test_purefa_volume.py::TestCreateVolume

# Run specific test method
pytest tests/unit/plugins/modules/test_purefa_volume.py::TestCreateVolume::test_create_volume_success
```

## Writing Tests

### Test File Naming

- Test files must start with `test_`
- Test classes must start with `Test`
- Test methods must start with `test_`

### Test Structure

Each module test file follows this structure:

```python
import sys
from unittest.mock import Mock, MagicMock, patch

# Mock external dependencies before importing the module
sys.modules["pypureclient"] = MagicMock()
sys.modules["pypureclient.flasharray"] = MagicMock()

from plugins.modules.purefa_example import (
    function_to_test,
)


class TestFunctionName:
    """Test cases for function_name"""

    @patch("plugins.modules.purefa_example.some_dependency")
    def test_function_success(self, mock_dep):
        """Test successful execution"""
        mock_module = Mock()
        mock_module.params = {"param1": "value1"}
        mock_module.check_mode = False

        mock_array = Mock()
        mock_array.get_rest_version.return_value = "2.38"

        result = function_to_test(mock_module, mock_array)

        assert result == expected_value
        mock_module.exit_json.assert_called_once_with(changed=True)
```

### Mocking Best Practices

1. **Mock external dependencies** before importing the module under test
2. **Use `@patch` decorators** to mock functions called within the tested function
3. **Set `.name` as an attribute** on Mock objects when the code accesses `.name`:
   ```python
   mock_obj = Mock()
   mock_obj.name = "example"  # Not mock_obj.name() or Mock(name="example")
   ```
4. **Use `side_effect`** for functions that need to return different values on successive calls:
   ```python
   mock_func.side_effect = [first_return, second_return, third_return]
   ```
5. **Use `SystemExit(1)`** for `fail_json.side_effect` when testing error paths:
   ```python
   mock_module.fail_json.side_effect = SystemExit(1)
   with pytest.raises(SystemExit):
       function_under_test(mock_module, mock_array)
   ```
6. **pypureclient objects use attribute access**, not subscript access. Mock nested attributes correctly:
   ```python
   # Correct - attribute access
   mock_interface = Mock()
   mock_interface.name = "eth0"
   mock_interface.eth = Mock()
   mock_interface.eth.gateway = "10.0.0.1"
   mock_vol.member = Mock()
   mock_vol.member.name = "volume1"

   # Wrong - subscript access (will cause errors)
   mock_interface = {"name": "eth0"}  # Don't do this
   mock_vol.member = {"name": "volume1"}  # Don't do this
   ```

## Coverage by Module

### High Coverage (80%+)

| Module | Coverage |
|--------|----------|
| purefa_arrayname.py | 90% |
| purefa_file.py | 90% |
| purefa_sso.py | 89% |
| purefa_timeout.py | 87% |
| purefa_console.py | 86% |
| purefa_eula.py | 86% |
| purefa_hardware.py | 85% |
| purefa_network.py | 83% |
| purefa_phonehome.py | 80% |
| purefa_proxy.py | 80% |

### Medium Coverage (70-79%)

| Module | Coverage |
|--------|----------|
| purefa_vlan.py | 74% |
| purefa_banner.py | 74% |
| purefa_smtp.py | 73% |
| purefa_syslog.py | 73% |
| purefa_api_helpers.py | 73% |
| purefa_pod_replica.py | 71% |
| purefa_user.py | 70% |

### Priority for Improvement (<55%)

| Module | Coverage | Missing Lines |
|--------|----------|---------------|
| purefa_policy.py | 51% | 360 |
| purefa_pod.py | 52% | 140 |
| purefa_messages.py | 52% | 29 |
| purefa_sessions.py | 53% | 34 |
| purefa_hg.py | 54% | 105 |
| purefa_inventory.py | 54% | 34 |

## CI/CD Integration

Tests are automatically run in GitHub Actions on:
- Pull requests to master
- Pushes to master

See `.github/workflows/main.yml` for CI configuration.

The CI pipeline runs:
```bash
python -m pytest tests/unit/ -v --tb=short
```

## Troubleshooting

### Import Errors

If you get import errors, ensure you're running pytest from the repository root:

```bash
cd /path/to/FlashArray-Collection
pytest tests/unit/
```

### Timeout Issues

If tests hang or timeout, try disabling pytest-sugar:

```bash
pytest tests/unit/ -p no:sugar --tb=no -q
```

### Missing Dependencies

Install all test dependencies:

```bash
pip install -r tests/requirements.txt
```

## Contributing

When adding new functionality:

1. Write tests for the new code
2. Ensure all tests pass: `pytest tests/unit/`
3. Check coverage: `pytest tests/unit/ --cov=plugins --cov-report=term`
4. Aim for 80%+ coverage on new code
5. Run Black formatter: `python -m black <test_file.py>`
6. Run pylint: `python -m pylint <test_file.py>`

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Ansible Testing Guide](https://docs.ansible.com/ansible/latest/dev_guide/testing.html)

