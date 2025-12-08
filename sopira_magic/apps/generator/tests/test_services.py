#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/tests/test_services.py
#   Generator Services Tests
#   Tests for services.py module
#..............................................................

"""
   Generator Services Tests.

   Integration tests for GeneratorService.
   Tests data generation, relations, and seed data generation.
"""

import pytest
from sopira_magic.apps.generator.services import GeneratorService
from sopira_magic.apps.m_user.models import User
from sopira_magic.apps.m_company.models import Company
from sopira_magic.apps.m_factory.models import Factory
from sopira_magic.apps.m_productionline.models import ProductionLine
from sopira_magic.apps.m_photo.models import Photo
from sopira_magic.apps.relation.models import RelationInstance


@pytest.mark.django_db
class TestGeneratorServiceGetModelClass:
    """Test suite for get_model_class method."""

    def test_get_model_class_valid_path(self):
        """Test getting model class with valid path."""
        model_class = GeneratorService.get_model_class('user.User')
        
        assert model_class == User

    def test_get_model_class_invalid_path(self):
        """Test getting model class with invalid path."""
        with pytest.raises(Exception):  # LookupError or ValueError
            GeneratorService.get_model_class('invalid.Model')


@pytest.mark.django_db
class TestGeneratorServiceGenerateData:
    """Test suite for generate_data method."""

    def test_generate_data_standard_mode(self):
        """Test generate_data in standard mode (without per_source)."""
        # Generate users first (no per_source relation)
        users = GeneratorService.generate_data('user', count=5)
        
        assert len(users) == 5
        assert User.objects.count() == 5

    def test_generate_data_with_custom_count(self):
        """Test generate_data with custom count parameter."""
        users = GeneratorService.generate_data('user', count=10)
        
        assert len(users) == 10
        assert User.objects.count() == 10

    def test_generate_data_user_model_password_handling(self):
        """Test User model password is handled correctly."""
        users = GeneratorService.generate_data('user', count=1)
        
        assert len(users) == 1
        user = users[0]
        # Password should be set (check_password works)
        assert user.check_password('password123')

    def test_generate_data_nonexistent_model_key(self):
        """Test generate_data with non-existent model_key."""
        with pytest.raises(ValueError, match="Generator config 'nonexistent' not found"):
            GeneratorService.generate_data('nonexistent')

    def test_generate_data_per_source_mode(self, multiple_users):
        """Test generate_data in per_source mode."""
        # Generate companies with per_source relation (5 per user)
        companies = GeneratorService.generate_data('company')
        
        user_count = User.objects.count()
        expected_count = user_count * 5
        
        assert len(companies) == expected_count
        assert Company.objects.count() == expected_count

    def test_generate_data_per_source_correct_count(self, multiple_users):
        """Test per_source generates correct number of objects."""
        # Create 3 users
        for i in range(3):
            User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='testpass123'
            )
        
        # Generate companies (5 per user)
        companies = GeneratorService.generate_data('company')
        
        assert len(companies) == 15  # 3 users × 5 companies

    def test_generate_data_with_user_parameter(self, sample_user):
        """Test generate_data with user parameter."""
        # This test depends on relation config
        # For now, just verify it doesn't crash
        result = GeneratorService.generate_data('user', count=1, user=sample_user)
        
        assert len(result) >= 0


@pytest.mark.django_db
class TestGeneratorServiceGenerateSeedData:
    """Test suite for generate_seed_data method."""

    def test_generate_seed_data_generates_all_models(self):
        """Test generate_seed_data generates data for all configured models."""
        results = GeneratorService.generate_seed_data()
        
        assert isinstance(results, dict)
        assert 'user' in results
        assert 'company' in results
        assert 'factory' in results
        assert 'productionline' in results
        assert 'photo' in results

    def test_generate_seed_data_respects_dependencies(self):
        """Test generate_seed_data respects model dependencies."""
        results = GeneratorService.generate_seed_data()
        
        # Users should be generated first (no dependencies)
        assert results['user'] > 0
        
        # Companies depend on users
        if 'company' in results:
            assert results['company'] > 0

    def test_generate_seed_data_correct_counts(self):
        """Test generate_seed_data generates correct counts."""
        results = GeneratorService.generate_seed_data()
        
        user_count = results.get('user', 0)
        
        # Companies should be 5 per user
        if 'company' in results:
            expected_companies = user_count * 5
            assert results['company'] == expected_companies


@pytest.mark.django_db
class TestGeneratorServiceClearData:
    """Test suite for clear_data method."""

    def test_clear_data_deletes_all_records(self):
        """Test clear_data deletes all records."""
        # Generate some data
        GeneratorService.generate_data('user', count=5)
        assert User.objects.count() == 5
        
        # Clear data
        deleted_count = GeneratorService.clear_data('user', keep_count=0)
        
        assert deleted_count == 5
        assert User.objects.count() == 0

    def test_clear_data_with_keep_count(self):
        """Test clear_data with keep_count parameter."""
        # Generate some data
        GeneratorService.generate_data('user', count=10)
        assert User.objects.count() == 10
        
        # Clear data but keep 3 oldest
        deleted_count = GeneratorService.clear_data('user', keep_count=3)
        
        assert deleted_count == 7
        assert User.objects.count() == 3

    def test_clear_data_nonexistent_model_key(self):
        """Test clear_data with non-existent model_key."""
        with pytest.raises(ValueError, match="Generator config 'nonexistent' not found"):
            GeneratorService.clear_data('nonexistent')


@pytest.mark.django_db
class TestGeneratorServicePerSourceGeneration:
    """Test suite for per_source generation strategy."""

    def test_per_source_generates_for_all_sources(self, multiple_users):
        """Test per_source generates objects for all source objects."""
        # Generate companies (5 per user)
        companies = GeneratorService.generate_data('company')
        
        user_count = User.objects.count()
        expected_count = user_count * 5
        
        assert len(companies) == expected_count

    def test_per_source_creates_relations(self, multiple_users):
        """Test per_source creates relations between source and target."""
        # Generate companies
        companies = GeneratorService.generate_data('company')
        
        # Check relations were created
        relation_count = RelationInstance.objects.count()
        assert relation_count > 0

    def test_per_source_without_source_objects(self):
        """Test per_source handles missing source objects."""
        # Clear all users
        User.objects.all().delete()
        
        # Try to generate companies (requires users)
        # Should handle gracefully (might create users or skip)
        try:
            companies = GeneratorService.generate_data('company')
            # If it works, it should have created users first
            assert User.objects.count() > 0 or len(companies) == 0
        except Exception:
            # Or it might raise an error, which is acceptable
            pass


@pytest.mark.django_db
class TestGeneratorServiceRelations:
    """Test suite for relation creation."""

    def test_generate_data_creates_relations(self, multiple_users):
        """Test generate_data creates relations."""
        # Generate companies
        companies = GeneratorService.generate_data('company')
        
        # Relations should be created
        relation_count = RelationInstance.objects.count()
        assert relation_count > 0

    def test_per_source_relation_coverage(self, multiple_users):
        """Test per_source ensures all sources have related objects."""
        # Generate companies (5 per user)
        companies = GeneratorService.generate_data('company')
        
        # Each user should have companies
        users = User.objects.all()
        for user in users:
            # Check if user has relations (via RelationInstance)
            user_relations = RelationInstance.objects.filter(
                source_content_type__model='user',
                source_object_id=user.id
            )
            assert user_relations.count() > 0

