#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/photo/models.py
#   Photo Models - Photo gallery
#   Photo management and gallery system
#..............................................................

"""
   Photo Models - Photo Gallery.

   Models for photo management and gallery functionality.
   Stores photo metadata and file information.

   Models:

   Photo (extends NamedWithCodeModel)
   - Photo model with gallery support
   - Inherits: id, uuid, created, updated, active, visible
   - Inherits: code, name, human_id, comment, note
   - Additional fields: photo_url, thumbnail_url, width, height, file_size, metadata (JSON)
   - Stores photo dimensions and URLs

   Usage:
   ```python
   from sopira_magic.apps.photo.models import Photo
   photo = Photo.objects.create(
       code='PHO-001',
       name='Factory Overview',
       photo_url='https://example.com/photo.jpg',
       thumbnail_url='https://example.com/thumb.jpg',
       width=1920,
       height=1080
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import NamedWithCodeModel


class Photo(NamedWithCodeModel):
    """Photo model."""
    photo_url = models.URLField(blank=True, default="")
    thumbnail_url = models.URLField(blank=True, default="")
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    file_size = models.BigIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta(NamedWithCodeModel.Meta):
        verbose_name = _("Photo")
        verbose_name_plural = _("Photos")
