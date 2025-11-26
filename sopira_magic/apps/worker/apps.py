#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/worker/apps.py
#   Worker App Config - Django app configuration
#   Worker management application configuration
#..............................................................

"""
   Worker App Config - Django App Configuration.

   Django AppConfig for worker application.
   Manages worker/employee entities with config-driven relations.

   Configuration:
   - App name: sopira_magic.apps.worker
   - Verbose name: Worker
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class WorkerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.worker'
    verbose_name = 'Worker'
