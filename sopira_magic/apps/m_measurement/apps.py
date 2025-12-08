#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_measurement/apps.py
#   Measurement App Config - Django app configuration
#   Measurement management application configuration
#..............................................................

"""
   Measurement App Config - Django App Configuration.

   Django AppConfig for measurement application.
   Manages measurement entities with config-driven relations.

   Configuration:
   - App name: sopira_magic.apps.m_measurement
   - Verbose name: Measurement
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - Relations handled via relation app (config-driven, not hardcoded)
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class MeasurementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.m_measurement'
    label = 'measurement'
    verbose_name = 'Measurement'

