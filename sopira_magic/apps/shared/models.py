#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/shared/models.py
#   Shared Models - Reusable base models
#   Common abstract models for shared functionality
#..............................................................

"""
   Shared Models - Reusable Base Models.

   Common abstract models that can be inherited by other models
   to add shared functionality across multiple apps.

   Models:

   1. SharedBaseModel (extends TimeStampedModel)
      - Abstract base model with common timestamp fields
      - Inherits: id, uuid, created, updated, active, visible
      - Can be used as alternative to TimeStampedModel

   2. SharedNamedModel (extends NamedWithCodeModel)
      - Abstract base model with naming fields
      - Inherits: all TimeStampedModel fields + code, name, human_id, comment, note
      - Can be used for entities with names and codes

   Usage:
   ```python
   class MyModel(SharedBaseModel):
       # Automatically gets: id, uuid, created, updated, active, visible
       pass
   ```
"""

from django.db import models
from sopira_magic.apps.core.models import TimeStampedModel, NamedWithCodeModel


class SharedBaseModel(TimeStampedModel):
    """Shared base model for common functionality."""
    class Meta:
        abstract = True


class SharedNamedModel(NamedWithCodeModel):
    """Shared named model with code."""
    class Meta:
        abstract = True
