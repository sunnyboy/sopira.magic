#..............................................................
#   apps/scoping/test_helpers.py
#   Unit test helper funkcie pre scoping engine
#..............................................................

"""
Unit test helper funkcie pre scoping engine.

Poskytuje nástroje na jednoduché testovanie scoping logiky s mock dátami.
Zvyšuje testovateľnosť a umožňuje písať robustné testy bez závislosti na konkrétnych modeloch.
"""

from typing import Dict, List, Any, Optional, Callable
from contextlib import contextmanager
from unittest.mock import Mock

from .types import ScopeType, UserRole
from . import registry


class MockScopeOwner:
    """Mock scope_owner objekt pre testovanie."""
    
    def __init__(self, role: UserRole = 'reader', id: str = 'test-owner-id'):
        self.role = role
        self.id = id
    
    def __str__(self):
        return f"MockScopeOwner(role={self.role}, id={self.id})"


def create_mock_scope_owner(role: UserRole = 'reader', id: str = 'test-owner-id') -> MockScopeOwner:
    """
    Vytvorí mock scope_owner objekt pre testovanie.
    
    Args:
        role: Role mock scope_owner
        id: ID mock scope_owner
        
    Returns:
        MockScopeOwner instance
    """
    return MockScopeOwner(role=role, id=id)


def create_mock_scope_provider(values_by_level: Dict[int, Dict[ScopeType, List[str]]]) -> Callable:
    """
    Vytvorí mock scope provider funkciu.
    
    Args:
        values_by_level: Dict mapujúci scope_level -> Dict[scope_type -> List[str]]
            Príklad: {1: {'selected': ['id1', 'id2'], 'accessible': ['id1', 'id2', 'id3']}}
        
    Returns:
        Callable funkcia kompatibilná s register_scope_provider
    """
    def mock_provider(scope_level: int, scope_owner: Any, scope_type: ScopeType, request=None) -> List[str]:
        level_values = values_by_level.get(scope_level, {})
        return level_values.get(scope_type, [])
    
    return mock_provider


async def create_async_mock_scope_provider(values_by_level: Dict[int, Dict[ScopeType, List[str]]]) -> Callable:
    """
    Vytvorí async mock scope provider funkciu pre async views.
    
    Args:
        values_by_level: Dict mapujúci scope_level -> Dict[scope_type -> List[str]]
            Príklad: {1: {'selected': ['id1', 'id2'], 'accessible': ['id1', 'id2', 'id3']}}
        
    Returns:
        Async callable funkcia kompatibilná s register_scope_provider pre async views
    """
    async def async_mock_provider(scope_level: int, scope_owner: Any, scope_type: ScopeType, request=None) -> List[str]:
        level_values = values_by_level.get(scope_level, {})
        return level_values.get(scope_type, [])
    
    return async_mock_provider


def create_mock_role_provider(role_by_owner: Dict[Any, UserRole]) -> Callable:
    """
    Vytvorí mock role provider funkciu.
    
    Args:
        role_by_owner: Dict mapujúci scope_owner -> role
            Príklad: {owner1: 'admin', owner2: 'reader'}
        
    Returns:
        Callable funkcia kompatibilná s register_role_provider
    """
    def mock_provider(scope_owner: Any) -> str:
        return role_by_owner.get(scope_owner, 'reader')
    
    return mock_provider


def create_test_rule(
    condition: str,
    action: str,
    scope_level: Optional[int] = None,
    scope_type: Optional[ScopeType] = None,
    when: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Vytvorí test scoping pravidlo.
    
    Args:
        condition: Condition name ('has_scope', 'no_scope', 'is_owner', 'is_assigned', 'is_selected')
        action: Action name ('include', 'exclude', 'filter_by', 'show_all')
        scope_level: Optional scope_level pre params
        scope_type: Optional scope_type pre params
        when: Optional 'when' podmienky
        
    Returns:
        ScopingRule dict
    """
    rule: Dict[str, Any] = {
        'condition': condition,
        'action': action,
    }
    
    params = {}
    if scope_level is not None:
        params['scope_level'] = scope_level
    if scope_type is not None:
        params['scope_type'] = scope_type
    
    if params:
        rule['params'] = params
    
    if when:
        rule['when'] = when
    
    return rule


@contextmanager
def with_mock_registry(
    scope_provider: Optional[Callable] = None,
    role_provider: Optional[Callable] = None
):
    """
    Context manager pre dočasné nastavenie mock registry.
    
    Použitie:
        with with_mock_registry(mock_scope_provider, mock_role_provider):
            # Test kód používajúci scoping engine
            pass
    
    Args:
        scope_provider: Optional mock scope provider
        role_provider: Optional mock role provider
    """
    # Ulož pôvodné registry
    original_scope_provider = None
    original_role_provider = None
    
    try:
        # Získaj pôvodné registry (ak existujú)
        if registry.is_registry_configured():
            # Poznámka: registry neposkytuje getter, takže musíme použiť iný prístup
            # Pre testovanie jednoducho prepíšeme
            pass
        
        # Nastav mock registry
        if scope_provider:
            registry.register_scope_provider(scope_provider)
        if role_provider:
            registry.register_role_provider(role_provider)
        
        yield
        
    finally:
        # Obnov pôvodné registry (ak boli)
        # Poznámka: V reálnych testoch by sme mali uložiť pôvodné hodnoty
        # Pre jednoduchosť resetujeme na None
        if scope_provider:
            registry.register_scope_provider(lambda *args: [])
        if role_provider:
            registry.register_role_provider(lambda *args: 'reader')


def assert_scoping_result(
    queryset,
    expected_count: Optional[int] = None,
    expected_min: Optional[int] = None,
    expected_max: Optional[int] = None,
    message: str = ""
):
    """
    Assertion helper pre overenie scoping výsledkov.
    
    Args:
        queryset: Django QuerySet po aplikovaní scoping
        expected_count: Presný očakávaný počet záznamov
        expected_min: Minimálny očakávaný počet záznamov
        expected_max: Maximálny očakávaný počet záznamov
        message: Voliteľná správa pre assertion error
        
    Raises:
        AssertionError: Ak výsledok nezodpovedá očakávaniu
    """
    actual_count = queryset.count()
    
    if expected_count is not None:
        assert actual_count == expected_count, (
            f"{message}Expected {expected_count} records, got {actual_count}"
        )
    
    if expected_min is not None:
        assert actual_count >= expected_min, (
            f"{message}Expected at least {expected_min} records, got {actual_count}"
        )
    
    if expected_max is not None:
        assert actual_count <= expected_max, (
            f"{message}Expected at most {expected_max} records, got {actual_count}"
        )


def create_test_config(
    ownership_hierarchy: List[str],
    scope_level_metadata: Optional[Dict[int, Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Vytvorí test ViewConfig.
    
    Args:
        ownership_hierarchy: List field names (napr. ['created_by', 'factory_id'])
        scope_level_metadata: Optional metadata pre scope levels
        
    Returns:
        ViewConfig dict
    """
    config: Dict[str, Any] = {
        'ownership_hierarchy': ownership_hierarchy,
    }
    
    if scope_level_metadata:
        config['scope_level_metadata'] = scope_level_metadata
    
    return config


