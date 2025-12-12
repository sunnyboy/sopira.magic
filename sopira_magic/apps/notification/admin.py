#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/notification/admin.py
#   Notification Admin - Django admin configuration
#   Admin interface for notification models
#..............................................................

"""
   Notification Admin - Django Admin Configuration.

   Django admin interface configuration for notification models.
   Provides management interface for templates, matrix, logs, and preferences.

   Admin Classes:

   1. NotificationTemplateAdmin
      - Displays: name, notification_type, template_source, enabled, created
      - Filters: notification_type, template_source, enabled
      - Actions: Preview template, Test send

   2. NotificationMatrixAdmin
      - Displays: notification_type, recipient_type, enabled
      - Filters: notification_type, recipient_type, enabled
      - Inline editing of multiple entries

   3. NotificationLogAdmin (read-only)
      - Displays: notification_type, recipient_email, status, sent_at
      - Filters: notification_type, status, created
      - Search: recipient_email

   4. NotificationPreferenceAdmin
      - Displays: user, created
      - Search: user username, user email
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import NotificationTemplate, NotificationPreference, NotificationMatrix, NotificationLog


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """NotificationTemplate admin configuration."""
    list_display = [
        'name',
        'notification_type',
        'template_source',
        'scope_aware',
        'enabled_badge',
        'created'
    ]
    list_filter = ['notification_type', 'template_source', 'enabled', 'scope_aware', 'created']
    search_fields = ['name', 'notification_type', 'subject']
    readonly_fields = ['created', 'updated']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'notification_type', 'enabled')
        }),
        ('Template Configuration', {
            'fields': ('template_source', 'subject', 'body', 'variables', 'scope_aware')
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['preview_template', 'test_send', 'enable_templates', 'disable_templates']
    
    def enabled_badge(self, obj):
        """Display enabled status as colored badge."""
        if obj.enabled:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">✓ Enabled</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px;">✗ Disabled</span>'
        )
    enabled_badge.short_description = 'Status'
    
    def preview_template(self, request, queryset):
        """Preview selected templates with sample data."""
        from .template_renderer import TemplateRenderer
        
        for template in queryset:
            try:
                subject, body = TemplateRenderer.preview_template(
                    template_source=template.template_source,
                    template_name=template.notification_type
                )
                self.message_user(
                    request,
                    f"Preview for {template.name}: Subject='{subject[:50]}...'"
                )
            except Exception as e:
                self.message_user(request, f"Preview failed for {template.name}: {e}", level='error')
    preview_template.short_description = "Preview selected templates"
    
    def test_send(self, request, queryset):
        """Test send notification for selected templates."""
        from .engine import NotificationEngine
        
        for template in queryset:
            try:
                result = NotificationEngine.preview_notification(template.notification_type)
                if result.get('error'):
                    self.message_user(
                        request,
                        f"Test failed for {template.name}: {result['error']}",
                        level='error'
                    )
                else:
                    self.message_user(
                        request,
                        f"Test preview for {template.name}: {len(result.get('recipients', []))} recipients"
                    )
            except Exception as e:
                self.message_user(request, f"Test failed for {template.name}: {e}", level='error')
    test_send.short_description = "Test send (preview only)"
    
    def enable_templates(self, request, queryset):
        """Enable selected templates."""
        updated = queryset.update(enabled=True)
        self.message_user(request, f"{updated} templates enabled")
    enable_templates.short_description = "Enable selected templates"
    
    def disable_templates(self, request, queryset):
        """Disable selected templates."""
        updated = queryset.update(enabled=False)
        self.message_user(request, f"{updated} templates disabled")
    disable_templates.short_description = "Disable selected templates"


@admin.register(NotificationMatrix)
class NotificationMatrixAdmin(admin.ModelAdmin):
    """NotificationMatrix admin configuration."""
    list_display = [
        'notification_type',
        'recipient_type',
        'recipient_identifier_short',
        'scope_pattern_short',
        'enabled_badge',
        'created'
    ]
    list_filter = ['notification_type', 'recipient_type', 'enabled', 'created']
    search_fields = ['notification_type', 'recipient_identifier', 'scope_pattern']
    readonly_fields = ['created', 'updated']
    
    fieldsets = (
        ('Notification Configuration', {
            'fields': ('notification_type', 'enabled')
        }),
        ('Recipient Configuration', {
            'fields': ('recipient_type', 'recipient_identifier')
        }),
        ('Scope Configuration', {
            'fields': ('scope_pattern', 'conditions')
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['enable_entries', 'disable_entries']
    
    def enabled_badge(self, obj):
        """Display enabled status as colored badge."""
        if obj.enabled:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">✓ Enabled</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px;">✗ Disabled</span>'
        )
    enabled_badge.short_description = 'Status'
    
    def recipient_identifier_short(self, obj):
        """Display shortened recipient identifier."""
        if obj.recipient_identifier:
            return obj.recipient_identifier[:30] + '...' if len(obj.recipient_identifier) > 30 else obj.recipient_identifier
        return '-'
    recipient_identifier_short.short_description = 'Recipient'
    
    def scope_pattern_short(self, obj):
        """Display shortened scope pattern."""
        if obj.scope_pattern:
            return obj.scope_pattern[:30] + '...' if len(obj.scope_pattern) > 30 else obj.scope_pattern
        return '-'
    scope_pattern_short.short_description = 'Scope Pattern'
    
    def enable_entries(self, request, queryset):
        """Enable selected matrix entries."""
        updated = queryset.update(enabled=True)
        self.message_user(request, f"{updated} matrix entries enabled")
    enable_entries.short_description = "Enable selected entries"
    
    def disable_entries(self, request, queryset):
        """Disable selected matrix entries."""
        updated = queryset.update(enabled=False)
        self.message_user(request, f"{updated} matrix entries disabled")
    disable_entries.short_description = "Disable selected entries"


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    """NotificationLog admin configuration (read-only)."""
    list_display = [
        'notification_type',
        'recipient_email',
        'status_badge',
        'sent_at',
        'created'
    ]
    list_filter = ['notification_type', 'status', 'created', 'sent_at']
    search_fields = ['recipient_email', 'notification_type', 'error_message']
    readonly_fields = [
        'notification_type',
        'recipient_email',
        'status',
        'error_message',
        'template_used',
        'context_data',
        'scope_identifier',
        'sent_at',
        'created',
        'updated'
    ]
    
    fieldsets = (
        ('Notification Info', {
            'fields': ('notification_type', 'recipient_email', 'status', 'sent_at')
        }),
        ('Template & Context', {
            'fields': ('template_used', 'context_data'),
            'classes': ('collapse',)
        }),
        ('Error Details', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Scope & Timestamps', {
            'fields': ('scope_identifier', 'created', 'updated'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Disable adding log entries via admin."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting log entries via admin."""
        return False
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'sent': '#28a745',
            'failed': '#dc3545',
            'pending': '#ffc107'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'Status'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """NotificationPreference admin configuration."""
    list_display = ['user', 'created']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created', 'updated']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Preferences', {
            'fields': ('preferences',)
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )

