#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/asgi.py
#   ASGI Configuration - ASGI config
#   ASGI application entry point for async deployment
#..............................................................

"""
   ASGI Configuration - ASGI Config.

   ASGI config for sopira_magic project.
   Exposes the ASGI callable as a module-level variable named ``application``.

   Usage:
   - Used by production ASGI servers (Daphne, Uvicorn, etc.)
   - Sets Django settings module: sopira_magic.settings
   - Entry point for ASGI-compatible servers (WebSocket support)

   For more information:
   https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sopira_magic.settings')

application = get_asgi_application()
