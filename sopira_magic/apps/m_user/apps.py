#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/user/apps.py
#   User App Config - Django app configuration
#   User application configuration
#..............................................................

"""
   User App Config - Django App Configuration.

   Django AppConfig for user application.
   Manages user accounts, preferences, and authentication.

   Configuration:
   - App name: sopira_magic.apps.user
   - Verbose name: User
   - Default auto field: BigAutoField
   - Custom user model: user.User (AUTH_USER_MODEL)
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - Cross-database cascade delete handled by core.signals (universal solution)
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.m_user'
    label = 'user'
    verbose_name = 'User'
