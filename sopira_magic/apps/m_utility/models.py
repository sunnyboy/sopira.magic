#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/utility/models.py
#   Utility Models - Business entity model
#   Universal model without hardcoded relations (config-driven)
#..............................................................

"""
   Utility Models - Business Entity Model.

   Utility model following config-driven architecture.
   No hardcoded ForeignKey relations - all relations managed via relation app.

   Models:

   Utility (extends NamedWithCodeModel)
   - Universal business entity model for utility management
   - Inherits: id, uuid, created, updated, active, visible
   - Inherits: code, name, human_id, comment, note
   - Additional fields: utility_type, value
   - Relations: Defined in relation app (config-driven)

   Architecture:
   - Relations managed via RelationService (relation app)
   - No hardcoded ForeignKeys in model definition
   - Config-driven relations defined in relation/config.py (SSOT)

   Usage:
   ```python
   from sopira_magic.apps.utility.models import Utility
   utility = Utility.objects.create(
       code='UTL-001',
       name='Water Supply',
       utility_type='water',
       value='m3'
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import NamedWithCodeModel


class Utility(NamedWithCodeModel):
    """Utility model - universal, no hardcoded relations."""
    utility_type = models.CharField(max_length=255, blank=True, default="")
    value = models.CharField(max_length=255, blank=True, default="")
    
    class Meta(NamedWithCodeModel.Meta):
        verbose_name = _("Utility")
        verbose_name_plural = _("Utilities")
