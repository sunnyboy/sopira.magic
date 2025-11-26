#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/search/models.py
#   Search Models - Elasticsearch configuration
#   Search index configuration and management
#..............................................................

"""
   Search Models - Elasticsearch Configuration.

   Models for configuring Elasticsearch search indexes.
   Stores search configuration for different models.

   Models:

   SearchConfig (extends TimeStampedModel)
   - Search index configuration model
   - Fields: model_name, index_name, fields (JSON), enabled
   - Unique constraint: model_name + index_name
   - Stores which fields are indexed for each model

   Usage:
   ```python
   from sopira_magic.apps.search.models import SearchConfig
   config = SearchConfig.objects.create(
       model_name='company.Company',
       index_name='companies',
       fields=['name', 'code', 'comment'],
       enabled=True
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import TimeStampedModel


class SearchConfig(TimeStampedModel):
    """Search configuration model."""
    model_name = models.CharField(max_length=255, db_index=True)
    index_name = models.CharField(max_length=255, db_index=True)
    fields = models.JSONField(default=list, blank=True)
    enabled = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Search Config")
        verbose_name_plural = _("Search Configs")
        unique_together = [['model_name', 'index_name']]
