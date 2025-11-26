#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/material/models.py
#   Material Models - Business entity model
#   Universal model without hardcoded relations (config-driven)
#..............................................................

"""
   Material Models - Business Entity Model.

   Material model following config-driven architecture.
   No hardcoded ForeignKey relations - all relations managed via relation app.

   Models:

   Material (extends NamedWithCodeModel)
   - Universal business entity model for material/raw material management
   - Inherits: id, uuid, created, updated, active, visible
   - Inherits: code, name, human_id, comment, note
   - Additional fields: unit, unit_price
   - Relations: Defined in relation app (config-driven)

   Architecture:
   - Relations managed via RelationService (relation app)
   - No hardcoded ForeignKeys in model definition
   - Config-driven relations defined in relation/config.py (SSOT)

   Usage:
   ```python
   from sopira_magic.apps.material.models import Material
   material = Material.objects.create(
       code='MAT-001',
       name='Steel Sheet',
       unit='kg',
       unit_price=10.50
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import NamedWithCodeModel


class Material(NamedWithCodeModel):
    """Material model - universal, no hardcoded relations."""
    unit = models.CharField(max_length=50, blank=True, default="")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta(NamedWithCodeModel.Meta):
        verbose_name = _("Material")
        verbose_name_plural = _("Materials")
