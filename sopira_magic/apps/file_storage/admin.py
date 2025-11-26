#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/file_storage/admin.py
#   File Storage Admin - Django admin configuration
#   Admin interface for file storage models
#..............................................................

"""
   File Storage Admin - Django Admin Configuration.

   Django admin interface configuration for file storage models.
   Provides management interface for storage configuration and file versions.

   Admin Classes:

   1. StorageConfigAdmin
      - Displays: name, storage_type, is_default, enabled, created
      - Filters: storage_type, is_default, enabled, created
      - Search: name

   2. FileVersionAdmin
      - Displays: file_path, version, storage_config, file_size, created
      - Filters: storage_config, created
      - Search: file_path
      - Ordering: -version (newest first)
"""

from django.contrib import admin
from .models import StorageConfig, FileVersion


@admin.register(StorageConfig)
class StorageConfigAdmin(admin.ModelAdmin):
    """StorageConfig admin configuration."""
    list_display = ['name', 'storage_type', 'is_default', 'enabled', 'created']
    list_filter = ['storage_type', 'is_default', 'enabled', 'created']
    search_fields = ['name']


@admin.register(FileVersion)
class FileVersionAdmin(admin.ModelAdmin):
    """FileVersion admin configuration."""
    list_display = ['file_path', 'version', 'storage_config', 'file_size', 'created']
    list_filter = ['storage_config', 'created']
    search_fields = ['file_path']
    ordering = ['-version']
