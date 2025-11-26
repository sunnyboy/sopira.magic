#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/tests/test_generate_data.py
#   Generate Data Command Tests
#   Tests for generate_data management command
#..............................................................

"""
   Generate Data Command Tests.

   Tests for generate_data management command.
   Tests command arguments, options, and error handling.
"""

import pytest
from io import StringIO
from django.core.management import call_command
from django.core.management.base import CommandError
from sopira_magic.apps.user.models import User
from sopira_magic.apps.company.models import Company


@pytest.mark.django_db
class TestGenerateDataCommand:
    """Test suite for generate_data command."""

    def test_generate_data_specific_model(self):
        """Test generating data for specific model."""
        out = StringIO()
        call_command('generate_data', 'user', '--count', '5', stdout=out)
        
        assert User.objects.count() == 5
        assert 'Successfully created 5 records' in out.getvalue()

    def test_generate_data_with_count(self):
        """Test generate_data with --count parameter."""
        out = StringIO()
        call_command('generate_data', 'user', '--count', '10', stdout=out)
        
        assert User.objects.count() == 10

    def test_generate_data_with_user(self, sample_user):
        """Test generate_data with --user parameter."""
        out = StringIO()
        call_command('generate_data', 'user', '--count', '1', '--user', sample_user.username, stdout=out)
        
        assert User.objects.count() >= 1

    def test_generate_data_with_seed(self):
        """Test generate_data with --seed flag."""
        out = StringIO()
        call_command('generate_data', '--seed', stdout=out)
        
        # Should generate data for all models
        assert User.objects.count() > 0
        assert 'Generation complete' in out.getvalue()

    def test_generate_data_with_clear(self):
        """Test generate_data with --clear flag."""
        # Generate some data first
        call_command('generate_data', 'user', '--count', '5')
        assert User.objects.count() == 5
        
        # Clear it
        out = StringIO()
        call_command('generate_data', 'user', '--clear', stdout=out)
        
        assert User.objects.count() == 0

    def test_generate_data_with_keep(self):
        """Test generate_data with --keep parameter."""
        # Generate some data first
        call_command('generate_data', 'user', '--count', '10')
        assert User.objects.count() == 10
        
        # Clear but keep 3
        out = StringIO()
        call_command('generate_data', 'user', '--clear', '--keep', '3', stdout=out)
        
        assert User.objects.count() == 3

    def test_generate_data_nonexistent_model(self):
        """Test generate_data with non-existent model."""
        with pytest.raises(CommandError):
            call_command('generate_data', 'nonexistent_model')

    def test_generate_data_nonexistent_user(self):
        """Test generate_data with non-existent user."""
        with pytest.raises(CommandError):
            call_command('generate_data', 'user', '--user', 'nonexistent_user')

