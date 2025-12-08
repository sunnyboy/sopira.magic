#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/factory/admin.py
#   Factory Admin - Django admin configuration
#   Admin interface for Factory model
#..............................................................

"""
   Factory Admin - Django Admin Configuration.

   Django admin interface configuration for Factory model.
   Extends NamedWithCodeModelAdmin for base functionality.

   Admin Classes:

   FactoryAdmin (extends NamedWithCodeModelAdmin)
   - Inherits base admin functionality from NamedWithCodeModelAdmin
   - Relations managed via relation app (not hardcoded)
   - Displays: code, name, human_id, active, visible, created
   - Filters: active, visible, created
   - Search: code, name, human_id
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import Factory


@admin.register(Factory)
class FactoryAdmin(NamedWithCodeModelAdmin):
    """Factory admin configuration."""
    # Relations are managed via relation app, not hardcoded here
    pass
