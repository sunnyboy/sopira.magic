#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/core/models.py
#   Core Models - Base abstract models
#   Foundation models for all business entities
#..............................................................

"""
Core Models - Base Abstract Models.

   Foundation abstract models that provide common fields and functionality
   for all business entities in the sopira.magic project.

   Base Models:

   1. TimeStampedModel
      - UUID primary key (id, uuid)
      - Timestamps (created, updated)
      - Status flags (active, visible)
      - Soft delete support via active flag
      - All business models inherit from this

   2. NamedWithCodeModel
      - Extends TimeStampedModel
      - Naming fields (code, name, human_id)
      - Documentation fields (comment, note)
      - Auto-generates human_id from code if not provided
      - Used for entities with names and codes (Company, Factory, etc.)

   Usage:
   ```python
   class Company(NamedWithCodeModel):
       # Automatically gets: id, uuid, created, updated, active, visible
       # Plus: code, name, human_id, comment, note
       pass
   ```
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation


# =============================================================================
# BASE MODELS
# =============================================================================

class TimeStampedModel(models.Model):
    """
    Base model with common timestamp and status fields.
    All business models should inherit from this.
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
    # Tags will be added via GenericRelation when tag app is available
    # tags = GenericRelation("tag.TaggedItem", related_query_name="%(app_label)s_%(class)s")

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} — {self.name}" if self.code else self.name

    def save(self, *args, **kwargs):
        if not self.human_id and self.code:
            self.human_id = self.code
        super().save(*args, **kwargs)

