#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/search/admin.py
#   Search Admin - Django admin configuration
#   Admin interface for SearchConfig model
#..............................................................

"""
   Search Admin - Django Admin Configuration.

   Django admin interface configuration for SearchConfig model.
   Provides management interface for Elasticsearch index configuration.

   Admin Classes:

   SearchConfigAdmin
   - Displays: model_name, index_name, enabled, created
   - Filters: enabled, created
   - Search: model_name, index_name
"""

from django.contrib import admin
from .models import SearchConfig


@admin.register(SearchConfig)
class SearchConfigAdmin(admin.ModelAdmin):
    """SearchConfig admin configuration."""
    list_display = ['model_name', 'index_name', 'enabled', 'created']
    list_filter = ['enabled', 'created']
    search_fields = ['model_name', 'index_name']
