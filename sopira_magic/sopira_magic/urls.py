#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/sopira_magic/urls.py
#   URL Configuration - Project package URL routing
#   Alternative URL configuration (duplicate of main urls.py)
#..............................................................

"""
URL Configuration - Project Package URL Routing.

   Alternative URL configuration file in the project package.
   Duplicate of main urls.py for consistency.

   Note: This file may be redundant - main urls.py should be used instead.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('sopira_magic.apps.authentification.urls')),
    path('api/', include('sopira_magic.apps.api.urls')),
]

