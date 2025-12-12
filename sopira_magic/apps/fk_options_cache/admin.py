"""
Django admin configuration for FK Options Cache module.
"""

from django.contrib import admin

from .models import CacheConfig, FKOptionsCache


@admin.register(CacheConfig)
class CacheConfigAdmin(admin.ModelAdmin):
    list_display = ("key", "ttl", "enabled", "updated", "created")
    list_filter = ("enabled",)
    search_fields = ("key",)


@admin.register(FKOptionsCache)
class FKOptionsCacheAdmin(admin.ModelAdmin):
    list_display = ("field_name", "factory", "record_count", "factories_count", "updated")
    list_filter = ("field_name", "factory")
    search_fields = ("field_name",)

