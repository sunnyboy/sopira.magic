#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/mobileapp/models.py
#   Mobile App Models - Mobile app configuration
#   React Native mobile app settings and configuration
#..............................................................

"""
   Mobile App Models - Mobile App Configuration.

   Models for React Native mobile app configuration and settings.
   Stores mobile app-specific configuration and version information.

   Models:

   MobileAppConfig (extends TimeStampedModel)
   - Mobile app configuration model
   - Fields: app_name, app_version, config (JSON), enabled
   - Stores app name, version, and configuration
   - Can be used for feature flags and app settings

   Usage:
   ```python
   from sopira_magic.apps.mobileapp.models import MobileAppConfig
   config = MobileAppConfig.objects.create(
       app_name='Sopira Magic',
       app_version='1.0.0',
       config={'features': {'push_notifications': True}}
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import TimeStampedModel


class MobileAppConfig(TimeStampedModel):
    """Mobile app configuration model."""
    app_name = models.CharField(max_length=255, db_index=True)
    app_version = models.CharField(max_length=50, blank=True, default="")
    config = models.JSONField(default=dict, blank=True)
    enabled = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Mobile App Config")
        verbose_name_plural = _("Mobile App Configs")
