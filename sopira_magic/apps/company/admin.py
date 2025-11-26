#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/company/admin.py
#   Company Admin - Django admin configuration
#   Admin interface for Company model
#..............................................................

"""
   Company Admin - Django Admin Configuration.

   Django admin interface configuration for Company model.
   Extends NamedWithCodeModelAdmin for base functionality.

   Admin Classes:

   CompanyAdmin (extends NamedWithCodeModelAdmin)
   - Inherits base admin functionality from NamedWithCodeModelAdmin
   - Relations managed via relation app (not hardcoded)
   - Displays: code, name, human_id, active, visible, created
   - Filters: active, visible, created
   - Search: code, name, human_id
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import Company


@admin.register(Company)
class CompanyAdmin(NamedWithCodeModelAdmin):
    """Company admin configuration."""
    # Relations are managed via relation app, not hardcoded here
    pass
