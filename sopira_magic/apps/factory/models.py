#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/factory/models.py
#   Factory Models - Business entity model
#   Universal model without hardcoded relations (config-driven)
#..............................................................

"""
   Factory Models - Business Entity Model.

   Factory model following config-driven architecture.
   No hardcoded ForeignKey relations - all relations managed via relation app.

   Models:

   Factory (extends NamedWithCodeModel)
   - Universal business entity model
   - Inherits: id, uuid, created, updated, active, visible
   - Inherits: code, name, human_id, comment, note
   - Relations: Defined in relation app (company_factory)

   Architecture:
   - Relations managed via RelationService (relation app)
   - No hardcoded ForeignKeys in model definition
   - Config-driven relations defined in relation/config.py (SSOT)

   Usage:
   ```python
   from sopira_magic.apps.factory.models import Factory
   from sopira_magic.apps.relation.services import RelationService
   factory = Factory.objects.create(code='FAC-001', name='My Factory')
   RelationService.create_relation(company, factory, 'company_factory')
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import NamedWithCodeModel


class Factory(NamedWithCodeModel):
    """Factory model - universal, no hardcoded relations."""
    
    class Meta(NamedWithCodeModel.Meta):
        verbose_name = _("Factory")
        verbose_name_plural = _("Factories")
