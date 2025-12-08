#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_machine/apps.py
#   Machine App Config - Django app configuration
#   Machine management application configuration
#..............................................................

"""
   Machine App Config - Django App Configuration.

   Django AppConfig for machine application.
   Manages machine entities with config-driven relations.

   Configuration:
   - App name: sopira_magic.apps.m_machine
   - Verbose name: Machine
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - Relations handled via relation app (config-driven, not hardcoded)
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class MachineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.m_machine'
    label = 'machine'
    verbose_name = 'Machine'

