#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/api/models.py
#   API Models - API Gateway configuration
#   Rate limiting, API keys, versioning models
#..............................................................

"""
   API Models - API Gateway Configuration.

   Models for API Gateway functionality including API key management,
   versioning, and rate limiting configuration.

   Models:

   1. APIKey (extends TimeStampedModel)
      - API key management for users
      - Fields: user, key, name, rate_limit, enabled, expires_at
      - Unique constraint on key
      - Rate limit: requests per hour

   2. APIVersion (extends TimeStampedModel)
      - API version management
      - Fields: version, base_url, enabled, deprecated
      - Unique constraint on version
      - Ordered by: -version (newest first)

   3. RateLimitConfig (extends TimeStampedModel)
      - Rate limiting configuration per endpoint
      - Fields: endpoint, rate_limit, burst_limit, enabled
      - Unique constraint on endpoint
      - Configures rate limits and burst protection

   Usage:
   ```python
   from sopira_magic.apps.api.models import APIKey, APIVersion, RateLimitConfig
   api_key = APIKey.objects.create(user=user, key='...', name='My API Key')
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import TimeStampedModel
from sopira_magic.apps.user.models import User


class APIKey(TimeStampedModel):
    """API key model."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_keys")
    key = models.CharField(max_length=255, db_index=True, unique=True)
    name = models.CharField(max_length=255, db_index=True)
    rate_limit = models.IntegerField(default=1000)  # Requests per hour
    enabled = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _("API Key")
        verbose_name_plural = _("API Keys")


class APIVersion(TimeStampedModel):
    """API version model."""
    version = models.CharField(max_length=50, db_index=True, unique=True)
    base_url = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)
    deprecated = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _("API Version")
        verbose_name_plural = _("API Versions")
        ordering = ['-version']


class RateLimitConfig(TimeStampedModel):
    """Rate limit configuration model."""
    endpoint = models.CharField(max_length=255, db_index=True)
    rate_limit = models.IntegerField(default=100)  # Requests per hour
    burst_limit = models.IntegerField(default=10)  # Burst protection
    enabled = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Rate Limit Config")
        verbose_name_plural = _("Rate Limit Configs")
        unique_together = [['endpoint']]
