# Generator Tests

Test suite for generator application.

## Structure

```
tests/
├── __init__.py
├── conftest.py          # App-specific fixtures
├── test_models.py       # Tests for GeneratorConfig model
├── test_config.py       # Tests for config.py module
├── test_datasets.py     # Tests for datasets.py module
├── test_field_generators.py  # Tests for field_generators.py module
├── test_services.py     # Tests for services.py module
├── test_generate_data.py     # Tests for generate_data command
├── test_generate_all_data.py # Tests for generate_all_data command
├── test_clear_all_data.py    # Tests for clear_all_data command
└── test_verify_relations.py  # Tests for verify_relations command
```

## Running Tests

### Run all generator tests
```bash
pytest sopira_magic/apps/generator/tests/
```

### Run specific test file
```bash
pytest sopira_magic/apps/generator/tests/test_services.py
```

### Run specific test
```bash
pytest sopira_magic/apps/generator/tests/test_services.py::TestGeneratorServiceGenerateData::test_generate_data_standard_mode
```

### Run with coverage
```bash
pytest --cov=sopira_magic.apps.generator sopira_magic/apps/generator/tests/
```

### Run with verbose output
```bash
pytest -v sopira_magic/apps/generator/tests/
```

## Test Categories

- **Unit Tests**: Test individual functions and methods in isolation
- **Integration Tests**: Test interactions between components and database

## Fixtures

### Global Fixtures (conftest.py in root)
- `api_client`: Django REST Framework API client
- `django_client`: Django test client
- `test_user`: Sample user for testing
- `admin_user`: Admin user for testing

### App-Specific Fixtures (conftest.py in tests/)
- `sample_user`: Sample user for generator tests
- `multiple_users`: Multiple users for per_source relation tests
- `sample_company`: Sample company for testing
- `clean_generator_config`: Clean GeneratorConfig before/after test
- `clean_relations`: Clean RelationInstance after test

## Adding New Tests

1. Create test file in `tests/` directory
2. Follow naming convention: `test_*.py`
3. Use pytest fixtures for test data
4. Mark database tests with `@pytest.mark.django_db`
5. Use descriptive test names

## Example Test

```python
@pytest.mark.django_db
class TestMyFeature:
    """Test suite for my feature."""
    
    def test_my_feature_basic(self):
        """Test basic functionality."""
        result = my_function()
        assert result is not None
```

