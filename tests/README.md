# FlashArray Collection - Test Suite

This directory contains the test suite for the Pure Storage FlashArray Ansible Collection.

## Directory Structure

```
tests/
├── unit/                           # Unit tests
│   └── plugins/
│       ├── modules/                # Module unit tests
│       └── module_utils/           # Utility function unit tests
│           ├── test_api_helpers.py # API helper tests
│           └── test_common.py      # Common utilities tests
├── integration/                    # Integration tests
│   └── targets/                    # Integration test targets
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
pytest
```

### Run Specific Test Files

```bash
# Run api_helpers tests
pytest tests/unit/plugins/module_utils/test_api_helpers.py

# Run common utilities tests
pytest tests/unit/plugins/module_utils/test_common.py
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=plugins --cov-report=html --cov-report=term

# View HTML coverage report
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html  # Windows
```

### Run Specific Test Classes or Methods

```bash
# Run specific test class
pytest tests/unit/plugins/module_utils/test_api_helpers.py::TestCheckResponse

# Run specific test method
pytest tests/unit/plugins/module_utils/test_api_helpers.py::TestCheckResponse::test_success_response
```

## Test Markers

Tests can be marked with the following markers:

- `@pytest.mark.unit` - Unit tests (fast, no external dependencies)
- `@pytest.mark.integration` - Integration tests (require FlashArray access)
- `@pytest.mark.slow` - Slow-running tests

Run tests by marker:

```bash
# Run only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"
```

## Writing Tests

### Test File Naming

- Test files must start with `test_`
- Test classes must start with `Test`
- Test methods must start with `test_`

### Using Fixtures

Common fixtures are defined in `conftest.py`:

```python
def test_example(mock_module, mock_array):
    """Test using shared fixtures."""
    # mock_module provides a mock Ansible module
    # mock_array provides a mock FlashArray client
    pass
```

### Example Test

```python
import pytest
from plugins.module_utils.api_helpers import check_response

class TestCheckResponse:
    def test_success_response(self, mock_module, mock_success_response):
        """Test that success response does not raise."""
        # Should not raise
        check_response(mock_success_response, mock_module, "Test operation")

    def test_error_response(self, mock_module, mock_error_response):
        """Test that error response calls fail_json."""
        with pytest.raises(Exception, match="fail_json"):
            check_response(mock_error_response, mock_module, "Test operation")
```

## Coverage Goals

- **Current Coverage**: ~0% (initial setup)
- **Short-term Goal**: 50% coverage (3 months)
- **Long-term Goal**: 80%+ coverage

### Priority Areas for Testing

1. ⏳ `api_helpers.py` - Core API helper functions
2. ⏳ `common.py` - Common utilities
3. ⏳ `purefa.py` - Core connection logic
4. ⏳ Critical modules (purefa_volume, purefa_host, etc.)

## CI/CD Integration

Tests are automatically run in GitHub Actions on:
- Pull requests
- Pushes to master
- Daily schedule

See `.github/workflows/main.yml` for CI configuration.

## Troubleshooting

### Import Errors

If you get import errors, ensure you're running pytest from the repository root:

```bash
cd /path/to/FlashArray-Collection
pytest
```

### Missing Dependencies

Install all test dependencies:

```bash
pip install -r tests/requirements.txt
```

## Contributing

When adding new functionality:

1. Write tests first (TDD approach recommended)
2. Ensure tests pass: `pytest`
3. Check coverage: `pytest --cov=plugins`
4. Aim for 80%+ coverage on new code

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Ansible Testing Guide](https://docs.ansible.com/projects/ansible/latest/dev_guide/testing.html)

