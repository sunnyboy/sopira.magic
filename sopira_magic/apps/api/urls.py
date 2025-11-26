#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/api/urls.py
#   API URLs - API Gateway URL routing
#   URL patterns for API Gateway endpoints
#..............................................................

"""
   API URLs - API Gateway URL Routing.

   URL configuration for API Gateway endpoints.
   All routes are prefixed with /api/ in main urls.py.

   URL Patterns:
   - /api/keys/ - API key management (CRUD)
   - /api/keys/{id}/regenerate/ - Regenerate API key (POST)
   - /api/versions/ - API version listing (read-only)

   App Name: api
   Router: DefaultRouter (DRF)
   Full URL examples:
   - /api/keys/
   - /api/versions/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'keys', views.APIKeyViewSet, basename='apikey')
router.register(r'versions', views.APIVersionViewSet, basename='apiversion')

urlpatterns = [
    path('', include(router.urls)),
]

