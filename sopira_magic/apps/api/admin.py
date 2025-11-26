#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/api/admin.py
#   API Admin - Django admin configuration
#   Admin interface for API Gateway models
#..............................................................

"""
   API Admin - Django Admin Configuration.

   Django admin interface configuration for API Gateway models.
   Provides management interface for API keys, versions, and rate limits.

   Admin Classes:

   1. APIKeyAdmin
      - Displays: name, user, rate_limit, enabled, expires_at, created
      - Filters: enabled, created
      - Search: name, key, user username
      - Read-only: key, created, updated

   2. APIVersionAdmin
      - Displays: version, base_url, enabled, deprecated, created
      - Filters: enabled, deprecated, created
      - Search: version, base_url

   3. RateLimitConfigAdmin
      - Displays: endpoint, rate_limit, burst_limit, enabled, created
      - Filters: enabled, created
      - Search: endpoint
"""

from django.contrib import admin
from .models import APIKey, APIVersion, RateLimitConfig


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """APIKey admin configuration."""
    list_display = ['name', 'user', 'rate_limit', 'enabled', 'expires_at', 'created']
    list_filter = ['enabled', 'created']
    search_fields = ['name', 'key', 'user__username']
    readonly_fields = ['key', 'created', 'updated']


@admin.register(APIVersion)
class APIVersionAdmin(admin.ModelAdmin):
    """APIVersion admin configuration."""
    list_display = ['version', 'base_url', 'enabled', 'deprecated', 'created']
    list_filter = ['enabled', 'deprecated', 'created']
    search_fields = ['version', 'base_url']


@admin.register(RateLimitConfig)
class RateLimitConfigAdmin(admin.ModelAdmin):
    """RateLimitConfig admin configuration."""
    list_display = ['endpoint', 'rate_limit', 'burst_limit', 'enabled', 'created']
    list_filter = ['enabled', 'created']
    search_fields = ['endpoint']
