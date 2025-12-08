#..............................................................
#   apps/scoping/middleware.py
#   Middleware pre automatické aplikovanie scoping
#..............................................................

"""
Middleware pre automatické aplikovanie scoping pravidiel.

Aplikuje scoping pravidlá automaticky na všetky relevantné requesty.
Centralizuje scoping logiku a znižuje šancu na omylné vynechanie filtrovania.
"""

import logging
from typing import Callable
from django.conf import settings
from django.http import HttpRequest, HttpResponse

from .engine import ScopingEngine
from .fallback import apply_with_fallback

logger = logging.getLogger(__name__)

# Konfigurácia z settings
MIDDLEWARE_ENABLED = getattr(settings, 'SCOPING_MIDDLEWARE_ENABLED', False)
MIDDLEWARE_TABLES = getattr(settings, 'SCOPING_MIDDLEWARE_TABLES', [])


class ScopingMiddleware:
    """
    Django middleware pre automatické aplikovanie scoping.
    
    Automaticky aplikuje scoping rules na API requesty pre konfigurované tabuľky.
    """
    
    def __init__(self, get_response: Callable):
        self.get_response = get_response
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Process request and apply scoping if needed.
        
        Args:
            request: Django HttpRequest
            
        Returns:
            HttpResponse
        """
        # Ak middleware nie je povolený, preskoč
        if not MIDDLEWARE_ENABLED:
            return self.get_response(request)
        
        # Spracuj request
        response = self.get_response(request)
        
        # Middleware aplikuje scoping na response, nie na request
        # Pre automatické scoping v ViewSets, použite ScopingEngine.apply_rules priamo
        # Tento middleware je skôr pre monitoring a logging
        
        return response
    
    def process_view(self, request: HttpRequest, view_func: Callable, view_args, view_kwargs):
        """
        Process view before it's called.
        
        Môže byť použitý pre automatické aplikovanie scoping na viewset querysets.
        """
        # Poznámka: Pre automatické scoping v ViewSets je lepšie použiť
        # ScopingEngine.apply_rules priamo v get_queryset metóde
        # Tento middleware je skôr pre monitoring
        
        return None


class ScopingViewSetMixin:
    """
    Mixin pre ViewSet pre automatické aplikovanie scoping.
    
    Použitie:
        class MyViewSet(ScopingViewSetMixin, ModelViewSet):
            queryset = Location.objects.all()
            # Scoping je automaticky aplikovaný v get_queryset
    """
    
    def get_queryset(self):
        """
        Override get_queryset pre automatické aplikovanie scoping.
        """
        queryset = super().get_queryset()
        
        # Získaj table_name z viewset
        table_name = getattr(self, '_view_name', None)
        if not table_name:
            # Skús získať z queryset model
            if hasattr(queryset, 'model'):
                model_name = queryset.model.__name__.lower()
                # Mapuj model name na table name
                table_name = model_name
        
        if not table_name:
            logger.warning(
                f"[ScopingMiddleware] Could not determine table_name for {self.__class__.__name__}, "
                "scoping not applied"
            )
            return queryset
        
        # Skontroluj, či má byť scoping aplikovaný pre túto tabuľku
        if MIDDLEWARE_TABLES and table_name not in MIDDLEWARE_TABLES:
            return queryset
        
        # Získaj config (musí byť poskytnutý cez VIEWS_MATRIX alebo viewset)
        config = getattr(self, '_view_config', None)
        if not config:
            # Skús získať z VIEWS_MATRIX
            try:
                from sopira_magic.apps.api.view_configs import VIEWS_MATRIX
                config = VIEWS_MATRIX.get(table_name)
            except ImportError:
                logger.warning(
                    f"[ScopingMiddleware] Could not import VIEWS_MATRIX, "
                    "scoping not applied"
                )
                return queryset
        
        if not config:
            logger.warning(
                f"[ScopingMiddleware] No config found for {table_name}, "
                "scoping not applied"
            )
            return queryset
        
        # Aplikuj scoping s fallback
        scope_owner = getattr(self.request, 'user', None)
        if not scope_owner:
            logger.warning(
                f"[ScopingMiddleware] No user in request, scoping not applied"
            )
            return queryset
        
        return apply_with_fallback(
            queryset,
            scope_owner,
            table_name,
            config,
            request=self.request
        )


