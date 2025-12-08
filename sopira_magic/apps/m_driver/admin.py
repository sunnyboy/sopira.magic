#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_driver/admin.py
#   Driver Admin - Django admin configuration
#   Admin interface for Driver model
#..............................................................

"""
   Driver Admin - Django Admin Configuration.

   Django admin interface configuration for Driver model.
   Extends NamedWithCodeModelAdmin for base functionality.
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import Driver


@admin.register(Driver)
class DriverAdmin(NamedWithCodeModelAdmin):
    """Driver admin configuration."""
    # Relations are managed via relation app, not hardcoded here
    pass

