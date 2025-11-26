#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/factory/apps.py
#   Factory App Config - Django app configuration
#   Factory management application configuration
#..............................................................

"""
   Factory App Config - Django App Configuration.

   Django AppConfig for factory application.
   Manages factory entities with config-driven relations.

   Configuration:
   - App name: sopira_magic.apps.factory
   - Verbose name: Factory
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - Relations handled via relation app (config-driven, not hardcoded)
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class FactoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.factory'
    verbose_name = 'Factory'
