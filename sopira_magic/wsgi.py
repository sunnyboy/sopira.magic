#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/wsgi.py
#   WSGI Configuration - WSGI config
#   WSGI application entry point for production deployment
#..............................................................

"""
   WSGI Configuration - WSGI Config.

   WSGI config for sopira_magic project.
   Exposes the WSGI callable as a module-level variable named ``application``.

   Usage:
   - Used by production WSGI servers (Gunicorn, uWSGI, etc.)
   - Sets Django settings module: sopira_magic.settings
   - Entry point for WSGI-compatible servers

   For more information:
   https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sopira_magic.settings')

application = get_wsgi_application()
