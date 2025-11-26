#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/apps.py
#   Authentification App Config - Django app configuration
#   Authentication application configuration
#..............................................................

"""
   Authentification App Config - Django App Configuration.

   Django AppConfig for authentication application.
   Manages user authentication, registration, password reset, and 2FA.

   Configuration:
   - App name: sopira_magic.apps.authentification
   - Verbose name: Authentification
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class AuthentificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.authentification'
    verbose_name = 'Authentification'
