#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/dashboard/apps.py
#   Dashboard App Config - Django app configuration
#   Dashboard application configuration
#..............................................................

"""
   Dashboard App Config - Django App Configuration.

   Django AppConfig for dashboard application.
   Manages dashboard configurations and layouts.

   Configuration:
   - App name: sopira_magic.apps.dashboard
   - Verbose name: Dashboard
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.dashboard'
    verbose_name = 'Dashboard'
