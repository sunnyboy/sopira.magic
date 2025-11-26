#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/relation/services.py
#   Relation Service - Dynamic relation management
#   Config-driven queries and relation operations
#..............................................................

"""
Relation Service - Dynamic Relation Management.

   Service for managing config-driven relations and building dynamic queries.
   Provides methods to create, query, and manage relations without hardcoded ForeignKeys.

   Key Features:
   - Config-driven relation operations
   - Dynamic query building based on relation config
   - GenericForeignKey support for flexible relations
   - Automatic relation registry management

   Core Methods:

   1. get_related_objects(source_obj, relation_key)
      - Returns QuerySet of related objects for a source object
      - Uses RelationInstance and GenericForeignKey

   2. create_relation(source_obj, target_obj, relation_key)
      - Creates a relation instance between two objects
      - Automatically creates RelationRegistry entry if needed

   3. delete_relation(source_obj, target_obj, relation_key)
      - Removes a relation instance

   4. build_query(model_class, relation_key, filters)
      - Builds dynamic QuerySet based on relation config
      - Supports filtering and optimization

   Usage:
   ```python
   from sopira_magic.apps.relation.services import RelationService
   companies = RelationService.get_related_objects(user, 'user_company')
   RelationService.create_relation(user, company, 'user_company')
   ```
"""

from typing import Dict, Any, List, Optional
from django.db import models
from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from .config import (
    RELATION_CONFIG,
    get_relation_config,
    get_relations_for_source,
    get_relations_for_target,
)


class RelationService:
    """Service for managing dynamic relations and building queries."""
    
    @staticmethod
    def get_model_class(model_path: str):
        """Get model class from model path (e.g., 'user.User')."""
        app_label, model_name = model_path.split('.')
        return apps.get_model(app_label, model_name)
    
    @staticmethod
    def get_related_objects(source_obj, relation_key: str) -> models.QuerySet:
        """
        Get related objects for a source object based on relation config.
        
        Args:
            source_obj: Source model instance
            relation_key: Key from RELATION_CONFIG (e.g., 'user_company')
        
        Returns:
            QuerySet of related objects
        """
        config = get_relation_config(relation_key)
        if not config:
            return models.QuerySet.none()
        
        target_model = RelationService.get_model_class(config['target'])
        
        if config['type'] == 'ForeignKey':
            # For FK relations, use RelationInstance
            source_ct = ContentType.objects.get_for_model(source_obj.__class__)
            relation = RelationService._get_or_create_relation(config)
            
            target_ids = RelationInstance.objects.filter(
                relation=relation,
                source_content_type=source_ct,
                source_object_id=source_obj.id
            ).values_list('target_object_id', flat=True)
            
            return target_model.objects.filter(id__in=target_ids)
        
        return models.QuerySet.none()
    
    @staticmethod
    def build_query(model_path: str, filters: Dict[str, Any]) -> models.QuerySet:
        """
        Build Django query from relation config and filters.
        
        Args:
            model_path: Model path (e.g., 'company.Company')
            filters: Dictionary with filter conditions (e.g., {'user': user_id})
        
        Returns:
            QuerySet
        """
        model_class = RelationService.get_model_class(model_path)
        queryset = model_class.objects.all()
        
        for filter_key, filter_value in filters.items():
            # Check if filter_key matches a relation config
            relations = get_relations_for_target(model_path)
            for relation_config in relations:
                if relation_config.get('field_name') == filter_key:
                    # This is a relation filter
                    source_model = RelationService.get_model_class(relation_config['source'])
                    source_ct = ContentType.objects.get_for_model(source_model)
                    relation = RelationService._get_or_create_relation(relation_config)
                    
                    # Get target IDs from RelationInstance
                    target_ids = RelationInstance.objects.filter(
                        relation=relation,
                        source_content_type=source_ct,
                        source_object_id=filter_value
                    ).values_list('target_object_id', flat=True)
                    
                    queryset = queryset.filter(id__in=target_ids)
                    break
            else:
                # Regular field filter
                queryset = queryset.filter(**{filter_key: filter_value})
        
        return queryset
    
    @staticmethod
    def create_relation(source_obj, target_obj, relation_key: str, metadata: dict = None):
        """
        Create a relation instance between two objects.
        
        Args:
            source_obj: Source model instance
            target_obj: Target model instance
            relation_key: Key from RELATION_CONFIG
            metadata: Optional metadata dictionary
        """
        config = get_relation_config(relation_key)
        if not config:
            raise ValueError(f"Relation config '{relation_key}' not found")
        
        relation = RelationService._get_or_create_relation(config)
        source_ct = ContentType.objects.get_for_model(source_obj.__class__)
        target_ct = ContentType.objects.get_for_model(target_obj.__class__)
        
        RelationInstance.objects.get_or_create(
            relation=relation,
            source_content_type=source_ct,
            source_object_id=source_obj.id,
            target_content_type=target_ct,
            target_object_id=target_obj.id,
            defaults={'metadata': metadata or {}}
        )
    
    @staticmethod
    def delete_relation(source_obj, target_obj, relation_key: str):
        """Delete a relation instance between two objects."""
        config = get_relation_config(relation_key)
        if not config:
            return
        
        relation = RelationService._get_or_create_relation(config)
        source_ct = ContentType.objects.get_for_model(source_obj.__class__)
        target_ct = ContentType.objects.get_for_model(target_obj.__class__)
        
        RelationInstance.objects.filter(
            relation=relation,
            source_content_type=source_ct,
            source_object_id=source_obj.id,
            target_content_type=target_ct,
            target_object_id=target_obj.id
        ).delete()
    
    @staticmethod
    def _get_or_create_relation(config: dict):
        """Get or create RelationRegistry entry from config."""
        from .models import RelationRegistry
        
        relation, created = RelationRegistry.objects.get_or_create(
            source_model=config['source'],
            target_model=config['target'],
            relation_type=config['type'],
            defaults={
                'field_name': config.get('field_name', ''),
                'related_name': config.get('related_name', ''),
                'on_delete': config.get('on_delete', 'PROTECT'),
                'config': config,
            }
        )
        return relation


# Import here to avoid circular import
from .models import RelationInstance
