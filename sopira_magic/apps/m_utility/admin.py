#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/utility/admin.py
#   Utility Admin - Django admin configuration
#   Admin interface for Utility model
#..............................................................

"""
   Utility Admin - Django Admin Configuration.

   Django admin interface configuration for Utility model.
   Extends NamedWithCodeModelAdmin with utility-specific fields.

   Admin Classes:

   UtilityAdmin (extends NamedWithCodeModelAdmin)
   - Displays: code, name, utility_type, value, active, visible
   - Filters: utility_type, active, visible
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import Utility


@admin.register(Utility)
class UtilityAdmin(NamedWithCodeModelAdmin):
    """Utility admin configuration."""
    list_display = ['code', 'name', 'utility_type', 'value', 'active', 'visible']
    list_filter = ['utility_type', 'active', 'visible']
