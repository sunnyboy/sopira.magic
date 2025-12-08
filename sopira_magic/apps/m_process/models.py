#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/process/models.py
#   Process Models - Business process models
#   Process management and temperature measurements
#..............................................................

"""
   Process Models - Business Process Models.

   Models for business process management and temperature measurements.
   No hardcoded ForeignKey relations - all relations managed via relation app.

   Models:

   1. Process (extends NamedWithCodeModel)
      - Business process model
      - Inherits: id, uuid, created, updated, active, visible
      - Inherits: code, name, human_id, comment, note
      - Additional fields: process_type, status, started_at, completed_at
      - Relations: Defined in relation app (config-driven)

   2. Measurement (extends NamedWithCodeModel)
      - Temperature measurement model
      - Inherits: id, uuid, created, updated, active, visible
      - Inherits: code, name, human_id, comment, note
      - Additional fields: temperature, measured_at, measurement_data (JSON)
      - Relations: Defined in relation app (config-driven)

   Architecture:
   - Relations managed via RelationService (relation app)
   - No hardcoded ForeignKeys in model definition
   - Config-driven relations defined in relation/config.py (SSOT)

   Usage:
   ```python
   from sopira_magic.apps.process.models import Process, Measurement
   process = Process.objects.create(code='PROC-001', name='Heating Process', status='running')
   measurement = Measurement.objects.create(temperature=85.5, measured_at=timezone.now())
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import NamedWithCodeModel


class Process(NamedWithCodeModel):
    """Process model - universal, no hardcoded relations."""
    process_type = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=50, default="pending")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta(NamedWithCodeModel.Meta):
        verbose_name = _("Process")
        verbose_name_plural = _("Processes")


class Measurement(NamedWithCodeModel):
    """Measurement model - for temperature measurements."""
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    measured_at = models.DateTimeField(null=True, blank=True)
    measurement_data = models.JSONField(default=dict, blank=True)
    
    class Meta(NamedWithCodeModel.Meta):
        verbose_name = _("Measurement")
        verbose_name_plural = _("Measurements")
