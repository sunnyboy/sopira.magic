#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/utility/apps.py
#   Utility App Config - Django app configuration
#   Utility management application configuration
#..............................................................

"""
   Utility App Config - Django App Configuration.

   Django AppConfig for utility application.
   Manages utility entities with config-driven relations.

   Configuration:
   - App name: sopira_magic.apps.utility
   - Verbose name: Utility
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class UtilityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.m_utility'
    label = 'utility'
    verbose_name = 'Utility'
