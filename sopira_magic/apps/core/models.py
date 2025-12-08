#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/core/models.py
#   Core Models - Base abstract models
#   Foundation models for all business entities
#..............................................................

"""
Core Models - Base Abstract Models.

   Foundation abstract models that provide common fields and functionality
   for all business entities in the sopira.magic project.

Hierarchy:
    TimeStampedModel (base)
        └── NamedWithCodeModel (+ code, name, human_id)
            └── CompanyOwnedModel (+ company FK)
                └── FactoryScopedModel (+ factory FK)

Scoping Integration:
    - FactoryScopedModel provides factory FK for scoping engine
    - Scoping rules are applied via VIEWS_MATRIX.ownership_hierarchy
    - Models inherit scoping-ready fields automatically

   Usage:
    # Lookup entity owned by factory
    class Location(FactoryScopedModel):
        pass  # Gets: factory FK, code, name, etc.
    
    # Entity with optional location
    class Pit(FactoryScopedModel):
        location = models.ForeignKey(...)  # Additional FK
"""

import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation


# =============================================================================
# LEVEL 0: BASE MODELS
# =============================================================================

class TimeStampedModel(models.Model):
    """
    Base model with common timestamp and status fields.
    All business models should inherit from this.
    
    Provides:
    - UUID primary key (id, uuid)
    - Timestamps (created, updated)
    - Status flags (active, visible)
    - Soft delete support via active flag
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Is the record active? (soft delete flag)")
    )
    visible = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Should the record be visible in UI listings?")
    )

    class Meta:
        abstract = True


class NamedWithCodeModel(TimeStampedModel):
    """
    Base model for entities with name and code.
    Extends TimeStampedModel with naming fields.
    
    Provides:
    - code: Unique identifier within scope
    - name: Human-readable name
    - human_id: Auto-generated from code
    - comment, note: Documentation fields
    """
    human_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        default=None,
        db_index=True,
        help_text=_("Human-readable ID unique within scope")
    )
    code = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Unique code within scope (e.g., abbreviation)")
    )
    name = models.CharField(max_length=255, db_index=True)
    comment = models.TextField(blank=True, default="")
    note = models.TextField(blank=True, default="")
    
    # Tags via GenericRelation (config-driven)
    tags = GenericRelation(
        "tag.TaggedItem",
        related_query_name="%(app_label)s_%(class)s"
    )

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} — {self.name}" if self.code else self.name

    def save(self, *args, **kwargs):
        if not self.human_id and self.code:
            self.human_id = self.code
        super().save(*args, **kwargs)


# =============================================================================
# LEVEL 1: COMPANY-SCOPED MODELS
# =============================================================================

class CompanyOwnedModel(NamedWithCodeModel):
    """
    Abstract base for models owned by Company.
    
    Scoping: User → Company (M2M) → This model
    
    Used by: Factory
    
    Note: company is nullable for migration compatibility.
    Use RunPython to populate, then make non-nullable.
    """
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)ss',
        help_text=_("Company that owns this entity"),
        null=True,  # Migration compatibility - make NOT NULL after data migration
        blank=True,
    )

    class Meta(NamedWithCodeModel.Meta):
        abstract = True
        indexes = [
            models.Index(fields=["company", "code"]),
            models.Index(fields=["company", "name"]),
        ]


# =============================================================================
# LEVEL 2: FACTORY-SCOPED MODELS
# =============================================================================

class FactoryScopedModel(NamedWithCodeModel):
    """
    Abstract base for models scoped to Factory.
    
    Scoping: User → Company → Factory → This model
    
    Provides:
    - factory FK for automatic scoping
    - Unique constraint: factory + code
    - Indexes for efficient filtering
    
    Used by: Location, Carrier, Driver, Pot, Pit, Machine, Camera
    
    Note: factory is nullable for migration compatibility.
    Use RunPython to populate, then make non-nullable.
    """
    factory = models.ForeignKey(
        'factory.Factory',
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)ss',
        help_text=_("Factory this entity belongs to"),
        null=True,  # Migration compatibility - make NOT NULL after data migration
        blank=True,
    )

    class Meta(NamedWithCodeModel.Meta):
        abstract = True
        indexes = [
            models.Index(fields=["factory", "code"]),
            models.Index(fields=["factory", "active"]),
        ]
    
    # Note: UniqueConstraint for factory+code should be defined in child models
    # because constraint names must be unique per model


# =============================================================================
# LEVEL 3: MEASUREMENT-RELATED MODELS
# =============================================================================

class MeasurementRelatedModel(TimeStampedModel):
    """
    Abstract base for models related to Measurement.
    
    Used by: Photo, Video (media attached to measurements)
    
    Provides:
    - measurement FK
    - Indexes for efficient filtering
    
    Note: measurement is nullable for migration compatibility.
    Use RunPython to populate, then make non-nullable.
    """
    measurement = models.ForeignKey(
        'measurement.Measurement',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)ss',
        help_text=_("Measurement this entity belongs to"),
        null=True,  # Migration compatibility - make NOT NULL after data migration
        blank=True,
    )

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["measurement"]),
        ]

