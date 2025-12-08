#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_machine/admin.py
#   Machine Admin - Django admin configuration
#   Admin interface for Machine model
#..............................................................

"""
   Machine Admin - Django Admin Configuration.

   Django admin interface configuration for Machine model.
   Extends NamedWithCodeModelAdmin for base functionality.
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import Machine


@admin.register(Machine)
class MachineAdmin(NamedWithCodeModelAdmin):
    """Machine admin configuration."""
    # Relations are managed via relation app, not hardcoded here
    pass

