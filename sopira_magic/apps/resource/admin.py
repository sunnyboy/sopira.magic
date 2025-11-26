#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/resource/admin.py
#   Resource Admin - Django admin configuration
#   Admin interface for Resource model
#..............................................................

"""
   Resource Admin - Django Admin Configuration.

   Django admin interface configuration for Resource model.
   Extends NamedWithCodeModelAdmin with resource-specific fields.

   Admin Classes:

   ResourceAdmin (extends NamedWithCodeModelAdmin)
   - Displays: code, name, resource_type, unit, quantity, active, visible
   - Filters: resource_type, active, visible
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import Resource


@admin.register(Resource)
class ResourceAdmin(NamedWithCodeModelAdmin):
    """Resource admin configuration."""
    list_display = ['code', 'name', 'resource_type', 'unit', 'quantity', 'active', 'visible']
    list_filter = ['resource_type', 'active', 'visible']
