#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/reporting/admin.py
#   Reporting Admin - Django admin configuration
#   Admin interface for reporting models
#..............................................................

"""
   Reporting Admin - Django Admin Configuration.

   Django admin interface configuration for reporting models.
   Provides management interface for report templates and scheduled reports.

   Admin Classes:

   1. ReportTemplateAdmin
      - Displays: name, report_type, enabled, created
      - Filters: report_type, enabled, created
      - Search: name

   2. ScheduledReportAdmin
      - Displays: name, template, schedule, enabled, created
      - Filters: enabled, created
      - Search: name
"""

from django.contrib import admin
from .models import ReportTemplate, ScheduledReport


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    """ReportTemplate admin configuration."""
    list_display = ['name', 'report_type', 'enabled', 'created']
    list_filter = ['report_type', 'enabled', 'created']
    search_fields = ['name']


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    """ScheduledReport admin configuration."""
    list_display = ['name', 'template', 'schedule', 'enabled', 'created']
    list_filter = ['enabled', 'created']
    search_fields = ['name']
