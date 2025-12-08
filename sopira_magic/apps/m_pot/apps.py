#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_pot/apps.py
#   Pot App Config - Django app configuration
#   Pot management application configuration
#..............................................................

"""
   Pot App Config - Django App Configuration.

   Django AppConfig for pot application.
   Manages pot entities with config-driven relations.

   Configuration:
   - App name: sopira_magic.apps.m_pot
   - Verbose name: Pot
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - Relations handled via relation app (config-driven, not hardcoded)
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class PotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.m_pot'
    label = 'pot'
    verbose_name = 'Pot'

