#..............................................................
#   apps/scoping/__init__.py
#   Public API for Scoping Module
#..............................................................

"""
Scoping Module - Public API.

Usage:
    from sopira_magic.apps.scoping import ScopingEngine, register_role_provider, register_scope_resolver
    
    # In core/apps.py:
    register_role_provider(my_role_provider)
    register_scope_resolver(my_scope_resolver)
    
    # In API viewsets:
    queryset = ScopingEngine.apply(queryset, request.user, table_name, config)
"""

from .engine import ScopingEngine
from .registry import register_role_provider, register_scope_resolver, get_scope_values, get_role
from .middleware import ScopingViewSetMixin

__all__ = [
    'ScopingEngine',
    'register_role_provider',
    'register_scope_resolver',
    'get_scope_values',
    'get_role',
    'ScopingViewSetMixin',
]

