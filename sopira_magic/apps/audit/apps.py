#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/audit/apps.py
#   Audit App Config - Django app configuration
#   Audit and compliance system configuration
#..............................................................

"""
   Audit App Config - Django App Configuration.

   Django AppConfig for audit application.
   Provides additional audit functionality beyond basic AuditLog.
   Uses LOGGING database (routed via DatabaseRouter).

   Configuration:
   - App name: sopira_magic.apps.audit
   - Verbose name: Audit
   - Default auto field: BigAutoField
   - Database: logging (separate from PRIMARY)
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.audit'
    verbose_name = 'Audit'
