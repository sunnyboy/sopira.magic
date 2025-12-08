#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_pit/admin.py
#   Pit Admin - Django admin configuration
#   Admin interface for Pit model
#..............................................................

"""
   Pit Admin - Django Admin Configuration.

   Django admin interface configuration for Pit model.
   Extends NamedWithCodeModelAdmin for base functionality.
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import Pit


@admin.register(Pit)
class PitAdmin(NamedWithCodeModelAdmin):
    """Pit admin configuration."""
    # Relations are managed via relation app, not hardcoded here
    pass

