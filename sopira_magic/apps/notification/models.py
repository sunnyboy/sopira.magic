#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/notification/models.py
#   Notification Models - Notification system
#   Templates, preferences, and notification management
#..............................................................

"""
   Notification Models - Notification System.

   Models for notification templates and user notification preferences.
   Supports multiple notification channels (email, SMS, push).

   Models:

   1. NotificationTemplate (extends TimeStampedModel)
      - Notification template model
      - Fields: name, notification_type, subject, body, enabled
      - Notification types: email, sms, push
      - Stores reusable notification templates

   2. NotificationPreference (extends TimeStampedModel)
      - User notification preferences
      - One-to-one relationship with User
      - Fields: user, preferences (JSON)
      - Stores user-specific notification settings

   Usage:
   ```python
   from sopira_magic.apps.notification.models import NotificationTemplate, NotificationPreference
   template = NotificationTemplate.objects.create(
       name='Welcome Email',
       notification_type='email',
       subject='Welcome!',
       body='Welcome to our platform...'
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import TimeStampedModel
from sopira_magic.apps.user.models import User


class NotificationTemplate(TimeStampedModel):
    """Notification template model."""
    name = models.CharField(max_length=255, db_index=True)
    notification_type = models.CharField(max_length=50, db_index=True)  # email, sms, push
    subject = models.CharField(max_length=255, blank=True, default="")
    body = models.TextField()
    enabled = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Notification Template")
        verbose_name_plural = _("Notification Templates")


class NotificationPreference(TimeStampedModel):
    """User notification preferences."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="notification_preferences")
    preferences = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = _("Notification Preference")
        verbose_name_plural = _("Notification Preferences")
