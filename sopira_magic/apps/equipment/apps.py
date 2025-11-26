#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/equipment/apps.py
#   Equipment App Config - Django app configuration
#   Equipment management application configuration
#..............................................................

"""
   Equipment App Config - Django App Configuration.

   Django AppConfig for equipment application.
   Manages equipment/asset entities with config-driven relations.

   Configuration:
   - App name: sopira_magic.apps.equipment
   - Verbose name: Equipment
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class EquipmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.equipment'
    verbose_name = 'Equipment'
