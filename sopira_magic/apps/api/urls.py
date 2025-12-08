#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/api/urls.py
#   API URLs - Config-driven API Gateway URL routing
#   Auto-generated from VIEWS_MATRIX and CUSTOM_ENDPOINTS
#..............................................................

"""
API URLs - Config-Driven API Gateway URL Routing.

   URL configuration for API Gateway endpoints.
   All routes are prefixed with /api/ in main urls.py.

This module uses MyUrls class to auto-generate URL patterns from:
- VIEWS_MATRIX: CRUD endpoints for all configured models
- CUSTOM_ENDPOINTS: Custom endpoints (auth, file uploads, etc.)

URL Generation:
- CRUD endpoints are auto-generated from VIEWS_MATRIX
- Custom endpoints are auto-generated from CUSTOM_ENDPOINTS
- Special viewsets (APIKey, APIVersion) are registered separately

   App Name: api
   Router: DefaultRouter (DRF)
"""

import logging
from typing import Dict, List
from importlib import import_module

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .view_factory import create_viewset
from .view_configs import VIEWS_MATRIX, CUSTOM_ENDPOINTS

logger = logging.getLogger(__name__)


class MyUrls:
    """
    Universal URL generator that configures itself from VIEWS_MATRIX and CUSTOM_ENDPOINTS.
    
    Config-driven URL generation - zero hardcode.
    Dynamically generates:
    - CRUD endpoints from VIEWS_MATRIX
    - Custom endpoints from CUSTOM_ENDPOINTS configuration
    
    Usage:
        urlpatterns = MyUrls.generate_urlpatterns()
    """
    
    # ViewSets that should NOT be auto-generated (have custom implementations)
    EXCLUDED_FROM_AUTO_GENERATION = {
        'users',  # Has custom UserListSerializer, keep separate
        'focusedviews',  # Has custom assign endpoint
        'annotations',  # Has specific config
    }
    
    @staticmethod
    def generate_urlpatterns() -> List:
        """
        Generate all URL patterns from VIEWS_MATRIX and CUSTOM_ENDPOINTS.
        
        Returns:
            List of URL patterns
        """
        router = DefaultRouter()
        
        # Register special viewsets (not in VIEWS_MATRIX)
        router.register(r'keys', views.APIKeyViewSet, basename='apikey')
        router.register(r'versions', views.APIVersionViewSet, basename='apiversion')
        
        # Auto-generate and register CRUD viewsets from VIEWS_MATRIX
        for view_name, config in VIEWS_MATRIX.items():
            # Determine if viewset should be read-only
            # If both serializer_read and serializer_write are None, use MySerializer and allow writes
            # If only serializer_read is set, default to read-only
            serializer_write = config.get('serializer_write')
            serializer_read = config.get('serializer_read')
            
            # If both are None, it's a full CRUD endpoint using MySerializer
            # If only read is set, it's read-only
            # If write is explicitly set, it's full CRUD
            if serializer_read is None and serializer_write is None:
                read_only = False  # Full CRUD with MySerializer
            elif serializer_write is not None:
                read_only = False  # Full CRUD with explicit serializers
            else:
                read_only = True  # Read-only
            
            ViewSet = create_viewset(view_name, read_only=read_only)
            router.register(view_name, ViewSet, basename=view_name)
            logger.debug(f"Registered ViewSet for '{view_name}' (read_only={read_only})")
        
        # Build URL patterns
        urlpatterns = [
            # Custom endpoints from CUSTOM_ENDPOINTS
            *MyUrls._generate_custom_urls(CUSTOM_ENDPOINTS),
            # Router URLs (CRUD endpoints)
            path('', include(router.urls)),
        ]
        
        logger.info(
            f"Generated {len(VIEWS_MATRIX)} CRUD endpoints and "
            f"{len(CUSTOM_ENDPOINTS)} custom endpoints"
        )
        
        return urlpatterns
    
    @staticmethod
    def _generate_custom_urls(endpoints_config: Dict) -> List:
        """
        Generate custom endpoint URLs from configuration.
        
        Dynamically imports view functions and creates URL patterns.
        
        Args:
            endpoints_config: Dictionary of custom endpoint configurations
            
        Returns:
            List of URL patterns
        """
        urlpatterns = []
        
        for endpoint_name, config in endpoints_config.items():
            try:
                # Dynamically import view function
                view_function_path = config['view_function']
                module_path, function_name = view_function_path.rsplit('.', 1)
                module = import_module(module_path)
                view_function = getattr(module, function_name)
                
                # Get URL path
                url_path = config['path']
                url_name = config.get('name', endpoint_name)
                
                # Create URL pattern
                urlpatterns.append(
                    path(url_path, view_function, name=url_name)
                )
                
                logger.debug(f"Registered custom endpoint: {url_path} -> {view_function_path}")
                
            except (ImportError, AttributeError) as e:
                logger.error(f"Failed to import view for endpoint '{endpoint_name}': {e}")
                continue
        
        return urlpatterns


app_name = 'api'

# Auto-generate all URL patterns from VIEWS_MATRIX and CUSTOM_ENDPOINTS
urlpatterns = MyUrls.generate_urlpatterns()

