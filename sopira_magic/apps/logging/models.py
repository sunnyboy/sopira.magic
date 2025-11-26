#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/logging/models.py
#   Logging Models - Application logs and audit trails
#   Uses LOGGING database for system logs and performance metrics
#..............................................................

"""
   Logging Models - Application Logs and Audit Trails.

   Models for system logging, audit trails, and performance metrics.
   Stored in LOGGING database (separate from business data).

   Models:

   1. SystemLog
      - System log entries (debug, info, warning, error, critical)
      - Fields: level, message, module, function, line_number, timestamp, user_id, request_path, extra_data
      - Indexed on: level + timestamp, user_id + timestamp
      - Ordered by: -timestamp (newest first)

   2. AuditLog
      - Audit log for data changes (GDPR, SOX compliance)
      - Fields: action, model_name, object_id, user_id, timestamp, before_data, after_data, ip_address, user_agent
      - Tracks: CREATE, UPDATE, DELETE, VIEW actions
      - Stores before/after data for change tracking

   3. PerformanceLog
      - Performance metrics and timing information
      - Fields: endpoint, method, duration_ms, timestamp, user_id, request_size, response_size, status_code
      - Indexed on: endpoint + timestamp, duration_ms
      - Tracks API performance and response times

   Database:
   - All models stored in LOGGING database (not PRIMARY)
   - Routed via DatabaseRouter based on app_label

   Usage:
   ```python
   from sopira_magic.apps.logging.models import SystemLog, AuditLog
   SystemLog.objects.create(level='INFO', message='User logged in', user_id=user.id)
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class SystemLog(models.Model):
    """System log entries."""
    LEVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, db_index=True)
    message = models.TextField()
    module = models.CharField(max_length=255, blank=True, default="")
    function = models.CharField(max_length=255, blank=True, default="")
    line_number = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user_id = models.UUIDField(null=True, blank=True, db_index=True)
    request_path = models.CharField(max_length=500, blank=True, default="")
    extra_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = _("System Log")
        verbose_name_plural = _("System Logs")
        indexes = [
            models.Index(fields=['level', 'timestamp']),
            models.Index(fields=['user_id', 'timestamp']),
        ]
        ordering = ['-timestamp']


class AuditLog(models.Model):
    """Audit log for data changes (GDPR, SOX compliance)."""
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
    ]
    
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, db_index=True)
    user_id = models.UUIDField(null=True, blank=True, db_index=True)
    username = models.CharField(max_length=255, blank=True, default="")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    model_name = models.CharField(max_length=255, db_index=True)
    field_name = models.CharField(max_length=255, blank=True, default="")
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, default="")
    extra_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = _("Audit Log")
        verbose_name_plural = _("Audit Logs")
        indexes = [
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['user_id', 'timestamp']),
            models.Index(fields=['model_name', 'timestamp']),
            models.Index(fields=['content_type', 'object_id']),
        ]
        ordering = ['-timestamp']


class PerformanceLog(models.Model):
    """Performance metrics logging."""
    endpoint = models.CharField(max_length=500, db_index=True)
    method = models.CharField(max_length=10, db_index=True)
    response_time_ms = models.FloatField(db_index=True)
    status_code = models.IntegerField(db_index=True)
    user_id = models.UUIDField(null=True, blank=True, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    query_count = models.IntegerField(null=True, blank=True)
    query_time_ms = models.FloatField(null=True, blank=True)
    memory_usage_mb = models.FloatField(null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = _("Performance Log")
        verbose_name_plural = _("Performance Logs")
        indexes = [
            models.Index(fields=['endpoint', 'timestamp']),
            models.Index(fields=['response_time_ms', 'timestamp']),
            models.Index(fields=['status_code', 'timestamp']),
        ]
        ordering = ['-timestamp']
