#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/api/serializers.py
#   API Serializers - Shared serializers for API Gateway
#   Domain-level serializers used by config-driven viewsets
#..............................................................

"""
API Serializers - DRF Serializers for API Gateway.

This module contains the universal ConfigDriven serializer factory.

Components:
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
from sopira_magic.apps.m_company.models import Company
from sopira_magic.apps.m_factory.models import Factory

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

# -------------------------------------------------------------------------
# [REMOVED] Hardcoded UserListSerializer - now using MySerializer (ConfigDriven)
# -------------------------------------------------------------------------
# UserListSerializer was removed to eliminate:
# 1. Hardcoded serializer (against ConfigDriven&SSOT principle)
# 2. N+1 queries on companies M2M field (PrimaryKeyRelatedField validation)
#
# Users now use MySerializer.create_serializer("users")
# -------------------------------------------------------------------------


# =============================================================================
# GENERIC RELATION TAGS FIELD
# =============================================================================

class GenericRelationTagsField(serializers.ListField):
    """
    Custom writable field for GenericRelation to TaggedItem.
    
    Read: Returns list of tag names
    Write: Accepts list of tag names
    
    ConfigDriven: Works for any model with GenericRelation to TaggedItem.
    """
    child = serializers.CharField()
    
    def to_representation(self, value):
        """Read: return list of tag names from GenericRelation."""
        if hasattr(value, 'select_related'):
            return list(value.select_related("tag").values_list("tag__name", flat=True))
        return []
    
    def to_internal_value(self, data):
        """Write: validate list of tag names."""
        if not isinstance(data, list):
            raise serializers.ValidationError("Tags must be a list")
        return [str(tag).strip() for tag in data if tag]


# =============================================================================
# MY SERIALIZER - UNIVERSAL CONFIG-DRIVEN SERIALIZER FACTORY
# =============================================================================

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
        
        # Add M2M and reverse FK fields (explicit serialization)
        # DRF doesn't auto-serialize M2M with through model, so we add them explicitly
        cls._add_m2m_and_reverse_fk_fields(model, serializer_attrs, view_name)
        
        # If GenericRelation fields detected, add custom update/create methods
        generic_relation_fields = serializer_attrs.pop('_generic_relation_fields', [])
        
        # Always add custom update method (for hooks + tags)
        # This replaces default DRF update to support before_update hooks and GenericRelation
        def update(self, instance, validated_data):
            """
            Custom update to handle:
            1. before_update hooks from config (e.g., SA protection)
            2. GenericRelation (tags) fields
            """
            from sopira_magic.apps.m_tag.models import Tag, TaggedItem
            from django.contrib.contenttypes.models import ContentType
            from sopira_magic.apps.api.view_configs import VIEWS_MATRIX
            
            # Initialize meta collections (ConfigDriven)
            self._meta_warnings = []
            self._meta_info = []
            self._meta_errors = []
            
            # 1. Call before_update hook if defined in config
            before_update_hook = config.get('before_update')
            if before_update_hook:
                request = self.context.get('request')
                result = before_update_hook(instance, validated_data, request)
                
                # Hook can return tuple (validated_data, warnings_list) or just validated_data
                if isinstance(result, tuple):
                    validated_data, warnings = result
                    if warnings and isinstance(warnings, list):
                        self._meta_warnings.extend(warnings)
                else:
                    validated_data = result
            
            # 2. Extract GenericRelation data from initial_data
            tags_data = {}
            for field_name in generic_relation_fields:
                if field_name in self.initial_data:
                    tags_data[field_name] = self.initial_data[field_name]
                    validated_data.pop(field_name, None)
            
            # 3. Standard update for other fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            
            # 4. Update GenericRelation (tags)
            for field_name, tag_names in tags_data.items():
                # Clear existing
                getattr(instance, field_name).all().delete()
                
                # Create new
                if tag_names:
                    content_type = ContentType.objects.get_for_model(instance)
                    for tag_name in tag_names:
                        if tag_name:
                            tag, _ = Tag.objects.get_or_create(name=tag_name.strip())
                            TaggedItem.objects.create(
                                content_type=content_type,
                                object_id=instance.pk,
                                tag=tag
                            )
            
            return instance
        
        serializer_attrs['update'] = update
        
        # Add create method if GenericRelation fields exist
        if generic_relation_fields:
            def create(self, validated_data):
                """Custom create to handle GenericRelation (tags) fields."""
                from sopira_magic.apps.m_tag.models import Tag, TaggedItem
                from django.contrib.contenttypes.models import ContentType
                
                # Extract tags data
                tags_data = {}
                for field_name in generic_relation_fields:
                    if field_name in self.initial_data:
                        tags_data[field_name] = self.initial_data[field_name]
                        validated_data.pop(field_name, None)
                
                # Create instance
                instance = self.Meta.model(**validated_data)
                instance.save()
                
                # Add tags
                for field_name, tag_names in tags_data.items():
                    if tag_names:
                        content_type = ContentType.objects.get_for_model(instance)
                        for tag_name in tag_names:
                            if tag_name:
                                tag, _ = Tag.objects.get_or_create(name=tag_name.strip())
                                TaggedItem.objects.create(
                                    content_type=content_type,
                                    object_id=instance.pk,
                                    tag=tag
                                )
                
                return instance
            
            serializer_attrs['create'] = create
        
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
    def _add_m2m_and_reverse_fk_fields(cls, model, serializer_attrs: Dict[str, Any], view_name: str):
        """
        Add explicit M2M and reverse FK field serialization.
        
        DRF doesn't auto-serialize M2M with through model or reverse FKs,
        so we detect and add them explicitly using PrimaryKeyRelatedField.
        
        Args:
            model: Django model class
            serializer_attrs: Dict to add serializer attributes to
            view_name: View name for special case handling
        """
        # Get model app_label and name for matching
        model_app_label = model._meta.app_label
        model_name = model._meta.object_name
        
        # Detect M2M fields (including those with through model)
        for field in model._meta.get_fields():
            if field.many_to_many and not field.auto_created:
                # M2M field (e.g., Company.users)
                field_name = field.name
                logger.debug(f"[MySerializer] Adding M2M field '{field_name}' for {model_name}")
                serializer_attrs[field_name] = serializers.PrimaryKeyRelatedField(
                    many=True,
                    queryset=field.related_model.objects.all(),
                    required=False
                )
        
        # Detect reverse M2M fields (e.g., User.companies via related_name)
        for related_object in model._meta.related_objects:
            if related_object.many_to_many:
                # Reverse M2M (e.g., User → companies via UserCompany)
                accessor_name = related_object.get_accessor_name()
                logger.debug(f"[MySerializer] Adding reverse M2M field '{accessor_name}' for {model_name}")
                serializer_attrs[accessor_name] = serializers.PrimaryKeyRelatedField(
                    many=True,
                    queryset=related_object.related_model.objects.all(),
                    required=False
                )
        
        # Detect reverse FK fields (e.g., Company → factories)
        for related_object in model._meta.related_objects:
            if related_object.one_to_many and not related_object.field.many_to_many:
                # Reverse FK (e.g., Company → Factory via Factory.company FK)
                accessor_name = related_object.get_accessor_name()
                logger.debug(f"[MySerializer] Adding reverse FK field '{accessor_name}' for {model_name}")
                # Don't specify source if it's the same as accessor_name (DRF assertion)
                serializer_attrs[accessor_name] = serializers.PrimaryKeyRelatedField(
                    many=True,
                    read_only=True  # Reverse FK is read-only, edit via related model
                )
        
        # Detect GenericRelation fields (e.g., tags)
        # ConfigDriven: automatically detects GenericRelation to TaggedItem
        from django.contrib.contenttypes.fields import GenericRelation
        
        for field in model._meta.get_fields():
            if isinstance(field, GenericRelation):
                field_name = field.name
                related_model = field.related_model
                
                # Check if it's pointing to TaggedItem
                if related_model.__name__ == 'TaggedItem':
                    logger.debug(f"[MySerializer] Adding GenericRelation tags field '{field_name}' for {model_name}")
                    
                    # Add writable field
                    serializer_attrs[field_name] = GenericRelationTagsField(
                        required=False,
                        allow_empty=True,
                        help_text=f"List of tag names for {field_name}"
                    )
                    
                    # Mark for custom update/create logic
                    if '_generic_relation_fields' not in serializer_attrs:
                        serializer_attrs['_generic_relation_fields'] = []
                    serializer_attrs['_generic_relation_fields'].append(field_name)
    
    @classmethod
    def clear_cache(cls):
        """Clear the serializer cache (useful for testing)."""
        cls._serializer_cache.clear()


# -------------------------------------------------------------------------
# [REMOVED] Hardcoded CompanySerializer - now using MySerializer (ConfigDriven)
# -------------------------------------------------------------------------
# CompanySerializer was removed to eliminate:
# 1. Hardcoded serializer (against ConfigDriven&SSOT principle)
# 2. N+1 queries on users M2M field (PrimaryKeyRelatedField validation)
# 3. Unnecessary factories field causing N+1 on Factory table
#
# Companies now use MySerializer.create_serializer("companies")
# -------------------------------------------------------------------------
