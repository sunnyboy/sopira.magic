#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/material/apps.py
#   Material App Config - Django app configuration
#   Material management application configuration
#..............................................................

"""
   Material App Config - Django App Configuration.

   Django AppConfig for material application.
   Manages material/raw material entities with config-driven relations.

   Configuration:
   - App name: sopira_magic.apps.material
   - Verbose name: Material
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class MaterialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.m_material'
    label = 'material'
    verbose_name = 'Material'
