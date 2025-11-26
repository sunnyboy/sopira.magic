#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/video/models.py
#   Video Models - Video gallery
#   Video management and gallery system
#..............................................................

"""
   Video Models - Video Gallery.

   Models for video management and gallery functionality.
   Stores video metadata and file information.

   Models:

   Video (extends NamedWithCodeModel)
   - Video model with gallery support
   - Inherits: id, uuid, created, updated, active, visible
   - Inherits: code, name, human_id, comment, note
   - Additional fields: video_url, thumbnail_url, duration, file_size, metadata (JSON)
   - Duration stored in seconds
   - Stores video URLs and metadata

   Usage:
   ```python
   from sopira_magic.apps.video.models import Video
   video = Video.objects.create(
       code='VID-001',
       name='Production Process',
       video_url='https://example.com/video.mp4',
       thumbnail_url='https://example.com/thumb.jpg',
       duration=3600  # 1 hour
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import NamedWithCodeModel


class Video(NamedWithCodeModel):
    """Video model."""
    video_url = models.URLField(blank=True, default="")
    thumbnail_url = models.URLField(blank=True, default="")
    duration = models.IntegerField(default=0)  # Duration in seconds
    file_size = models.BigIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta(NamedWithCodeModel.Meta):
        verbose_name = _("Video")
        verbose_name_plural = _("Videos")
