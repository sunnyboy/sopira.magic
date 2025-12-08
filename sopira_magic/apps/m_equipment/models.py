#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/equipment/models.py
#   Equipment Models - Business entity model
#   Universal model without hardcoded relations (config-driven)
#..............................................................

"""
   Equipment Models - Business Entity Model.

   Equipment model following config-driven architecture.
   No hardcoded ForeignKey relations - all relations managed via relation app.

   Models:

   Equipment (extends NamedWithCodeModel)
   - Universal business entity model for equipment/asset management
   - Inherits: id, uuid, created, updated, active, visible
   - Inherits: code, name, human_id, comment, note
   - Additional fields: equipment_type, brand, model, serial_number
   - Relations: Defined in relation app (config-driven)

   Architecture:
   - Relations managed via RelationService (relation app)
   - No hardcoded ForeignKeys in model definition
   - Config-driven relations defined in relation/config.py (SSOT)

   Usage:
   ```python
   from sopira_magic.apps.equipment.models import Equipment
   equipment = Equipment.objects.create(
       code='EQ-001',
       name='Production Machine',
       equipment_type='CNC',
       brand='Brand Name',
       model='Model XYZ'
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import NamedWithCodeModel


class Equipment(NamedWithCodeModel):
    """Equipment model - universal, no hardcoded relations."""
    equipment_type = models.CharField(max_length=255, blank=True, default="")
    brand = models.CharField(max_length=255, blank=True, default="")
    model = models.CharField(max_length=255, blank=True, default="")
    serial_number = models.CharField(max_length=255, blank=True, default="")
    
    class Meta(NamedWithCodeModel.Meta):
        verbose_name = _("Equipment")
        verbose_name_plural = _("Equipment")
