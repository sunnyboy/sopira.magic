#..............................................................
#   apps/scoping/middleware.py
#   ViewSet mixin for automatic scoping (CLEAN REWRITE)
#..............................................................

"""
ViewSet mixin for automatic scoping.

Provides ScopingViewSetMixin that automatically applies scoping rules
to ViewSet querysets using the new clean scoping engine.
"""

import logging
from typing import Any

from .engine import ScopingEngine

logger = logging.getLogger(__name__)


class ScopingViewSetMixin:
    """
    Mixin for ViewSet to automatically apply scoping rules.
    
    Usage:
        class MyViewSet(ScopingViewSetMixin, ModelViewSet):
            queryset = Company.objects.all()
            # Scoping is automatically applied in get_queryset
    
    The mixin expects:
        - self._view_name: table name (e.g., 'companies')
        - self._view_config: ViewConfig dict from VIEWS_MATRIX
        - self.request.user: scope owner (authenticated user)
    """
    
    def get_queryset(self):
        """
        Override get_queryset to automatically apply scoping.
        """
        logger.warning(f"[ScopingViewSetMixin] ========== get_queryset() CALLED ==========")
        queryset = super().get_queryset()
        logger.warning(f"[ScopingViewSetMixin] Base queryset count: {queryset.count()}")
        
        # Get table name
        table_name = getattr(self, '_view_name', None)
        if not table_name:
            # Fallback: try to get from queryset model
            if hasattr(queryset, 'model'):
                table_name = queryset.model.__name__.lower()
        
        if not table_name:
            logger.warning(
                f"[ScopingViewSetMixin] Could not determine table_name for {self.__class__.__name__}, "
                "scoping not applied"
            )
            return queryset
        
        # Get config
        config = getattr(self, '_view_config', None)
        if not config:
            # Try to get from VIEWS_MATRIX
            try:
                from sopira_magic.apps.api.view_configs import VIEWS_MATRIX
                config = VIEWS_MATRIX.get(table_name, {})
            except ImportError:
                logger.warning(
                    f"[ScopingViewSetMixin] Could not import VIEWS_MATRIX, "
                    "scoping not applied for {table_name}"
                )
                return queryset
        
        # Get scope owner (user)
        scope_owner = getattr(self.request, 'user', None)
        if not scope_owner or not scope_owner.is_authenticated:
            logger.debug(
                f"[ScopingViewSetMixin] No authenticated user in request, "
                f"returning empty queryset for {table_name}"
            )
            return queryset.none()
        
        # Apply scoping using new clean engine
        try:
            filtered_queryset = ScopingEngine.apply(
                queryset,
                scope_owner,
                table_name,
                config
            )
            
            logger.debug(
                f"[ScopingViewSetMixin] Scoping applied for {table_name}: "
                f"{queryset.count()} → {filtered_queryset.count()} records"
            )
            
            return filtered_queryset
        
        except Exception as e:
            logger.error(
                f"[ScopingViewSetMixin] Error applying scoping for {table_name}: {e}",
                exc_info=True
            )
            # On error, return empty queryset for safety
            return queryset.none()

