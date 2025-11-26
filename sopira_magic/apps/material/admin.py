#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/material/admin.py
#   Material Admin - Django admin configuration
#   Admin interface for Material model
#..............................................................

"""
   Material Admin - Django Admin Configuration.

   Django admin interface configuration for Material model.
   Extends NamedWithCodeModelAdmin with material-specific fields.

   Admin Classes:

   MaterialAdmin (extends NamedWithCodeModelAdmin)
   - Displays: code, name, unit, unit_price, active, visible
   - Filters: active, visible
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import Material


@admin.register(Material)
class MaterialAdmin(NamedWithCodeModelAdmin):
    """Material admin configuration."""
    list_display = ['code', 'name', 'unit', 'unit_price', 'active', 'visible']
    list_filter = ['active', 'visible']
