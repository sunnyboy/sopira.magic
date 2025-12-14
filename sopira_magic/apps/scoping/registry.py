#..............................................................
#   apps/scoping/registry.py
#   Callback Registry for Scope Resolution
#..............................................................

"""
Registry for scope resolution callbacks.

Core/apps.py registers two callbacks:
1. role_provider: User → abstract scoping role
2. scope_resolver: (level, user, type) → List[scope IDs]

This keeps scoping module independent from specific models.
"""

from typing import List, Callable, Optional

# Global callback storage
_role_provider: Optional[Callable] = None
_scope_resolver: Optional[Callable] = None


def register_role_provider(callback: Callable[[object], str]) -> None:
    """
    Register callback that maps user to abstract scoping role.
    
    Args:
        callback: Function(user) → str (role: 'superuser', 'admin', 'staff', ...)
    """
    global _role_provider
    _role_provider = callback


def register_scope_resolver(callback: Callable[[int, object, str], List[str]]) -> None:
    """
    Register callback that resolves scope values for a given level.
    
    Args:
        callback: Function(level, user, scope_type) → List[str] (scope IDs)
    """
    global _scope_resolver
    _scope_resolver = callback


def get_role(user: object) -> str:
    """
    Get abstract scoping role for user.
    
    Args:
        user: User object
        
    Returns:
        Role string (e.g., 'superuser', 'admin', 'staff', 'reader')
    """
    if _role_provider:
        return _role_provider(user)
    return "reader"  # Safe default


def get_scope_values(level: int, user: object, scope_type: str) -> List[str]:
    """
    Get scope values (IDs) for a given level and user.
    
    Args:
        level: Scope level (0=user, 1=company, 2=factory, ...)
        user: User object
        scope_type: 'accessible' or 'selected'
        
    Returns:
        List of scope IDs (as strings)
    """
    if _scope_resolver:
        return _scope_resolver(level, user, scope_type)
    return []  # Safe default - empty scope




