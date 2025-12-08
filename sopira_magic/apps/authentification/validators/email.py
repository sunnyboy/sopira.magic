#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/validators/email.py
#   Email Validator - Config-driven email validation
#   Email validation using AUTH_CONFIG
#..............................................................

"""
Email Validator - Config-Driven Email Validation.

Validates email addresses according to AUTH_CONFIG validation rules.

Usage:
```python
from sopira_magic.apps.authentification.validators import validate_email
is_valid, error = validate_email("user@example.com")
```
"""

import re
from typing import Optional, Tuple

from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError

from ..config import get_validation_config


def validate_email(email: str, config: Optional[dict] = None) -> Tuple[bool, Optional[str]]:
    """Validate email according to AUTH_CONFIG rules.

    Args:
        email: Email address to validate
        config: Optional custom config (defaults to AUTH_CONFIG)

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if email is valid, False otherwise
        - error_message: Error message if invalid, None if valid

    Example:
        ```python
        is_valid, error = validate_email("user@example.com")
        if not is_valid:
            print(f"Email error: {error}")
        ```
    """
    # Basic email format validation using Django's validator
    try:
        django_validate_email(email)
    except ValidationError:
        return False, "Invalid email format"

    # Use validation from AUTH_CONFIG
    validation_config = config or get_validation_config("email") or {}

    # Extract domain from email
    email_parts = email.split("@")
    if len(email_parts) != 2:
        return False, "Invalid email format"

    domain = email_parts[1].lower()

    # Check allowed domains
    allowed_domains = validation_config.get("allowed_domains", [])
    if allowed_domains:  # Empty list means all domains allowed
        if domain not in [d.lower() for d in allowed_domains]:
            return False, f"Email domain '{domain}' is not allowed"

    # Check blocked domains
    blocked_domains = validation_config.get("blocked_domains", [])
    if domain in [d.lower() for d in blocked_domains]:
        return False, f"Email domain '{domain}' is blocked"

    return True, None

