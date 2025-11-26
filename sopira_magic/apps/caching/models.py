#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/caching/models.py
#   Caching Models - Cache configuration
#   Cache settings and TTL management
#..............................................................

"""
   Caching Models - Cache Configuration.

   Models for cache configuration and TTL (Time To Live) management.
   Stores cache settings for different cache keys.

   Models:

   CacheConfig (extends TimeStampedModel)
   - Cache configuration model
   - Fields: key (unique), config (JSON), ttl (seconds), enabled
   - Unique constraint on key
   - TTL: Time to live in seconds (default 3600)
   - Stores cache configuration per key

   Usage:
   ```python
   from sopira_magic.apps.caching.models import CacheConfig
   config = CacheConfig.objects.create(
       key='user_dashboard',
       config={'backend': 'redis'},
       ttl=1800  # 30 minutes
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import TimeStampedModel


class CacheConfig(TimeStampedModel):
    """Cache configuration model."""
    key = models.CharField(max_length=255, db_index=True, unique=True)
    config = models.JSONField(default=dict, blank=True)
    ttl = models.IntegerField(default=3600)  # Time to live in seconds
    enabled = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Cache Config")
        verbose_name_plural = _("Cache Configs")
