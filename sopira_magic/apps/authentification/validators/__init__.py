#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/validators/__init__.py
#   Authentication Validators - Module exports
#   Config-driven validators for authentication
#..............................................................

"""
Authentication Validators - Module Exports.

Config-driven validators for authentication fields.
All validators use AUTH_CONFIG instead of hardcoded rules.
"""

from .password import validate_password
from .username import validate_username
from .email import validate_email

# validate_session is imported lazily to avoid AppRegistryNotReady error
# Use: from sopira_magic.apps.authentification.validators.session import validate_session

__all__ = [
    "validate_password",
    "validate_username",
    "validate_email",
]


def get_session_validator():
    """Lazy import of validate_session to avoid AppRegistryNotReady."""
    from .session import validate_session
    return validate_session

