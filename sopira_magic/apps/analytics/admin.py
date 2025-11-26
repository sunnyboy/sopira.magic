#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/analytics/admin.py
#   Analytics Admin - Django admin configuration
#   Admin interface for AnalyticsConfig model
#..............................................................

"""
   Analytics Admin - Django Admin Configuration.

   Django admin interface configuration for AnalyticsConfig model.
   Provides management interface for analytics configuration.

   Admin Classes:

   AnalyticsConfigAdmin
   - Displays: name, enabled, created
   - Filters: enabled, created
   - Search: name
"""

from django.contrib import admin
from .models import AnalyticsConfig


@admin.register(AnalyticsConfig)
class AnalyticsConfigAdmin(admin.ModelAdmin):
    """AnalyticsConfig admin configuration."""
    list_display = ['name', 'enabled', 'created']
    list_filter = ['enabled', 'created']
    search_fields = ['name']
