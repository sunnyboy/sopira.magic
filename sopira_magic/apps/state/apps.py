#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/state/apps.py
#   State App Config - Django app configuration
#   UI state persistence application configuration
#..............................................................

"""
   State App Config - Django App Configuration.

   Django AppConfig for state application.
   Manages UI state persistence and workspace management.
   Uses STATE database (routed via DatabaseRouter).

   Configuration:
   - App name: sopira_magic.apps.state
   - Verbose name: State
   - Default auto field: BigAutoField
   - Database: state (separate from PRIMARY)
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - Cross-database cascade delete handled by core.signals (universal solution)
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class StateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.state'
    verbose_name = 'State'
