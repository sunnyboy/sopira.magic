#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/tests/test_config.py
#   Generator Config Tests
#   Tests for config.py module
#..............................................................

"""
   Generator Config Tests.

   Unit tests for generator configuration module.
   Tests config retrieval and validation.
"""

import pytest
from sopira_magic.apps.generator.config import (
    get_generator_config,
    get_all_generator_configs,
    GENERATOR_CONFIG
)


class TestGeneratorConfig:
    """Test suite for generator configuration."""

    def test_get_generator_config_existing_key(self):
        """Test getting config for existing model key."""
        config = get_generator_config('user')
        
        assert config is not None
        assert 'model' in config
        assert 'fields' in config
        assert config['model'] == 'user.User'

    def test_get_generator_config_nonexistent_key(self):
        """Test getting config for non-existent key."""
        config = get_generator_config('nonexistent_model')
        
        # get_generator_config returns {} for non-existent keys
        assert config == {} or config is None

    def test_get_all_generator_configs(self):
        """Test getting all generator configs."""
        all_configs = get_all_generator_configs()
        
        assert isinstance(all_configs, dict)
        assert len(all_configs) > 0
        assert 'user' in all_configs
        assert 'company' in all_configs
        assert 'factory' in all_configs

    def test_generator_config_structure_user(self):
        """Test GENERATOR_CONFIG structure for user model."""
        config = GENERATOR_CONFIG.get('user')
        
        assert config is not None
        assert 'model' in config
        assert 'fields' in config
        assert config['model'] == 'user.User'
        assert 'username' in config['fields']
        assert 'email' in config['fields']

    def test_generator_config_structure_company(self):
        """Test GENERATOR_CONFIG structure for company model."""
        config = GENERATOR_CONFIG.get('company')
        
        assert config is not None
        assert 'model' in config
        assert 'fields' in config
        assert 'relations' in config
        assert config['model'] == 'company.Company'
        assert 'name' in config['fields']

    def test_generator_config_field_configs(self):
        """Test field configurations are valid."""
        config = get_generator_config('user')
        
        assert 'fields' in config
        for field_name, field_config in config['fields'].items():
            assert isinstance(field_config, dict)
            # Some fields might not have 'type' if they use auto-detection
            # Just check it's a dict

    def test_generator_config_relation_configs(self):
        """Test relation configurations are valid."""
        config = get_generator_config('company')
        
        if 'relations' in config:
            for relation_field, relation_config in config['relations'].items():
                assert isinstance(relation_config, dict)
                assert 'type' in relation_config or 'model' in relation_config

    def test_generator_config_per_source_relation(self):
        """Test per_source relation configuration."""
        config = get_generator_config('company')
        
        if 'relations' in config:
            for relation_config in config['relations'].values():
                if relation_config.get('type') == 'per_source':
                    assert 'count_per_source' in relation_config
                    assert 'model' in relation_config

    def test_all_configs_have_model_path(self):
        """Test all configs have valid model path."""
        all_configs = get_all_generator_configs()
        
        for key, config in all_configs.items():
            assert 'model' in config
            assert '.' in config['model']  # Should be 'app.Model' format

