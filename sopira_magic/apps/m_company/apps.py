#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/company/apps.py
#   Company App Config - Django app configuration
#   Company management application configuration
#..............................................................

"""
   Company App Config - Django App Configuration.

   Django AppConfig for company application.
   Manages company entities with config-driven relations.

   Configuration:
   - App name: sopira_magic.apps.company
   - Verbose name: Company
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - Relations handled via relation app (config-driven, not hardcoded)
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class CompanyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.m_company'
    label = 'company'
    verbose_name = 'Company'
