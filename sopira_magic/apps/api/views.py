#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/api/views.py
#   API Views - API Gateway viewsets
#   REST API views for API key and version management
#..............................................................

"""
   API Views - API Gateway Viewsets.

   REST API viewsets for API Gateway functionality.
   Provides endpoints for API key management and API versioning.

   Viewsets:

   1. APIKeyViewSet (ModelViewSet)
      - Full CRUD operations for API keys
      - Custom action: regenerate (POST) - regenerates API key
      - TODO: Add serializer and permissions

   2. APIVersionViewSet (ReadOnlyModelViewSet)
      - Read-only access to API versions
      - Filters: enabled=True
      - TODO: Add serializer

   Endpoints:
   - /api/keys/ - API key management
   - /api/keys/{id}/regenerate/ - Regenerate API key
   - /api/versions/ - API version listing
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import APIKey, APIVersion, RateLimitConfig


class APIKeyViewSet(viewsets.ModelViewSet):
    """API Key management viewset."""
    queryset = APIKey.objects.all()
    # TODO: Add serializer and permissions
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate API key."""
        # TODO: Implement key regeneration
        return Response({'message': 'Key regenerated'})


class APIVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """API Version viewset."""
    queryset = APIVersion.objects.filter(enabled=True)
    # TODO: Add serializer

