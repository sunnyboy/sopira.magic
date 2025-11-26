#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/internationalization/admin.py
#   Internationalization Admin - Django admin configuration
#   Admin interface for Translation model
#..............................................................

"""
   Internationalization Admin - Django Admin Configuration.

   Django admin interface configuration for Translation model.
   Provides management interface for translations and i18n.

   Admin Classes:

   TranslationAdmin
   - Displays: key, language, context, created
   - Filters: language, context, created
   - Search: key, value
"""

from django.contrib import admin
from .models import Translation


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    """Translation admin configuration."""
    list_display = ['key', 'language', 'context', 'created']
    list_filter = ['language', 'context', 'created']
    search_fields = ['key', 'value']
