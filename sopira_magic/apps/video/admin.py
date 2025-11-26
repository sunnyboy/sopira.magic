#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/video/admin.py
#   Video Admin - Django admin configuration
#   Admin interface for Video model
#..............................................................

"""
   Video Admin - Django Admin Configuration.

   Django admin interface configuration for Video model.
   Extends NamedWithCodeModelAdmin with video-specific fields.

   Admin Classes:

   VideoAdmin (extends NamedWithCodeModelAdmin)
   - Displays: code, name, duration, file_size, active, visible
   - Filters: active, visible
   - Search: code, name
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import Video


@admin.register(Video)
class VideoAdmin(NamedWithCodeModelAdmin):
    """Video admin configuration."""
    list_display = ['code', 'name', 'duration', 'file_size', 'active', 'visible']
    list_filter = ['active', 'visible']
    search_fields = ['code', 'name']
