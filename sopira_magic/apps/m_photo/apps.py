#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/photo/apps.py
#   Photo App Config - Django app configuration
#   Photo gallery system configuration
#..............................................................

"""
   Photo App Config - Django App Configuration.

   Django AppConfig for photo application.
   Manages photo gallery and photo metadata.

   Configuration:
   - App name: sopira_magic.apps.photo
   - Verbose name: Photo
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class PhotoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.m_photo'
    label = 'photo'
    verbose_name = 'Photo'
