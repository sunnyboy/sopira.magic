#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/logging/admin.py
#   Logging Admin - Django admin configuration
#   Admin interface for logging models
#..............................................................

"""
   Logging Admin - Django Admin Configuration.

   Django admin interface configuration for logging models.
   Provides management interface for SystemLog, AuditLog, and PerformanceLog.

   Admin Classes:

   1. SystemLogAdmin
      - Displays: level, message, module, function, timestamp, user_id
      - Filters: level, timestamp
      - Search: message, module, function
      - Read-only: timestamp
      - Date hierarchy: timestamp

   2. AuditLogAdmin
      - Displays: action, user_id, username, model_name, field_name, timestamp
      - Filters: action, model_name, timestamp
      - Search: username, model_name, field_name
      - Read-only: timestamp
      - Date hierarchy: timestamp

   3. PerformanceLogAdmin
      - Displays: endpoint, method, response_time_ms, status_code, timestamp
      - Filters: method, status_code, timestamp
      - Search: endpoint
      - Read-only: timestamp
      - Date hierarchy: timestamp
"""

from django.contrib import admin
from .models import SystemLog, AuditLog, PerformanceLog


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    """SystemLog admin configuration."""
    list_display = ['level', 'message', 'module', 'function', 'timestamp', 'user_id']
    list_filter = ['level', 'timestamp']
    search_fields = ['message', 'module', 'function']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """AuditLog admin configuration."""
    list_display = ['action', 'user_id', 'username', 'model_name', 'field_name', 'timestamp']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['username', 'model_name', 'field_name']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(PerformanceLog)
class PerformanceLogAdmin(admin.ModelAdmin):
    """PerformanceLog admin configuration."""
    list_display = ['endpoint', 'method', 'response_time_ms', 'status_code', 'timestamp']
    list_filter = ['method', 'status_code', 'timestamp']
    search_fields = ['endpoint']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
