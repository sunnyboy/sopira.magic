#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/api/serializers.py
#   API Serializers - Shared serializers for API Gateway
#   Domain-level serializers used by config-driven viewsets
#..............................................................

"""
API Serializers - DRF Serializers for API Gateway.

This module contains serializers used by the config-driven API layer.
Serializers here are still domain-specific, but they are wired through
configuration (VIEWS_MATRIX) instead of being hard-coded into viewsets.

Components:
- UserListSerializer: read-only representation of User rows for admin tables.
- MySerializer: Config-driven serializer factory that auto-generates serializers
  from VIEWS_MATRIX configuration with computed fields and FK display labels.

MySerializer Features:
- Auto-includes all model fields (fields = '__all__')
- Auto-generates computed fields (created_by_username, label, tags)
- Auto-generates FK display labels from fk_display_template
- Integrates with RELATION_CONFIG for FK field discovery
"""

import logging
from typing import Type, Optional, Dict, Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

logger = logging.getLogger(__name__)

User = get_user_model()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_fk_display_label(obj: Any, template: str) -> Optional[str]:
    """
    Generate FK display label from template and object.
    
    Template format: "{code}-{human_id}-{name}"
    Placeholders: {code}, {human_id}, {name}, {id}, {uuid}
    
    Args:
        obj: Related object instance
        template: Template string with placeholders
        
    Returns:
        Formatted display label or None if obj is None
    """
    if obj is None:
        return None
    
    try:
        # Build context from object attributes
        context = {
            'code': getattr(obj, 'code', ''),
            'human_id': getattr(obj, 'human_id', ''),
            'name': getattr(obj, 'name', ''),
            'id': str(getattr(obj, 'id', '')),
            'uuid': str(getattr(obj, 'uuid', '')),
        }
        return template.format(**context)
    except (KeyError, AttributeError) as e:
        logger.warning(f"Failed to generate FK display label: {e}")
        return str(obj)


# =============================================================================
# SERIALIZERS
# =============================================================================

class UserListSerializer(serializers.ModelSerializer):
    """Read-only serializer for listing users in admin tables.

    This serializer is intentionally minimal and stable so it can serve as
    a Single Source of Truth (SSOT) for the users table in the frontend.
    """

    class Meta:
        model = User
        # Fields are part of SSOT for the users table config
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "is_staff",
            "date_joined",
        )
        read_only_fields = fields


class MySerializer(serializers.ModelSerializer):
    """
    Universal Serializer Factory that configures itself from VIEWS_MATRIX.
    
    Config-driven serializer generation - zero hardcode.
    Automatically includes all model fields and adds computed fields from config.
    
    Features:
    - Auto-includes all model fields (fields = '__all__')
    - Auto-generates created_by_username if model has created_by
    - Auto-generates label field if model has code and name
    - Auto-generates tags field if model has tags relation
    - Auto-generates FK display labels from fk_display_template
    
    Usage:
        # In view_factory.py or views.py
        serializer_class = MySerializer.create_serializer("factories")
        
        # Or directly in config
        "serializer_read": None,  # Will use MySerializer.create_serializer()
    """
    
    # Cache for generated serializer classes
    _serializer_cache: Dict[str, Type['MySerializer']] = {}
    
    @classmethod
    def create_serializer(cls, view_name: str) -> Type['MySerializer']:
        """
        Factory method to create configured Serializer from VIEWS_MATRIX.
        
        Dynamically builds Serializer class with:
        - All model fields automatically included (fields = '__all__')
        - Computed fields from config (created_by_username, label, tags, etc.)
        - FK display labels from fk_display_template
        
        Args:
            view_name: Key in VIEWS_MATRIX (e.g., "factories", "cameras")
            
        Returns:
            Configured Serializer class
            
        Raises:
            ValueError: If view_name not found in VIEWS_MATRIX
        """
        # Return cached serializer if available
        if view_name in cls._serializer_cache:
            return cls._serializer_cache[view_name]
        
        # Lazy import to avoid circular imports
        from .view_configs import VIEWS_MATRIX
        
        config = VIEWS_MATRIX.get(view_name)
        if not config:
            raise ValueError(f"View '{view_name}' not found in VIEWS_MATRIX")
        
        model = config['model']
        
        # Build Meta class dynamically
        Meta = type('Meta', (), {
            'model': model,
            'fields': '__all__',
            'read_only_fields': config.get('read_only_fields', ['id', 'uuid', 'created', 'updated']),
        })
        
        # Build serializer attributes
        serializer_attrs: Dict[str, Any] = {'Meta': Meta}
        
        # Add created_by_username if model has created_by field
        if hasattr(model, 'created_by'):
            serializer_attrs['created_by_username'] = serializers.SerializerMethodField()
            serializer_attrs['get_created_by_username'] = lambda self, obj: (
                obj.created_by.username if obj.created_by else None
            )
        
        # Add label field if model has code and name
        if hasattr(model, 'code') and hasattr(model, 'name'):
            serializer_attrs['label'] = serializers.SerializerMethodField()
            serializer_attrs['get_label'] = lambda self, obj: (
                f"{obj.name} ({obj.code})" if obj.code and obj.name 
                else (obj.name or obj.code or str(obj))
            )
        
        # Add tags field if model has tags relation
        if hasattr(model, 'tags'):
            serializer_attrs['tags'] = serializers.SerializerMethodField()
            serializer_attrs['get_tags'] = lambda self, obj: (
                list(obj.tags.select_related("tag").values_list("tag__name", flat=True))
                if hasattr(obj, 'tags') else []
            )
        
        # Add FK display labels based on fk_fields config
        fk_fields = config.get('fk_fields', {})
        if fk_fields:
            for fk_field_name, fk_view_name in fk_fields.items():
                # Get template from FK view config
                fk_view_config = VIEWS_MATRIX.get(fk_view_name, {})
                fk_template = fk_view_config.get('fk_display_template')
                
                if fk_template:
                    display_field_name = f"{fk_field_name}_display_label"
                    serializer_attrs[display_field_name] = serializers.SerializerMethodField()
                    # Create getter with closure to capture fk_field_name and fk_template
                    serializer_attrs[f'get_{display_field_name}'] = cls._create_fk_display_getter(
                        fk_field_name, fk_template
                    )
        
        # Create serializer class
        serializer_class = type(
            f"{model.__name__}Serializer",
            (cls,),
            serializer_attrs
        )
        
        # Cache the serializer
        cls._serializer_cache[view_name] = serializer_class
        
        logger.debug(f"Created serializer for '{view_name}': {serializer_class.__name__}")
        
        return serializer_class
    
    @staticmethod
    def _create_fk_display_getter(fk_field_name: str, template: str):
        """
        Create a getter method for FK display label.
        
        Uses closure to capture fk_field_name and template.
        
        Args:
            fk_field_name: Name of FK field (e.g., "factory")
            template: Display template (e.g., "{code}-{human_id}-{name}")
            
        Returns:
            Getter function for SerializerMethodField
        """
        def getter(self, obj):
            fk_obj = getattr(obj, fk_field_name, None)
            return get_fk_display_label(fk_obj, template=template)
        return getter
    
    @classmethod
    def clear_cache(cls):
        """Clear the serializer cache (useful for testing)."""
        cls._serializer_cache.clear()
