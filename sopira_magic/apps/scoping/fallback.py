#..............................................................
#   apps/scoping/fallback.py
#   Fallback stratégie pre graceful degradation
#..............................................................

"""
Fallback stratégie pre graceful degradation pri chybách scoping engine.

Zabezpečuje, že ak nový systém zlyhá, aplikácia automaticky prepne na jednoduchší
alebo starší spôsob filtrovania. Kritické pre produkčnú stabilitu.
"""

import logging
from typing import Dict, Any, Optional
from django.db.models import QuerySet, Q
from django.conf import settings

from .engine import ScopingEngine
from . import registry

logger = logging.getLogger(__name__)

# Fallback úrovne
FALLBACK_NONE = 'none'  # Žiadne filtrovanie
FALLBACK_SIMPLE = 'simple'  # Jednoduché filtrovanie
FALLBACK_ENGINE = 'engine'  # Nový scoping engine (default)

# Konfigurácia z settings
FALLBACK_ENABLED = getattr(settings, 'SCOPING_FALLBACK_ENABLED', True)
FALLBACK_LEVEL = getattr(settings, 'SCOPING_FALLBACK_LEVEL', FALLBACK_ENGINE)


def simple_fallback_filter(
    queryset: QuerySet,
    scope_owner: Any,
    config: Dict[str, Any]
) -> QuerySet:
    """
    Jednoduchý fallback filter - základné scoping bez pravidiel.
    
    Používa len základné filtrovanie podľa ownership_hierarchy bez komplexných pravidiel.
    
    Args:
        queryset: Django QuerySet
        scope_owner: Abstraktný objekt reprezentujúci vlastníka scope
        config: ViewConfig z VIEWS_MATRIX
        
    Returns:
        Filtered QuerySet
    """
    ownership_hierarchy = config.get('ownership_hierarchy', [])
    
    if not ownership_hierarchy:
        logger.warning("[Fallback] No ownership_hierarchy in config, returning unfiltered queryset")
        return queryset
    
    # Použi prvý level ownership_hierarchy (owner field)
    owner_field = ownership_hierarchy[0]
    
    # Jednoduché filtrovanie: len owner field
    try:
        queryset = queryset.filter(**{owner_field: scope_owner})
        logger.debug(f"[Fallback] Applied simple filter: {owner_field}={scope_owner}")
    except Exception as e:
        logger.error(f"[Fallback] Error applying simple filter: {e}")
        return queryset
    
    return queryset


def no_filter_fallback(queryset: QuerySet) -> QuerySet:
    """
    Fallback bez filtrovania - vráti unfiltered queryset.
    
    Používa sa len pre superuser alebo v prípade kritických chýb.
    
    Args:
        queryset: Django QuerySet
        
    Returns:
        Unfiltered QuerySet
    """
    logger.warning("[Fallback] Using no-filter fallback - returning unfiltered queryset")
    return queryset


def apply_with_fallback(
    queryset: QuerySet,
    scope_owner: Any,
    table_name: str,
    config: Dict[str, Any],
    request=None,
    fallback_level: Optional[str] = None,
    use_metrics: bool = True
) -> QuerySet:
    """
    Aplikuje scoping s fallback stratégiou.
    
    Pokúsi sa použiť nový scoping engine, a ak zlyhá, prepne na fallback.
    
    Args:
        queryset: Django QuerySet
        scope_owner: Abstraktný objekt reprezentujúci vlastníka scope
        table_name: Názov tabuľky
        config: ViewConfig z VIEWS_MATRIX
        request: Optional Django request object
        fallback_level: Optional fallback level override (None = use settings)
        use_metrics: Ak True, zaznamená metriky
        
    Returns:
        Filtered QuerySet
    """
    if not FALLBACK_ENABLED:
        # Fallback disabled - používaj len nový engine (bez fallback, aby sa zabránilo rekurzii)
        return ScopingEngine._apply_rules_internal(
            queryset, scope_owner, table_name, config, request, 
            role=ScopingEngine._get_scope_owner_role(scope_owner)
        )
    
    fallback = fallback_level or FALLBACK_LEVEL
    
    # Get scope_owner role pre metriky
    role = ScopingEngine._get_scope_owner_role(scope_owner)
    
    # Použi metrics context manager ak je povolený
    metrics_context = None
    if use_metrics:
        try:
            from .metrics import ScopingMetricsContext
            metrics_context = ScopingMetricsContext(table_name, role)
        except ImportError:
            metrics_context = None
    
    if metrics_context:
        metrics_context.__enter__()
    
    try:
        # Pokús sa použiť nový scoping engine (voláme _apply_rules_internal priamo, nie apply_rules)
        result = ScopingEngine._apply_rules_internal(
            queryset, scope_owner, table_name, config, request, role
        )
        if metrics_context:
            metrics_context.success = True
        return result
    except Exception as e:
        if metrics_context:
            metrics_context.success = False
        logger.error(
            f"[Fallback] Scoping engine failed for {table_name}: {e}. "
            f"Falling back to {fallback}"
        )
        
        # Aplikuj fallback podľa úrovne
        try:
            if fallback == FALLBACK_SIMPLE:
                result = simple_fallback_filter(queryset, scope_owner, config)
            elif fallback == FALLBACK_NONE:
                result = no_filter_fallback(queryset)
            else:
                # FALLBACK_ENGINE alebo neznámy - vráť unfiltered
                logger.warning(f"[Fallback] Unknown fallback level {fallback}, using no-filter")
                result = no_filter_fallback(queryset)
            
            # Fallback bol úspešný
            if metrics_context:
                metrics_context.success = True
            return result
        except Exception as fallback_error:
            if metrics_context:
                metrics_context.success = False
            logger.error(f"[Fallback] Fallback also failed: {fallback_error}")
            raise
    finally:
        if metrics_context:
            metrics_context.__exit__(None, None, None)


def should_use_fallback() -> bool:
    """
    Kontroluje, či by sa mal použiť fallback.
    
    Returns:
        bool - True ak registry nie je nakonfigurované alebo sú iné problémy
    """
    if not FALLBACK_ENABLED:
        return False
    
    # Ak registry nie je nakonfigurované, použij fallback
    if not registry.is_registry_configured():
        logger.warning("[Fallback] Registry not configured, should use fallback")
        return True
    
    return False


