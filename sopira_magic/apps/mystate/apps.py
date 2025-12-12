#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/mystate/apps.py
#   MyState App Config - Django app configuration
#   Modern UI state persistence application configuration
#..............................................................

"""
   MyState App Config - Django App Configuration.

   Django AppConfig for mystate application.
   Manages UI state persistence with LocalStorage + Database architecture.
   Uses STATE database (routed via DatabaseRouter).

   Configuration:
   - App name: sopira_magic.apps.mystate
   - Verbose name: MyState
   - Default auto field: BigAutoField
   - Database: state (shared with legacy state module)

   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - Cross-database references use UUID (not ForeignKey) for User
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class MyStateConfig(AppConfig):
    """Django AppConfig for mystate application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.mystate'
    verbose_name = 'MyState'
