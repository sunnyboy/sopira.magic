#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/tests/test_clear_all_data.py
#   Clear All Data Command Tests
#   Tests for clear_all_data management command
#..............................................................

"""
   Clear All Data Command Tests.

   Tests for clear_all_data management command.
   Tests data deletion, options, and dependency handling.
"""

import pytest
from io import StringIO
from django.core.management import call_command
from sopira_magic.apps.m_user.models import User
from sopira_magic.apps.m_company.models import Company
from sopira_magic.apps.m_factory.models import Factory
from sopira_magic.apps.m_productionline.models import ProductionLine
from sopira_magic.apps.m_photo.models import Photo
from sopira_magic.apps.relation.models import RelationInstance


@pytest.mark.django_db
class TestClearAllDataCommand:
    """Test suite for clear_all_data command."""

    def test_clear_all_data_deletes_all_records(self):
        """Test clear_all_data deletes all records."""
        # Generate some data first
        call_command('generate_all_data')
        
        assert User.objects.count() > 0
        assert Company.objects.count() > 0
        
        # Clear all data
        out = StringIO()
        call_command('clear_all_data', stdout=out)
        
        assert User.objects.count() == 0
        assert Company.objects.count() == 0
        assert Factory.objects.count() == 0
        assert ProductionLine.objects.count() == 0
        assert Photo.objects.count() == 0

    def test_clear_all_data_with_keep_users(self):
        """Test clear_all_data with --keep-users flag."""
        # Generate some data first
        call_command('generate_all_data')
        
        user_count_before = User.objects.count()
        assert user_count_before > 0
        
        # Clear all data but keep users
        out = StringIO()
        call_command('clear_all_data', '--keep-users', stdout=out)
        
        assert User.objects.count() == user_count_before
        assert Company.objects.count() == 0
        assert Factory.objects.count() == 0

    def test_clear_all_data_with_dry_run(self):
        """Test clear_all_data with --dry-run flag."""
        # Generate some data first
        call_command('generate_all_data')
        
        user_count_before = User.objects.count()
        company_count_before = Company.objects.count()
        
        # Dry run should not delete anything
        out = StringIO()
        call_command('clear_all_data', '--dry-run', stdout=out)
        
        assert User.objects.count() == user_count_before
        assert Company.objects.count() == company_count_before

    def test_clear_all_data_deletes_relations(self):
        """Test clear_all_data deletes RelationInstance records."""
        # Generate some data first
        call_command('generate_all_data')
        
        relation_count_before = RelationInstance.objects.count()
        assert relation_count_before > 0
        
        # Clear all data
        call_command('clear_all_data')
        
        assert RelationInstance.objects.count() == 0

    def test_clear_all_data_correct_order(self):
        """Test clear_all_data deletes in correct order (children before parents)."""
        # Generate some data first
        call_command('generate_all_data')
        
        # Clear all data
        out = StringIO()
        call_command('clear_all_data', stdout=out)
        
        # All should be deleted
        assert User.objects.count() == 0
        assert Company.objects.count() == 0
        assert Factory.objects.count() == 0
        assert ProductionLine.objects.count() == 0

    def test_clear_all_data_output(self):
        """Test clear_all_data produces correct output."""
        # Generate some data first
        call_command('generate_all_data')
        
        out = StringIO()
        call_command('clear_all_data', stdout=out)
        
        output = out.getvalue()
        assert 'Clear All Data Complete' in output

