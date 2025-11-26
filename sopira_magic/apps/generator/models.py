#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/models.py
#   Generator Models - Data generation configuration storage
#   Database model for storing generator configurations
#..............................................................

"""
   Generator Models - Data Generation Configuration Storage.

   Database model for storing data generation configurations.
   Allows dynamic configuration management via Django admin.

   Models:

   GeneratorConfig (extends TimeStampedModel)
   - Stores generator configurations in database
   - Fields: model_name, config (JSON), template, enabled
   - Unique constraint on model_name
   - Can be managed via Django admin

   Note:
   - Primary configuration is in config.py (SSOT)
   - This model allows runtime configuration overrides
   - Used for dynamic configuration management

   Usage:
   ```python
   from sopira_magic.apps.generator.models import GeneratorConfig
   config = GeneratorConfig.objects.get(model_name='user')
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import TimeStampedModel


class GeneratorConfig(TimeStampedModel):
    """Configuration for data generation."""
    model_name = models.CharField(max_length=255, db_index=True)
    config = models.JSONField(default=dict, blank=True)
    template = models.TextField(blank=True, default="")
    enabled = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Generator Config")
        verbose_name_plural = _("Generator Configs")
        unique_together = [['model_name']]
