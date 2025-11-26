#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/productionline/apps.py
#   ProductionLine App Config - Django app configuration
#   Production line management application configuration
#..............................................................

"""
   ProductionLine App Config - Django App Configuration.

   Django AppConfig for productionline application.
   Manages production line entities with config-driven relations.

   Configuration:
   - App name: sopira_magic.apps.productionline
   - Verbose name: Productionline
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - Relations handled via relation app (config-driven, not hardcoded)
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class ProductionlineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.productionline'
    verbose_name = 'Productionline'
