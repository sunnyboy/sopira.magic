#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/worker/models.py
#   Worker Models - Business entity model
#   Universal model without hardcoded relations (config-driven)
#..............................................................

"""
   Worker Models - Business Entity Model.

   Worker model following config-driven architecture.
   No hardcoded ForeignKey relations - all relations managed via relation app.

   Models:

   Worker (extends NamedWithCodeModel)
   - Universal business entity model for worker/employee management
   - Inherits: id, uuid, created, updated, active, visible
   - Inherits: code, name, human_id, comment, note
   - Additional fields: first_name, last_name, email, phone, position
   - Relations: Defined in relation app (config-driven)

   Architecture:
   - Relations managed via RelationService (relation app)
   - No hardcoded ForeignKeys in model definition
   - Config-driven relations defined in relation/config.py (SSOT)

   Usage:
   ```python
   from sopira_magic.apps.worker.models import Worker
   worker = Worker.objects.create(
       code='WRK-001',
       name='John Doe',
       first_name='John',
       last_name='Doe',
       email='john@example.com',
       position='Operator'
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import NamedWithCodeModel


class Worker(NamedWithCodeModel):
    """Worker model - universal, no hardcoded relations."""
    first_name = models.CharField(max_length=255, blank=True, default="")
    last_name = models.CharField(max_length=255, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    position = models.CharField(max_length=100, blank=True, default="")
    
    class Meta(NamedWithCodeModel.Meta):
        verbose_name = _("Worker")
        verbose_name_plural = _("Workers")
