#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_driver/apps.py
#   Driver App Config - Django app configuration
#   Driver management application configuration
#..............................................................

"""
   Driver App Config - Django App Configuration.

   Django AppConfig for driver application.
   Manages driver entities with config-driven relations.

   Configuration:
   - App name: sopira_magic.apps.m_driver
   - Verbose name: Driver
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - Relations handled via relation app (config-driven, not hardcoded)
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class DriverConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.m_driver'
    label = 'driver'
    verbose_name = 'Driver'

