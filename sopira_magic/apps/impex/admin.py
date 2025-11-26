#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/impex/admin.py
#   Impex Admin - Django admin configuration
#   Admin interface for import/export models
#..............................................................

"""
   Impex Admin - Django Admin Configuration.

   Django admin interface configuration for import/export models.
   Provides management interface for import, export, and communication interfaces.

   Admin Classes:

   1. ImportConfigAdmin
      - Displays: name, import_type, enabled, created
      - Filters: import_type, enabled, created
      - Search: name

   2. ExportConfigAdmin
      - Displays: name, export_type, enabled, created
      - Filters: export_type, enabled, created
      - Search: name

   3. CommunicationInterfaceAdmin
      - Displays: name, interface_type, enabled, created
      - Filters: interface_type, enabled, created
      - Search: name
"""

from django.contrib import admin
from .models import ImportConfig, ExportConfig, CommunicationInterface


@admin.register(ImportConfig)
class ImportConfigAdmin(admin.ModelAdmin):
    """ImportConfig admin configuration."""
    list_display = ['name', 'import_type', 'enabled', 'created']
    list_filter = ['import_type', 'enabled', 'created']
    search_fields = ['name']


@admin.register(ExportConfig)
class ExportConfigAdmin(admin.ModelAdmin):
    """ExportConfig admin configuration."""
    list_display = ['name', 'export_type', 'enabled', 'created']
    list_filter = ['export_type', 'enabled', 'created']
    search_fields = ['name']


@admin.register(CommunicationInterface)
class CommunicationInterfaceAdmin(admin.ModelAdmin):
    """CommunicationInterface admin configuration."""
    list_display = ['name', 'interface_type', 'enabled', 'created']
    list_filter = ['interface_type', 'enabled', 'created']
    search_fields = ['name']
