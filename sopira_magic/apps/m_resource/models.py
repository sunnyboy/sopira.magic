#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/resource/models.py
#   Resource Models - Business entity model
#   Universal model without hardcoded relations (config-driven)
#..............................................................

"""
   Resource Models - Business Entity Model.

   Resource model following config-driven architecture.
   No hardcoded ForeignKey relations - all relations managed via relation app.

   Models:

   Resource (extends NamedWithCodeModel)
   - Universal business entity model for resource management
   - Inherits: id, uuid, created, updated, active, visible
   - Inherits: code, name, human_id, comment, note
   - Additional fields: resource_type, unit, quantity
   - Relations: Defined in relation app (config-driven)

   Architecture:
   - Relations managed via RelationService (relation app)
   - No hardcoded ForeignKeys in model definition
   - Config-driven relations defined in relation/config.py (SSOT)

   Usage:
   ```python
   from sopira_magic.apps.resource.models import Resource
   resource = Resource.objects.create(
       code='RES-001',
       name='Electricity',
       resource_type='energy',
       unit='kWh',
       quantity=1000.00
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import NamedWithCodeModel


class Resource(NamedWithCodeModel):
    """Resource model - universal, no hardcoded relations."""
    resource_type = models.CharField(max_length=255, blank=True, default="")
    unit = models.CharField(max_length=50, blank=True, default="")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta(NamedWithCodeModel.Meta):
        verbose_name = _("Resource")
        verbose_name_plural = _("Resources")
