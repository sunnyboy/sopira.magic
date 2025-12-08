#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_pot/admin.py
#   Pot Admin - Django admin configuration
#   Admin interface for Pot model
#..............................................................

"""
   Pot Admin - Django Admin Configuration.

   Django admin interface configuration for Pot model.
   Extends NamedWithCodeModelAdmin for base functionality.
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import Pot


@admin.register(Pot)
class PotAdmin(NamedWithCodeModelAdmin):
    """Pot admin configuration."""
    # Relations are managed via relation app, not hardcoded here
    pass

