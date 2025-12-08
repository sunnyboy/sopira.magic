#..............................................................
#   apps/scoping/presets.py
#   Preddefinované konfigurácie pre bežné scoping patterny
#..............................................................

"""
Preddefinované konfigurácie pre bežné scoping patterny.

Poskytuje štandardné šablóny pre bežné scoping patterny (factory-scoped, user-scoped, global).
Urýchľuje konfiguráciu nových tabuliek a zabezpečuje konzistentnosť.
"""

from typing import Dict, List, Any, Optional
from .types import ScopingRule, UserRole


def get_factory_scoped_preset() -> Dict[str, List[ScopingRule]]:
    """
    Vráti factory-scoped preset pravidiel.
    
    Preset pre tabuľky scoped by factory (scope_level 1).
    
    Returns:
        Dict[role] -> List[ScopingRule]
    """
    return {
        'superuser': [
            {
                'condition': 'is_selected',
                'action': 'filter_by',
                'params': {'scope_level': 1, 'scope_type': 'selected'},
            },
            {
                'condition': 'no_scope',
                'action': 'include',
            },
        ],
        'admin': [
            {
                'condition': 'is_assigned',
                'action': 'filter_by',
                'params': {'scope_level': 1, 'scope_type': 'accessible'},
            },
        ],
        'staff': [
            {
                'condition': 'is_assigned',
                'action': 'filter_by',
                'params': {'scope_level': 1, 'scope_type': 'accessible'},
            },
        ],
        'editor': [
            {
                'condition': 'is_assigned',
                'action': 'filter_by',
                'params': {'scope_level': 1, 'scope_type': 'accessible'},
            },
        ],
        'reader': [
            {
                'condition': 'is_assigned',
                'action': 'filter_by',
                'params': {'scope_level': 1, 'scope_type': 'accessible'},
            },
        ],
        'adhoc': [
            {
                'condition': 'is_assigned',
                'action': 'filter_by',
                'params': {'scope_level': 1, 'scope_type': 'accessible'},
            },
        ],
    }


def get_user_scoped_preset() -> Dict[str, List[ScopingRule]]:
    """
    Vráti user-scoped preset pravidiel.
    
    Preset pre tabuľky scoped by user (scope_level 0).
    
    Returns:
        Dict[role] -> List[ScopingRule]
    """
    return {
        'superuser': [
            {
                'condition': 'show_all',
                'action': 'show_all',
            },
        ],
        'admin': [
            {
                'condition': 'is_owner',
                'action': 'filter_by',
            },
        ],
        'staff': [
            {
                'condition': 'is_owner',
                'action': 'filter_by',
            },
        ],
        'editor': [
            {
                'condition': 'is_owner',
                'action': 'filter_by',
            },
        ],
        'reader': [
            {
                'condition': 'is_owner',
                'action': 'filter_by',
            },
        ],
        'adhoc': [
            {
                'condition': 'is_owner',
                'action': 'filter_by',
            },
        ],
    }


def get_global_preset() -> Dict[str, List[ScopingRule]]:
    """
    Vráti global preset pravidiel (žiadne scoping).
    
    Preset pre tabuľky bez scoping (len superuser vidí všetko).
    
    Returns:
        Dict[role] -> List[ScopingRule]
    """
    return {
        'superuser': [
            {
                'condition': 'show_all',
                'action': 'show_all',
            },
        ],
        'admin': [
            {
                'condition': 'show_all',
                'action': 'show_all',
            },
        ],
        'staff': [
            {
                'condition': 'show_all',
                'action': 'show_all',
            },
        ],
        'editor': [
            {
                'condition': 'show_all',
                'action': 'show_all',
            },
        ],
        'reader': [
            {
                'condition': 'show_all',
                'action': 'show_all',
            },
        ],
        'adhoc': [
            {
                'condition': 'show_all',
                'action': 'show_all',
            },
        ],
    }


def get_hybrid_preset() -> Dict[str, List[ScopingRule]]:
    """
    Vráti hybrid preset pravidiel (kombinácia factory a user scoping).
    
    Preset pre tabuľky scoped by factory a user (scope_level 0 a 1).
    
    Returns:
        Dict[role] -> List[ScopingRule]
    """
    return {
        'superuser': [
            {
                'condition': 'is_selected',
                'action': 'filter_by',
                'params': {'scope_level': 1, 'scope_type': 'selected'},
            },
            {
                'condition': 'is_owner',
                'action': 'include',
            },
        ],
        'admin': [
            {
                'condition': 'is_assigned',
                'action': 'filter_by',
                'params': {'scope_level': 1, 'scope_type': 'accessible'},
            },
            {
                'condition': 'is_owner',
                'action': 'include',
            },
        ],
        'staff': [
            {
                'condition': 'is_assigned',
                'action': 'filter_by',
                'params': {'scope_level': 1, 'scope_type': 'accessible'},
            },
            {
                'condition': 'is_owner',
                'action': 'include',
            },
        ],
        'editor': [
            {
                'condition': 'is_assigned',
                'action': 'filter_by',
                'params': {'scope_level': 1, 'scope_type': 'accessible'},
            },
            {
                'condition': 'is_owner',
                'action': 'include',
            },
        ],
        'reader': [
            {
                'condition': 'is_assigned',
                'action': 'filter_by',
                'params': {'scope_level': 1, 'scope_type': 'accessible'},
            },
            {
                'condition': 'is_owner',
                'action': 'include',
            },
        ],
        'adhoc': [
            {
                'condition': 'is_assigned',
                'action': 'filter_by',
                'params': {'scope_level': 1, 'scope_type': 'accessible'},
            },
            {
                'condition': 'is_owner',
                'action': 'include',
            },
        ],
    }


def create_custom_preset(
    scope_levels: List[int],
    roles: List[UserRole],
    base_preset: Optional[str] = None
) -> Dict[str, List[ScopingRule]]:
    """
    Vytvorí custom preset podľa zadaných parametrov.
    
    Args:
        scope_levels: List scope_levels ktoré sa majú použiť
        roles: List rolí pre ktoré sa má vytvoriť preset
        base_preset: Optional základný preset ('factory', 'user', 'global', 'hybrid')
        
    Returns:
        Dict[role] -> List[ScopingRule]
    """
    # Začni so základným presetom ak je zadaný
    if base_preset == 'factory':
        preset = get_factory_scoped_preset()
    elif base_preset == 'user':
        preset = get_user_scoped_preset()
    elif base_preset == 'global':
        preset = get_global_preset()
    elif base_preset == 'hybrid':
        preset = get_hybrid_preset()
    else:
        preset = {}
    
    # Filtruj len požadované role
    if roles:
        preset = {role: preset.get(role, []) for role in roles}
    
    # Uprav scope_levels v pravidlách
    for role, rules in preset.items():
        for rule in rules:
            params = rule.get('params', {})
            if 'scope_level' in params:
                # Použi prvý scope_level ak je v zozname
                if scope_levels and params['scope_level'] not in scope_levels:
                    params['scope_level'] = scope_levels[0]
    
    return preset


