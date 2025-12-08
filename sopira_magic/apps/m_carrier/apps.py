#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_carrier/apps.py
#   Carrier App Config - Django app configuration
#   Carrier management application configuration
#..............................................................

"""
   Carrier App Config - Django App Configuration.

   Django AppConfig for carrier application.
   Manages carrier entities with config-driven relations.

   Configuration:
   - App name: sopira_magic.apps.m_carrier
   - Verbose name: Carrier
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - Relations handled via relation app (config-driven, not hardcoded)
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class CarrierConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.m_carrier'
    label = 'carrier'
    verbose_name = 'Carrier'

