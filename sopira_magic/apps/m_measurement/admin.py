#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_measurement/admin.py
#   Measurement Admin - Django admin configuration
#   Admin interface for Measurement model
#..............................................................

"""
   Measurement Admin - Django Admin Configuration.

   Django admin interface configuration for Measurement model.
   Extends TimeStampedModelAdmin for base functionality.
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import TimeStampedModelAdmin
from .models import Measurement


@admin.register(Measurement)
class MeasurementAdmin(TimeStampedModelAdmin):
    """Measurement admin configuration."""
    # Relations are managed via relation app, not hardcoded here
    pass

