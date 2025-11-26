#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/video/apps.py
#   Video App Config - Django app configuration
#   Video gallery system configuration
#..............................................................

"""
   Video App Config - Django App Configuration.

   Django AppConfig for video application.
   Manages video gallery and video metadata.

   Configuration:
   - App name: sopira_magic.apps.video
   - Verbose name: Video
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class VideoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.video'
    verbose_name = 'Video'
