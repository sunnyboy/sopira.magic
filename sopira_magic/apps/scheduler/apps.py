#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/scheduler/apps.py
#   Scheduler App Config - Django app configuration
#   Task scheduling system configuration
#..............................................................

"""
   Scheduler App Config - Django App Configuration.

   Django AppConfig for scheduler application.
   Manages scheduled tasks, execution tracking, and retry logic.

   Configuration:
   - App name: sopira_magic.apps.scheduler
   - Verbose name: Scheduler
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class SchedulerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.scheduler'
    verbose_name = 'Scheduler'
