#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/notification/admin.py
#   Notification Admin - Django admin configuration
#   Admin interface for notification models
#..............................................................

"""
   Notification Admin - Django Admin Configuration.

   Django admin interface configuration for notification models.
   Provides management interface for notification templates and preferences.

   Admin Classes:

   1. NotificationTemplateAdmin
      - Displays: name, notification_type, enabled, created
      - Filters: notification_type, enabled, created
      - Search: name, subject

   2. NotificationPreferenceAdmin
      - Displays: user, created
      - Search: user username, user email
"""

from django.contrib import admin
from .models import NotificationTemplate, NotificationPreference


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """NotificationTemplate admin configuration."""
    list_display = ['name', 'notification_type', 'enabled', 'created']
    list_filter = ['notification_type', 'enabled', 'created']
    search_fields = ['name', 'subject']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """NotificationPreference admin configuration."""
    list_display = ['user', 'created']
    search_fields = ['user__username', 'user__email']
