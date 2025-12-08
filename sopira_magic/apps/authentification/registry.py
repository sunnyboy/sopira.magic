#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/registry.py
#   Authentication Registry - Callback registry pattern
#   Abstract callback registration for custom authentication logic
#..............................................................

"""
Authentication Registry - Callback Registry Pattern.

Registry pattern for abstracting custom authentication logic.
Allows host applications to register custom callbacks for:
- Audit logging
- Notification sending
- User data serialization
- Role management
- Password validation

Usage:
```python
from sopira_magic.apps.authentification.registry import (
    register_audit_logger,
    get_audit_logger,
)

def custom_audit_logger(action, user, **kwargs):
    # Custom audit logging logic
    pass

register_audit_logger(custom_audit_logger)
logger = get_audit_logger()
if logger:
    logger('LOGIN', user, success=True)
```
"""

from typing import Any, Callable, Dict, Optional

logger = None  # Will be set by logging module


def _get_logger():
    """Get logger instance."""
    global logger
    if logger is None:
        import logging
        logger = logging.getLogger(__name__)
    return logger


# =============================================================================
# REGISTRY STORAGE
# =============================================================================

_audit_logger: Optional[Callable] = None
_notification_sender: Optional[Callable] = None
_user_serializer: Optional[Callable] = None
_role_provider: Optional[Callable] = None
_password_validator: Optional[Callable] = None


# =============================================================================
# REGISTRY FUNCTIONS
# =============================================================================


def register_audit_logger(callback: Callable[[str, Optional[Any], Dict[str, Any]], None]) -> None:
    """Register custom audit logger callback.

    Args:
        callback: Function that accepts (action, user, **kwargs) and logs audit events

    Example:
        ```python
        def my_audit_logger(action, user, **kwargs):
            # Log to custom audit system
            pass

        register_audit_logger(my_audit_logger)
        ```
    """
    global _audit_logger
    _audit_logger = callback
    _get_logger().info("Audit logger registered")


def register_notification_sender(callback: Callable[[str, Dict[str, Any]], None]) -> None:
    """Register custom notification sender callback.

    Args:
        callback: Function that accepts (notification_type, data) and sends notifications

    Example:
        ```python
        def my_notification_sender(notification_type, data):
            # Send email/SMS/push notification
            pass

        register_notification_sender(my_notification_sender)
        ```
    """
    global _notification_sender
    _notification_sender = callback
    _get_logger().info("Notification sender registered")


def register_user_serializer(callback: Callable[[Any], Dict[str, Any]]) -> None:
    """Register custom user data serializer callback.

    Args:
        callback: Function that accepts user object and returns serialized user data

    Example:
        ```python
        def my_user_serializer(user):
            return {
                'id': user.id,
                'username': user.username,
                'custom_field': user.custom_field,
            }

        register_user_serializer(my_user_serializer)
        ```
    """
    global _user_serializer
    _user_serializer = callback
    _get_logger().info("User serializer registered")


def register_role_provider(callback: Callable[[Any], Dict[str, Any]]) -> None:
    """Register custom role provider callback.

    Args:
        callback: Function that accepts user object and returns role information

    Example:
        ```python
        def my_role_provider(user):
            role = UserPreference.role_for_user(user)
            return {
                'role': role,
                'role_display': UserPreference.UserRole(role).label,
                'role_priority': UserPreference.ROLE_PRIORITY.get(role, 0),
                'is_admin': UserPreference.user_is_admin(user),
            }

        register_role_provider(my_role_provider)
        ```
    """
    global _role_provider
    _role_provider = callback
    _get_logger().info("Role provider registered")


def register_password_validator(callback: Callable[[str, Dict[str, Any]], tuple[bool, Optional[str]]]) -> None:
    """Register custom password validator callback.

    Args:
        callback: Function that accepts (password, config) and returns (is_valid, error_message)

    Example:
        ```python
        def my_password_validator(password, config):
            if len(password) < config.get('min_length', 8):
                return False, 'Password too short'
            return True, None

        register_password_validator(my_password_validator)
        ```
    """
    global _password_validator
    _password_validator = callback
    _get_logger().info("Password validator registered")


# =============================================================================
# GETTER FUNCTIONS
# =============================================================================


def get_audit_logger() -> Optional[Callable]:
    """Get registered audit logger callback.

    Returns:
        Registered audit logger callback, or None if not registered

    Example:
        ```python
        logger = get_audit_logger()
        if logger:
            logger('LOGIN', user, success=True, ip_address='127.0.0.1')
        ```
    """
    return _audit_logger


def get_notification_sender() -> Optional[Callable]:
    """Get registered notification sender callback.

    Returns:
        Registered notification sender callback, or None if not registered

    Example:
        ```python
        sender = get_notification_sender()
        if sender:
            sender('login_notification', {'user': user, 'ip': '127.0.0.1'})
        ```
    """
    return _notification_sender


def get_user_serializer() -> Optional[Callable]:
    """Get registered user serializer callback.

    Returns:
        Registered user serializer callback, or None if not registered

    Example:
        ```python
        serializer = get_user_serializer()
        if serializer:
            user_data = serializer(user)
        else:
            user_data = default_serialize_user(user)
        ```
    """
    return _user_serializer


def get_role_provider() -> Optional[Callable]:
    """Get registered role provider callback.

    Returns:
        Registered role provider callback, or None if not registered

    Example:
        ```python
        provider = get_role_provider()
        if provider:
            role_data = provider(user)
        else:
            role_data = default_get_role(user)
        ```
    """
    return _role_provider


def get_password_validator() -> Optional[Callable]:
    """Get registered password validator callback.

    Returns:
        Registered password validator callback, or None if not registered

    Example:
        ```python
        validator = get_password_validator()
        if validator:
            is_valid, error = validator(password, config)
        else:
            is_valid, error = default_validate_password(password, config)
        ```
    """
    return _password_validator

