#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/document/admin.py
#   Document Admin - Django admin configuration
#   Admin interface for Document model
#..............................................................

"""
   Document Admin - Django Admin Configuration.

   Django admin interface configuration for Document model.
   Extends NamedWithCodeModelAdmin with document-specific fields.

   Admin Classes:

   DocumentAdmin (extends NamedWithCodeModelAdmin)
   - Displays: code, name, document_type, file_size, mime_type, active, visible
   - Filters: document_type, active, visible
   - Search: code, name, file_path
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import Document


@admin.register(Document)
class DocumentAdmin(NamedWithCodeModelAdmin):
    """Document admin configuration."""
    list_display = ['code', 'name', 'document_type', 'file_size', 'mime_type', 'active', 'visible']
    list_filter = ['document_type', 'active', 'visible']
    search_fields = ['code', 'name', 'file_path']
