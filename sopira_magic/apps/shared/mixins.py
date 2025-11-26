#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/shared/mixins.py
#   Shared Mixins - Reusable model mixins
#   Common mixins for Django models
#..............................................................

"""
   Shared Mixins - Reusable Model Mixins.

   Abstract model mixins that can be added to any Django model
   to provide common functionality like tracking, soft delete, ordering.

   Mixins:

   1. CreatedByMixin
      - Adds created_by ForeignKey field
      - Tracks user who created the record
      - Related name: %(class)s_created

   2. UpdatedByMixin
      - Adds updated_by ForeignKey field
      - Tracks user who last updated the record
      - Related name: %(class)s_updated

   3. SoftDeleteMixin
      - Adds deleted_at DateTimeField
      - Overrides delete() to set deleted_at instead of deleting
      - Provides restore() method to restore soft-deleted objects

   4. TimestampMixin
      - Adds created_at and updated_at fields
      - Alternative to TimeStampedModel
      - Indexed on created_at

   5. OrderableMixin
      - Adds order IntegerField
      - Default ordering by order field
      - Useful for manual ordering of objects

   6. PublishableMixin
      - Adds published BooleanField and published_at DateTimeField
      - Provides publish() and unpublish() methods
      - Tracks publication status and timestamp

   Usage:
   ```python
   class MyModel(CreatedByMixin, SoftDeleteMixin, models.Model):
       name = models.CharField(max_length=255)
       # Automatically gets: created_by, deleted_at
   ```
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class CreatedByMixin(models.Model):
    """Mixin to add created_by field."""
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
        editable=False
    )
    
    class Meta:
        abstract = True


class UpdatedByMixin(models.Model):
    """Mixin to add updated_by field."""
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
        editable=False
    )
    
    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """Mixin for soft delete functionality."""
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete - set deleted_at instead of actually deleting."""
        from django.utils import timezone
        self.deleted_at = timezone.now()
        self.save(using=using)
    
    def restore(self):
        """Restore soft-deleted object."""
        self.deleted_at = None
        self.save()


class TimestampMixin(models.Model):
    """Mixin for timestamp fields (alternative to TimeStampedModel)."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class OrderableMixin(models.Model):
    """Mixin for ordering functionality."""
    order = models.IntegerField(default=0, db_index=True)
    
    class Meta:
        abstract = True
        ordering = ['order']


class PublishableMixin(models.Model):
    """Mixin for publish/unpublish functionality."""
    published = models.BooleanField(default=False, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def publish(self):
        """Publish the object."""
        from django.utils import timezone
        self.published = True
        self.published_at = timezone.now()
        self.save()
    
    def unpublish(self):
        """Unpublish the object."""
        self.published = False
        self.save()
