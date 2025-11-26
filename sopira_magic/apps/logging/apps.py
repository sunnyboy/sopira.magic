#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/logging/apps.py
#   Logging App Config - Django app configuration
#   Application logging system configuration
#..............................................................

"""
   Logging App Config - Django App Configuration.

   Django AppConfig for logging application.
   Manages system logs, audit trails, and performance metrics.
   Uses LOGGING database (routed via DatabaseRouter).

   Configuration:
   - App name: sopira_magic.apps.logging
   - Verbose name: Logging
   - Default auto field: BigAutoField
   - Database: logging (separate from PRIMARY)
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class LoggingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.logging'
    verbose_name = 'Logging'
