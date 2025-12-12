#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/notification/models.py
#   Notification Models - Notification system
#   Templates, matrix, logs, and preferences
#..............................................................

"""
   Notification Models - Notification System.

   Models for notification templates, communication matrix, audit logs,
   and user notification preferences. Supports multiple notification channels.

   Models:

   1. NotificationTemplate (extends TimeStampedModel)
      - Notification template model (DB or file-based)
      - Fields: name, notification_type, template_source, subject, body, variables, enabled
      - Supports: database templates (stored in body) and file templates (HTML files)

   2. NotificationMatrix (extends TimeStampedModel)
      - Communication matrix - kto dostane aké notifikácie
      - Fields: notification_type, recipient_type, recipient_identifier, enabled, scope_pattern
      - Supports: admin, user, custom recipients, scope-aware routing

   3. NotificationLog (extends TimeStampedModel)
      - Audit log pre odoslané notifikácie
      - Fields: notification_type, recipient_email, status, error_message, context_data
      - Tracks: všetky odoslané/failed notifikácie

   4. NotificationPreference (extends TimeStampedModel)
      - User notification preferences
      - One-to-one relationship with User
      - Fields: user, preferences (JSON)

   Usage:
   ```python
   from sopira_magic.apps.notification.models import NotificationTemplate, NotificationMatrix
   template = NotificationTemplate.objects.get(notification_type='login_notification')
   matrix_entries = NotificationMatrix.objects.filter(notification_type='login_notification', enabled=True)
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import TimeStampedModel
from sopira_magic.apps.m_user.models import User


class NotificationTemplate(TimeStampedModel):
    """Notification template model - supports DB and file-based templates."""
    
    # Basic info
    name = models.CharField(max_length=255, db_index=True, help_text="Human-readable template name")
    notification_type = models.CharField(
        max_length=100, 
        unique=True, 
        db_index=True,
        help_text="Notification type identifier (e.g., 'login_notification')"
    )
    
    # Template configuration
    template_source = models.CharField(
        max_length=20,
        choices=[
            ('database', 'Database Template'),
            ('file', 'File Template'),
        ],
        default='database',
        help_text="Where is template stored - in DB or as file"
    )
    
    # Template content (for database templates)
    subject = models.CharField(
        max_length=255, 
        blank=True, 
        default="",
        help_text="Subject template (can use {variables})"
    )
    body = models.TextField(
        blank=True,
        default="",
        help_text="Body template (for database templates, can use {variables})"
    )
    
    # Template metadata
    variables = models.JSONField(
        default=list,
        blank=True,
        help_text="List of variables available in template (e.g., ['username', 'email'])"
    )
    scope_aware = models.BooleanField(
        default=False,
        help_text="Is this notification scope-aware (recipients filtered by scope)"
    )
    
    # Status
    enabled = models.BooleanField(default=True, help_text="Is this template active")
    
    class Meta:
        verbose_name = _("Notification Template")
        verbose_name_plural = _("Notification Templates")
        ordering = ['notification_type']
    
    def __str__(self):
        return f"{self.name} ({self.notification_type})"


class NotificationMatrix(TimeStampedModel):
    """Communication matrix - defines kto dostane aké notifikácie."""
    
    # Notification type
    notification_type = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Notification type identifier (matches NotificationTemplate.notification_type)"
    )
    
    # Recipient configuration
    recipient_type = models.CharField(
        max_length=50,
        choices=[
            ('admin', 'Admin (from settings.ADMIN_EMAIL)'),
            ('user', 'User (from context)'),
            ('scope_admins', 'Scope Admins (admins in user scope)'),
            ('custom', 'Custom Email Address'),
            ('role', 'All Users with Role'),
        ],
        default='admin',
        help_text="Type of recipient"
    )
    
    recipient_identifier = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Email address (for custom) or role name (for role) or empty (for admin/user)"
    )
    
    # Scope configuration
    scope_pattern = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Scope pattern for filtering recipients (empty = no scope filtering)"
    )
    
    # Additional conditions
    conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional conditions for sending (e.g., {'user_role': 'ADMIN'})"
    )
    
    # Status
    enabled = models.BooleanField(
        default=True,
        help_text="Is this matrix entry active"
    )
    
    class Meta:
        verbose_name = _("Notification Matrix")
        verbose_name_plural = _("Notification Matrix")
        ordering = ['notification_type', 'recipient_type']
        indexes = [
            models.Index(fields=['notification_type', 'enabled']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} → {self.recipient_type}"


class NotificationLog(TimeStampedModel):
    """Audit log pre všetky odoslané notifikácie."""
    
    # Notification info
    notification_type = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Type of notification sent"
    )
    
    # Recipient info
    recipient_email = models.EmailField(
        help_text="Email address where notification was sent"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('sent', 'Sent Successfully'),
            ('failed', 'Failed to Send'),
            ('pending', 'Pending'),
        ],
        default='pending',
        db_index=True,
        help_text="Status of notification delivery"
    )
    
    # Error tracking
    error_message = models.TextField(
        blank=True,
        default="",
        help_text="Error message if sending failed"
    )
    
    # Template used
    template_used = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Template name that was used"
    )
    
    # Context data
    context_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Context data used for rendering template (for debugging)"
    )
    
    # Scope reference (optional)
    # Note: Using CharField instead of FK to avoid hard dependency on scoping module
    scope_identifier = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Scope identifier if notification was scope-aware"
    )
    
    # Additional metadata
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When was notification actually sent"
    )
    
    class Meta:
        verbose_name = _("Notification Log")
        verbose_name_plural = _("Notification Logs")
        ordering = ['-created']
        indexes = [
            models.Index(fields=['notification_type', 'status']),
            models.Index(fields=['recipient_email']),
            models.Index(fields=['-created']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} → {self.recipient_email} ({self.status})"


class NotificationPreference(TimeStampedModel):
    """User notification preferences."""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="notification_preferences"
    )
    preferences = models.JSONField(
        default=dict, 
        blank=True,
        help_text="User-specific notification preferences (e.g., {'login_notification': False})"
    )
    
    class Meta:
        verbose_name = _("Notification Preference")
        verbose_name_plural = _("Notification Preferences")
    
    def __str__(self):
        return f"Preferences for {self.user.username}"

