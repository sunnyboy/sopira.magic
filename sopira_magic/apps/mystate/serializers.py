#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/mystate/serializers.py
#   MyState Serializers - DRF serializers for state management
#   Proper serialization with validation
#..............................................................

"""
   MyState Serializers - DRF Serializers for State Management.

   Serializers for SavedState and SharedState models with proper
   validation and computed fields.

   Serializers:
   - SavedStateSerializer: Full serializer for saved presets
   - SavedStateListSerializer: Lightweight list serializer
   - SharedStateSerializer: Serializer for sharing relationships
   - ShareCreateSerializer: For creating new shares

   Important:
   - NO HARDCODING: Validation uses MYSTATE_CONFIG
   - Cross-DB user lookup done in views, not serializers
"""

from rest_framework import serializers
from .models import SavedState, SharedState
from .config import validate_scope_type, get_scope_types, get_child_scopes, SCOPE_HIERARCHY


# =============================================================================
# CHILD STATE SNAPSHOT SERIALIZER
# =============================================================================

class ChildStateSnapshotSerializer(serializers.Serializer):
    """
    Serializer for a child scope's state snapshot within parent preset.
    
    Used in children_state field of SavedState.
    """
    preset_name = serializers.CharField(
        required=False, 
        allow_null=True,
        help_text="Name of active preset (if child has named preset)"
    )
    preset_id = serializers.UUIDField(
        required=False, 
        allow_null=True,
        help_text="UUID of active preset (if child has named preset)"
    )
    state_data = serializers.DictField(
        required=True,
        help_text="Raw state data for the child scope"
    )


# =============================================================================
# SAVED STATE SERIALIZERS
# =============================================================================

class SavedStateSerializer(serializers.ModelSerializer):
    """
    Full serializer for SavedState model.
    
    Includes validation and computed fields.
    Supports hierarchical children_state for cascading presets.
    """
    
    # Read-only computed fields
    scope_display = serializers.SerializerMethodField()
    child_preset_names = serializers.SerializerMethodField()
    
    # Children state - validated dict of child snapshots
    children_state = serializers.DictField(
        child=ChildStateSnapshotSerializer(),
        required=False,
        allow_empty=True,
        help_text="Hierarchical snapshot of child scopes"
    )
    
    class Meta:
        model = SavedState
        fields = [
            'id',
            'uuid',
            'user_id',
            'scope_type',
            'scope_key',
            'preset_name',
            'description',
            'state_data',
            'children_state',
            'is_default',
            'created',
            'updated',
            # Computed fields
            'scope_display',
            'child_preset_names',
        ]
        read_only_fields = ['id', 'uuid', 'user_id', 'created', 'updated']
    
    def get_scope_display(self, obj) -> str:
        """Human-readable scope identifier."""
        return f"{obj.scope_type}:{obj.scope_key}"
    
    def get_child_preset_names(self, obj) -> dict:
        """Get mapping of child scope types to their active preset names."""
        return obj.get_child_preset_names() if hasattr(obj, 'get_child_preset_names') else {}
    
    def validate_scope_type(self, value: str) -> str:
        """Validate scope_type against MYSTATE_CONFIG."""
        if not validate_scope_type(value):
            valid_types = get_scope_types()
            raise serializers.ValidationError(
                f"Invalid scope_type '{value}'. Must be one of: {valid_types}"
            )
        return value
    
    def validate_preset_name(self, value: str) -> str:
        """Validate preset name is not empty and reasonable length."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Preset name cannot be empty.")
        if len(value) > 255:
            raise serializers.ValidationError("Preset name cannot exceed 255 characters.")
        return value
    
    def validate_children_state(self, value):
        """
        Validate children_state contains only valid child scope types.
        """
        if not value:
            return value
        
        # Get the scope_type from initial_data or instance
        scope_type = self.initial_data.get('scope_type')
        if not scope_type and self.instance:
            scope_type = self.instance.scope_type
        
        if scope_type:
            valid_children = get_child_scopes(scope_type)
            for child_scope in value.keys():
                if child_scope not in valid_children:
                    raise serializers.ValidationError(
                        f"Invalid child scope '{child_scope}' for parent scope '{scope_type}'. "
                        f"Valid children are: {valid_children}"
                    )
        
        return value
    
    def validate(self, attrs):
        """Cross-field validation."""
        # Check for duplicate preset name within same user+scope (on create)
        if not self.instance:  # Creating new
            user_id = self.context.get('user_id')
            scope_type = attrs.get('scope_type')
            scope_key = attrs.get('scope_key')
            preset_name = attrs.get('preset_name')
            
            if user_id and scope_type and scope_key and preset_name:
                exists = SavedState.objects.using('state').filter(
                    user_id=user_id,
                    scope_type=scope_type,
                    scope_key=scope_key,
                    preset_name=preset_name
                ).exists()
                
                if exists:
                    raise serializers.ValidationError({
                        'preset_name': f"Preset '{preset_name}' already exists for this scope."
                    })
        
        return attrs


class SavedStateListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing saved states.
    
    Excludes full state_data and children_state for performance.
    Includes summary information about children.
    """
    
    scope_display = serializers.SerializerMethodField()
    state_summary = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()
    child_preset_names = serializers.SerializerMethodField()
    
    class Meta:
        model = SavedState
        fields = [
            'id',
            'uuid',
            'scope_type',
            'scope_key',
            'preset_name',
            'description',
            'is_default',
            'created',
            'updated',
            # Computed fields
            'scope_display',
            'state_summary',
            'has_children',
            'child_preset_names',
        ]
    
    def get_scope_display(self, obj) -> str:
        return f"{obj.scope_type}:{obj.scope_key}"
    
    def get_state_summary(self, obj) -> dict:
        """Summary of state data (keys only, not full values)."""
        if obj.state_data:
            return {
                'keys': list(obj.state_data.keys()),
                'size': len(str(obj.state_data)),
            }
        return {'keys': [], 'size': 0}
    
    def get_has_children(self, obj) -> bool:
        """Check if preset has children state."""
        return obj.has_children() if hasattr(obj, 'has_children') else bool(obj.children_state)
    
    def get_child_preset_names(self, obj) -> dict:
        """Get mapping of child scope types to their active preset names."""
        return obj.get_child_preset_names() if hasattr(obj, 'get_child_preset_names') else {}


class SharedStateSerializer(serializers.ModelSerializer):
    """
    Serializer for SharedState model.
    
    Includes nested preset info and user display names.
    """
    
    # Nested preset (read-only)
    source_preset_detail = SavedStateListSerializer(source='source_preset', read_only=True)
    
    class Meta:
        model = SharedState
        fields = [
            'id',
            'uuid',
            'source_preset',
            'source_preset_detail',
            'shared_by_id',
            'shared_with_id',
            'can_edit',
            'created',
            'updated',
        ]
        read_only_fields = ['id', 'uuid', 'shared_by_id', 'created', 'updated']


class ShareCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new share.
    
    Used for POST /api/mystate/saved/{id}/share/
    """
    
    shared_with_id = serializers.UUIDField(
        help_text="UUID of user to share with"
    )
    can_edit = serializers.BooleanField(
        default=False,
        help_text="Can the recipient edit this preset?"
    )
    
    def validate_shared_with_id(self, value):
        """Validate the target user exists (done in view for cross-DB)."""
        # Cross-DB validation happens in view
        return value
    
    def validate(self, attrs):
        """Ensure not sharing with self."""
        user_id = self.context.get('user_id')
        shared_with_id = attrs.get('shared_with_id')
        
        if user_id and shared_with_id and str(user_id) == str(shared_with_id):
            raise serializers.ValidationError({
                'shared_with_id': "Cannot share preset with yourself."
            })
        
        return attrs


class ConfigSerializer(serializers.Serializer):
    """
    Serializer for exposing MYSTATE_CONFIG to frontend.
    
    Used for GET /api/mystate/config/
    """
    
    scopes = serializers.DictField()
    state_fields = serializers.DictField()
    debounce = serializers.DictField()
    localStorage_prefix = serializers.CharField()
    localStorage_version = serializers.IntegerField()
