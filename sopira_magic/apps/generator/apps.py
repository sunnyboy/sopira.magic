#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/apps.py
#   Generator App Config - Django app configuration
#   Data generation system configuration
#..............................................................

"""
   Generator App Config - Django App Configuration.

   Django AppConfig for generator application.
   Provides universal data generation for any Django model.

   Configuration:
   - App name: sopira_magic.apps.generator
   - Verbose name: Generator
   - Default auto field: BigAutoField

   Features:
   - Config-driven data generation (SSOT)
   - Universal generator for any model
   - Field type auto-detection
   - Dependency resolution
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - Generator works for any model based on GENERATOR_CONFIG (SSOT)
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class GeneratorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.generator'
    verbose_name = 'Generator'
