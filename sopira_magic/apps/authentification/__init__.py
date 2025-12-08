#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/__init__.py
#   Authentication Module - Public API exports
#   Config-driven authentication module
#..............................................................

"""
Authentication Module - Public API Exports.

Config-driven authentication module using AUTH_CONFIG as SSOT.
All authentication logic is driven by configuration, no hardcoded domain logic.

Public API:
- AuthEngine: Main authentication engine
- AUTH_CONFIG: Single Source of Truth configuration
- Registry functions: register_audit_logger, register_notification_sender, etc.
- Validators: validate_password, validate_username, validate_email
"""

from .engine import AuthEngine
from .config import AUTH_CONFIG, get_auth_config, is_endpoint_enabled
from .registry import (
    register_audit_logger,
    register_notification_sender,
    register_user_serializer,
    register_role_provider,
    register_password_validator,
    get_audit_logger,
    get_notification_sender,
    get_user_serializer,
    get_role_provider,
    get_password_validator,
)
from .validators import validate_password, validate_username, validate_email
from .types import AuthAction, AuthProvider

__all__ = [
    # Engine
    "AuthEngine",
    # Config
    "AUTH_CONFIG",
    "get_auth_config",
    "is_endpoint_enabled",
    # Registry
    "register_audit_logger",
    "register_notification_sender",
    "register_user_serializer",
    "register_role_provider",
    "register_password_validator",
    "get_audit_logger",
    "get_notification_sender",
    "get_user_serializer",
    "get_role_provider",
    "get_password_validator",
    # Validators
    "validate_password",
    "validate_username",
    "validate_email",
    # Types
    "AuthAction",
    "AuthProvider",
]
