#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/mystate/urls.py
#   MyState URLs - API endpoint routing
#   URL configuration for mystate API
#..............................................................

"""
   MyState URLs - API Endpoint Routing.

   URL patterns for mystate API endpoints using DRF router.

   Endpoints:
   - /api/mystate/saved/ - SavedState CRUD
   - /api/mystate/shared/ - SharedState read/delete
   - /api/mystate/config/ - MYSTATE_CONFIG exposure
   - /api/mystate/default/ - Get default preset for scope

   Usage:
   Include in main urls.py:
   ```python
   path('api/mystate/', include('sopira_magic.apps.mystate.urls')),
   ```
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SavedStateViewSet,
    SharedStateViewSet,
    config_view,
    default_preset_view,
)

# Create router for viewsets
router = DefaultRouter()
router.register(r'saved', SavedStateViewSet, basename='savedstate')
router.register(r'shared', SharedStateViewSet, basename='sharedstate')

app_name = 'mystate'

urlpatterns = [
    # ViewSet routes
    path('', include(router.urls)),
    
    # Function-based views
    path('config/', config_view, name='config'),
    path('default/', default_preset_view, name='default'),
]
