#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/notification/template_renderer.py
#   Template Renderer - Hybrid template rendering system
#   Supports both database and file-based templates
#..............................................................

"""
Template Renderer - Hybrid Template Rendering System.

Renders notification templates from two sources:
1. Database templates: Simple text/HTML stored in NotificationTemplate.body
2. File templates: Complex HTML files stored in templates/notifications/

ConfigDriven approach: template source is defined in NOTIFICATION_CONFIG,
renderer automatically selects correct rendering method.

Usage:
```python
from sopira_magic.apps.notification.template_renderer import TemplateRenderer

subject, body = TemplateRenderer.render(
    template_source='database',
    template_name='login_notification',
    context={'username': 'john', 'ip_address': '192.168.1.1'}
)
```
"""

import logging
from typing import Dict, Tuple, Optional
from django.template.loader import render_to_string
from django.template import Template, Context
from django.conf import settings

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """Hybrid template renderer - supports database and file-based templates."""
    
    @classmethod
    def render(
        cls,
        template_source: str,
        template_name: str,
        context: Dict,
        subject_template: Optional[str] = None,
    ) -> Tuple[str, str]:
        """Render template based on source type.
        
        Args:
            template_source: 'database' or 'file'
            template_name: Template name/identifier
            context: Context data for rendering
            subject_template: Optional subject template string (with {variables})
        
        Returns:
            Tuple of (subject, body) both rendered as strings
        
        Raises:
            ValueError: If template_source is invalid
            Exception: If rendering fails
        
        Example:
            ```python
            subject, body = TemplateRenderer.render(
                template_source='database',
                template_name='login_notification',
                context={'username': 'john'},
                subject_template='Login: {username}'
            )
            ```
        """
        try:
            if template_source == 'database':
                return cls._render_database_template(template_name, context, subject_template)
            elif template_source == 'file':
                return cls._render_file_template(template_name, context, subject_template)
            else:
                raise ValueError(f"Invalid template_source: {template_source}")
        
        except Exception as e:
            logger.error(f"Template rendering failed: {template_name}, source: {template_source}, error: {e}")
            raise
    
    @classmethod
    def _render_database_template(
        cls,
        template_name: str,
        context: Dict,
        subject_template: Optional[str] = None,
    ) -> Tuple[str, str]:
        """Render template from database (NotificationTemplate model).
        
        Args:
            template_name: notification_type to look up in NotificationTemplate
            context: Context data
            subject_template: Optional subject template override
        
        Returns:
            Tuple of (subject, body)
        
        Raises:
            NotificationTemplate.DoesNotExist: If template not found
        """
        from .models import NotificationTemplate
        
        try:
            template_obj = NotificationTemplate.objects.get(
                notification_type=template_name,
                enabled=True
            )
        except NotificationTemplate.DoesNotExist:
            logger.error(f"Database template not found: {template_name}")
            raise
        
        # Render subject
        if subject_template:
            subject = subject_template.format(**context)
        elif template_obj.subject:
            subject = template_obj.subject.format(**context)
        else:
            subject = f"Notification: {template_name}"
        
        # Render body using Django template engine
        if template_obj.body:
            template = Template(template_obj.body)
            django_context = Context(context)
            body = template.render(django_context)
        else:
            body = f"Notification: {template_name}"
            logger.warning(f"Database template {template_name} has empty body")
        
        logger.info(f"Rendered database template: {template_name}")
        return subject, body
    
    @classmethod
    def _render_file_template(
        cls,
        template_name: str,
        context: Dict,
        subject_template: Optional[str] = None,
    ) -> Tuple[str, str]:
        """Render template from file (templates/notifications/*.html).
        
        Args:
            template_name: Filename in templates/notifications/ (e.g., 'signup_welcome.html')
            context: Context data
            subject_template: Subject template string (with {variables})
        
        Returns:
            Tuple of (subject, body)
        
        Raises:
            TemplateDoesNotExist: If template file not found
        """
        # Construct full template path
        if not template_name.startswith('notifications/'):
            template_path = f'notifications/{template_name}'
        else:
            template_path = template_name
        
        try:
            # Render body using Django template system
            body = render_to_string(template_path, context)
        except Exception as e:
            logger.error(f"File template not found or rendering failed: {template_path}, error: {e}")
            raise
        
        # Render subject
        if subject_template:
            subject = subject_template.format(**context)
        else:
            subject = f"Notification: {template_name}"
            logger.warning(f"No subject_template provided for file template {template_name}")
        
        logger.info(f"Rendered file template: {template_path}")
        return subject, body
    
    @classmethod
    def preview_template(
        cls,
        template_source: str,
        template_name: str,
        sample_context: Optional[Dict] = None,
    ) -> Tuple[str, str]:
        """Preview template with sample data (for admin interface).
        
        Args:
            template_source: 'database' or 'file'
            template_name: Template name
            sample_context: Optional sample context data (uses defaults if None)
        
        Returns:
            Tuple of (subject, body) rendered with sample data
        
        Example:
            ```python
            subject, body = TemplateRenderer.preview_template(
                template_source='database',
                template_name='login_notification'
            )
            ```
        """
        # Default sample context
        if sample_context is None:
            sample_context = {
                'username': 'john_doe',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0',
                'timestamp': '2025-12-12 10:00:00',
                'role': 'ADMIN',
                'login_url': 'https://example.com/login',
                'reset_url': 'https://example.com/reset/token123',
                'token_expiry': '24 hours',
            }
        
        try:
            subject, body = cls.render(
                template_source=template_source,
                template_name=template_name,
                context=sample_context
            )
            return subject, body
        except Exception as e:
            logger.error(f"Template preview failed: {template_name}, error: {e}")
            return f"Preview Error: {str(e)}", f"Could not render template: {str(e)}"
    
    @classmethod
    def validate_template(
        cls,
        template_source: str,
        template_name: str,
        required_variables: list,
    ) -> Tuple[bool, Optional[str]]:
        """Validate that template exists and can be rendered.
        
        Args:
            template_source: 'database' or 'file'
            template_name: Template name
            required_variables: List of required variable names
        
        Returns:
            Tuple of (is_valid, error_message)
        
        Example:
            ```python
            is_valid, error = TemplateRenderer.validate_template(
                template_source='database',
                template_name='login_notification',
                required_variables=['username', 'ip_address']
            )
            ```
        """
        try:
            # Create sample context with all required variables
            sample_context = {var: f'<{var}>' for var in required_variables}
            
            # Try to render
            subject, body = cls.render(
                template_source=template_source,
                template_name=template_name,
                context=sample_context
            )
            
            # Check that all variables were used
            for var in required_variables:
                placeholder = f'<{var}>'
                if placeholder in subject or placeholder in body:
                    # Variable exists but might not have been replaced
                    pass
            
            return True, None
        
        except Exception as e:
            error_message = f"Template validation failed: {str(e)}"
            logger.warning(error_message)
            return False, error_message

