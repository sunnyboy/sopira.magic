#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/mobileapp/admin.py
#   Mobile App Admin - Django admin configuration
#   Admin interface for MobileAppConfig model
#..............................................................

"""
   Mobile App Admin - Django Admin Configuration.

   Django admin interface configuration for MobileAppConfig model.
   Provides management interface for React Native mobile app configuration.

   Admin Classes:

   MobileAppConfigAdmin
   - Displays: app_name, app_version, enabled, created
   - Filters: enabled, created
   - Search: app_name
"""

from django.contrib import admin
from .models import MobileAppConfig


@admin.register(MobileAppConfig)
class MobileAppConfigAdmin(admin.ModelAdmin):
    """MobileAppConfig admin configuration."""
    list_display = ['app_name', 'app_version', 'enabled', 'created']
    list_filter = ['enabled', 'created']
    search_fields = ['app_name']
