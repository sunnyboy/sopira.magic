#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_location/admin.py
#   Location Admin - Django admin configuration
#   Admin interface for Location model
#..............................................................

"""
   Location Admin - Django Admin Configuration.

   Django admin interface configuration for Location model.
   Extends NamedWithCodeModelAdmin for base functionality.

   Admin Classes:

   LocationAdmin (extends NamedWithCodeModelAdmin)
   - Inherits base admin functionality from NamedWithCodeModelAdmin
   - Relations managed via relation app (not hardcoded)
   - Displays: code, name, human_id, active, visible, created
   - Filters: active, visible, created
   - Search: code, name, human_id
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import Location


@admin.register(Location)
class LocationAdmin(NamedWithCodeModelAdmin):
    """Location admin configuration."""
    # Relations are managed via relation app, not hardcoded here
    pass

