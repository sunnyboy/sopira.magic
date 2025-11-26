#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/dashboard/admin.py
#   Dashboard Admin - Django admin configuration
#   Admin interface for Dashboard model
#..............................................................

"""
   Dashboard Admin - Django Admin Configuration.

   Django admin interface configuration for Dashboard model.
   Provides management interface for dashboard configurations.

   Admin Classes:

   DashboardAdmin
   - Displays: name, is_default, created, updated
   - Filters: is_default, created
   - Search: name, description
"""

from django.contrib import admin
from .models import Dashboard


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    """Dashboard admin configuration."""
    list_display = ['name', 'is_default', 'created', 'updated']
    list_filter = ['is_default', 'created']
    search_fields = ['name', 'description']
