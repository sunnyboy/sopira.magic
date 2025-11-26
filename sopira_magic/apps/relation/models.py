#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/relation/models.py
#   Relation Models - Dynamic relation registry
#   Config-driven relations without hardcoded ForeignKeys
#..............................................................

"""
   Relation Models - Dynamic Relation Registry.

   Models for managing config-driven relations between any Django models
   without hardcoding ForeignKey fields in model definitions.

   Models:

   1. RelationRegistry (extends TimeStampedModel)
      - Stores relation definitions (source_model, target_model, relation_type)
      - Config-driven: relations defined in config.py (SSOT)
      - Supports: ForeignKey, ManyToMany, OneToOne
      - Metadata: field_name, related_name, on_delete, config (JSON)

   2. RelationInstance (extends TimeStampedModel)
      - Stores actual relation instances between objects
      - Uses GenericForeignKey for flexible source/target objects
      - Links: relation (FK to RelationRegistry), source_object, target_object
      - Metadata: JSON field for additional relation data

   Architecture:
   - Relations defined in config.py (SSOT)
   - RelationRegistry initialized via management command
   - RelationInstance created via RelationService
   - No hardcoded ForeignKeys in business models

   Usage:
   ```python
   from sopira_magic.apps.relation.models import RelationRegistry, RelationInstance
   # Relations managed via RelationService, not directly
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from sopira_magic.apps.core.models import TimeStampedModel


class RelationRegistry(TimeStampedModel):
    """Registry for config-driven relations between models."""
    source_model = models.CharField(max_length=255, db_index=True)
    target_model = models.CharField(max_length=255, db_index=True)
    relation_type = models.CharField(max_length=64, db_index=True)  # FK, M2M, O2O, etc.
    field_name = models.CharField(max_length=255, blank=True, default="")
    related_name = models.CharField(max_length=255, blank=True, default="")
    on_delete = models.CharField(max_length=20, default="PROTECT")  # PROTECT, CASCADE, SET_NULL, etc.
    config = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = _("Relation Registry")
        verbose_name_plural = _("Relation Registries")
        unique_together = [['source_model', 'target_model', 'relation_type']]
        indexes = [
            models.Index(fields=['source_model', 'relation_type']),
            models.Index(fields=['target_model', 'relation_type']),
        ]


class RelationInstance(TimeStampedModel):
    """Instance of a relation between two objects."""
    relation = models.ForeignKey(
        RelationRegistry,
        on_delete=models.CASCADE,
        related_name="instances"
    )
    
    # Source object (GenericForeignKey)
    source_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="relation_sources"
    )
    source_object_id = models.UUIDField()
    source_object = GenericForeignKey('source_content_type', 'source_object_id')
    
    # Target object (GenericForeignKey)
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="relation_targets"
    )
    target_object_id = models.UUIDField()
    target_object = GenericForeignKey('target_content_type', 'target_object_id')
    
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = _("Relation Instance")
        verbose_name_plural = _("Relation Instances")
        indexes = [
            models.Index(fields=['source_content_type', 'source_object_id']),
            models.Index(fields=['target_content_type', 'target_object_id']),
            models.Index(fields=['relation', 'source_content_type', 'source_object_id']),
        ]
        unique_together = [['relation', 'source_content_type', 'source_object_id', 'target_content_type', 'target_object_id']]
