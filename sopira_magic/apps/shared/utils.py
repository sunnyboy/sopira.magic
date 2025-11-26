#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/shared/utils.py
#   Shared Utils - Common utility functions
#   Reusable helper functions across applications
#..............................................................

"""
   Shared Utils - Common Utility Functions.

   Reusable utility functions used across multiple applications.
   Provides common helper functions for caching, formatting, and data manipulation.

   Functions:

   1. get_or_set_cache(key, func, timeout)
      - Get value from cache or set it using provided function
      - Args: key (str), func (callable), timeout (int, default 3600)
      - Returns: Cached or computed value

   2. safe_get_attr(obj, attr_path, default)
      - Safely get nested attribute from object
      - Args: obj, attr_path (dot-separated path), default
      - Returns: Attribute value or default
      - Example: safe_get_attr(user, 'profile.name', 'Unknown')

   3. format_currency(amount, currency)
      - Format amount as currency string
      - Args: amount (float), currency (str, default 'EUR')
      - Returns: Formatted currency string

   4. truncate_string(text, max_length, suffix)
      - Truncate string to max_length with suffix
      - Args: text (str), max_length (int, default 100), suffix (str, default '...')
      - Returns: Truncated string

   Usage:
   ```python
   from sopira_magic.apps.shared.utils import get_or_set_cache, safe_get_attr
   value = get_or_set_cache('key', lambda: expensive_operation(), timeout=3600)
   name = safe_get_attr(user, 'profile.name', 'Unknown')
   ```
"""

from typing import Any, Dict, Optional
from django.db import models
from django.core.cache import cache


def get_or_set_cache(key: str, func, timeout: int = 3600) -> Any:
    """
    Get value from cache or set it using provided function.
    
    Args:
        key: Cache key
        func: Function to call if value not in cache
        timeout: Cache timeout in seconds
    
    Returns:
        Cached or computed value
    """
    value = cache.get(key)
    if value is None:
        value = func()
        cache.set(key, value, timeout)
    return value


def safe_get_attr(obj: Any, attr_path: str, default: Any = None) -> Any:
    """
    Safely get nested attribute from object.
    
    Args:
        obj: Object to get attribute from
        attr_path: Dot-separated attribute path (e.g., 'user.profile.name')
        default: Default value if attribute doesn't exist
    
    Returns:
        Attribute value or default
    """
    try:
        for attr in attr_path.split('.'):
            obj = getattr(obj, attr)
        return obj
    except (AttributeError, TypeError):
        return default


def format_currency(amount: float, currency: str = 'EUR') -> str:
    """Format amount as currency string."""
    return f"{amount:,.2f} {currency}"


def truncate_string(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """Truncate string to max_length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
