#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/core/apps.py
#   Core App Config - Django app configuration
#   Core application configuration
#..............................................................

"""
   Core App Config - Django App Configuration.

   Django AppConfig for core application.
   Provides base models, utilities, and middleware for the project.

   Configuration:
   - App name: sopira_magic.apps.core
   - Verbose name: Core
   - Default auto field: BigAutoField
   
   Signals:
   - Automatically registers universal cross-database cascade delete signals
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.core'
    verbose_name = 'Core'
    
    def ready(self):
        """Register signals when app is ready."""
        import sopira_magic.apps.core.signals  # noqa: F401

