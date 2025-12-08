#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_camera/models.py
#   Camera Models - Factory-scoped with credentials
#..............................................................

"""
Camera Models.

Camera extends FactoryScopedModel - inherits factory FK automatically.
ServiceCredential is O2O with Camera (security separation pattern).

Scoping: User → Company → Factory → Camera
Security: Credentials isolated in separate model (security separation)
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import FactoryScopedModel, TimeStampedModel


class Camera(FactoryScopedModel):
    """Camera - scoped to Factory with optional Location."""
    
    # Optional location FK (camera can be at specific location)
    location = models.ForeignKey(
        'location.Location',
        on_delete=models.SET_NULL,
        related_name='cameras',
        blank=True,
        null=True,
        help_text=_("Location within factory (optional)"),
    )
    
    # Device info
    manufacturer = models.CharField(max_length=128, blank=True, default="")
    manufacturer_name = models.CharField(max_length=128, blank=True, default="")
    camera_serie = models.CharField(max_length=128, blank=True, default="")
    camera_sn = models.CharField(max_length=128, blank=True, default="")
    
    # Dates
    purchased_date = models.DateField(null=True, blank=True)
    installed_date = models.DateField(null=True, blank=True)
    fw_number = models.CharField(max_length=128, blank=True, default="")
    fw_updated_date = models.DateField(null=True, blank=True)
    
    # Network config
    installation_type = models.CharField(max_length=64, blank=True, default="")
    ip = models.GenericIPAddressField(blank=True, null=True)
    port = models.PositiveIntegerField(default=0)
    port_type = models.CharField(max_length=32, blank=True, default="")
    protocol = models.CharField(max_length=32, blank=True, default="")
    http_port = models.PositiveIntegerField(default=0)
    rtsp_port = models.PositiveIntegerField(default=0)
    
    # Stream config
    channel = models.CharField(max_length=64, blank=True, default="")
    stream_type = models.CharField(max_length=64, blank=True, default="")
    resolution = models.CharField(max_length=64, blank=True, default="")
    video_quality = models.CharField(max_length=64, blank=True, default="")
    bitrate = models.CharField(max_length=64, blank=True, default="")
    max_bitrate = models.CharField(max_length=64, blank=True, default="")
    video_encoding = models.CharField(max_length=64, blank=True, default="")
    iframe_interval = models.PositiveIntegerField(null=True, blank=True)
    
    # Paths
    video_path = models.CharField(max_length=255, blank=True, default="")
    picture_path = models.CharField(max_length=255, blank=True, default="")
    path_prefix = models.CharField(max_length=255, blank=True, default="")
    path_suffix = models.CharField(max_length=255, blank=True, default="")
    
    # JSON config
    settings_payload = models.JSONField(default=dict, blank=True)
    
    class Meta(FactoryScopedModel.Meta):
        verbose_name = _("Camera")
        verbose_name_plural = _("Cameras")
        indexes = [
            *FactoryScopedModel.Meta.indexes,
            models.Index(fields=["factory", "location"]),
            models.Index(fields=["ip"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["factory", "code"],
                name="uq_camera_factory_code",
            ),
        ]


class ServiceCredential(TimeStampedModel):
    """
    Camera credentials - security separation pattern.
    
    O2O with Camera - isolated for:
    - Separate access control (admin-only)
    - Encrypted storage support
    - Audit trail
    """
    
    camera = models.OneToOneField(
        Camera,
        on_delete=models.CASCADE,
        related_name='credential',
        help_text=_("Camera this credential belongs to"),
    )
    
    # Credentials (consider encryption in production)
    username = models.CharField(max_length=128, blank=True, default="")
    password = models.CharField(max_length=256, blank=True, default="")
    
    # Additional auth options
    api_key = models.CharField(max_length=256, blank=True, default="")
    auth_token = models.CharField(max_length=512, blank=True, default="")
    certificate_path = models.CharField(max_length=255, blank=True, default="")
    
    # Metadata
    last_verified = models.DateTimeField(null=True, blank=True)
    is_valid = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Service Credential")
        verbose_name_plural = _("Service Credentials")
    
    def __str__(self):
        return f"Credential for {self.camera.code}"

