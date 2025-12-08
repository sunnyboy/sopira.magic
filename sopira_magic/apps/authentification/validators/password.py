#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/validators/password.py
#   Password Validator - Config-driven password validation
#   Password validation using AUTH_CONFIG
#..............................................................

"""
Password Validator - Config-Driven Password Validation.

Validates passwords according to AUTH_CONFIG validation rules.
Supports custom validators via registry pattern.

Usage:
```python
from sopira_magic.apps.authentification.validators import validate_password
is_valid, error = validate_password("MyPassword123")
```
"""

import re
from typing import Optional, Tuple

from ..config import get_validation_config
from ..registry import get_password_validator


def validate_password(password: str, config: Optional[dict] = None) -> Tuple[bool, Optional[str]]:
    """Validate password according to AUTH_CONFIG rules.

    Args:
        password: Password to validate
        config: Optional custom config (defaults to AUTH_CONFIG)

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if password is valid, False otherwise
        - error_message: Error message if invalid, None if valid

    Example:
        ```python
        is_valid, error = validate_password("MyPassword123")
        if not is_valid:
            print(f"Password error: {error}")
        ```
    """
    # Check for custom validator first
    custom_validator = get_password_validator()
    if custom_validator:
        validation_config = config or get_validation_config("password") or {}
        return custom_validator(password, validation_config)

    # Use default validation from AUTH_CONFIG
    validation_config = config or get_validation_config("password") or {}

    # Check minimum length
    min_length = validation_config.get("min_length", 8)
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long"

    # Check for uppercase
    if validation_config.get("require_uppercase", False):
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"

    # Check for lowercase
    if validation_config.get("require_lowercase", False):
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"

    # Check for numbers
    if validation_config.get("require_numbers", False):
        if not re.search(r"\d", password):
            return False, "Password must contain at least one number"

    # Check for special characters
    if validation_config.get("require_special", False):
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain at least one special character"

    # Check forbidden patterns
    forbidden_patterns = validation_config.get("forbidden_patterns", [])
    password_lower = password.lower()
    for pattern in forbidden_patterns:
        if pattern.lower() in password_lower:
            return False, f"Password cannot contain '{pattern}'"

    return True, None

