#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/impex/apps.py
#   Impex App Config - Django app configuration
#   Import/Export system configuration
#..............................................................

"""
   Impex App Config - Django App Configuration.

   Django AppConfig for impex application.
   Manages data import, export, migration, and communication interfaces.

   Configuration:
   - App name: sopira_magic.apps.impex
   - Verbose name: Impex
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class ImpexConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.impex'
    verbose_name = 'Impex'
