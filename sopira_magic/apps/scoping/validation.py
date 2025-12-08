#..............................................................
#   apps/scoping/validation.py
#   Validácia scoping pravidiel pri štarte aplikácie
#..............................................................

"""
Validácia scoping pravidiel pri štarte aplikácie.

Zabezpečuje, že konfiguračné chyby v scoping pravidlách sú odhalené ihneď po spustení
aplikácie, nie počas produkčného behu. Zabraňuje runtime chybám a zaručuje konzistentné správanie.
"""

import logging
from typing import Dict, List, Any, Optional
from django.conf import settings

from .types import ScopingRule, ScopingCondition, ScopingAction, ScopingRuleWhen, UserRole
from .rules import SCOPING_RULES_MATRIX
from . import registry

logger = logging.getLogger(__name__)


class ScopingValidationError(Exception):
    """Exception pre scoping validation chyby."""
    pass


def validate_scoping_rules_matrix() -> List[str]:
    """
    Validuje celú SCOPING_RULES_MATRIX a vráti zoznam chýb.
    
    Returns:
        List[str] - zoznam chybových hlásení (prázdny ak nie sú chyby)
    """
    errors = []
    
    if not SCOPING_RULES_MATRIX:
        errors.append("SCOPING_RULES_MATRIX is empty")
        return errors
    
    # Validuj každú tabuľku a rolu
    for table_name, table_rules in SCOPING_RULES_MATRIX.items():
        if not isinstance(table_rules, dict):
            errors.append(f"Table '{table_name}': rules must be a dict mapping roles to rule lists")
            continue
        
        for role, rules in table_rules.items():
            if not isinstance(rules, list):
                errors.append(f"Table '{table_name}'/Role '{role}': rules must be a list")
                continue
            
            for i, rule in enumerate(rules):
                rule_errors = validate_rule(rule, table_name, role, rule_index=i)
                errors.extend(rule_errors)
    
    return errors


def validate_rule(rule: Dict[str, Any], table_name: str, role: str, rule_index: int = 0) -> List[str]:
    """
    Validuje jedno scoping pravidlo.
    
    Args:
        rule: ScopingRule dict
        table_name: Názov tabuľky
        role: Názov role
        rule_index: Index pravidla v zozname (pre lepšie error messages)
        
    Returns:
        List[str] - zoznam chybových hlásení (prázdny ak nie sú chyby)
    """
    errors = []
    rule_path = f"{table_name}/{role}[{rule_index}]"
    
    # Kontrola povinných polí
    if 'condition' not in rule:
        errors.append(f"{rule_path}: Missing required field 'condition'")
        return errors
    
    if 'action' not in rule:
        errors.append(f"{rule_path}: Missing required field 'action'")
        return errors
    
    condition = rule['condition']
    action = rule['action']
    
    # Validácia condition
    valid_conditions: List[ScopingCondition] = ['has_scope', 'no_scope', 'is_owner', 'is_assigned', 'is_selected']
    if condition not in valid_conditions:
        errors.append(
            f"{rule_path}: Invalid condition '{condition}'. "
            f"Must be one of: {', '.join(valid_conditions)}"
        )
    
    # Validácia action
    valid_actions: List[ScopingAction] = ['include', 'exclude', 'filter_by', 'show_all']
    if action not in valid_actions:
        errors.append(
            f"{rule_path}: Invalid action '{action}'. "
            f"Must be one of: {', '.join(valid_actions)}"
        )
    
    # Validácia params
    params = rule.get('params', {})
    if params:
        if not isinstance(params, dict):
            errors.append(f"{rule_path}: 'params' must be a dict")
        else:
            # Validácia scope_level
            if 'scope_level' in params:
                scope_level = params['scope_level']
                if not isinstance(scope_level, int) or scope_level < 0:
                    errors.append(
                        f"{rule_path}: 'params.scope_level' must be a non-negative integer, got {scope_level}"
                    )
            
            # Validácia scope_type
            if 'scope_type' in params:
                scope_type = params['scope_type']
                if scope_type not in ['selected', 'accessible']:
                    errors.append(
                        f"{rule_path}: 'params.scope_type' must be 'selected' or 'accessible', got '{scope_type}'"
                    )
    
    # Validácia 'when' podmienok
    when = rule.get('when')
    if when:
        when_errors = validate_when_conditions(when, rule_path)
        errors.extend(when_errors)
    
    return errors


def validate_when_conditions(when: Dict[str, Any], rule_path: str) -> List[str]:
    """
    Validuje 'when' podmienky v pravidle.
    
    Args:
        when: ScopingRuleWhen dict
        rule_path: Cesta k pravidlu (pre error messages)
        
    Returns:
        List[str] - zoznam chybových hlásení
    """
    errors = []
    
    # Validácia role
    if 'role' in when:
        roles = when['role']
        if not isinstance(roles, list):
            errors.append(f"{rule_path}.when: 'role' must be a list")
        else:
            valid_roles: List[UserRole] = ['superuser', 'admin', 'staff', 'editor', 'reader', 'adhoc']
            for role in roles:
                if role not in valid_roles:
                    errors.append(
                        f"{rule_path}.when: Invalid role '{role}' in 'role' list. "
                        f"Must be one of: {', '.join(valid_roles)}"
                    )
    
    # Validácia table
    if 'table' in when:
        tables = when['table']
        if not isinstance(tables, list):
            errors.append(f"{rule_path}.when: 'table' must be a list")
        else:
            for table in tables:
                if not isinstance(table, str):
                    errors.append(f"{rule_path}.when: All items in 'table' list must be strings")
    
    # Validácia field
    if 'field' in when:
        field = when['field']
        if not isinstance(field, str):
            errors.append(f"{rule_path}.when: 'field' must be a string")
    
    return errors


def validate_registry() -> List[str]:
    """
    Kontroluje, či sú registry callbacks registrované.
    
    Returns:
        List[str] - zoznam varovaní (nie chýb - registry môže byť registrovaný neskôr)
    """
    warnings = []
    
    if not registry.is_registry_configured():
        warnings.append(
            "Scoping registry callbacks are not configured. "
            "Call register_scope_provider() and register_role_provider() before using scoping engine."
        )
    
    return warnings


def validate_scope_level_in_config(
    rule: ScopingRule,
    config: Dict[str, Any],
    rule_path: str
) -> List[str]:
    """
    Validuje, že scope_level v pravidle je platný pre danú konfiguráciu.
    
    Args:
        rule: ScopingRule
        config: ViewConfig z VIEWS_MATRIX
        rule_path: Cesta k pravidlu (pre error messages)
        
    Returns:
        List[str] - zoznam chybových hlásení
    """
    errors = []
    
    params = rule.get('params', {})
    scope_level = params.get('scope_level')
    
    if scope_level is not None:
        ownership_hierarchy = config.get('ownership_hierarchy', [])
        if scope_level >= len(ownership_hierarchy):
            errors.append(
                f"{rule_path}: scope_level {scope_level} is out of range. "
                f"ownership_hierarchy has {len(ownership_hierarchy)} levels (0-{len(ownership_hierarchy)-1})"
            )
    
    return errors


def validate_all(view_configs: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, List[str]]:
    """
    Kompletná validácia všetkých scoping pravidiel a konfigurácií.
    
    Args:
        view_configs: Optional dict tabuľka -> ViewConfig (pre validáciu scope_level)
        
    Returns:
        Dict s kľúčmi 'errors' a 'warnings'
    """
    result = {
        'errors': [],
        'warnings': []
    }
    
    # Validácia pravidiel
    rule_errors = validate_scoping_rules_matrix()
    result['errors'].extend(rule_errors)
    
    # Validácia registry
    registry_warnings = validate_registry()
    result['warnings'].extend(registry_warnings)
    
    # Validácia scope_level voči konfiguráciám (ak sú poskytnuté)
    if view_configs:
        for table_name, config in view_configs.items():
            table_rules = SCOPING_RULES_MATRIX.get(table_name, {})
            for role, rules in table_rules.items():
                for i, rule in enumerate(rules):
                    rule_path = f"{table_name}/{role}[{i}]"
                    scope_level_errors = validate_scope_level_in_config(rule, config, rule_path)
                    result['errors'].extend(scope_level_errors)
    
    return result


def validate_and_raise(view_configs: Optional[Dict[str, Dict[str, Any]]] = None, raise_on_warnings: bool = False):
    """
    Validuje všetko a vyhodí výnimku pri chybách.
    
    Args:
        view_configs: Optional dict tabuľka -> ViewConfig
        raise_on_warnings: Ak True, vyhodí výnimku aj pri warnings
        
    Raises:
        ScopingValidationError: Ak sú chyby alebo (ak raise_on_warnings=True) warnings
    """
    result = validate_all(view_configs)
    
    if result['errors']:
        error_msg = "Scoping validation errors:\n" + "\n".join(f"  - {e}" for e in result['errors'])
        logger.error(error_msg)
        raise ScopingValidationError(error_msg)
    
    if raise_on_warnings and result['warnings']:
        warning_msg = "Scoping validation warnings:\n" + "\n".join(f"  - {w}" for w in result['warnings'])
        logger.warning(warning_msg)
        raise ScopingValidationError(warning_msg)
    
    if result['warnings']:
        for warning in result['warnings']:
            logger.warning(f"Scoping validation warning: {warning}")


