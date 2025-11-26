#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/endpoint/models.py
#   Endpoint Models - External endpoint models
#   Cameras, sensors, IoT device management
#..............................................................

"""
   Endpoint Models - External Endpoint Models.

   Models for managing external endpoints like cameras, sensors, and IoT devices.
   No hardcoded ForeignKey relations - all relations managed via relation app.

   Models:

   Endpoint (extends NamedWithCodeModel)
   - External endpoint/device model
   - Inherits: id, uuid, created, updated, active, visible
   - Inherits: code, name, human_id, comment, note
   - Additional fields: endpoint_type, url, api_key, status, last_connected
   - Endpoint types: camera, sensor, iot
   - Relations: Defined in relation app (config-driven)

   Architecture:
   - Relations managed via RelationService (relation app)
   - No hardcoded ForeignKeys in model definition
   - Config-driven relations defined in relation/config.py (SSOT)

   Usage:
   ```python
   from sopira_magic.apps.endpoint.models import Endpoint
   endpoint = Endpoint.objects.create(
       code='CAM-001',
       name='Production Camera',
       endpoint_type='camera',
       url='http://camera.example.com',
       status='active'
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import NamedWithCodeModel


class Endpoint(NamedWithCodeModel):
    """Endpoint model - universal, no hardcoded relations."""
    endpoint_type = models.CharField(max_length=255, blank=True, default="")  # camera, sensor, iot
    url = models.URLField(blank=True, default="")
    api_key = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=50, default="active")
    last_connected = models.DateTimeField(null=True, blank=True)
    
    class Meta(NamedWithCodeModel.Meta):
        verbose_name = _("Endpoint")
        verbose_name_plural = _("Endpoints")
