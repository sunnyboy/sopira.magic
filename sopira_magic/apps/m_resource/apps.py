#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/resource/apps.py
#   Resource App Config - Django app configuration
#   Resource management application configuration
#..............................................................

"""
   Resource App Config - Django App Configuration.

   Django AppConfig for resource application.
   Manages resource entities with config-driven relations.

   Configuration:
   - App name: sopira_magic.apps.resource
   - Verbose name: Resource
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class ResourceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.m_resource'
    label = 'resource'
    verbose_name = 'Resource'
