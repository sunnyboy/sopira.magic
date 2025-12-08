#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/process/apps.py
#   Process App Config - Django app configuration
#   Business process management application configuration
#..............................................................

"""
   Process App Config - Django App Configuration.

   Django AppConfig for process application.
   Manages business processes and temperature measurements.

   Configuration:
   - App name: sopira_magic.apps.process
   - Verbose name: Process
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class ProcessConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.m_process'
    label = 'process'
    verbose_name = 'Process'
