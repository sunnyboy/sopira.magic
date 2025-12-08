#..............................................................
#   apps/scoping/decorators.py
#   Dokumentačné decorators pre automatické scoping
#..............................................................

"""
Dokumentačné decorators pre automatické aplikovanie scoping na view funkcie.

Automaticky pridáva scoping kontext k view funkciám a zjednodušuje používanie engine.
Znižuje boilerplate kód a zabezpečuje konzistentné použitie.
"""

import functools
import logging
from typing import Dict, Any, Optional, Callable

from .engine import ScopingEngine
from .fallback import apply_with_fallback

logger = logging.getLogger(__name__)


def apply_scoping(table_name: str, config: Optional[Dict[str, Any]] = None, use_fallback: bool = True):
    """
    Decorator pre automatické aplikovanie scoping na view funkciu.
    
    Automaticky aplikuje scoping rules na queryset vrátený z view.
    Vyžaduje, aby view vracala QuerySet alebo ViewSet s get_queryset metódou.
    
    Použitie:
        @apply_scoping('locations')
        def my_view(request):
            queryset = Location.objects.all()
            # Scoping je automaticky aplikovaný
            return queryset
    
    Args:
        table_name: Názov tabuľky pre scoping rules
        config: Optional ViewConfig z VIEWS_MATRIX (ak None, musí byť v request)
        use_fallback: Ak True, používa fallback stratégie pri chybách
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Získaj request z args alebo kwargs
            request = None
            if args and hasattr(args[0], 'user'):
                request = args[0]
            elif 'request' in kwargs:
                request = kwargs['request']
            
            if not request or not hasattr(request, 'user'):
                logger.warning(
                    f"[ScopingDecorator] No request/user found in {func.__name__}, "
                    "scoping not applied"
                )
                return func(*args, **kwargs)
            
            # Získaj scope_owner z request
            scope_owner = request.user
            
            # Získaj config ak nie je poskytnutý
            view_config = config
            if view_config is None:
                # Skús získať z request alebo viewset
                if hasattr(request, 'view_config'):
                    view_config = request.view_config
                elif hasattr(args[0], 'get_view_config'):
                    view_config = args[0].get_view_config()
            
            if view_config is None:
                logger.warning(
                    f"[ScopingDecorator] No config found for {func.__name__}, "
                    "scoping not applied"
                )
                return func(*args, **kwargs)
            
            # Zavolaj pôvodnú funkciu
            result = func(*args, **kwargs)
            
            # Aplikuj scoping na výsledok
            if hasattr(result, 'filter'):  # QuerySet
                if use_fallback:
                    result = apply_with_fallback(
                        result,
                        scope_owner,
                        table_name,
                        view_config,
                        request
                    )
                else:
                    result = ScopingEngine.apply_rules(
                        result,
                        scope_owner,
                        table_name,
                        view_config,
                        request
                    )
            elif hasattr(result, 'get_queryset'):  # ViewSet
                # Pre ViewSet aplikujeme scoping na queryset
                queryset = result.get_queryset()
                if use_fallback:
                    queryset = apply_with_fallback(
                        queryset,
                        scope_owner,
                        table_name,
                        view_config,
                        request
                    )
                else:
                    queryset = ScopingEngine.apply_rules(
                        queryset,
                        scope_owner,
                        table_name,
                        view_config,
                        request
                    )
                # Nahraď queryset v ViewSet
                result.queryset = queryset
            
            return result
        
        return wrapper
    return decorator


def scoping_context(table_name: str):
    """
    Decorator pre pridanie scoping kontextu do response.
    
    Pridá scoping metadata do response pre debugging a monitoring.
    
    Použitie:
        @scoping_context('locations')
        def my_view(request):
            # Response bude obsahovať scoping kontext
            return Response(...)
    
    Args:
        table_name: Názov tabuľky
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Pridaj scoping kontext do response
            if hasattr(result, 'data'):
                if not hasattr(result.data, '__dict__'):
                    result.data = dict(result.data) if result.data else {}
                
                result.data['_scoping'] = {
                    'table': table_name,
                    'applied': True,
                }
            
            return result
        
        return wrapper
    return decorator


