"""
Models for FK options caching (config-driven, SSOT via VIEWS_MATRIX).
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

class CacheConfig(models.Model):
    """Cache configuration model (TTL, enabled flag)."""

    id = models.BigAutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)
    key = models.CharField(max_length=255, db_index=True, unique=True)
    config = models.JSONField(default=dict, blank=True)
    ttl = models.IntegerField(default=3600)  # seconds
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Cache Config")
        verbose_name_plural = _("Cache Configs")

    def __str__(self) -> str:
        return f"{self.key} (ttl={self.ttl}s)"


class FKOptionsCache(models.Model):
    """Persistent snapshot of FK options for fast responses and observability."""

    id = models.BigAutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)
    field_name = models.CharField(max_length=100, db_index=True)
    factory = models.ForeignKey(
        "factory.Factory",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="fk_options_cache",
    )
    options = models.JSONField(default=list, blank=True)
    record_count = models.IntegerField(default=0)
    factories_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = _("FK Options Cache")
        verbose_name_plural = _("FK Options Caches")
        unique_together = [("field_name", "factory")]
        indexes = [
            models.Index(fields=["field_name"]),
            models.Index(fields=["field_name", "factory"]),
        ]

    def __str__(self) -> str:
        scope = f"factory={self.factory_id}" if self.factory_id else "global"
        return f"{self.field_name} ({scope})"

