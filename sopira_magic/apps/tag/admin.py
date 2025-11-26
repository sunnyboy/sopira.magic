#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/tag/admin.py
#   Tag Admin - Django admin configuration
#   Admin interface for Tag and TaggedItem models
#..............................................................

"""
   Tag Admin - Django Admin Configuration.

   Django admin interface configuration for Tag and TaggedItem models.
   Provides management interface for tagging system.

   Admin Classes:

   1. TagAdmin
      - Displays: name, color, created
      - Filters: created
      - Search: name

   2. TaggedItemAdmin
      - Displays: tag, content_type, object_id, created
      - Filters: content_type, created
      - Search: tag name
"""

from django.contrib import admin
from .models import Tag, TaggedItem


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Tag admin configuration."""
    list_display = ['name', 'color', 'created']
    list_filter = ['created']
    search_fields = ['name']


@admin.register(TaggedItem)
class TaggedItemAdmin(admin.ModelAdmin):
    """TaggedItem admin configuration."""
    list_display = ['tag', 'content_type', 'object_id', 'created']
    list_filter = ['content_type', 'created']
    search_fields = ['tag__name']
