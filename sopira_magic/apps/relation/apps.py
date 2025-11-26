#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/relation/apps.py
#   Relation App Config - Django app configuration
#   Dynamic relation system configuration
#..............................................................

"""
   Relation App Config - Django App Configuration.

   Django AppConfig for relation application.
   Manages config-driven dynamic relations between models.

   Configuration:
   - App name: sopira_magic.apps.relation
   - Verbose name: Relation
   - Default auto field: BigAutoField

   Startup Behavior:
   - Automatically initializes RelationRegistry from RELATION_CONFIG on Django startup
   - Runs init_relations management command in background thread
   - Silently fails if database is not ready yet
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - Relations defined in RELATION_CONFIG (SSOT), not hardcoded in models
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class RelationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.relation'
    verbose_name = 'Relation'
    
    def ready(self):
        """Initialize relations from config on Django startup."""
        # Only run in main process, not in worker threads
        import os
        import threading
        
        # Check if we're in the main thread and not during migrations
        if os.environ.get('RUN_MAIN') == 'true':
            # Use threading to defer execution after app initialization
            def init_relations():
                try:
                    from django.core.management import call_command
                    call_command('init_relations', verbosity=0)
                except Exception:
                    # Silently fail if database is not ready yet
                    pass
            
            # Defer execution to avoid database access during app initialization
            threading.Timer(0.1, init_relations).start()