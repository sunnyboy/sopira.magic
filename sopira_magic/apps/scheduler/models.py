#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/scheduler/models.py
#   Scheduler Models - Scheduled tasks system
#   Task scheduling, execution tracking, retry logic
#..............................................................

"""
   Scheduler Models - Scheduled Tasks System.

   Models for scheduled task management and execution tracking.
   Provides task scheduling with cron expressions and retry logic.

   Models:

   1. ScheduledTask (extends TimeStampedModel)
      - Scheduled task definition model
      - Fields: name, task_type, schedule (cron), config (JSON), enabled, last_run, next_run
      - Schedule: cron expression for task scheduling
      - Tracks last and next execution times

   2. TaskExecution (extends TimeStampedModel)
      - Task execution log model
      - Fields: task (FK), status, started_at, completed_at, error_message, retry_count
      - Status: success, failed, running
      - Ordered by: -created (newest first)
      - Tracks execution history and retry attempts

   Usage:
   ```python
   from sopira_magic.apps.scheduler.models import ScheduledTask, TaskExecution
   task = ScheduledTask.objects.create(
       name='Daily Backup',
       task_type='backup',
       schedule='0 2 * * *',  # 2 AM daily
       config={'target': 'database'}
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import TimeStampedModel


class ScheduledTask(TimeStampedModel):
    """Scheduled task model."""
    name = models.CharField(max_length=255, db_index=True)
    task_type = models.CharField(max_length=255, db_index=True)
    schedule = models.CharField(max_length=255)  # cron expression
    config = models.JSONField(default=dict, blank=True)
    enabled = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _("Scheduled Task")
        verbose_name_plural = _("Scheduled Tasks")


class TaskExecution(TimeStampedModel):
    """Task execution log model."""
    task = models.ForeignKey(ScheduledTask, on_delete=models.CASCADE, related_name="executions")
    status = models.CharField(max_length=50, db_index=True)  # success, failed, running
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, default="")
    retry_count = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = _("Task Execution")
        verbose_name_plural = _("Task Executions")
        ordering = ['-created']
