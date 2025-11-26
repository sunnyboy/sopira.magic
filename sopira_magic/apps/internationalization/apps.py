#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/internationalization/apps.py
#   Internationalization App Config - Django app configuration
#   Translation and i18n system configuration
#..............................................................

"""
   Internationalization App Config - Django App Configuration.

   Django AppConfig for internationalization application.
   Manages translations and multi-language support.

   Configuration:
   - App name: sopira_magic.apps.internationalization
   - Verbose name: Internationalization
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class InternationalizationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.internationalization'
    verbose_name = 'Internationalization'
