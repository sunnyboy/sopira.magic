#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/file_storage/models.py
#   File Storage Models - File storage configuration
#   S3, Local, Azure storage with versioning
#..............................................................

"""
   File Storage Models - File Storage Configuration.

   Models for file storage configuration and versioning.
   Supports multiple storage backends (S3, Local, Azure).

   Models:

   1. StorageConfig (extends TimeStampedModel)
      - Storage backend configuration model
      - Fields: name, storage_type, config (JSON), is_default, enabled
      - Storage types: s3, local, azure
      - Stores storage backend configuration in JSON

   2. FileVersion (extends TimeStampedModel)
      - File version tracking model
      - Fields: file_path, version, storage_config (FK), file_size, metadata (JSON)
      - Unique constraint: file_path + version
      - Ordered by: -version (newest first)
      - Tracks file versions across storage backends

   Usage:
   ```python
   from sopira_magic.apps.file_storage.models import StorageConfig, FileVersion
   storage = StorageConfig.objects.create(
       name='S3 Production',
       storage_type='s3',
       config={'bucket': 'my-bucket', 'region': 'us-east-1'}
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import TimeStampedModel


class StorageConfig(TimeStampedModel):
    """Storage configuration model."""
    name = models.CharField(max_length=255, db_index=True)
    storage_type = models.CharField(max_length=50, db_index=True)  # s3, local, azure
    config = models.JSONField(default=dict, blank=True)
    is_default = models.BooleanField(default=False, db_index=True)
    enabled = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Storage Config")
        verbose_name_plural = _("Storage Configs")


class FileVersion(TimeStampedModel):
    """File version model."""
    file_path = models.CharField(max_length=1024, db_index=True)
    version = models.IntegerField(default=1)
    storage_config = models.ForeignKey(StorageConfig, on_delete=models.CASCADE, related_name="file_versions")
    file_size = models.BigIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = _("File Version")
        verbose_name_plural = _("File Versions")
        unique_together = [['file_path', 'version']]
        ordering = ['-version']
