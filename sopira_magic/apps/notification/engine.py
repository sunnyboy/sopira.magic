#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/notification/engine.py
#   Notification Engine - Core notification service
#   ConfigDriven orchestration of notification sending
#..............................................................

"""
Notification Engine - Core Notification Service.

ConfigDriven orchestrator for notification sending:
1. Validates notification config (NOTIFICATION_CONFIG)
2. Resolves recipients (NotificationMatrix + ScopeResolver)
3. Renders templates (TemplateRenderer)
4. Sends emails via SMTP
5. Logs results (NotificationLog)

Usage:
```python
from sopira_magic.apps.notification.engine import NotificationEngine

result = NotificationEngine.send_notification(
    notification_type='login_notification',
    context={
        'user': user,
        'username': 'john',
        'ip_address': '192.168.1.1',
        'timestamp': '2025-12-12 10:00:00'
    }
)
```
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .config import (
    get_notification_config,
    is_notification_enabled,
    get_template_config,
    get_default_recipients,
    is_scope_aware,
    get_smtp_config,
    get_logging_config,
)
from .template_renderer import TemplateRenderer
from .scope_resolver import ScopeResolver

logger = logging.getLogger(__name__)


class NotificationEngine:
    """Core notification engine - orchestrates entire notification flow."""
    
    @classmethod
    def _serialize_context(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize context to JSON-safe format.
        
        Converts User objects and other non-serializable objects to strings/dicts.
        
        Args:
            context: Original context with potentially non-serializable objects
        
        Returns:
            JSON-safe dictionary
        """
        serialized = {}
        
        for key, value in context.items():
            try:
                # Handle User objects
                if hasattr(value, '_meta') and hasattr(value._meta, 'model_name'):
                    # Django model instance
                    serialized[key] = {
                        '_model': value._meta.model_name,
                        'id': str(getattr(value, 'id', '')),
                        'username': str(getattr(value, 'username', '')),
                        'email': str(getattr(value, 'email', '')),
                    }
                # Handle datetime objects
                elif hasattr(value, 'isoformat'):
                    serialized[key] = value.isoformat()
                # Handle other objects
                elif isinstance(value, (str, int, float, bool, type(None))):
                    serialized[key] = value
                elif isinstance(value, (list, tuple)):
                    serialized[key] = [cls._serialize_value(v) for v in value]
                elif isinstance(value, dict):
                    serialized[key] = cls._serialize_context(value)
                else:
                    # Fallback to string representation
                    serialized[key] = str(value)
            except Exception as e:
                logger.warning(f"Failed to serialize context key '{key}': {e}")
                serialized[key] = f"<{type(value).__name__}>"
        
        return serialized
    
    @classmethod
    def _serialize_value(cls, value: Any) -> Any:
        """Serialize single value to JSON-safe format."""
        if hasattr(value, '_meta') and hasattr(value._meta, 'model_name'):
            return {
                '_model': value._meta.model_name,
                'id': str(getattr(value, 'id', '')),
            }
        elif hasattr(value, 'isoformat'):
            return value.isoformat()
        elif isinstance(value, (str, int, float, bool, type(None))):
            return value
        else:
            return str(value)
    
    @classmethod
    def send_notification(
        cls,
        notification_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send notification - main entry point.
        
        Args:
            notification_type: Notification type identifier (from NOTIFICATION_CONFIG)
            context: Context data for template rendering and recipient resolution
        
        Returns:
            Dictionary with result:
            {
                'success': bool,
                'sent_count': int,
                'failed_count': int,
                'recipients': List[str],
                'errors': List[str]
            }
        
        Example:
            ```python
            result = NotificationEngine.send_notification(
                notification_type='login_notification',
                context={'user': user, 'username': 'john', 'ip_address': '192.168.1.1'}
            )
            ```
        """
        logger.info(f"🔔 Sending notification: {notification_type}")
        
        result = {
            'success': False,
            'sent_count': 0,
            'failed_count': 0,
            'recipients': [],
            'errors': []
        }
        
        try:
            # 1. Check if notification is enabled
            if not is_notification_enabled(notification_type):
                logger.info(f"Notification {notification_type} is disabled in config")
                result['errors'].append('Notification disabled in config')
                return result
            
            # 2. Get notification config
            config = get_notification_config(notification_type)
            if not config:
                logger.error(f"Notification config not found: {notification_type}")
                result['errors'].append('Notification config not found')
                return result
            
            # 3. Resolve recipients
            recipients = cls.resolve_recipients(notification_type, context, config)
            if not recipients:
                logger.warning(f"No recipients resolved for {notification_type}")
                result['errors'].append('No recipients found')
                return result
            
            result['recipients'] = recipients
            logger.info(f"Resolved {len(recipients)} recipients: {recipients}")
            
            # 4. Render template
            subject, body = cls.render_template(notification_type, context, config)
            logger.debug(f"Rendered template - Subject: {subject}")
            
            # 5. Send emails
            for recipient in recipients:
                send_result = cls.send_email(
                    recipient=recipient,
                    subject=subject,
                    body=body,
                    notification_type=notification_type,
                    context=context
                )
                
                if send_result['success']:
                    result['sent_count'] += 1
                else:
                    result['failed_count'] += 1
                    result['errors'].append(f"{recipient}: {send_result.get('error', 'Unknown error')}")
            
            # 6. Final result
            result['success'] = result['sent_count'] > 0
            
            logger.info(
                f"✅ Notification {notification_type} completed: "
                f"sent={result['sent_count']}, failed={result['failed_count']}"
            )
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Notification {notification_type} failed: {e}", exc_info=True)
            result['errors'].append(str(e))
            return result
    
    @classmethod
    def resolve_recipients(
        cls,
        notification_type: str,
        context: Dict[str, Any],
        config: Dict[str, Any]
    ) -> List[str]:
        """Resolve recipients from config, matrix, and scope.
        
        Args:
            notification_type: Notification type
            context: Context data
            config: Notification config from NOTIFICATION_CONFIG
        
        Returns:
            List of email addresses
        """
        from .models import NotificationMatrix
        
        recipients = []
        user = context.get('user')
        
        # Try to get recipients from NotificationMatrix
        try:
            matrix_recipients = ScopeResolver.resolve_recipients_from_matrix(
                notification_type=notification_type,
                context=context,
                user=user
            )
            recipients.extend(matrix_recipients)
        except Exception as e:
            logger.warning(f"Failed to resolve recipients from matrix: {e}")
        
        # If no matrix entries, use default recipients from config
        if not recipients:
            default_recipients = get_default_recipients(notification_type)
            logger.debug(f"Using default recipients from config: {default_recipients}")
            
            for recipient_type in default_recipients:
                if recipient_type == 'admin':
                    admin_email = ScopeResolver.get_default_admin_email()
                    if admin_email:
                        recipients.append(admin_email)
                
                elif recipient_type == 'user':
                    if user and hasattr(user, 'email'):
                        recipients.append(user.email)
                    elif context.get('email'):
                        recipients.append(context.get('email'))
                
                elif recipient_type == 'scope_admins':
                    if user:
                        scope_admins = ScopeResolver.get_scope_admins(user)
                        recipients.extend(scope_admins)
        
        # Apply scope filtering if scope_aware
        if is_scope_aware(notification_type) and user:
            # Get scope pattern from first matrix entry (if exists)
            try:
                matrix_entry = NotificationMatrix.objects.filter(
                    notification_type=notification_type,
                    enabled=True
                ).first()
                
                if matrix_entry and matrix_entry.scope_pattern:
                    recipients = ScopeResolver.filter_by_scope(
                        recipients=recipients,
                        user=user,
                        scope_pattern=matrix_entry.scope_pattern
                    )
            except Exception as e:
                logger.warning(f"Failed to apply scope filtering: {e}")
        
        # Remove duplicates and validate
        recipients = list(set(recipients))
        recipients = ScopeResolver.filter_valid_emails(recipients)
        
        return recipients
    
    @classmethod
    def render_template(
        cls,
        notification_type: str,
        context: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Tuple[str, str]:
        """Render notification template.
        
        Args:
            notification_type: Notification type
            context: Context data for rendering
            config: Notification config
        
        Returns:
            Tuple of (subject, body)
        """
        template_config = get_template_config(notification_type)
        if not template_config:
            logger.error(f"Template config not found for {notification_type}")
            return f"Notification: {notification_type}", f"Context: {context}"
        
        template_source = template_config.get('template_source')
        template_name = template_config.get('template_name')
        subject_template = template_config.get('subject_template')
        
        try:
            subject, body = TemplateRenderer.render(
                template_source=template_source,
                template_name=template_name,
                context=context,
                subject_template=subject_template
            )
            return subject, body
        
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            # Fallback to simple text
            return (
                f"Notification: {notification_type}",
                f"Template rendering failed. Context: {context}"
            )
    
    @classmethod
    def send_email(
        cls,
        recipient: str,
        subject: str,
        body: str,
        notification_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send single email via SMTP and log result.
        
        Args:
            recipient: Recipient email address
            subject: Email subject
            body: Email body
            notification_type: Notification type for logging
            context: Context data for logging
        
        Returns:
            Dictionary with {'success': bool, 'error': str}
        """
        from .models import NotificationLog
        
        result = {'success': False, 'error': ''}
        log_entry = None
        
        try:
            # Create log entry
            logging_config = get_logging_config()
            if logging_config.get('log_all_notifications', True):
                # Serialize context to JSON-safe format
                serialized_context = cls._serialize_context(context) if logging_config.get('include_context_data', True) else {}
                
                log_entry = NotificationLog.objects.create(
                    notification_type=notification_type,
                    recipient_email=recipient,
                    status='pending',
                    template_used=get_template_config(notification_type).get('template_name', ''),
                    context_data=serialized_context
                )
            
            # Send email via Django's send_mail
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
            
            sent_count = send_mail(
                subject=subject,
                message=body,  # Plain text version
                from_email=from_email,
                recipient_list=[recipient],
                html_message=body,  # HTML version
                fail_silently=False,
            )
            
            if sent_count > 0:
                result['success'] = True
                if log_entry:
                    log_entry.status = 'sent'
                    log_entry.sent_at = timezone.now()
                    log_entry.save()
                
                logger.info(f"✉️  Email sent successfully to {recipient}")
            else:
                result['error'] = 'send_mail returned 0'
                if log_entry:
                    log_entry.status = 'failed'
                    log_entry.error_message = result['error']
                    log_entry.save()
        
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Failed to send email to {recipient}: {e}")
            
            if log_entry:
                log_entry.status = 'failed'
                log_entry.error_message = str(e)
                log_entry.save()
        
        return result
    
    @classmethod
    def preview_notification(
        cls,
        notification_type: str,
        sample_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Preview notification with sample data (for admin/testing).
        
        Args:
            notification_type: Notification type
            sample_context: Optional sample context (uses defaults if None)
        
        Returns:
            Dictionary with preview data:
            {
                'subject': str,
                'body': str,
                'recipients': List[str],
                'config': Dict
            }
        """
        if not sample_context:
            # Create sample context
            from sopira_magic.apps.m_user.models import User
            try:
                sample_user = User.objects.first()
            except:
                sample_user = None
            
            sample_context = {
                'user': sample_user,
                'username': 'sample_user',
                'email': 'sample@example.com',
                'first_name': 'Sample',
                'last_name': 'User',
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0',
                'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                'role': 'ADMIN',
            }
        
        config = get_notification_config(notification_type)
        if not config:
            return {'error': 'Notification config not found'}
        
        try:
            # Resolve recipients
            recipients = cls.resolve_recipients(notification_type, sample_context, config)
            
            # Render template
            subject, body = cls.render_template(notification_type, sample_context, config)
            
            return {
                'subject': subject,
                'body': body,
                'recipients': recipients,
                'config': config,
                'enabled': is_notification_enabled(notification_type),
            }
        
        except Exception as e:
            logger.error(f"Preview failed: {e}")
            return {'error': str(e)}

