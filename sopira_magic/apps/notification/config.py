#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/notification/config.py
#   Notification Config - SSOT for notification settings
#   Single source of truth for all notification configurations
#..............................................................

"""
Notification Configuration - SINGLE SOURCE OF TRUTH.

ConfigDriven prístup: všetky notification nastavenia sú sústredené v jednej
SSOT konfigurácii. Žiadny hardcode - všetka logika vychádza z tejto konfigurácie.

Configuration Structure:
- NOTIFICATION_CONFIG: Complete notification configuration dictionary
- Helper functions: get_notification_config(), is_notification_enabled(), get_template_config()

Usage:
```python
from sopira_magic.apps.notification.config import NOTIFICATION_CONFIG, get_notification_config
notif_config = get_notification_config('login_notification')
if notif_config.get('enabled'):
    # Process notification
```
"""

from typing import Dict, Optional, List
from types import MappingProxyType


# =============================================================================
# NOTIFICATION CONFIGURATION - SSOT
# =============================================================================

_RAW_NOTIFICATION_CONFIG: Dict = {
    # SMTP Backend Configuration
    "smtp": {
        "backend": "smtp",
        "enabled": True,
        "timeout": 30,
    },
    
    # Notification Types Configuration
    "notification_types": {
        # Login Notification - SA dostane info o prihlásení
        "login_notification": {
            "enabled": True,
            "channel": "email",
            "template_source": "file",  # Pekný HTML template
            "template_name": "login_notification.html",
            "scope_aware": True,  # Len admini v scope usera
            "default_recipients": ["admin"],  # admin = ADMIN_EMAIL z settings
            "subject_template": "🔐 Login Notification - {username}",
            "variables": ["username", "email", "ip_address", "user_agent", "timestamp", "role"],
        },
        
        # Signup Notification Admin - SA dostane info o novom účte
        "signup_notification_admin": {
            "enabled": True,
            "channel": "email",
            "template_source": "database",  # Simple text v DB
            "template_name": "signup_notification_admin",
            "scope_aware": True,  # Len admini v scope nového usera
            "default_recipients": ["admin"],
            "subject_template": "👤 New User Signup - {username}",
            "variables": ["username", "email", "role", "timestamp", "ip_address"],
        },
        
        # Signup Welcome User - Nový user dostane welcome email
        "signup_notification_user": {
            "enabled": True,
            "channel": "email",
            "template_source": "file",  # Pekný HTML súbor
            "template_name": "signup_welcome.html",
            "scope_aware": False,  # Ide priamo userovi
            "default_recipients": ["user"],  # user = context['user']
            "subject_template": "Welcome to Sopira Magic, {first_name}!",
            "variables": ["first_name", "last_name", "username", "email", "login_url"],
        },
        
        # Password Reset - User dostane reset link
        "password_reset": {
            "enabled": True,
            "channel": "email",
            "template_source": "file",  # HTML súbor
            "template_name": "password_reset.html",
            "scope_aware": False,  # Ide priamo userovi
            "default_recipients": ["user"],
            "subject_template": "🔑 Password Reset Request",
            "variables": ["username", "email", "reset_url", "uid", "token", "token_expiry"],
        },
        
        # Password Reset Confirm - User dostane potvrdenie o zmene hesla
        "password_reset_confirm": {
            "enabled": True,
            "channel": "email",
            "template_source": "database",
            "template_name": "password_reset_confirm",
            "scope_aware": False,
            "default_recipients": ["user"],
            "subject_template": "✅ Password Changed Successfully",
            "variables": ["username", "email", "timestamp", "ip_address"],
        },
    },
    
    # Fallback Configuration
    "fallback": {
        "use_console_backend_on_error": False,  # Pri chybe neprepnúť na console
        "log_failed_notifications": True,
        "retry_failed": False,  # Neimplementované zatiaľ
        "max_retries": 3,
    },
    
    # Logging Configuration
    "logging": {
        "log_all_notifications": True,
        "log_success": True,
        "log_failures": True,
        "include_context_data": True,  # Ukladať context do logu
    },
}

# Immutable proxy to prevent accidental modifications
NOTIFICATION_CONFIG: Dict = MappingProxyType(_RAW_NOTIFICATION_CONFIG)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_notification_config(notification_type: str) -> Optional[Dict]:
    """Get notification configuration for a specific notification type.
    
    Args:
        notification_type: Notification type (e.g., 'login_notification', 'signup_notification_admin')
    
    Returns:
        Configuration dictionary for the notification type, or None if not found
    
    Example:
        ```python
        login_config = get_notification_config('login_notification')
        if login_config and login_config.get('enabled'):
            # Process notification
        ```
    """
    notification_types = NOTIFICATION_CONFIG.get("notification_types", {})
    return notification_types.get(notification_type)  # type: ignore


def is_notification_enabled(notification_type: str) -> bool:
    """Check if a notification type is enabled.
    
    Args:
        notification_type: Notification type (e.g., 'login_notification')
    
    Returns:
        True if notification is enabled, False otherwise
    
    Example:
        ```python
        if is_notification_enabled('login_notification'):
            # Send notification
        ```
    """
    config = get_notification_config(notification_type)
    if config:
        return config.get("enabled", False)
    return False


def get_template_config(notification_type: str) -> Optional[Dict]:
    """Get template configuration for a notification type.
    
    Args:
        notification_type: Notification type
    
    Returns:
        Dictionary with template_source, template_name, variables
    
    Example:
        ```python
        template_config = get_template_config('login_notification')
        source = template_config.get('template_source')  # 'database' or 'file'
        ```
    """
    config = get_notification_config(notification_type)
    if not config:
        return None
    
    return {
        "template_source": config.get("template_source"),
        "template_name": config.get("template_name"),
        "variables": config.get("variables", []),
        "subject_template": config.get("subject_template", ""),
    }


def get_smtp_config() -> Dict:
    """Get SMTP configuration.
    
    Returns:
        SMTP configuration dictionary
    
    Example:
        ```python
        smtp_config = get_smtp_config()
        if smtp_config.get('enabled'):
            # Use SMTP backend
        ```
    """
    return NOTIFICATION_CONFIG.get("smtp", {})  # type: ignore


def get_logging_config() -> Dict:
    """Get logging configuration.
    
    Returns:
        Logging configuration dictionary
    
    Example:
        ```python
        logging_config = get_logging_config()
        if logging_config.get('log_all_notifications'):
            # Log this notification
        ```
    """
    return NOTIFICATION_CONFIG.get("logging", {})  # type: ignore


def get_default_recipients(notification_type: str) -> List[str]:
    """Get default recipients for a notification type.
    
    Args:
        notification_type: Notification type
    
    Returns:
        List of recipient types ('admin', 'user', etc.)
    
    Example:
        ```python
        recipients = get_default_recipients('login_notification')
        # ['admin']
        ```
    """
    config = get_notification_config(notification_type)
    if config:
        return config.get("default_recipients", [])
    return []


def is_scope_aware(notification_type: str) -> bool:
    """Check if notification type is scope-aware.
    
    Args:
        notification_type: Notification type
    
    Returns:
        True if scope-aware, False otherwise
    
    Example:
        ```python
        if is_scope_aware('login_notification'):
            # Resolve recipients via scope
        ```
    """
    config = get_notification_config(notification_type)
    if config:
        return config.get("scope_aware", False)
    return False


def get_all_notification_types() -> List[str]:
    """Get all configured notification types.
    
    Returns:
        List of notification type names
    
    Example:
        ```python
        all_types = get_all_notification_types()
        # ['login_notification', 'signup_notification_admin', ...]
        ```
    """
    notification_types = NOTIFICATION_CONFIG.get("notification_types", {})
    return list(notification_types.keys())

