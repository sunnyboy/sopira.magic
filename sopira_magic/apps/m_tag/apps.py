#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/tag/apps.py
#   Tag App Config - Django app configuration
#   Tag management system configuration
#..............................................................

"""
   Tag App Config - Django App Configuration.

   Django AppConfig for tag application.
   Manages generic tagging system for any Django model.

   Configuration:
   - App name: sopira_magic.apps.tag
   - Verbose name: Tag
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class TagConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.m_tag'
    label = 'tag'
    verbose_name = 'Tag'
