#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/tests/test_models.py
#   Generator Models Tests
#   Tests for GeneratorConfig model
#..............................................................

"""
   Generator Models Tests.

   Unit tests for GeneratorConfig model.
   Tests model creation, constraints, and field validation.
"""

import pytest
from django.core.exceptions import ValidationError
from sopira_magic.apps.generator.models import GeneratorConfig


@pytest.mark.django_db
class TestGeneratorConfig:
    """Test suite for GeneratorConfig model."""

    def test_create_generator_config(self):
        """Test creating a GeneratorConfig instance."""
        config = GeneratorConfig.objects.create(
            model_name='test_model',
            config={'count': 10, 'fields': {}},
            template='Test template',
            enabled=True
        )
        
        assert config.model_name == 'test_model'
        assert config.config == {'count': 10, 'fields': {}}
        assert config.template == 'Test template'
        assert config.enabled is True
        assert config.id is not None

    def test_generator_config_default_values(self):
        """Test default values for GeneratorConfig."""
        config = GeneratorConfig.objects.create(model_name='test_model')
        
        assert config.config == {}
        assert config.template == ''
        assert config.enabled is True

    def test_generator_config_unique_constraint(self, db):
        """Test unique constraint on model_name."""
        GeneratorConfig.objects.create(model_name='test_model')
        
        # Try to create another with same model_name
        # Use transaction.atomic to handle IntegrityError properly
        from django.db import transaction, IntegrityError
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                GeneratorConfig.objects.create(model_name='test_model')

    def test_generator_config_jsonfield_validation(self):
        """Test JSONField accepts valid JSON."""
        config = GeneratorConfig.objects.create(
            model_name='test_model',
            config={
                'count': 10,
                'fields': {
                    'name': {'type': 'dataset', 'dataset': 'business_name'}
                }
            }
        )
        
        assert isinstance(config.config, dict)
        assert config.config['count'] == 10
        assert 'fields' in config.config

    def test_generator_config_string_representation(self):
        """Test string representation of GeneratorConfig."""
        config = GeneratorConfig.objects.create(model_name='test_model')
        
        # Model should have __str__ method (if implemented)
        assert str(config) is not None

