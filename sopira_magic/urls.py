#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/urls.py
#   URL Configuration - Main project URL routing
#   Root URL dispatcher for sopira.magic project
#..............................................................

"""
   URL Configuration - Main Project URL Routing.

   Root URL dispatcher that routes requests to appropriate app views.
   Central entry point for all URL patterns in the project.

   URL Patterns:
   - /admin/ → Django admin interface
   - /api/auth/ → Authentication endpoints (login, signup, password reset)
   - /api/ → API Gateway endpoints (all API routes)

   Architecture:
   - Modular URL configuration via app-specific urls.py files
   - RESTful API structure under /api/ prefix
   - Authentication endpoints separated under /api/auth/
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('sopira_magic.apps.authentification.urls')),
    path('api/', include('sopira_magic.apps.api.urls')),
]
