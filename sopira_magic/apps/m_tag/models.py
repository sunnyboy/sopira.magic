#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/tag/models.py
#   Tag Models - Tag management system
#   Generic tagging system for any model
#..............................................................

"""
   Tag Models - Tag Management System.

   Generic tagging system that allows tagging any Django model
   using GenericForeignKey. Provides flexible tagging without
   hardcoding relations.

   Models:

   1. Tag (extends TimeStampedModel)
      - Tag definition model
      - Fields: name (unique), color (hex), description
      - Ordered by: name
      - Unique constraint on name

   2. TaggedItem (extends TimeStampedModel)
      - Generic relation to any model
      - Fields: tag (FK), content_type, object_id, content_object (GenericFK)
      - Unique constraint: tag + content_type + object_id
      - Indexed on: content_type + object_id

   Architecture:
   - Uses GenericForeignKey for flexible tagging
   - Can tag any model without modifying its definition
   - Tags are reusable across different model types

   Usage:
   ```python
   from sopira_magic.apps.tag.models import Tag, TaggedItem
   tag = Tag.objects.create(name='important', color='#FF0000')
   TaggedItem.objects.create(tag=tag, content_object=company)
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from sopira_magic.apps.core.models import TimeStampedModel


class Tag(TimeStampedModel):
    """Tag model."""
    name = models.CharField(max_length=255, db_index=True, unique=True)
    color = models.CharField(max_length=7, blank=True, default="#000000")  # Hex color
    description = models.TextField(blank=True, default="")
    
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TaggedItem(TimeStampedModel):
    """TaggedItem model - Generic relation to any model."""
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="tagged_items")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        verbose_name = _("Tagged Item")
        verbose_name_plural = _("Tagged Items")
        unique_together = [['tag', 'content_type', 'object_id']]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
