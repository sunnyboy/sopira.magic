#..............................................................
#   apps/scoping/engine.py
#   Scoping Engine - Rule Engine with request-level cache
#..............................................................

"""
Scoping Engine - Config-driven rule engine for applying scoping rules.

This engine evaluates scoping rules from SCOPING_RULES_MATRIX and applies them
to querysets using Django Q objects. Uses request-level cache for performance.

Features:
- Config-driven rules from SSOT matrix
- Request-level cache (automatic invalidation per request)
- Fallback to old system if rules not defined
- Support for complex conditions and actions
- Úplne abstraktný - bez závislostí na konkrétnych modeloch
"""

import logging
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet, Q

from .types import ScopingRule, ScopingMatrix, ScopeType, ScopingRuleWhen, UserRole
from .rules import (
    should_use_scoping_engine,
    get_scoping_rules,
)
from . import registry

logger = logging.getLogger(__name__)


class ScopingEngine:
    """
    Config-driven scoping engine with rule evaluation and request-level cache.
    
    Evaluates scoping rules from SCOPING_RULES_MATRIX and applies them to querysets.
    Uses request-level cache to avoid repeated DB queries within the same request.
    Úplne abstraktný - pracuje s scope_owner namiesto user, bez závislostí na konkrétnych modeloch.
    """
    
    @staticmethod
    def get_scope_level_metadata(config: Dict[str, Any]) -> Dict[int, Dict[str, str]]:
        """
        Generate metadata for each scope level for debugging.
        
        Uses scope_level_metadata from config if defined, otherwise generates from ownership_hierarchy.
        
        Args:
            config: ViewConfig from VIEWS_MATRIX
            
        Returns:
            Dict mapping scope_level to metadata with user-friendly names
            Example: {0: {"name": "User", "field": "created_by"}, 1: {"name": "Factory", "field": "factory_id"}}
        """
        ownership_hierarchy = config.get('ownership_hierarchy', [])
        scope_level_metadata = config.get('scope_level_metadata', {})
        
        # If metadata is already defined, use it
        if scope_level_metadata:
            return scope_level_metadata
        
        # Otherwise, generate from ownership_hierarchy
        metadata = {}
        for level, field_name in enumerate(ownership_hierarchy):
            # Generate user-friendly name from field name
            # Remove _id suffix and capitalize
            friendly_name = field_name.replace('_id', '').replace('_', ' ').title()
            metadata[level] = {
                "name": friendly_name,
                "field": field_name,
            }
        
        return metadata
    
    @staticmethod
    def _matches_when(when: ScopingRuleWhen, table_name: str, role: str) -> bool:
        """
        Kontroluje, či pravidlo zodpovedá 'when' podmienkam.
        
        Args:
            when: ScopingRuleWhen dict s podmienkami
            table_name: Názov tabuľky
            role: Role scope_owner
            
        Returns:
            bool - True ak pravidlo zodpovedá podmienkam
        """
        # Kontrola role
        if 'role' in when:
            allowed_roles = when['role']
            if allowed_roles and role not in allowed_roles:
                return False
        
        # Kontrola table
        if 'table' in when:
            allowed_tables = when['table']
            if allowed_tables and table_name not in allowed_tables:
                return False
        
        # field sa kontroluje v kontexte konkrétneho fieldu, nie tu
        # (toto by sa kontrolovalo pri aplikovaní na konkrétny field)
        
        return True
    
    @staticmethod
    def _get_scope_owner_role(scope_owner: Any) -> str:
        """
        Get scope_owner role as string.
        
        Args:
            scope_owner: Abstraktný objekt reprezentujúci vlastníka scope
            
        Returns:
            Role string ('superuser', 'admin', 'staff', 'editor', 'reader', 'adhoc')
        """
        return registry.get_scope_owner_role(scope_owner)
    
    @staticmethod
    def _evaluate_condition(
        condition: str, 
        scope_owner: Any, 
        request=None, 
        params: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Q:
        """
        Evaluate a scoping condition and return Django Q object.
        
        Uses abstract scope_level from ownership_hierarchy instead of hardcoded field names.
        
        Args:
            condition: Condition name ('has_scope', 'no_scope', 'is_owner', 'is_assigned', 'is_selected')
            scope_owner: Abstraktný objekt reprezentujúci vlastníka scope
            request: Optional Django request object for caching
            params: Optional parameters for the condition (may contain scope_level, scope_type)
            config: Optional ViewConfig from VIEWS_MATRIX (contains ownership_hierarchy)
            
        Returns:
            Django Q object representing the condition
        """
        params = params or {}
        config = config or {}
        
        # Get field name from scope_level (abstract level) or fallback to old way
        scope_level = params.get('scope_level')
        if scope_level is not None and config.get('ownership_hierarchy'):
            # Use abstract scope_level - map to field name from ownership_hierarchy
            ownership_hierarchy = config['ownership_hierarchy']
            if scope_level < len(ownership_hierarchy):
                field_name = ownership_hierarchy[scope_level]
            else:
                logger.warning(f"[ScopingEngine] scope_level {scope_level} out of range for ownership_hierarchy {ownership_hierarchy}")
                field_name = params.get('field', 'id')  # Fallback
        else:
            # Fallback to old way (for backward compatibility)
            field_name = params.get('field', 'id')
        
        if condition == 'has_scope':
            return Q(**{f'{field_name}__isnull': False})
        
        elif condition == 'no_scope':
            return Q(**{f'{field_name}__isnull': True})
        
        elif condition == 'is_owner':
            # Prvý field v ownership_hierarchy je vždy owner field
            ownership_hierarchy = config.get('ownership_hierarchy', [])
            owner_field = ownership_hierarchy[0] if ownership_hierarchy else 'created_by'
            return Q(**{owner_field: scope_owner})
        
        elif condition == 'is_assigned':
            # Get accessible values (cached per request)
            scope_type: ScopeType = params.get('scope_type', 'accessible')
            values = registry.get_scope_values(scope_level, scope_owner, scope_type, request)
            if not values:
                return Q(pk__in=[])  # Empty Q object (no matches)
            return Q(**{f'{field_name}__in': values})
        
        elif condition == 'is_selected':
            # Get selected values (cached per request)
            scope_type: ScopeType = params.get('scope_type', 'selected')
            values = registry.get_scope_values(scope_level, scope_owner, scope_type, request)
            if not values:
                return Q(pk__in=[])  # Empty Q object (no matches)
            return Q(**{f'{field_name}__in': values})
        
        else:
            logger.warning(f"[ScopingEngine] Unknown condition: {condition}")
            return Q()  # Empty Q object (no filtering)
    
    @staticmethod
    def _apply_action(action: str, existing_q: Q, condition_q: Q) -> Q:
        """
        Apply a scoping action to combine Q objects.
        
        Args:
            action: Action name ('include', 'exclude', 'filter_by', 'show_all')
            existing_q: Existing Q object (from previous rules)
            condition_q: Q object from current condition
            
        Returns:
            Combined Q object
        """
        if action == 'include':
            # OR: existing_filter | Q(condition)
            return existing_q | condition_q
        
        elif action == 'exclude':
            # NOT: ~Q(condition)
            return existing_q & ~condition_q
        
        elif action == 'filter_by':
            # AND: existing_filter & Q(condition)
            return existing_q & condition_q
        
        elif action == 'show_all':
            # No filtering: return existing_q (or empty Q if first rule)
            return existing_q if existing_q else Q()
        
        else:
            logger.warning(f"[ScopingEngine] Unknown action: {action}")
            return existing_q  # Keep existing filter
    
    @classmethod
    def apply_rules(
        cls,
        queryset: QuerySet,
        scope_owner: Any,
        table_name: str,
        config: Dict[str, Any],
        request=None,
        use_metrics: bool = True,
        use_fallback: bool = True,
    ) -> QuerySet:
        """
        Apply scoping rules to queryset.
        
        Evaluates rules from SCOPING_RULES_MATRIX and applies them to queryset.
        Falls back to old system if rules not defined or feature flag disabled.
        Uses fallback strategy if enabled and engine fails.
        
        Args:
            queryset: Django QuerySet to filter
            scope_owner: Abstraktný objekt reprezentujúci vlastníka scope
            table_name: Table name (e.g., 'cameras', 'machines')
            config: ViewConfig from VIEWS_MATRIX
            request: Optional Django request object for caching
            use_metrics: Ak True, zaznamená metriky
            use_fallback: Ak True, použije fallback stratégie pri chybách
            
        Returns:
            Filtered QuerySet
        """
        # Check if scoping engine should be used for this table
        if not should_use_scoping_engine(table_name):
            # Fallback: return queryset without filtering (old system removed)
            logger.debug(f"[ScopingEngine] Scoping engine disabled for {table_name}, returning unfiltered queryset")
            return queryset
        
        # Ak je fallback povolený, použij apply_with_fallback
        if use_fallback:
            from .fallback import apply_with_fallback
            return apply_with_fallback(
                queryset, scope_owner, table_name, config, request, 
                use_metrics=use_metrics
            )
        
        # Inak použij priamy engine (pre backward compatibility alebo explicitné vypnutie fallback)
        # Get scope_owner role
        role = cls._get_scope_owner_role(scope_owner)
        
        # Použi metrics context manager ak je povolený
        if use_metrics:
            try:
                from .metrics import ScopingMetricsContext
                metrics_context = ScopingMetricsContext(table_name, role)
            except ImportError:
                metrics_context = None
        else:
            metrics_context = None
        
        if metrics_context:
            metrics_context.__enter__()
        
        try:
            result = cls._apply_rules_internal(queryset, scope_owner, table_name, config, request, role)
            if metrics_context:
                metrics_context.success = True
            return result
        except Exception as e:
            if metrics_context:
                metrics_context.success = False
            raise
        finally:
            if metrics_context:
                metrics_context.__exit__(None, None, None)
    
    @classmethod
    def _apply_rules_internal(
        cls,
        queryset: QuerySet,
        scope_owner: Any,
        table_name: str,
        config: Dict[str, Any],
        request=None,
        role: Optional[str] = None,
    ) -> QuerySet:
        
        # Get scoping rules for this table and role
        rules = get_scoping_rules(table_name, role)
        
        if not rules:
            # No rules defined → return queryset without filtering
            logger.debug(f"[ScopingEngine] No rules defined for {table_name}/{role}, returning unfiltered queryset")
            return queryset
        
        # Evaluate rules and build Q object
        combined_q = Q()  # Start with empty Q
        
        for rule in rules:
            condition = rule.get('condition')
            action = rule.get('action')
            params = rule.get('params', {})
            when = rule.get('when')
            
            if not condition or not action:
                logger.warning(f"[ScopingEngine] Invalid rule: {rule}")
                continue
            
            # Check 'when' conditions - skip rule if conditions don't match
            if when and not cls._matches_when(when, table_name, role):
                logger.debug(f"[ScopingEngine] Rule skipped due to 'when' conditions: {rule}")
                continue
            
            # Evaluate condition (pass config for ownership_hierarchy mapping)
            condition_q = cls._evaluate_condition(condition, scope_owner, request, params, config)
            
            # Apply action
            combined_q = cls._apply_action(action, combined_q, condition_q)
        
        # Apply combined Q object to queryset
        if combined_q:
            queryset = queryset.filter(combined_q)
        # If combined_q is empty Q(), queryset remains unchanged (show_all behavior)
        
        # Generate metadata for debugging
        metadata = cls.get_scope_level_metadata(config)
        logger.debug(
            f"[ScopingEngine] Applied {len(rules)} rules for {table_name}/{role}, "
            f"Q: {combined_q}, scope_level_metadata: {metadata}"
        )
        
        return queryset

