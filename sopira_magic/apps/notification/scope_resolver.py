#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/notification/scope_resolver.py
#   Scope Resolver - Scope-aware recipient resolution
#   Integrates with scoping module for hierarchical notifications
#..............................................................

"""
Scope Resolver - Scope-Aware Recipient Resolution.

Resolves notification recipients based on scoping rules.
Integrates with sopira_magic.apps.scoping for hierarchical access control.

Key Features:
- Get admin emails in user's scope
- Filter recipients based on scope patterns
- Support for scope-aware notification routing

Usage:
```python
from sopira_magic.apps.notification.scope_resolver import ScopeResolver

# Get admins in user's scope
admins = ScopeResolver.get_scope_admins(user)

# Filter recipients by scope
filtered = ScopeResolver.filter_by_scope(recipients, user, scope_pattern='same_company')
```
"""

import logging
from typing import List, Optional, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class ScopeResolver:
    """Resolves notification recipients using scoping rules."""
    
    @classmethod
    def get_scope_admins(cls, user: Any) -> List[str]:
        """Get admin email addresses in user's scope.
        
        Args:
            user: User object (scope owner)
        
        Returns:
            List of admin email addresses in user's scope
        
        Example:
            ```python
            admins = ScopeResolver.get_scope_admins(user)
            # ['admin1@example.com', 'admin2@example.com']
            ```
        """
        from sopira_magic.apps.m_user.models import User
        
        try:
            # Get all users with ADMIN or SUPERADMIN role
            admin_users = User.objects.filter(
                role__in=['ADMIN', 'SUPERADMIN'],
                email__isnull=False
            ).exclude(email='')
            
            # TODO: Apply scoping filter here when scoping is fully integrated
            # For now, return all admins (SUPERADMIN sees everything)
            # In future: apply ScopingEngine.apply_rules to filter by scope
            
            admin_emails = list(admin_users.values_list('email', flat=True))
            
            logger.debug(f"Found {len(admin_emails)} scope admins for user {user.username}")
            return admin_emails
        
        except Exception as e:
            logger.error(f"Error getting scope admins: {e}")
            return []
    
    @classmethod
    def filter_by_scope(
        cls,
        recipients: List[str],
        user: Any,
        scope_pattern: str = ''
    ) -> List[str]:
        """Filter recipients based on scope pattern.
        
        Args:
            recipients: List of email addresses
            user: User object (scope owner)
            scope_pattern: Scope pattern to apply (e.g., 'same_company', 'same_factory')
        
        Returns:
            Filtered list of email addresses
        
        Example:
            ```python
            filtered = ScopeResolver.filter_by_scope(
                recipients=['admin1@example.com', 'admin2@example.com'],
                user=current_user,
                scope_pattern='same_company'
            )
            ```
        """
        if not scope_pattern:
            # No scope filtering
            return recipients
        
        try:
            # TODO: Implement scope-based filtering
            # For now, return all recipients
            # In future: use scoping engine to filter based on hierarchy
            
            logger.debug(
                f"Scope filtering not yet implemented, pattern: {scope_pattern}, "
                f"returning all {len(recipients)} recipients"
            )
            return recipients
        
        except Exception as e:
            logger.error(f"Error filtering by scope: {e}")
            return recipients
    
    @classmethod
    def resolve_recipients_from_matrix(
        cls,
        notification_type: str,
        context: dict,
        user: Optional[Any] = None
    ) -> List[str]:
        """Resolve recipients from NotificationMatrix for given notification type.
        
        Args:
            notification_type: Notification type identifier
            context: Context data (contains user, email, etc.)
            user: Optional user object (scope owner)
        
        Returns:
            List of resolved email addresses
        
        Example:
            ```python
            recipients = ScopeResolver.resolve_recipients_from_matrix(
                notification_type='login_notification',
                context={'user': user, 'email': 'user@example.com'},
                user=user
            )
            ```
        """
        from .models import NotificationMatrix
        
        recipients = []
        
        try:
            # Get all enabled matrix entries for this notification type
            matrix_entries = NotificationMatrix.objects.filter(
                notification_type=notification_type,
                enabled=True
            )
            
            for entry in matrix_entries:
                recipient_type = entry.recipient_type
                
                if recipient_type == 'admin':
                    # Add admin email from settings
                    admin_email = getattr(settings, 'ADMIN_EMAIL', None)
                    if admin_email:
                        recipients.append(admin_email)
                
                elif recipient_type == 'user':
                    # Add user email from context
                    user_obj = context.get('user')
                    if user_obj and hasattr(user_obj, 'email'):
                        recipients.append(user_obj.email)
                    elif context.get('email'):
                        recipients.append(context.get('email'))
                
                elif recipient_type == 'scope_admins':
                    # Add scope admins
                    if user:
                        scope_admins = cls.get_scope_admins(user)
                        recipients.extend(scope_admins)
                
                elif recipient_type == 'custom':
                    # Add custom email from recipient_identifier
                    if entry.recipient_identifier:
                        recipients.append(entry.recipient_identifier)
                
                elif recipient_type == 'role':
                    # Add all users with specific role
                    if entry.recipient_identifier:
                        role_emails = cls._get_users_by_role(entry.recipient_identifier)
                        recipients.extend(role_emails)
            
            # Remove duplicates
            recipients = list(set(recipients))
            
            # Apply scope filtering if needed
            if user:
                for entry in matrix_entries:
                    if entry.scope_pattern:
                        recipients = cls.filter_by_scope(
                            recipients,
                            user,
                            entry.scope_pattern
                        )
                        break  # Apply only first scope pattern
            
            logger.info(
                f"Resolved {len(recipients)} recipients for {notification_type} "
                f"from {matrix_entries.count()} matrix entries"
            )
            return recipients
        
        except Exception as e:
            logger.error(f"Error resolving recipients from matrix: {e}")
            return []
    
    @classmethod
    def _get_users_by_role(cls, role: str) -> List[str]:
        """Get email addresses of all users with specific role.
        
        Args:
            role: Role name (e.g., 'ADMIN', 'STAFF')
        
        Returns:
            List of email addresses
        """
        from sopira_magic.apps.m_user.models import User
        
        try:
            users = User.objects.filter(
                role=role,
                email__isnull=False
            ).exclude(email='')
            
            return list(users.values_list('email', flat=True))
        
        except Exception as e:
            logger.error(f"Error getting users by role {role}: {e}")
            return []
    
    @classmethod
    def get_default_admin_email(cls) -> Optional[str]:
        """Get default admin email from settings.
        
        Returns:
            Admin email address or None
        
        Example:
            ```python
            admin_email = ScopeResolver.get_default_admin_email()
            ```
        """
        return getattr(settings, 'ADMIN_EMAIL', None)
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email address format.
        
        Args:
            email: Email address to validate
        
        Returns:
            True if valid, False otherwise
        """
        import re
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @classmethod
    def filter_valid_emails(cls, emails: List[str]) -> List[str]:
        """Filter out invalid email addresses.
        
        Args:
            emails: List of email addresses
        
        Returns:
            List of valid email addresses
        
        Example:
            ```python
            valid_emails = ScopeResolver.filter_valid_emails(['test@example.com', 'invalid'])
            # ['test@example.com']
            ```
        """
        valid_emails = [email for email in emails if cls.validate_email(email)]
        
        if len(valid_emails) < len(emails):
            invalid_count = len(emails) - len(valid_emails)
            logger.warning(f"Filtered out {invalid_count} invalid email addresses")
        
        return valid_emails

