#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/endpoint/apps.py
#   Endpoint App Config - Django app configuration
#   External endpoint management application configuration
#..............................................................

"""
   Endpoint App Config - Django App Configuration.

   Django AppConfig for endpoint application.
   Manages external endpoints (cameras, sensors, IoT devices).

   Configuration:
   - App name: sopira_magic.apps.endpoint
   - Verbose name: Endpoint
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class EndpointConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.endpoint'
    verbose_name = 'Endpoint'
