#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/alarm/admin.py
#   Alarm Admin - Django admin configuration
#   Admin interface for alarm models
#..............................................................

"""
   Alarm Admin - Django Admin Configuration.

   Django admin interface configuration for alarm models.
   Provides management interface for alarm rules and escalations.

   Admin Classes:

   1. AlarmRuleAdmin
      - Displays: name, rule_type, enabled, created
      - Filters: rule_type, enabled, created
      - Search: name

   2. AlarmEscalationAdmin
      - Displays: rule, level, delay_minutes, created
      - Filters: created
      - Ordering: rule, level
"""

from django.contrib import admin
from .models import AlarmRule, AlarmEscalation


@admin.register(AlarmRule)
class AlarmRuleAdmin(admin.ModelAdmin):
    """AlarmRule admin configuration."""
    list_display = ['name', 'rule_type', 'enabled', 'created']
    list_filter = ['rule_type', 'enabled', 'created']
    search_fields = ['name']


@admin.register(AlarmEscalation)
class AlarmEscalationAdmin(admin.ModelAdmin):
    """AlarmEscalation admin configuration."""
    list_display = ['rule', 'level', 'delay_minutes', 'created']
    list_filter = ['created']
    ordering = ['rule', 'level']
