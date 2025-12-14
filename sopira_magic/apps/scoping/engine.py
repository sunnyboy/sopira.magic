#..............................................................
#   apps/scoping/engine.py
#   Core Scoping Engine (CLEAN REWRITE)
#..............................................................

"""
Scoping Engine - Core logic for applying scoping rules.

Clean, simple, ConfigDriven approach:
1. Check feature flags
2. Check superuser bypass
3. Get rules from config
4. Evaluate rules → Q object
5. Apply to queryset
"""

import logging
from typing import Any, Dict
from django.db.models import QuerySet, Q

from .config import (
    USE_SCOPING_ENGINE,
    USE_SCOPING_ENGINE_FOR_TABLES,
    SCOPING_RULES_MATRIX
)
from . import registry

logger = logging.getLogger(__name__)


class ScopingEngine:
    """
    Scoping Engine - applies scoping rules to querysets.
    
    Single entry point: apply(queryset, user, table_name, config)
    """
    
    @classmethod
    def apply(
        cls,
        queryset: QuerySet,
        user: object,
        table_name: str,
        config: Dict[str, Any]
    ) -> QuerySet:
        """
        Apply scoping rules to queryset.
        
        Args:
            queryset: Django QuerySet
            user: User object (scope owner)
            table_name: Table name (e.g., 'companies')
            config: ViewConfig from VIEWS_MATRIX
            
        Returns:
            Filtered QuerySet
        """
        # Step 1: Check feature flags
        if not USE_SCOPING_ENGINE:
            logger.debug(f"[Scoping] Engine disabled globally")
            return queryset
        
        if not USE_SCOPING_ENGINE_FOR_TABLES.get(table_name, False):
            logger.debug(f"[Scoping] Engine disabled for table '{table_name}'")
            return queryset
        
        # Step 2: Check superuser bypass
        if cls._is_superuser(user):
            logger.debug(f"[Scoping] Superuser bypass for '{table_name}'")
            return queryset
        
        # Step 3: Get role and rules
        role = registry.get_role(user)
        rules = SCOPING_RULES_MATRIX.get(table_name, {}).get(role)
        
        logger.debug(f"[Scoping] Table: {table_name}, Role: {role}, Rules: {rules}")
        
        # Step 4: No rules = deny by default (security)
        if rules is None:
            logger.warning(f"[Scoping] No rules for '{table_name}' + '{role}' → EMPTY")
            return queryset.none()
        
        # Step 5: Empty rules [] = allow all (superuser case)
        if not rules:
            logger.debug(f"[Scoping] Empty rules for '{table_name}' + '{role}' → ALL")
            return queryset
        
        # Step 6: Evaluate rules
        combined_q = Q()
        for rule in rules:
            rule_q = cls._evaluate_rule(rule, user, config)
            action = rule.get('action', 'filter_by')
            
            if action == 'filter_by':
                combined_q = combined_q & rule_q
            elif action == 'include':
                combined_q = combined_q | rule_q
            elif action == 'exclude':
                combined_q = combined_q & ~rule_q
        
        # Step 7: Check if Q is empty (no scope)
        if cls._is_empty_q(combined_q):
            logger.debug(f"[Scoping] Empty Q for '{table_name}' → EMPTY")
            return queryset.none()
        
        # Step 8: Apply Q
        logger.debug(f"[Scoping] Applying Q: {combined_q}")
        return queryset.filter(combined_q)
    
    @staticmethod
    def _is_superuser(user: object) -> bool:
        """Check if user is superuser."""
        return getattr(user, 'is_superuser', False) or \
               getattr(user, 'role', '').lower() == 'superadmin'
    
    @staticmethod
    def _evaluate_rule(rule: Dict[str, Any], user: object, config: Dict[str, Any]) -> Q:
        """
        Evaluate a single scoping rule.
        
        Rule structure:
        {
            'condition': 'is_assigned',
            'action': 'filter_by',
            'params': {'scope_level': 1, 'scope_type': 'accessible'}
        }
        """
        condition = rule['condition']
        params = rule.get('params', {})
        
        if condition == 'is_owner':
            # Direct ownership (e.g., user owns their own profile)
            ownership_hierarchy = config.get('ownership_hierarchy', [])
            owner_field = ownership_hierarchy[0] if ownership_hierarchy else 'id'
            return Q(**{owner_field: user.id})
        
        elif condition == 'is_assigned':
            # User is assigned to scope (via RelationInstance)
            scope_level = params.get('scope_level')
            scope_type = params.get('scope_type', 'accessible')
            
            # Get scope field from config
            field_name = ScopingEngine._resolve_field_name(scope_level, config)
            
            # Get scope values from registry
            values = registry.get_scope_values(scope_level, user, scope_type)
            
            if not values:
                return Q(pk__in=[])  # Empty scope
            
            return Q(**{f'{field_name}__in': values})
        
        elif condition == 'has_scope':
            # Object has scope assigned (not null)
            scope_level = params.get('scope_level')
            field_name = ScopingEngine._resolve_field_name(scope_level, config)
            return Q(**{f'{field_name}__isnull': False})
        
        elif condition == 'no_scope':
            # Object has no scope (null)
            scope_level = params.get('scope_level')
            field_name = ScopingEngine._resolve_field_name(scope_level, config)
            return Q(**{f'{field_name}__isnull': True})
        
        elif condition == 'show_all':
            # No filter
            return Q()
        
        else:
            logger.warning(f"[Scoping] Unknown condition: {condition}")
            return Q(pk__in=[])  # Deny by default
    
    @staticmethod
    def _resolve_field_name(scope_level: int, config: Dict[str, Any]) -> str:
        """
        Resolve database field name from conceptual scope level.
        
        Uses config's scope_level_mapping and ownership_hierarchy.
        """
        if scope_level is None:
            return 'id'
        
        # Get mapping from config
        mapping = config.get('scope_level_mapping', {})
        ownership_hierarchy = config.get('ownership_hierarchy', [])
        
        # Try mapping first
        if mapping and scope_level in mapping:
            index = mapping[scope_level]
            if index < len(ownership_hierarchy):
                return ownership_hierarchy[index]
        
        # Fallback to direct index
        if scope_level < len(ownership_hierarchy):
            return ownership_hierarchy[scope_level]
        
        # Final fallback
        return 'id'
    
    @staticmethod
    def _is_empty_q(q: Q) -> bool:
        """
        Check if Q object represents empty filter (e.g., Q(pk__in=[])).
        """
        if not q:  # Empty Q() = no filter
            return False
        
        # Check for Q(pk__in=[]) pattern
        if hasattr(q, 'children') and len(q.children) == 1:
            child = q.children[0]
            if isinstance(child, tuple) and len(child) == 2:
                field, value = child
                if field == 'pk__in' and isinstance(value, list) and len(value) == 0:
                    return True
        
        return False
