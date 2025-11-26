#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/admin.py
#   Generator Admin - Django admin configuration
#   Admin interface for GeneratorConfig model
#..............................................................

"""
   Generator Admin - Django Admin Configuration.

   Django admin interface configuration for GeneratorConfig model.
   Allows management of data generation configurations via admin interface.

   Admin Classes:

   GeneratorConfigAdmin
   - Displays: model_name, enabled, created, updated
   - Filters: enabled, created
   - Search: model_name
   - Read-only: created, updated

   Usage:
   - Access via Django admin at /admin/generator/generatorconfig/
   - Allows enabling/disabling generator configurations
   - View and edit generator configurations stored in database
"""

from django.contrib import admin
from .models import GeneratorConfig


@admin.register(GeneratorConfig)
class GeneratorConfigAdmin(admin.ModelAdmin):
    """GeneratorConfig admin configuration."""
    list_display = ['model_name', 'enabled', 'created', 'updated']
    list_filter = ['enabled', 'created']
    search_fields = ['model_name']
    readonly_fields = ['created', 'updated']
