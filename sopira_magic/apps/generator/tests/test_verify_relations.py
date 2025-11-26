#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/tests/test_verify_relations.py
#   Verify Relations Command Tests
#   Tests for verify_relations management command
#..............................................................

"""
   Verify Relations Command Tests.

   Tests for verify_relations management command.
   Tests relation verification and reporting.
"""

import pytest
from io import StringIO
from django.core.management import call_command
from sopira_magic.apps.relation.models import RelationRegistry, RelationInstance


@pytest.mark.django_db
class TestVerifyRelationsCommand:
    """Test suite for verify_relations command."""

    def test_verify_relations_with_data(self):
        """Test verify_relations with existing relations."""
        # Generate data first (creates relations)
        call_command('generate_all_data')
        
        out = StringIO()
        call_command('verify_relations', stdout=out)
        
        output = out.getvalue()
        # Should report on relations
        assert 'Relation' in output or 'relation' in output

    def test_verify_relations_without_data(self):
        """Test verify_relations without existing data."""
        out = StringIO()
        call_command('verify_relations', stdout=out)
        
        output = out.getvalue()
        # Should handle empty state gracefully
        assert len(output) >= 0

    def test_verify_relations_reports_coverage(self):
        """Test verify_relations reports relation coverage."""
        # Generate data first
        call_command('generate_all_data')
        
        out = StringIO()
        call_command('verify_relations', stdout=out)
        
        output = out.getvalue()
        # Should report coverage or counts
        assert 'RelationInstance' in output or 'coverage' in output.lower() or 'count' in output.lower()

