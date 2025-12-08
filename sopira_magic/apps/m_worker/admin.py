#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/worker/admin.py
#   Worker Admin - Django admin configuration
#   Admin interface for Worker model
#..............................................................

"""
   Worker Admin - Django Admin Configuration.

   Django admin interface configuration for Worker model.
   Extends NamedWithCodeModelAdmin with worker-specific fields.

   Admin Classes:

   WorkerAdmin (extends NamedWithCodeModelAdmin)
   - Displays: code, name, first_name, last_name, email, active, visible
   - Filters: active, visible
   - Search: code, name, first_name, last_name, email
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import Worker


@admin.register(Worker)
class WorkerAdmin(NamedWithCodeModelAdmin):
    """Worker admin configuration."""
    list_display = ['code', 'name', 'first_name', 'last_name', 'email', 'active', 'visible']
    list_filter = ['active', 'visible']
    search_fields = ['code', 'name', 'first_name', 'last_name', 'email']
