#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/file_storage/apps.py
#   File Storage App Config - Django app configuration
#   File storage system configuration
#..............................................................

"""
   File Storage App Config - Django App Configuration.

   Django AppConfig for file_storage application.
   Manages file storage backends (S3, Local, Azure) and versioning.

   Configuration:
   - App name: sopira_magic.apps.file_storage
   - Verbose name: File_storage
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class File_storageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.file_storage'
    verbose_name = 'File_storage'
