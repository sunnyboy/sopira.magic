#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/reporting/apps.py
#   Reporting App Config - Django app configuration
#   Report generation system configuration
#..............................................................

"""
   Reporting App Config - Django App Configuration.

   Django AppConfig for reporting application.
   Manages report templates and scheduled report generation.

   Configuration:
   - App name: sopira_magic.apps.reporting
   - Verbose name: Reporting
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class ReportingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.reporting'
    verbose_name = 'Reporting'
