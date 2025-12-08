#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/tests/test_generate_all_data.py
#   Generate All Data Command Tests
#   Tests for generate_all_data management command
#..............................................................

"""
   Generate All Data Command Tests.

   Tests for generate_all_data management command.
   Tests seed data generation for all models.
"""

import pytest
from io import StringIO
from django.core.management import call_command
from sopira_magic.apps.m_user.models import User
from sopira_magic.apps.m_company.models import Company
from sopira_magic.apps.m_factory.models import Factory
from sopira_magic.apps.m_productionline.models import ProductionLine
from sopira_magic.apps.m_photo.models import Photo


@pytest.mark.django_db
class TestGenerateAllDataCommand:
    """Test suite for generate_all_data command."""

    def test_generate_all_data_creates_all_models(self):
        """Test generate_all_data creates data for all models."""
        out = StringIO()
        call_command('generate_all_data', stdout=out)
        
        assert User.objects.count() > 0
        assert Company.objects.count() > 0
        assert Factory.objects.count() > 0
        assert ProductionLine.objects.count() > 0
        assert Photo.objects.count() > 0

    def test_generate_all_data_correct_counts(self):
        """Test generate_all_data generates correct counts."""
        call_command('generate_all_data')
        
        user_count = User.objects.count()
        company_count = Company.objects.count()
        factory_count = Factory.objects.count()
        productionline_count = ProductionLine.objects.count()
        photo_count = Photo.objects.count()
        
        # Check per_source relations
        assert company_count == user_count * 5
        assert factory_count == company_count * 3
        assert productionline_count == factory_count * 4
        assert photo_count == user_count * 20

    def test_generate_all_data_respects_dependencies(self):
        """Test generate_all_data respects model dependencies."""
        call_command('generate_all_data')
        
        # Users should exist before companies
        assert User.objects.count() > 0
        assert Company.objects.count() > 0
        
        # Companies should exist before factories
        assert Factory.objects.count() > 0

    def test_generate_all_data_output(self):
        """Test generate_all_data produces correct output."""
        out = StringIO()
        call_command('generate_all_data', stdout=out)
        
        output = out.getvalue()
        assert 'Generating seed data' in output or 'Generation complete' in output

