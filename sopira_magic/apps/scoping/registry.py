#..............................................................
#   apps/scoping/registry.py
#   Abstraktný callback registry pre získanie scoping dát
#..............................................................

"""
Abstraktný callback registry pre získanie scoping dát bez závislostí na konkrétnych modeloch.
Host app poskytne implementáciu cez register_scope_provider() a register_role_provider().

Thread-safe: Všetky operácie sú chránené threading.Lock pre bezpečný prístup
pri súbežných požiadavkách v produkčnom prostredí.
"""

import threading
from typing import List, Optional, Callable, Literal, Any

ScopeType = Literal['selected', 'accessible']

# Thread-safe lock pre registry operácie
_registry_lock = threading.Lock()

# Abstraktná callback funkcia (None ak nie je registrovaná)
# scope_owner je úplne abstraktný objekt - môže to byť User, Company, alebo čokoľvek
_scope_provider: Optional[Callable[[int, Any, ScopeType, Optional[object]], List[str]]] = None
_role_provider: Optional[Callable[[Any], str]] = None

def register_scope_provider(callback: Callable[[int, Any, ScopeType, Optional[object]], List[str]]):
    """
    Registruje abstraktnú callback funkciu pre získanie scope hodnôt.
    
    Thread-safe: Operácia je chránená lockom pre bezpečný prístup pri súbežných požiadavkách.
    
    Args:
        callback: Funkcia (scope_level, scope_owner, scope_type, request) -> List[str]
    """
    global _scope_provider
    with _registry_lock:
        _scope_provider = callback

def register_role_provider(callback: Callable[[Any], str]):
    """
    Registruje callback funkciu pre získanie role scope_owner.
    
    Thread-safe: Operácia je chránená lockom pre bezpečný prístup pri súbežných požiadavkách.
    
    Args:
        callback: Funkcia (scope_owner) -> str
    """
    global _role_provider
    with _registry_lock:
        _role_provider = callback

def get_scope_values(scope_level: int, scope_owner: Any, scope_type: ScopeType, request=None) -> List[str]:
    """
    Vráti zoznam hodnôt pre daný scope_level a scope_type.
    
    Thread-safe: Čítanie je chránené lockom pre bezpečný prístup pri súbežných požiadavkách.
    
    Args:
        scope_level: Abstraktná úroveň scope (0, 1, 2...) - mapuje sa na field z ownership_hierarchy
        scope_owner: Abstraktný objekt reprezentujúci vlastníka scope (môže to byť User, Company, alebo čokoľvek)
        scope_type: 'selected' alebo 'accessible'
        request: Optional Django request object pre caching
        
    Returns:
        List[str] - zoznam hodnôt (UUIDs/IDs) pre daný scope_level a scope_type
    """
    with _registry_lock:
        provider = _scope_provider
    
    if provider:
        return provider(scope_level, scope_owner, scope_type, request)
    # Fallback: prázdny zoznam ak nie je registrovaný
    return []

def get_scope_owner_role(scope_owner: Any) -> str:
    """
    Vráti role scope_owner.
    
    Thread-safe: Čítanie je chránené lockom pre bezpečný prístup pri súbežných požiadavkách.
    
    Args:
        scope_owner: Abstraktný objekt reprezentujúci vlastníka scope
        
    Returns:
        str - role (definovaná v config, nie hardcoded)
    """
    with _registry_lock:
        provider = _role_provider
    
    if provider:
        return provider(scope_owner)
    # Fallback: 'reader' ak nie je registrovaný
    return 'reader'

def is_registry_configured() -> bool:
    """
    Kontroluje, či sú registry callbacks nakonfigurované.
    
    Thread-safe: Čítanie je chránené lockom.
    
    Returns:
        bool - True ak sú oba callbacks registrované, False inak
    """
    with _registry_lock:
        return _scope_provider is not None and _role_provider is not None

