#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/types.py
#   Authentication Types - TypedDict and Enum definitions
#   SSOT type definitions for authentication configuration
#..............................................................

"""
Authentication Types - SSOT Type Definitions.

TypedDict and Enum definitions for authentication configuration.
All types are used in AUTH_CONFIG to ensure type safety.

Types:
- AuthAction: Enum of authentication action types
- AuthProvider: Enum of authentication provider types
- LoginConfig: TypedDict for login endpoint configuration
- SignupConfig: TypedDict for signup endpoint configuration
- PasswordResetConfig: TypedDict for password reset configuration
- ValidationConfig: TypedDict for validation configuration
- AuditConfig: TypedDict for audit configuration
- NotificationConfig: TypedDict for notification configuration
- SessionConfig: TypedDict for session configuration
- AuthConfig: TypedDict for complete authentication configuration

Usage:
```python
from sopira_magic.apps.authentification.types import AuthAction, LoginConfig
action = AuthAction.LOGIN
config: LoginConfig = {"enabled": True, "require_csrf": True, ...}
```
"""

from enum import Enum
from typing import List, Optional, TypedDict


class AuthAction(str, Enum):
    """Authentication action types - SSOT."""

    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    SIGNUP = "SIGNUP"
    LOGIN_FAILED = "LOGIN_FAILED"
    PASSWORD_RESET = "PASSWORD_RESET"
    PASSWORD_RESET_CONFIRM = "PASSWORD_RESET_CONFIRM"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    VERIFY_2FA = "VERIFY_2FA"
    CHECK_AUTH = "CHECK_AUTH"


class AuthProvider(str, Enum):
    """Authentication provider types - SSOT."""

    SESSION = "SESSION"  # Django session-based
    JWT = "JWT"  # JSON Web Token
    OAUTH = "OAUTH"  # OAuth2
    OAUTH_GOOGLE = "OAUTH_GOOGLE"
    OAUTH_GITHUB = "OAUTH_GITHUB"
    OAUTH_FACEBOOK = "OAUTH_FACEBOOK"


class LoginConfig(TypedDict, total=False):
    """Login endpoint configuration."""

    enabled: bool
    require_csrf: bool
    session_timeout: int  # seconds
    max_attempts: int
    lockout_duration: int  # seconds
    audit_enabled: bool
    notification_enabled: bool


class SignupConfig(TypedDict, total=False):
    """Signup endpoint configuration."""

    enabled: bool
    require_email_verification: bool
    default_role: str  # e.g., "ADMIN", "READER"
    auto_login: bool
    audit_enabled: bool
    notification_enabled: bool


class LogoutConfig(TypedDict, total=False):
    """Logout endpoint configuration."""

    enabled: bool
    clear_session: bool
    invalidate_tokens: bool
    audit_enabled: bool


class PasswordResetConfig(TypedDict, total=False):
    """Password reset endpoint configuration."""

    enabled: bool
    token_expiry: int  # seconds
    email_template: str
    require_email: bool
    audit_enabled: bool
    notification_enabled: bool


class PasswordResetConfirmConfig(TypedDict, total=False):
    """Password reset confirmation endpoint configuration."""

    enabled: bool
    token_validation: bool
    min_password_length: int
    audit_enabled: bool
    notification_enabled: bool


class Verify2FAConfig(TypedDict, total=False):
    """2FA verification endpoint configuration."""

    enabled: bool
    provider: str  # e.g., "TOTP", "SMS"
    code_length: int
    expiry: int  # seconds
    audit_enabled: bool


class CheckAuthConfig(TypedDict, total=False):
    """Check authentication endpoint configuration."""

    enabled: bool
    return_user_data: bool
    include_permissions: bool


class PasswordValidationConfig(TypedDict, total=False):
    """Password validation configuration."""

    min_length: int
    require_uppercase: bool
    require_lowercase: bool
    require_numbers: bool
    require_special: bool
    forbidden_patterns: List[str]  # e.g., ["password", "123456"]


class UsernameValidationConfig(TypedDict, total=False):
    """Username validation configuration."""

    min_length: int
    max_length: int
    allowed_chars: str  # regex pattern
    forbidden_patterns: List[str]


class EmailValidationConfig(TypedDict, total=False):
    """Email validation configuration."""

    require_verification: bool
    allowed_domains: List[str]
    blocked_domains: List[str]


class ValidationConfig(TypedDict, total=False):
    """Complete validation configuration."""

    password: PasswordValidationConfig
    username: UsernameValidationConfig
    email: EmailValidationConfig


class AuditConfig(TypedDict, total=False):
    """Audit logging configuration."""

    audit_enabled: bool
    audit_actions: List[AuthAction]
    audit_fields: List[str]  # Fields to include in audit log


class NotificationConfig(TypedDict, total=False):
    """Notification configuration."""

    notifications_enabled: bool
    login_notification: dict  # {enabled, email_template, recipients}
    signup_notification: dict  # {enabled, email_template, recipients}
    password_reset_notification: dict  # {enabled, email_template}


class SessionConfig(TypedDict, total=False):
    """Session management configuration."""

    session_timeout: int  # seconds
    session_cookie_name: str
    session_cookie_secure: bool
    session_cookie_httponly: bool
    session_cookie_samesite: str  # "Lax", "Strict", "None"


class AuthConfig(TypedDict, total=False):
    """Complete authentication configuration - SSOT."""

    login: LoginConfig
    signup: SignupConfig
    logout: LogoutConfig
    password_reset: PasswordResetConfig
    password_reset_confirm: PasswordResetConfirmConfig
    verify_2fa: Verify2FAConfig
    check_auth: CheckAuthConfig
    validation: ValidationConfig
    audit: AuditConfig
    notification: NotificationConfig
    session: SessionConfig

