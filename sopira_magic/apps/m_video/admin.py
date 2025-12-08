#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_video/admin.py
#   Video Admin - Django admin configuration
#..............................................................

"""
Video Admin - MeasurementRelated media admin.
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import TimeStampedModelAdmin
from .models import Video


@admin.register(Video)
class VideoAdmin(TimeStampedModelAdmin):
    """Video admin configuration."""
    list_display = ['id', 'measurement', 'duration', 'file_size', 'active', 'visible']
    list_filter = ['active', 'visible']
    search_fields = ['video_url']
    raw_id_fields = ['measurement']
