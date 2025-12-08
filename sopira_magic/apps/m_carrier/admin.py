#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_carrier/admin.py
#   Carrier Admin - Django admin configuration
#   Admin interface for Carrier model
#..............................................................

"""
   Carrier Admin - Django Admin Configuration.

   Django admin interface configuration for Carrier model.
   Extends NamedWithCodeModelAdmin for base functionality.
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import Carrier


@admin.register(Carrier)
class CarrierAdmin(NamedWithCodeModelAdmin):
    """Carrier admin configuration."""
    # Relations are managed via relation app, not hardcoded here
    pass

