#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/notification/apps.py
#   Notification App Config - Django app configuration
#   Notification system configuration
#..............................................................

"""
   Notification App Config - Django App Configuration.

   Django AppConfig for notification application.
   Manages notification templates and user preferences.

   Configuration:
   - App name: sopira_magic.apps.notification
   - Verbose name: Notification
   - Default auto field: BigAutoField
   
   Startup Behavior:
   - Automatically registers notification handler with Auth module
   - Enables loose coupling via registry pattern
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.notification'
    verbose_name = 'Notification'
    
    def ready(self):
        """Called when Django starts - register integrations."""
        # Register notification handler with Auth module
        try:
            from .integration import register_with_auth
            register_with_auth()
        except Exception as e:
            # Don't crash on startup if registration fails
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not register notification integration on startup: {e}")
