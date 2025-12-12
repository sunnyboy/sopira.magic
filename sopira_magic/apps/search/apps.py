#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/search/apps.py
#   Search App Config - Django app configuration
#   Elasticsearch search system configuration
#..............................................................

"""
   Search App Config - Django App Configuration.

   Django AppConfig for search application.
   Manages Elasticsearch index configuration and search functionality.

   Configuration:
   - App name: sopira_magic.apps.search
   - Verbose name: Search
   - Default auto field: BigAutoField
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class SearchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.search'
    verbose_name = 'Search'

    def ready(self):
        # Register signals for automatic indexing
        try:
            from sopira_magic.apps.search.signals import register_model_signals
            register_model_signals()
        except Exception as exc:  # pragma: no cover - startup path
            import logging
            logging.getLogger(__name__).warning("[Search] Nepodarilo sa zaregistrovať signály: %s", exc)
