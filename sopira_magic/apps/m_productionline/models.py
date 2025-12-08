#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/productionline/models.py
#   ProductionLine Models - Business entity model
#   Universal model without hardcoded relations (config-driven)
#..............................................................

"""
   ProductionLine Models - Business Entity Model.

   ProductionLine model following config-driven architecture.
   No hardcoded ForeignKey relations - all relations managed via relation app.

   Models:

   ProductionLine (extends NamedWithCodeModel)
   - Universal business entity model
   - Inherits: id, uuid, created, updated, active, visible
   - Inherits: code, name, human_id, comment, note
   - Relations: Defined in relation app (factory_productionline)

   Architecture:
   - Relations managed via RelationService (relation app)
   - No hardcoded ForeignKeys in model definition
   - Config-driven relations defined in relation/config.py (SSOT)

   Usage:
   ```python
   from sopira_magic.apps.productionline.models import ProductionLine
   from sopira_magic.apps.relation.services import RelationService
   line = ProductionLine.objects.create(code='PL-001', name='Production Line 1')
   RelationService.create_relation(factory, line, 'factory_productionline')
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import NamedWithCodeModel


class ProductionLine(NamedWithCodeModel):
    """ProductionLine model - universal, no hardcoded relations."""
    
    class Meta(NamedWithCodeModel.Meta):
        verbose_name = _("Production Line")
        verbose_name_plural = _("Production Lines")
