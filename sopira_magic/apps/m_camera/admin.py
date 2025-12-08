#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_camera/admin.py
#   Camera Admin - Django admin configuration
#   Admin interface for Camera model
#..............................................................

"""
   Camera Admin - Django Admin Configuration.

   Django admin interface configuration for Camera model.
   Extends NamedWithCodeModelAdmin for base functionality.
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import Camera


@admin.register(Camera)
class CameraAdmin(NamedWithCodeModelAdmin):
    """Camera admin configuration."""
    # Relations are managed via relation app, not hardcoded here
    pass

