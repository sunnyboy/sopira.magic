#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/caching/services.py
#   FK Options Cache Service - Config-driven FK dropdown caching
#   Optimizes FK dropdown loading by caching options
#..............................................................

"""
FK Options Cache Service.

Config-driven service for caching FK dropdown options.
Reduces database queries for frequently used FK dropdowns.

Features:
- Automatic cache key generation from VIEWS_MATRIX
- User-scoped caching (respects scoping)
- TTL-based invalidation via CacheConfig model
- Signal-based cache invalidation on model changes

Usage:
    from sopira_magic.apps.caching.services import FKCacheService
    
    # Get cached FK options for a view
    options = FKCacheService.get_fk_options('factories', user)
    
    # Rebuild cache for a view
    FKCacheService.rebuild_cache('factories', user)
    
    # Invalidate cache on model change (called by signals)
    FKCacheService.invalidate_cache('factories', user)
"""

import logging
import hashlib
from typing import Dict, List, Any, Optional

from django.core.cache import cache
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

User = get_user_model()


class FKCacheService:
    """
    Config-driven FK Options Cache Service.
    
    Caches FK dropdown options for faster loading.
    Uses VIEWS_MATRIX configuration for automatic setup.
    """
    
    # Default TTL in seconds (1 hour)
    DEFAULT_TTL = 3600
    
    # Cache key prefix
    CACHE_PREFIX = "fk_options"
    
    @classmethod
    def get_cache_key(cls, view_name: str, user_id: Optional[str] = None) -> str:
        """
        Generate cache key for FK options.
        
        Args:
            view_name: View name from VIEWS_MATRIX (e.g., "factories")
            user_id: Optional user ID for user-scoped caching
            
        Returns:
            Cache key string
        """
        if user_id:
            return f"{cls.CACHE_PREFIX}:{view_name}:user:{user_id}"
        return f"{cls.CACHE_PREFIX}:{view_name}:global"
    
    @classmethod
    def get_fk_options(
        cls,
        view_name: str,
        user: Optional[Any] = None,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get cached FK options for a view.
        
        Args:
            view_name: View name from VIEWS_MATRIX
            user: Optional user for scoped options
            force_refresh: If True, bypass cache and fetch fresh data
            
        Returns:
            List of FK option dictionaries [{id, label, ...}, ...]
        """
        user_id = str(user.id) if user else None
        cache_key = cls.get_cache_key(view_name, user_id)
        
        # Check cache first (unless force_refresh)
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached
        
        # Fetch fresh data
        options = cls._fetch_fk_options(view_name, user)
        
        # Get TTL from CacheConfig or use default
        ttl = cls._get_ttl(view_name)
        
        # Store in cache
        cache.set(cache_key, options, ttl)
        logger.debug(f"Cached {len(options)} options for {cache_key} (TTL: {ttl}s)")
        
        return options
    
    @classmethod
    def _fetch_fk_options(cls, view_name: str, user: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Fetch FK options from database.
        
        Uses VIEWS_MATRIX configuration for model, filters, and display template.
        
        Args:
            view_name: View name from VIEWS_MATRIX
            user: Optional user for scoped queries
            
        Returns:
            List of FK option dictionaries
        """
        from sopira_magic.apps.api.view_configs import VIEWS_MATRIX
        
        config = VIEWS_MATRIX.get(view_name)
        if not config:
            logger.warning(f"View '{view_name}' not found in VIEWS_MATRIX")
            return []
        
        model = config['model']
        base_filters = config.get('base_filters', {})
        fk_display_template = config.get('fk_display_template', '{name}')
        
        # Build queryset with base filters
        qs = model.objects.all()
        if base_filters:
            qs = qs.filter(**base_filters)
        
        # Apply scoping via ScopingEngine (ak user poskytnutý)
        if user:
            try:
                from sopira_magic.apps.scoping.engine import ScopingEngine
                qs = ScopingEngine.apply(qs, user, view_name, config)
            except Exception as exc:
                logger.warning("ScopingEngine failed for %s: %s", view_name, exc)
        
        # Build options list
        options = []
        for obj in qs[:1000]:  # Limit to prevent huge lists
            option = {
                'id': str(obj.id),
                'value': str(obj.id),
            }
            
            # Generate label from template
            try:
                context = {
                    'code': getattr(obj, 'code', ''),
                    'human_id': getattr(obj, 'human_id', ''),
                    'name': getattr(obj, 'name', ''),
                    'id': str(obj.id),
                }
                option['label'] = fk_display_template.format(**context)
            except (KeyError, AttributeError):
                option['label'] = str(obj)
            
            options.append(option)
        
        return options
    
    @classmethod
    def _get_ttl(cls, view_name: str) -> int:
        """
        Get TTL for view from CacheConfig or return default.
        
        Args:
            view_name: View name from VIEWS_MATRIX
            
        Returns:
            TTL in seconds
        """
        try:
            from .models import CacheConfig
            config = CacheConfig.objects.filter(
                key=f"fk_options:{view_name}",
                enabled=True
            ).first()
            if config:
                return config.ttl
        except Exception as e:
            logger.debug(f"Could not fetch CacheConfig for {view_name}: {e}")
        
        return cls.DEFAULT_TTL
    
    @classmethod
    def rebuild_cache(cls, view_name: str, user: Optional[Any] = None) -> int:
        """
        Rebuild cache for a specific view.
        
        Args:
            view_name: View name from VIEWS_MATRIX
            user: Optional user for scoped cache
            
        Returns:
            Number of options cached
        """
        options = cls.get_fk_options(view_name, user, force_refresh=True)
        return len(options)
    
    @classmethod
    def invalidate_cache(cls, view_name: str, user: Optional[Any] = None) -> None:
        """
        Invalidate cache for a specific view.
        
        Args:
            view_name: View name from VIEWS_MATRIX
            user: Optional user for scoped cache
        """
        user_id = str(user.id) if user else None
        cache_key = cls.get_cache_key(view_name, user_id)
        cache.delete(cache_key)
        logger.debug(f"Invalidated cache: {cache_key}")
        
        # Also invalidate global cache if user-specific was invalidated
        if user_id:
            global_key = cls.get_cache_key(view_name, None)
            cache.delete(global_key)
            logger.debug(f"Invalidated global cache: {global_key}")
    
    @classmethod
    def invalidate_all(cls, view_name: str) -> None:
        """
        Invalidate all caches for a view (global + all user-scoped).
        
        Args:
            view_name: View name from VIEWS_MATRIX
        """
        # This is a simplified implementation
        # Full implementation would use cache.delete_pattern() if available
        global_key = cls.get_cache_key(view_name, None)
        cache.delete(global_key)
        logger.info(f"Invalidated all caches for {view_name}")
    
    @classmethod
    def get_all_fk_options(cls, user: Optional[Any] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all FK options for all views with fk_display_template.
        
        Useful for frontend to preload all FK dropdowns at once.
        
        Args:
            user: Optional user for scoped options
            
        Returns:
            Dictionary {view_name: [options, ...], ...}
        """
        from sopira_magic.apps.api.view_configs import VIEWS_MATRIX
        
        result = {}
        for view_name, config in VIEWS_MATRIX.items():
            # Only include views with FK display template (they can be FK sources)
            if config.get('fk_display_template'):
                result[view_name] = cls.get_fk_options(view_name, user)
        
        return result

