#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/process/admin.py
#   Process Admin - Django admin configuration
#   Admin interface for Process and Measurement models
#..............................................................

"""
   Process Admin - Django Admin Configuration.

   Django admin interface configuration for Process and Measurement models.
   Provides management interface for business processes and temperature measurements.

   Admin Classes:

   1. ProcessAdmin (extends NamedWithCodeModelAdmin)
      - Displays: code, name, process_type, status, started_at, completed_at, active, visible
      - Filters: process_type, status, active, visible

   2. MeasurementAdmin (extends NamedWithCodeModelAdmin)
      - Displays: code, name, temperature, measured_at, active, visible
      - Filters: active, visible
      - Date hierarchy: measured_at
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import Process, Measurement


@admin.register(Process)
class ProcessAdmin(NamedWithCodeModelAdmin):
    """Process admin configuration."""
    list_display = ['code', 'name', 'process_type', 'status', 'started_at', 'completed_at', 'active', 'visible']
    list_filter = ['process_type', 'status', 'active', 'visible']


@admin.register(Measurement)
class MeasurementAdmin(NamedWithCodeModelAdmin):
    """Measurement admin configuration."""
    list_display = ['code', 'name', 'temperature', 'measured_at', 'active', 'visible']
    list_filter = ['active', 'visible']
    date_hierarchy = 'measured_at'
