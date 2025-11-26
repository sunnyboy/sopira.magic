#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/alarm/apps.py
#   Alarm App Config - Django app configuration
#   Alarm system configuration
#..............................................................

"""
   Alarm App Config - Django App Configuration.

   Django AppConfig for alarm application.
   Manages alarm rules and escalation policies.

   Configuration:
   - App name: sopira_magic.apps.alarm
   - Verbose name: Alarm
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class AlarmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.alarm'
    verbose_name = 'Alarm'
