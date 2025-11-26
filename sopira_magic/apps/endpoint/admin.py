#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/endpoint/admin.py
#   Endpoint Admin - Django admin configuration
#   Admin interface for Endpoint model
#..............................................................

"""
   Endpoint Admin - Django Admin Configuration.

   Django admin interface configuration for Endpoint model.
   Extends NamedWithCodeModelAdmin with endpoint-specific fields.

   Admin Classes:

   EndpointAdmin (extends NamedWithCodeModelAdmin)
   - Displays: code, name, endpoint_type, status, last_connected, active, visible
   - Filters: endpoint_type, status, active, visible
   - Search: code, name, url
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import Endpoint


@admin.register(Endpoint)
class EndpointAdmin(NamedWithCodeModelAdmin):
    """Endpoint admin configuration."""
    list_display = ['code', 'name', 'endpoint_type', 'status', 'last_connected', 'active', 'visible']
    list_filter = ['endpoint_type', 'status', 'active', 'visible']
    search_fields = ['code', 'name', 'url']
