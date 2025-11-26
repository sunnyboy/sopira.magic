#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/alarm/models.py
#   Alarm Models - Alarm system
#   Alarm rules, escalation, and alert management
#..............................................................

"""
   Alarm Models - Alarm System.

   Models for alarm rules and escalation management.
   Provides configurable alarm system with escalation levels.

   Models:

   1. AlarmRule (extends TimeStampedModel)
      - Alarm rule definition model
      - Fields: name, rule_type, condition (JSON), action (JSON), enabled
      - Stores alarm conditions and actions
      - Configurable via JSON fields

   2. AlarmEscalation (extends TimeStampedModel)
      - Alarm escalation level model
      - Fields: rule (FK), level, delay_minutes, action (JSON)
      - Links to AlarmRule
      - Ordered by: level
      - Defines escalation levels and delays

   Usage:
   ```python
   from sopira_magic.apps.alarm.models import AlarmRule, AlarmEscalation
   rule = AlarmRule.objects.create(
       name='High Temperature Alert',
       rule_type='temperature',
       condition={'threshold': 100},
       action={'type': 'email', 'recipients': ['admin@example.com']}
   )
   escalation = AlarmEscalation.objects.create(
       rule=rule,
       level=1,
       delay_minutes=5,
       action={'type': 'sms'}
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import TimeStampedModel


class AlarmRule(TimeStampedModel):
    """Alarm rule model."""
    name = models.CharField(max_length=255, db_index=True)
    rule_type = models.CharField(max_length=50, db_index=True)
    condition = models.JSONField(default=dict, blank=True)
    action = models.JSONField(default=dict, blank=True)
    enabled = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Alarm Rule")
        verbose_name_plural = _("Alarm Rules")


class AlarmEscalation(TimeStampedModel):
    """Alarm escalation model."""
    rule = models.ForeignKey(AlarmRule, on_delete=models.CASCADE, related_name="escalations")
    level = models.IntegerField(default=1)
    delay_minutes = models.IntegerField(default=0)
    action = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = _("Alarm Escalation")
        verbose_name_plural = _("Alarm Escalations")
        ordering = ['level']
