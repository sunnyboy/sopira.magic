#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/validators/username.py
#   Username Validator - Config-driven username validation
#   Username validation using AUTH_CONFIG
#..............................................................

"""
Username Validator - Config-Driven Username Validation.

Validates usernames according to AUTH_CONFIG validation rules.

Usage:
```python
from sopira_magic.apps.authentification.validators import validate_username
is_valid, error = validate_username("myusername")
```
"""

import re
from typing import Optional, Tuple

from ..config import get_validation_config


def validate_username(username: str, config: Optional[dict] = None) -> Tuple[bool, Optional[str]]:
    """Validate username according to AUTH_CONFIG rules.

    Args:
        username: Username to validate
        config: Optional custom config (defaults to AUTH_CONFIG)

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if username is valid, False otherwise
        - error_message: Error message if invalid, None if valid

    Example:
        ```python
        is_valid, error = validate_username("myusername")
        if not is_valid:
            print(f"Username error: {error}")
        ```
    """
    # Use validation from AUTH_CONFIG
    validation_config = config or get_validation_config("username") or {}

    # Check minimum length
    min_length = validation_config.get("min_length", 3)
    if len(username) < min_length:
        return False, f"Username must be at least {min_length} characters long"

    # Check maximum length
    max_length = validation_config.get("max_length", 150)
    if len(username) > max_length:
        return False, f"Username must be at most {max_length} characters long"

    # Check allowed characters
    allowed_chars = validation_config.get("allowed_chars", r"^[a-zA-Z0-9_]+$")
    if not re.match(allowed_chars, username):
        return False, "Username contains invalid characters"

    # Check forbidden patterns
    forbidden_patterns = validation_config.get("forbidden_patterns", [])
    username_lower = username.lower()
    for pattern in forbidden_patterns:
        if pattern.lower() in username_lower:
            return False, f"Username cannot contain '{pattern}'"

    return True, None

