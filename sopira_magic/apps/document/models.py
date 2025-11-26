#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/document/models.py
#   Document Models - Document management
#   Document storage and versioning system
#..............................................................

"""
   Document Models - Document Management.

   Models for document management and versioning.
   Stores document metadata and file information.

   Models:

   Document (extends NamedWithCodeModel)
   - Document model with file management
   - Inherits: id, uuid, created, updated, active, visible
   - Inherits: code, name, human_id, comment, note
   - Additional fields: document_type, file_path, file_size, mime_type, metadata (JSON)
   - Stores document metadata and file references

   Usage:
   ```python
   from sopira_magic.apps.document.models import Document
   document = Document.objects.create(
       code='DOC-001',
       name='User Manual',
       document_type='pdf',
       file_path='/documents/user_manual.pdf',
       file_size=1024000,
       mime_type='application/pdf'
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import NamedWithCodeModel


class Document(NamedWithCodeModel):
    """Document model."""
    document_type = models.CharField(max_length=255, blank=True, default="")
    file_path = models.CharField(max_length=1024, blank=True, default="")
    file_size = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=255, blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta(NamedWithCodeModel.Meta):
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
