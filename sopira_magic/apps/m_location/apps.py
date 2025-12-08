#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_location/apps.py
#   Location App Config - Django app configuration
#   Location management application configuration
#..............................................................

"""
   Location App Config - Django App Configuration.

   Django AppConfig for location application.
   Manages location entities with config-driven relations.

   Configuration:
   - App name: sopira_magic.apps.m_location
   - Verbose name: Location
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - Relations handled via relation app (config-driven, not hardcoded)
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class LocationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.m_location'
    label = 'location'
    verbose_name = 'Location'

