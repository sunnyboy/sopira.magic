#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/caching/admin.py
#   Caching Admin - Django admin configuration
#   Admin interface for CacheConfig model
#..............................................................

"""
   Caching Admin - Django Admin Configuration.

   Django admin interface configuration for CacheConfig model.
   Provides management interface for cache configuration.

   Admin Classes:

   CacheConfigAdmin
   - Displays: key, ttl, enabled, created
   - Filters: enabled, created
   - Search: key
"""

from django.contrib import admin
from .models import CacheConfig


@admin.register(CacheConfig)
class CacheConfigAdmin(admin.ModelAdmin):
    """CacheConfig admin configuration."""
    list_display = ['key', 'ttl', 'enabled', 'created']
    list_filter = ['enabled', 'created']
    search_fields = ['key']
