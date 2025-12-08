#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_photo/models.py
#   Photo Models - Measurement-related media
#..............................................................

"""
Photo Models.

Photo extends MeasurementRelatedModel - inherits measurement FK automatically.
Scoping: User → Company → Factory → Measurement → Photo
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import MeasurementRelatedModel


class Photo(MeasurementRelatedModel):
    """Photo - attached to Measurement."""
    
    photo_url = models.URLField(blank=True, default="")
    thumbnail_url = models.URLField(blank=True, default="")
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    file_size = models.BigIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta(MeasurementRelatedModel.Meta):
        verbose_name = _("Photo")
        verbose_name_plural = _("Photos")
