#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/config.py
#   Authentication Config - SSOT for authentication settings
#   Single source of truth for all authentication configurations
#..............................................................

"""
Authentication Configuration - SINGLE SOURCE OF TRUTH.

ConfigDriven prístup: všetky authentication nastavenia sú sústredené v jednej
SSOT konfigurácii. Žiadny hardcode - všetka logika vychádza z tejto konfigurácie.

Configuration Structure:
- AUTH_CONFIG: Complete authentication configuration dictionary
- Helper functions: get_auth_config(), get_validation_config(), is_endpoint_enabled()

Usage:
```python
from sopira_magic.apps.authentification.config import AUTH_CONFIG, get_auth_config
login_config = get_auth_config('login')
if login_config.get('enabled'):
    # Process login
```
"""

from typing import Dict, Optional
from types import MappingProxyType

from .types import (
    AuthConfig,
    AuthAction,
    LoginConfig,
    SignupConfig,
    LogoutConfig,
    PasswordResetConfig,
    PasswordResetConfirmConfig,
    Verify2FAConfig,
    CheckAuthConfig,
    ValidationConfig,
    AuditConfig,
    NotificationConfig,
    SessionConfig,
)


# =============================================================================
# AUTHENTICATION CONFIGURATION - SSOT
# =============================================================================

_RAW_AUTH_CONFIG: AuthConfig = {
    "login": {
        "enabled": True,
        "require_csrf": True,
        "session_timeout": 86400,  # 24 hours
        "max_attempts": 5,
        "lockout_duration": 300,  # 5 minutes
        "audit_enabled": True,
        "notification_enabled": True,
    },
    "signup": {
        "enabled": True,
        "require_email_verification": False,
        "default_role": "ADMIN",  # New users are ADMIN by default (Thermal Eye pattern)
        "auto_login": True,
        "audit_enabled": True,
        "notification_enabled": True,
    },
    "logout": {
        "enabled": True,
        "clear_session": True,
        "invalidate_tokens": False,  # Not implemented yet
        "audit_enabled": True,
    },
    "password_reset": {
        "enabled": True,
        "token_expiry": 86400,  # 24 hours
        "email_template": "password_reset",
        "require_email": True,
        "audit_enabled": True,
        "notification_enabled": True,
    },
    "password_reset_confirm": {
        "enabled": True,
        "token_validation": True,
        "min_password_length": 8,
        "audit_enabled": True,
        "notification_enabled": False,
    },
    "verify_2fa": {
        "enabled": False,  # Not implemented yet
        "provider": "TOTP",
        "code_length": 6,
        "expiry": 300,  # 5 minutes
        "audit_enabled": True,
    },
    "check_auth": {
        "enabled": True,
        "return_user_data": True,
        "include_permissions": True,
    },
    "validation": {
        "password": {
            "min_length": 8,
            "require_uppercase": False,
            "require_lowercase": False,
            "require_numbers": False,
            "require_special": False,
            "forbidden_patterns": ["password", "123456", "qwerty"],
        },
        "username": {
            "min_length": 3,
            "max_length": 150,
            "allowed_chars": r"^[a-zA-Z0-9_]+$",
            "forbidden_patterns": ["admin", "root", "system"],
        },
        "email": {
            "require_verification": False,
            "allowed_domains": [],  # Empty = all domains allowed
            "blocked_domains": [],
        },
    },
    "audit": {
        "audit_enabled": True,
        "audit_actions": [
            AuthAction.LOGIN,
            AuthAction.LOGOUT,
            AuthAction.SIGNUP,
            AuthAction.LOGIN_FAILED,
            AuthAction.PASSWORD_RESET,
            AuthAction.PASSWORD_RESET_CONFIRM,
        ],
        "audit_fields": [
            "username",
            "email",
            "ip_address",
            "user_agent",
            "timestamp",
            "success",
        ],
    },
    "notification": {
        "notifications_enabled": True,
        "login_notification": {
            "enabled": True,
            "email_template": "login_notification",
            "recipients": ["admin"],  # "admin" = settings.ADMIN_EMAIL
        },
        "signup_notification": {
            "enabled": True,
            "email_template": "signup_notification",
            "recipients": ["admin"],
        },
        "password_reset_notification": {
            "enabled": True,
            "email_template": "password_reset",
        },
    },
    "session": {
        "session_timeout": 86400,  # 24 hours
        "session_cookie_name": "sessionid",
        "session_cookie_secure": False,  # Set via SecurityEngine
        "session_cookie_httponly": True,
        "session_cookie_samesite": "Lax",
    },
}

# Immutable proxy to prevent accidental modifications
AUTH_CONFIG: AuthConfig = MappingProxyType(_RAW_AUTH_CONFIG)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_auth_config(endpoint: str) -> Optional[Dict]:
    """Get authentication configuration for a specific endpoint.

    Args:
        endpoint: Endpoint name (e.g., 'login', 'signup', 'logout')

    Returns:
        Configuration dictionary for the endpoint, or None if not found

    Example:
        ```python
        login_config = get_auth_config('login')
        if login_config and login_config.get('enabled'):
            # Process login
        ```
    """
    return AUTH_CONFIG.get(endpoint)  # type: ignore


def get_validation_config(validation_type: str) -> Optional[Dict]:
    """Get validation configuration for a specific validation type.

    Args:
        validation_type: Validation type (e.g., 'password', 'username', 'email')

    Returns:
        Validation configuration dictionary, or None if not found

    Example:
        ```python
        password_config = get_validation_config('password')
        min_length = password_config.get('min_length', 8)
        ```
    """
    validation = AUTH_CONFIG.get("validation")
    if validation:
        return validation.get(validation_type)  # type: ignore
    return None


def is_endpoint_enabled(endpoint: str) -> bool:
    """Check if an authentication endpoint is enabled.

    Args:
        endpoint: Endpoint name (e.g., 'login', 'signup', 'logout')

    Returns:
        True if endpoint is enabled, False otherwise

    Example:
        ```python
        if is_endpoint_enabled('login'):
            # Process login request
        ```
    """
    config = get_auth_config(endpoint)
    if config:
        return config.get("enabled", False)
    return False


def get_audit_config() -> AuditConfig:
    """Get audit configuration.

    Returns:
        Audit configuration dictionary

    Example:
        ```python
        audit_config = get_audit_config()
        if audit_config.get('audit_enabled'):
            # Log action
        ```
    """
    return AUTH_CONFIG.get("audit", {})  # type: ignore


def get_notification_config() -> NotificationConfig:
    """Get notification configuration.

    Returns:
        Notification configuration dictionary

    Example:
        ```python
        notif_config = get_notification_config()
        if notif_config.get('notifications_enabled'):
            # Send notification
        ```
    """
    return AUTH_CONFIG.get("notification", {})  # type: ignore


def get_session_config() -> SessionConfig:
    """Get session configuration.

    Returns:
        Session configuration dictionary

    Example:
        ```python
        session_config = get_session_config()
        timeout = session_config.get('session_timeout', 86400)
        ```
    """
    return AUTH_CONFIG.get("session", {})  # type: ignore

