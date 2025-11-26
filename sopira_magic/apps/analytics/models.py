#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/analytics/models.py
#   Analytics Models - Analytics configuration
#   Analytics settings and configuration management
#..............................................................

"""
   Analytics Models - Analytics Configuration.

   Models for analytics configuration and settings.
   Stores analytics configuration for different use cases.

   Models:

   AnalyticsConfig (extends TimeStampedModel)
   - Analytics configuration model
   - Fields: name, config (JSON), enabled
   - Stores analytics settings and configuration
   - Can be used for various analytics providers and settings

   Usage:
   ```python
   from sopira_magic.apps.analytics.models import AnalyticsConfig
   config = AnalyticsConfig.objects.create(
       name='Production Analytics',
       config={'provider': 'custom', 'settings': {...}},
       enabled=True
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import TimeStampedModel


class AnalyticsConfig(TimeStampedModel):
    """Analytics configuration model."""
    name = models.CharField(max_length=255, db_index=True)
    config = models.JSONField(default=dict, blank=True)
    enabled = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Analytics Config")
        verbose_name_plural = _("Analytics Configs")
