#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/mystate/views.py
#   MyState Views - DRF ViewSets for state management API
#   Proper REST API with ViewSets
#..............................................................

"""
   MyState Views - DRF ViewSets for State Management API.

   ViewSets for SavedState and SharedState with proper REST patterns.
   All queries use STATE database via .using('state').

   ViewSets:
   - SavedStateViewSet: CRUD for saved presets with custom actions
   - SharedStateViewSet: Read/delete for shared presets
   - ConfigView: Expose MYSTATE_CONFIG to frontend

   Important:
   - All DB operations use .using('state')
   - User validation done via cross-DB lookup
   - NO HARDCODING: Uses MYSTATE_CONFIG for validation
"""

import logging
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import SavedState, SharedState
from .serializers import (
    SavedStateSerializer,
    SavedStateListSerializer,
    SharedStateSerializer,
    ShareCreateSerializer,
    ConfigSerializer,
)
from .config import MYSTATE_CONFIG, validate_scope_type, get_child_scopes, SCOPE_HIERARCHY

logger = logging.getLogger(__name__)


class SavedStateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SavedState CRUD operations.
    
    Endpoints:
    - GET /api/mystate/saved/ - List user's saved states
    - POST /api/mystate/saved/ - Create new saved state
    - GET /api/mystate/saved/{id}/ - Get specific saved state
    - PATCH /api/mystate/saved/{id}/ - Update saved state
    - DELETE /api/mystate/saved/{id}/ - Delete saved state
    - POST /api/mystate/saved/{id}/set-default/ - Set as default
    - POST /api/mystate/saved/{id}/share/ - Share with another user
    
    Query params:
    - scope_type: Filter by scope type ('table', 'page', 'global')
    - scope_key: Filter by scope key (e.g., 'companies')
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return SavedStateListSerializer
        return SavedStateSerializer
    
    def get_queryset(self):
        """
        Get queryset filtered by current user.
        Uses STATE database.
        """
        user = self.request.user
        queryset = SavedState.objects.using('state').filter(user_id=user.id)
        
        # Filter by scope_type if provided
        scope_type = self.request.query_params.get('scope_type')
        if scope_type:
            queryset = queryset.filter(scope_type=scope_type)
        
        # Filter by scope_key if provided
        scope_key = self.request.query_params.get('scope_key')
        if scope_key:
            queryset = queryset.filter(scope_key=scope_key)
        
        return queryset.order_by('-updated', 'preset_name')
    
    def get_serializer_context(self):
        """Add user_id to serializer context."""
        context = super().get_serializer_context()
        if self.request.user.is_authenticated:
            context['user_id'] = self.request.user.id
        return context
    
    def perform_create(self, serializer):
        """Set user_id on create."""
        serializer.save(user_id=self.request.user.id)
    
    def create(self, request, *args, **kwargs):
        """
        Create with proper database routing.
        
        Supports hierarchical presets with children_state.
        Frontend should provide children_state if saving a parent scope
        that has active child presets.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        
        # Extract children_state if provided
        children_state = validated_data.pop('children_state', None)
        
        # Create using STATE database
        instance = SavedState.objects.using('state').create(
            user_id=request.user.id,
            **validated_data
        )
        
        # Set children_state if provided
        if children_state:
            instance.children_state = children_state
            instance.save(using='state')
        
        output_serializer = SavedStateSerializer(instance, context=self.get_serializer_context())
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update with proper database routing."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Update fields
        for attr, value in serializer.validated_data.items():
            setattr(instance, attr, value)
        instance.save(using='state')
        
        output_serializer = SavedStateSerializer(instance, context=self.get_serializer_context())
        return Response(output_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete with proper database routing."""
        instance = self.get_object()
        instance.delete(using='state')
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'], url_path='set-default')
    def set_default(self, request, pk=None):
        """
        Set this preset as the default for its scope.
        
        POST /api/mystate/saved/{id}/set-default/
        """
        instance = self.get_object()
        instance.is_default = True
        instance.save(using='state')  # save() handles unsetting other defaults
        
        serializer = SavedStateSerializer(instance, context=self.get_serializer_context())
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='load')
    def load(self, request, pk=None):
        """
        Load preset with full hierarchical state for cascading application.
        
        GET /api/mystate/saved/{id}/load/
        
        Returns:
        - Full preset data including state_data and children_state
        - For each child in children_state, includes:
          - preset_name: Name of child's active preset (if any)
          - preset_id: UUID of child's active preset (if any)
          - state_data: Raw state data to apply
        
        Frontend should use this to:
        1. Apply own state_data to current scope
        2. For each child in children_state:
           - Apply child's state_data to the child scope
           - Update child's activePresetName if preset_name is provided
        """
        instance = self.get_object()
        
        # Return full serialized data including children_state
        serializer = SavedStateSerializer(instance, context=self.get_serializer_context())
        
        return Response({
            **serializer.data,
            # Add metadata about hierarchy
            '_hierarchy': {
                'valid_children': get_child_scopes(instance.scope_type),
                'has_children': instance.has_children(),
            }
        })
    
    @action(detail=True, methods=['post'], url_path='share')
    def share(self, request, pk=None):
        """
        Share this preset with another user.
        
        POST /api/mystate/saved/{id}/share/
        Body: { "shared_with_id": "<uuid>", "can_edit": false }
        """
        instance = self.get_object()
        
        # Validate share request
        serializer = ShareCreateSerializer(
            data=request.data,
            context={'user_id': request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        
        shared_with_id = serializer.validated_data['shared_with_id']
        can_edit = serializer.validated_data.get('can_edit', False)
        
        # Check if share already exists
        existing = SharedState.objects.using('state').filter(
            source_preset=instance,
            shared_with_id=shared_with_id
        ).first()
        
        if existing:
            # Update existing share
            existing.can_edit = can_edit
            existing.save(using='state')
            share = existing
        else:
            # Create new share
            share = SharedState.objects.using('state').create(
                source_preset=instance,
                shared_by_id=request.user.id,
                shared_with_id=shared_with_id,
                can_edit=can_edit,
            )
        
        output_serializer = SharedStateSerializer(share)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class SharedStateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for SharedState (read-only + delete).
    
    Shows presets shared WITH the current user.
    
    Endpoints:
    - GET /api/mystate/shared/ - List presets shared with me
    - GET /api/mystate/shared/{id}/ - Get specific shared preset
    - DELETE /api/mystate/shared/{id}/ - Remove share (unsubscribe)
    
    Query params:
    - scope_type: Filter by scope type
    - scope_key: Filter by scope key
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = SharedStateSerializer
    
    def get_queryset(self):
        """
        Get presets shared with current user.
        Uses STATE database.
        """
        user = self.request.user
        queryset = SharedState.objects.using('state').filter(
            shared_with_id=user.id
        ).select_related('source_preset')
        
        # Filter by scope_type if provided
        scope_type = self.request.query_params.get('scope_type')
        if scope_type:
            queryset = queryset.filter(source_preset__scope_type=scope_type)
        
        # Filter by scope_key if provided
        scope_key = self.request.query_params.get('scope_key')
        if scope_key:
            queryset = queryset.filter(source_preset__scope_key=scope_key)
        
        return queryset.order_by('-created')
    
    def destroy(self, request, *args, **kwargs):
        """
        Remove share (user unsubscribes from shared preset).
        
        DELETE /api/mystate/shared/{id}/
        """
        instance = self.get_object()
        instance.delete(using='state')
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def config_view(request):
    """
    Expose MYSTATE_CONFIG to frontend.
    
    GET /api/mystate/config/
    
    Returns the configuration including:
    - scopes: Scope type definitions
    - state_fields: Available state fields with defaults
    - debounce: Timing configuration
    - localStorage settings
    """
    serializer = ConfigSerializer(MYSTATE_CONFIG)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def default_preset_view(request):
    """
    Get default preset for a scope (if exists).
    
    GET /api/mystate/default/?scope_type=table&scope_key=companies
    
    Returns the default preset for the specified scope, or 404 if none.
    """
    scope_type = request.query_params.get('scope_type')
    scope_key = request.query_params.get('scope_key')
    
    if not scope_type or not scope_key:
        return Response(
            {'detail': 'scope_type and scope_key are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not validate_scope_type(scope_type):
        return Response(
            {'detail': f'Invalid scope_type: {scope_type}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # First check user's own default
    preset = SavedState.objects.using('state').filter(
        user_id=request.user.id,
        scope_type=scope_type,
        scope_key=scope_key,
        is_default=True
    ).first()
    
    if preset:
        serializer = SavedStateSerializer(preset)
        return Response(serializer.data)
    
    # No default found
    return Response(
        {'detail': 'No default preset found for this scope'},
        status=status.HTTP_404_NOT_FOUND
    )
