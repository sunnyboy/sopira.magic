#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_video/models.py
#   Video Models - Measurement-related media
#..............................................................

"""
Video Models.

Video extends MeasurementRelatedModel - inherits measurement FK automatically.
Scoping: User → Company → Factory → Measurement → Video
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import MeasurementRelatedModel


class Video(MeasurementRelatedModel):
    """Video - attached to Measurement."""
    
    video_url = models.URLField(blank=True, default="")
    thumbnail_url = models.URLField(blank=True, default="")
    duration = models.IntegerField(default=0)
    file_size = models.BigIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta(MeasurementRelatedModel.Meta):
        verbose_name = _("Video")
        verbose_name_plural = _("Videos")
