#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/dashboard/models.py
#   Dashboard Models - Dashboard configuration
#   Dashboard configuration and layout management
#..............................................................

"""
   Dashboard Models - Dashboard Configuration.

   Models for dashboard configuration and layout management.
   Stores dashboard definitions with widgets, layouts, and settings.

   Models:

   Dashboard (extends TimeStampedModel)
   - Dashboard configuration model
   - Fields: name, description, config (JSON), is_default
   - Indexed on: is_default
   - Stores dashboard layout and widget configuration in JSON

   Usage:
   ```python
   from sopira_magic.apps.dashboard.models import Dashboard
   dashboard = Dashboard.objects.create(
       name='Production Dashboard',
       config={'widgets': [...], 'layout': {...}},
       is_default=True
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import TimeStampedModel


class Dashboard(TimeStampedModel):
    """Dashboard configuration model."""
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, default="")
    config = models.JSONField(default=dict, blank=True)
    is_default = models.BooleanField(default=False, db_index=True)
    
    class Meta:
        verbose_name = _("Dashboard")
        verbose_name_plural = _("Dashboards")
        indexes = [
            models.Index(fields=['is_default']),
        ]
