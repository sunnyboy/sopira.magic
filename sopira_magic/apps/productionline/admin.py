#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/productionline/admin.py
#   ProductionLine Admin - Django admin configuration
#   Admin interface for ProductionLine model
#..............................................................

"""
   ProductionLine Admin - Django Admin Configuration.

   Django admin interface configuration for ProductionLine model.
   Extends NamedWithCodeModelAdmin for base functionality.

   Admin Classes:

   ProductionLineAdmin (extends NamedWithCodeModelAdmin)
   - Inherits base admin functionality from NamedWithCodeModelAdmin
   - Relations managed via relation app (not hardcoded)
   - Displays: code, name, human_id, active, visible, created
   - Filters: active, visible, created
   - Search: code, name, human_id
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import ProductionLine


@admin.register(ProductionLine)
class ProductionLineAdmin(NamedWithCodeModelAdmin):
    """ProductionLine admin configuration."""
    # Relations are managed via relation app, not hardcoded here
    pass
