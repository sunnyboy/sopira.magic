#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/photo/admin.py
#   Photo Admin - Django admin configuration
#   Admin interface for Photo model
#..............................................................

"""
   Photo Admin - Django Admin Configuration.

   Django admin interface configuration for Photo model.
   Extends NamedWithCodeModelAdmin with photo-specific fields.

   Admin Classes:

   PhotoAdmin (extends NamedWithCodeModelAdmin)
   - Displays: code, name, width, height, file_size, active, visible
   - Filters: active, visible
   - Search: code, name
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import Photo


@admin.register(Photo)
class PhotoAdmin(NamedWithCodeModelAdmin):
    """Photo admin configuration."""
    list_display = ['code', 'name', 'width', 'height', 'file_size', 'active', 'visible']
    list_filter = ['active', 'visible']
    search_fields = ['code', 'name']
