#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/core/admin.py
#   Core Admin - Base admin classes
#   Reusable admin configurations for base models
#..............................................................

"""
Core Admin - Base Admin Classes.

   Reusable Django admin configurations for base abstract models.
   Provides common admin functionality for TimeStampedModel and NamedWithCodeModel.

   Admin Classes:

   1. TimeStampedModelAdmin
      - Base admin for TimeStampedModel
      - Displays: id, uuid, created, updated, active, visible
      - Filters: active, visible, created, updated
      - Read-only: id, uuid, created, updated

   2. NamedWithCodeModelAdmin
      - Base admin for NamedWithCodeModel
      - Displays: code, name, human_id, active, visible, created
      - Filters: active, visible, created
      - Search: code, name, human_id
      - Read-only: id, uuid, created, updated

   Usage:
   ```python
   class CompanyAdmin(NamedWithCodeModelAdmin):
       # Inherits all base functionality
       pass
   ```
"""

from django.contrib import admin
from .models import TimeStampedModel, NamedWithCodeModel


class TimeStampedModelAdmin(admin.ModelAdmin):
    """Base admin class for TimeStampedModel."""
    list_display = ['id', 'uuid', 'created', 'updated', 'active', 'visible']
    list_filter = ['active', 'visible', 'created', 'updated']
    readonly_fields = ['id', 'uuid', 'created', 'updated']


class NamedWithCodeModelAdmin(admin.ModelAdmin):
    """Base admin class for NamedWithCodeModel."""
    list_display = ['code', 'name', 'human_id', 'active', 'visible', 'created']
    list_filter = ['active', 'visible', 'created']
    search_fields = ['code', 'name', 'human_id']
    readonly_fields = ['id', 'uuid', 'created', 'updated']

