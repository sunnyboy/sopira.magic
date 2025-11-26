#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/caching/apps.py
#   Caching App Config - Django app configuration
#   Cache configuration system
#..............................................................

"""
   Caching App Config - Django App Configuration.

   Django AppConfig for caching application.
   Manages cache configuration and TTL settings.

   Configuration:
   - App name: sopira_magic.apps.caching
   - Verbose name: Caching
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class CachingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.caching'
    verbose_name = 'Caching'
