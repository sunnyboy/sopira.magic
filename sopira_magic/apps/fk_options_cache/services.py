"""
FK Options Cache Service - config-driven, SSOT via VIEWS_MATRIX.

Responsibilities:
- Build FK dropdown options from VIEWS_MATRIX (fk_display_template, base_filters)
- Apply scoping via ScopingEngine when available
- Cache results in Django cache (TTL from CacheConfig or default)
- Persist last snapshot in FKOptionsCache for observability
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import QuerySet
from django.utils import timezone

from sopira_magic.apps.api.view_configs import VIEWS_MATRIX
from sopira_magic.apps.scoping.engine import ScopingEngine
from .models import CacheConfig, FKOptionsCache

logger = logging.getLogger(__name__)
User = get_user_model()


class FKCacheService:
    """Config-driven FK Options Cache Service."""

    DEFAULT_TTL = 3600  # seconds
    CACHE_PREFIX = "fk_options"

    @classmethod
    def get_cache_key(cls, view_name: str, user_id: Optional[str] = None) -> str:
        if user_id:
            return f"{cls.CACHE_PREFIX}:{view_name}:user:{user_id}"
        return f"{cls.CACHE_PREFIX}:{view_name}:global"

    @classmethod
    def get_fk_options(
        cls,
        view_name: str,
        user: Optional[Any] = None,
        request=None,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """Get FK options (from cache or freshly built)."""
        user_id = str(user.id) if user else None
        cache_key = cls.get_cache_key(view_name, user_id)

        if not force_refresh:
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug("FK cache hit for %s", cache_key)
                return cached

        result = cls._fetch_fk_options(view_name, user, request)
        ttl = cls._get_ttl(view_name)
        cache.set(cache_key, result, ttl)
        logger.debug("Cached FK options for %s (ttl=%ss)", cache_key, ttl)
        return result

    @classmethod
    def _fetch_fk_options(
        cls,
        view_name: str,
        user: Optional[Any] = None,
        request=None,
    ) -> Dict[str, Any]:
        config = VIEWS_MATRIX.get(view_name)
        if not config:
            logger.warning("View '%s' not found in VIEWS_MATRIX", view_name)
            return {"options": [], "count": 0, "cache_age": None, "factories_count": 0}

        model = config.get("model")
        if model is None:
            logger.warning("View '%s' missing model in VIEWS_MATRIX", view_name)
            return {"options": [], "count": 0, "cache_age": None, "factories_count": 0}

        base_filters = config.get("base_filters", {})
        fk_display_template = config.get("fk_display_template", "{name}")

        qs: QuerySet = model.objects.all()
        if base_filters:
            qs = qs.filter(**base_filters)

        # Apply scoping via ScopingEngine only if view is factory_scoped
        if config.get("factory_scoped"):
            try:
                qs = ScopingEngine.apply_rules(qs, user, view_name, config, request)
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("ScopingEngine failed for %s: %s", view_name, exc)

        options: List[Dict[str, Any]] = []
        factory_ids = set()

        for obj in qs[:1000]:  # Safety guard
            option = {
                "id": str(obj.id),
                "value": str(obj.id),
            }
            # Build label
            try:
                context = {
                    "code": getattr(obj, "code", ""),
                    "human_id": getattr(obj, "human_id", ""),
                    "name": getattr(obj, "name", ""),
                    "id": str(obj.id),
                    # User-specific fields for label templates
                    "username": getattr(obj, "username", ""),
                    "first_name": getattr(obj, "first_name", ""),
                    "last_name": getattr(obj, "last_name", ""),
                    "email": getattr(obj, "email", ""),
                }
                option["label"] = fk_display_template.format(**context)
            except Exception:
                option["label"] = str(obj)

            # Preserve common fields used on FE for templates
            for attr in ("code", "name", "human_id"):
                val = getattr(obj, attr, None)
                if val not in (None, ""):
                    option[attr] = val
            # Preserve user-ident fields for FE rendering/custom templates
            for attr in ("username", "first_name", "last_name", "email"):
                val = getattr(obj, attr, None)
                if val not in (None, ""):
                    option[attr] = val

            # Track factories_count if factory field exists
            for f_field in ("factory_id", "factory"):
                if hasattr(obj, f_field):
                    factory_value = getattr(obj, f_field)
                    factory_ids.add(str(factory_value)) if factory_value else None
                    break

            options.append(option)

        record_count = len(options)
        factories_count = len(factory_ids)
        now = timezone.now()

        # Persist snapshot for observability
        FKOptionsCache.objects.update_or_create(
            field_name=view_name,
            factory=None,
            defaults={
                "options": options,
                "record_count": record_count,
                "factories_count": factories_count,
            },
        )

        return {
            "options": options,
            "count": record_count,
            "cache_age": "0s",
            "factories_count": factories_count,
            "updated": now,
        }

    @classmethod
    def _get_ttl(cls, view_name: str) -> int:
        try:
            cfg = CacheConfig.objects.filter(
                key=f"{cls.CACHE_PREFIX}:{view_name}", enabled=True
            ).first()
            if cfg:
                return cfg.ttl
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("CacheConfig lookup failed for %s: %s", view_name, exc)
        return cls.DEFAULT_TTL

    @classmethod
    def rebuild_cache(cls, view_name: str, user: Optional[Any] = None, request=None) -> Dict[str, Any]:
        result = cls.get_fk_options(view_name, user=user, request=request, force_refresh=True)
        return result

    @classmethod
    def invalidate_cache(cls, view_name: str, user: Optional[Any] = None) -> None:
        user_id = str(user.id) if user else None
        cache_key = cls.get_cache_key(view_name, user_id)
        cache.delete(cache_key)
        logger.debug("Invalidated FK cache %s", cache_key)

    @classmethod
    def invalidate_all(cls, view_name: str) -> None:
        # Basic invalidation (global + user-scoped if present in cache backend)
        cache.delete(cls.get_cache_key(view_name, None))
        logger.info("Invalidated all FK caches for %s", view_name)

    @classmethod
    def get_all_fk_options(cls, user: Optional[Any] = None, request=None) -> Dict[str, Dict[str, Any]]:
        result = {}
        for view_name, config in VIEWS_MATRIX.items():
            if config.get("fk_display_template"):
                result[view_name] = cls.get_fk_options(view_name, user=user, request=request)
        return result

