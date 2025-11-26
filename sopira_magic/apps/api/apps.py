#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/api/apps.py
#   API App Config - Django app configuration
#   API Gateway application configuration
#..............................................................

"""
   API App Config - Django App Configuration.

   Django AppConfig for API Gateway application.
   Manages API keys, versioning, and rate limiting.

   Configuration:
   - App name: sopira_magic.apps.api
   - Verbose name: Api
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.api'
    verbose_name = 'Api'
