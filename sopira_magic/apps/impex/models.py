#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/impex/models.py
#   Impex Models - Import/Export system
#   Data import, export, migration, and communication interfaces
#..............................................................

"""
   Impex Models - Import/Export System.

   Models for data import, export, migration, and communication interfaces.
   Supports multiple formats and communication protocols.

   Models:

   1. ImportConfig (extends TimeStampedModel)
      - Import configuration model
      - Fields: name, import_type, config (JSON), enabled
      - Import types: csv, excel, json, xml
      - Stores import configuration and settings

   2. ExportConfig (extends TimeStampedModel)
      - Export configuration model
      - Fields: name, export_type, config (JSON), enabled
      - Export types: csv, excel, json, xml
      - Stores export configuration and settings

   3. CommunicationInterface (extends TimeStampedModel)
      - Communication interface model
      - Fields: name, interface_type, config (JSON), enabled
      - Interface types: api, websocket, mqtt, etc.
      - Stores communication interface configuration

   Usage:
   ```python
   from sopira_magic.apps.impex.models import ImportConfig, ExportConfig
   import_config = ImportConfig.objects.create(
       name='CSV Import',
       import_type='csv',
       config={'delimiter': ',', 'encoding': 'utf-8'}
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import TimeStampedModel


class ImportConfig(TimeStampedModel):
    """Import configuration model."""
    name = models.CharField(max_length=255, db_index=True)
    import_type = models.CharField(max_length=50, db_index=True)  # csv, excel, json, xml
    config = models.JSONField(default=dict, blank=True)
    enabled = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Import Config")
        verbose_name_plural = _("Import Configs")


class ExportConfig(TimeStampedModel):
    """Export configuration model."""
    name = models.CharField(max_length=255, db_index=True)
    export_type = models.CharField(max_length=50, db_index=True)  # csv, excel, json, xml
    config = models.JSONField(default=dict, blank=True)
    enabled = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Export Config")
        verbose_name_plural = _("Export Configs")


class CommunicationInterface(TimeStampedModel):
    """Communication interface model."""
    name = models.CharField(max_length=255, db_index=True)
    interface_type = models.CharField(max_length=50, db_index=True)  # api, websocket, mqtt, etc.
    config = models.JSONField(default=dict, blank=True)
    enabled = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Communication Interface")
        verbose_name_plural = _("Communication Interfaces")
