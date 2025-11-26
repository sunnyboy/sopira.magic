#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/state/admin.py
#   State Admin - Django admin configuration
#   Admin interface for UI state models
#..............................................................

"""
   State Admin - Django Admin Configuration.

   Django admin interface configuration for UI state models.
   Provides management interface for TableState, SavedWorkspace, and EnvironmentState.

   Admin Classes:

   1. TableStateAdmin
      - Displays: user, table_name, component, is_active, created
      - Filters: table_name, is_active, created
      - Search: user username, table_name, component

   2. SavedWorkspaceAdmin
      - Displays: user, name, is_default, created
      - Filters: is_default, created
      - Search: user username, name

   3. EnvironmentStateAdmin
      - Displays: user, environment_name, is_active, created
      - Filters: environment_name, is_active, created
      - Search: user username, environment_name
"""

from django.contrib import admin
from .models import TableState, SavedWorkspace, EnvironmentState


@admin.register(TableState)
class TableStateAdmin(admin.ModelAdmin):
    """TableState admin configuration."""
    list_display = ['user', 'table_name', 'component', 'is_active', 'created']
    list_filter = ['table_name', 'is_active', 'created']
    search_fields = ['user__username', 'table_name', 'component']


@admin.register(SavedWorkspace)
class SavedWorkspaceAdmin(admin.ModelAdmin):
    """SavedWorkspace admin configuration."""
    list_display = ['user', 'name', 'is_default', 'created']
    list_filter = ['is_default', 'created']
    search_fields = ['user__username', 'name']


@admin.register(EnvironmentState)
class EnvironmentStateAdmin(admin.ModelAdmin):
    """EnvironmentState admin configuration."""
    list_display = ['user', 'environment_name', 'is_active', 'created']
    list_filter = ['environment_name', 'is_active', 'created']
    search_fields = ['user__username', 'environment_name']
