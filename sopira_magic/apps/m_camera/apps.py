#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_camera/apps.py
#   Camera App Config - Django app configuration
#   Camera management application configuration
#..............................................................

"""
   Camera App Config - Django App Configuration.

   Django AppConfig for camera application.
   Manages camera entities with config-driven relations.

   Configuration:
   - App name: sopira_magic.apps.m_camera
   - Verbose name: Camera
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - Relations handled via relation app (config-driven, not hardcoded)
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class CameraConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.m_camera'
    label = 'camera'
    verbose_name = 'Camera'

