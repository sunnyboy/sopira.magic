#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_pit/apps.py
#   Pit App Config - Django app configuration
#   Pit management application configuration
#..............................................................

"""
   Pit App Config - Django App Configuration.

   Django AppConfig for pit application.
   Manages pit entities with config-driven relations.

   Configuration:
   - App name: sopira_magic.apps.m_pit
   - Verbose name: Pit
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - Relations handled via relation app (config-driven, not hardcoded)
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class PitConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.m_pit'
    label = 'pit'
    verbose_name = 'Pit'

