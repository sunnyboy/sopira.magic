#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/validators/session.py
#   Session Validator - Config-driven session validation
#   Session validation using AUTH_CONFIG
#..............................................................

"""
Session Validator - Config-Driven Session Validation.

Validates sessions according to AUTH_CONFIG session rules.

Usage:
```python
from sopira_magic.apps.authentification.validators import validate_session
is_valid = validate_session(request)
```
"""

from typing import Optional

from django.utils import timezone

from ..config import get_session_config


def validate_session(request, config: Optional[dict] = None) -> bool:
    """Validate session according to AUTH_CONFIG rules.

    Args:
        request: Django request object
        config: Optional custom config (defaults to AUTH_CONFIG)

    Returns:
        True if session is valid, False otherwise

    Example:
        ```python
        if validate_session(request):
            # Session is valid
            pass
        ```
    """
    if not hasattr(request, "session"):
        return False

    if not request.session.session_key:
        return False

    # Use session config from AUTH_CONFIG
    session_config = config or get_session_config()

    # Check session timeout
    session_timeout = session_config.get("session_timeout", 86400)  # Default 24 hours

    try:
        # Import Session here to avoid AppRegistryNotReady error
        from django.contrib.sessions.models import Session
        session = Session.objects.get(session_key=request.session.session_key)
        # Check if session has expired based on last activity
        if session.expire_date:
            if timezone.now() > session.expire_date:
                return False
    except (Session.DoesNotExist, ImportError):
        return False

    return True

