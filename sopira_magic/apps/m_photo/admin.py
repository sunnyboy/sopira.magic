#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_photo/admin.py
#   Photo Admin - Django admin configuration
#..............................................................

"""
Photo Admin - MeasurementRelated media admin.
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import TimeStampedModelAdmin
from .models import Photo


@admin.register(Photo)
class PhotoAdmin(TimeStampedModelAdmin):
    """Photo admin configuration."""
    list_display = ['id', 'measurement', 'width', 'height', 'file_size', 'active', 'visible']
    list_filter = ['active', 'visible']
    search_fields = ['photo_url']
    raw_id_fields = ['measurement']
