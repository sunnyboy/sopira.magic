#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/analytics/apps.py
#   Analytics App Config - Django app configuration
#   Analytics system configuration
#..............................................................

"""
   Analytics App Config - Django App Configuration.

   Django AppConfig for analytics application.
   Manages analytics configuration and settings.

   Configuration:
   - App name: sopira_magic.apps.analytics
   - Verbose name: Analytics
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.analytics'
    verbose_name = 'Analytics'
