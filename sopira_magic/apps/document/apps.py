#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/document/apps.py
#   Document App Config - Django app configuration
#   Document management system configuration
#..............................................................

"""
   Document App Config - Django App Configuration.

   Django AppConfig for document application.
   Manages document storage and versioning.

   Configuration:
   - App name: sopira_magic.apps.document
   - Verbose name: Document
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class DocumentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.document'
    verbose_name = 'Document'
