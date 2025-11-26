#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/mobileapp/apps.py
#   Mobile App Config - Django app configuration
#   React Native mobile app configuration
#..............................................................

"""
   Mobile App Config - Django App Configuration.

   Django AppConfig for mobileapp application.
   Manages React Native mobile app configuration and settings.

   Configuration:
   - App name: sopira_magic.apps.mobileapp
   - Verbose name: Mobileapp
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class MobileappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.mobileapp'
    verbose_name = 'Mobileapp'
