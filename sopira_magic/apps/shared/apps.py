#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/shared/apps.py
#   Shared App Config - Django app configuration
#   Shared utilities and base classes configuration
#..............................................................

"""
   Shared App Config - Django App Configuration.

   Django AppConfig for shared application.
   Provides reusable utilities, mixins, decorators, and base models.

   Configuration:
   - App name: sopira_magic.apps.shared
   - Verbose name: Shared
   - Default auto field: BigAutoField

   Features:
   - Shared base models (SharedBaseModel, SharedNamedModel)
   - Utility functions (caching, formatting, attribute access)
   - Reusable decorators (cache_result, require_permission, timing)
   - Model mixins (CreatedByMixin, SoftDeleteMixin, etc.)
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class SharedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.shared'
    verbose_name = 'Shared'
