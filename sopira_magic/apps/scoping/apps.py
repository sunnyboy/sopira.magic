#..............................................................
#   apps/scoping/apps.py
#   Django AppConfig for Scoping Module
#..............................................................

"""
Django AppConfig for Scoping Module.

No initialization needed here - callbacks are registered in core/apps.py.
"""

from django.apps import AppConfig


class ScopingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.scoping'
    verbose_name = 'Scoping Engine'
    
    def ready(self):
        """
        Django app initialization.
        
        Nothing to do here - callbacks are registered by core/apps.py.
        """
        pass




