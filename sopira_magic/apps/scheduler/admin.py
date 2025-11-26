#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/scheduler/admin.py
#   Scheduler Admin - Django admin configuration
#   Admin interface for scheduler models
#..............................................................

"""
   Scheduler Admin - Django Admin Configuration.

   Django admin interface configuration for scheduler models.
   Provides management interface for scheduled tasks and execution logs.

   Admin Classes:

   1. ScheduledTaskAdmin
      - Displays: name, task_type, schedule, enabled, last_run, next_run, created
      - Filters: task_type, enabled, created
      - Search: name

   2. TaskExecutionAdmin
      - Displays: task, status, started_at, completed_at, retry_count, created
      - Filters: status, created
      - Search: task name
      - Read-only: created, updated
"""

from django.contrib import admin
from .models import ScheduledTask, TaskExecution


@admin.register(ScheduledTask)
class ScheduledTaskAdmin(admin.ModelAdmin):
    """ScheduledTask admin configuration."""
    list_display = ['name', 'task_type', 'schedule', 'enabled', 'last_run', 'next_run', 'created']
    list_filter = ['task_type', 'enabled', 'created']
    search_fields = ['name']


@admin.register(TaskExecution)
class TaskExecutionAdmin(admin.ModelAdmin):
    """TaskExecution admin configuration."""
    list_display = ['task', 'status', 'started_at', 'completed_at', 'retry_count', 'created']
    list_filter = ['status', 'created']
    search_fields = ['task__name']
    readonly_fields = ['created', 'updated']
