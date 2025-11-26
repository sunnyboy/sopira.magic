#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/company/models.py
#   Company Models - Business entity model
#   Universal model without hardcoded relations (config-driven)
#..............................................................

"""
   Company Models - Business Entity Model.

   Company model following config-driven architecture.
   No hardcoded ForeignKey relations - all relations managed via relation app.

   Models:

   Company (extends NamedWithCodeModel)
   - Universal business entity model
   - Inherits: id, uuid, created, updated, active, visible
   - Inherits: code, name, human_id, comment, note
   - Relations: Defined in relation app (user_company)

   Architecture:
   - Relations managed via RelationService (relation app)
   - No hardcoded ForeignKeys in model definition
   - Config-driven relations defined in relation/config.py (SSOT)

   Usage:
   ```python
   from sopira_magic.apps.company.models import Company
   from sopira_magic.apps.relation.services import RelationService
   company = Company.objects.create(code='COMP-001', name='My Company')
   RelationService.create_relation(user, company, 'user_company')
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import NamedWithCodeModel


class Company(NamedWithCodeModel):
    """Company model - universal, no hardcoded relations."""
    
    class Meta(NamedWithCodeModel.Meta):
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")
