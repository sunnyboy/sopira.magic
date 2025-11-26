#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/reporting/models.py
#   Reporting Models - Report generation system
#   Templates, scheduled reports, and report management
#..............................................................

"""
   Reporting Models - Report Generation System.

   Models for report templates and scheduled report generation.
   Supports multiple report formats (PDF, CSV, Excel).

   Models:

   1. ReportTemplate (extends TimeStampedModel)
      - Report template model
      - Fields: name, report_type, template, config (JSON), enabled
      - Report types: pdf, csv, excel
      - Stores report templates and configuration

   2. ScheduledReport (extends TimeStampedModel)
      - Scheduled report model
      - Fields: name, template (FK), schedule (cron), enabled
      - Links to ReportTemplate
      - Schedule: cron expression for report generation

   Usage:
   ```python
   from sopira_magic.apps.reporting.models import ReportTemplate, ScheduledReport
   template = ReportTemplate.objects.create(
       name='Monthly Production Report',
       report_type='pdf',
       template='...'
   )
   scheduled = ScheduledReport.objects.create(
       name='Monthly Report',
       template=template,
       schedule='0 0 1 * *'  # First day of month
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import TimeStampedModel


class ReportTemplate(TimeStampedModel):
    """Report template model."""
    name = models.CharField(max_length=255, db_index=True)
    report_type = models.CharField(max_length=50, db_index=True)  # pdf, csv, excel
    template = models.TextField(blank=True, default="")
    config = models.JSONField(default=dict, blank=True)
    enabled = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Report Template")
        verbose_name_plural = _("Report Templates")


class ScheduledReport(TimeStampedModel):
    """Scheduled report model."""
    name = models.CharField(max_length=255, db_index=True)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name="scheduled_reports")
    schedule = models.CharField(max_length=255)  # cron expression
    enabled = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Scheduled Report")
        verbose_name_plural = _("Scheduled Reports")
