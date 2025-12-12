"""
Search Service - Elasticsearch integration + DB fallback.

Config-driven fulltext nad všetkými poľami + FK labelmi (fk_display_template).
Používa VIEWS_MATRIX ako SSOT a pri nefunkčnom ES padá na DB search.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Model, Q

try:
    from elasticsearch import Elasticsearch, helpers  # type: ignore
    from elasticsearch import exceptions as es_exceptions  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Elasticsearch = None  # type: ignore
    helpers = None  # type: ignore
    es_exceptions = None  # type: ignore

from sopira_magic.apps.api.serializers import MySerializer, get_fk_display_label
from sopira_magic.apps.api.view_configs import VIEWS_MATRIX
from sopira_magic.apps.scoping import registry as scoping_registry

logger = logging.getLogger(__name__)

TRUTHY = {"1", "true", "yes", "on", "y", "t"}


def _map_field_to_es_type(field) -> Dict[str, Any]:
    """
    Convert Django field type to a simple Elasticsearch mapping.
    """
    from django.db import models

    if isinstance(field, (models.IntegerField, models.AutoField)):
        return {"type": "long"}
    if isinstance(field, (models.FloatField, models.DecimalField)):
        return {"type": "double"}
    if isinstance(field, models.BooleanField):
        return {"type": "boolean"}
    if isinstance(field, (models.DateTimeField,)):
        return {"type": "date"}
    # Default: text + keyword for sorting/aggregations
    return {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}


class SearchService:
    """
    Core service pre vyhľadávanie (ES + fallback DB).
    """

    def __init__(self) -> None:
        self.enabled = settings.SEARCH_ELASTIC_ENABLED and bool(settings.ELASTICSEARCH_URL) and Elasticsearch
        self._client: Optional[Elasticsearch] = None
        self.request_timeout = getattr(settings, "SEARCH_REQUEST_TIMEOUT", 5)
        self.max_page_size = getattr(settings, "SEARCH_MAX_PAGE_SIZE", 200)
        self.ca_certs = getattr(settings, "ELASTICSEARCH_CA_CERT", None)
        self.verify_certs = getattr(settings, "ELASTICSEARCH_VERIFY_CERTS", False)
        self.disabled_after_error = False

    # ------------------------------------------------------------------ #
    # ES CLIENT HELPERS
    # ------------------------------------------------------------------ #
    def _client_or_none(self) -> Optional[Elasticsearch]:
        if not self.enabled or self.disabled_after_error:
            return None
        if self._client is None:
            self._client = Elasticsearch(
                settings.ELASTICSEARCH_URL,
                request_timeout=self.request_timeout,
                ca_certs=self.ca_certs,
                verify_certs=self.verify_certs,
            )
        return self._client

    # ------------------------------------------------------------------ #
    # CONFIG HELPERS
    # ------------------------------------------------------------------ #
    def get_enabled_views(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: cfg for name, cfg in VIEWS_MATRIX.items()
            if cfg.get("dynamic_search", True)
        }

    def index_name(self, view_name: str) -> str:
        prefix = getattr(settings, "SEARCH_INDEX_PREFIX", "idx")
        return f"{prefix}_{view_name}"

    def _get_fk_label_fields(self, view_name: str) -> Dict[str, str]:
        """Return {fk_field_name: template} for FK display labels."""
        config = VIEWS_MATRIX.get(view_name, {})
        fk_fields = config.get("fk_fields", {}) or {}
        labels: Dict[str, str] = {}
        for fk_field_name, fk_view in fk_fields.items():
            fk_view_config = VIEWS_MATRIX.get(fk_view, {})
            template = fk_view_config.get("fk_display_template") or config.get("fk_display_template")
            if template:
                labels[fk_field_name] = template
        return labels

    # ------------------------------------------------------------------ #
    # INDEX DEFINITION
    # ------------------------------------------------------------------ #
    def build_mapping(self, view_name: str) -> Dict[str, Any]:
        config = VIEWS_MATRIX.get(view_name)
        if not config:
            raise ValueError(f"View '{view_name}' nie je vo VIEWS_MATRIX")

        model: Model = config["model"]
        properties: Dict[str, Any] = {
            "id": {"type": "keyword"},
            "view": {"type": "keyword"},
            "__fulltext": {"type": "text"},
            "data": {"type": "object", "enabled": True},
            "scope": {"type": "object", "enabled": True},
        }

        # Model fields
        for field in model._meta.get_fields():
            # Skip reverse and m2m fields (index only direct scalars/FK)
            if field.many_to_many or field.one_to_many:
                continue
            if field.is_relation and not field.many_to_one and not field.one_to_one:
                continue
            properties[field.name] = _map_field_to_es_type(field)

        # FK display labels
        for fk_field, _template in self._get_fk_label_fields(view_name).items():
            properties[f"{fk_field}_label"] = {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}

        # Scope fields
        for field_name in config.get("ownership_hierarchy", []):
            properties[field_name] = {"type": "keyword"}

        return {"mappings": {"properties": properties}}

    # ------------------------------------------------------------------ #
    # INDEXING
    # ------------------------------------------------------------------ #
    def _serializer_for(self, view_name: str):
        return MySerializer.create_serializer(view_name)

    def _serialize_instance(self, view_name: str, instance: Model) -> Dict[str, Any]:
        cfg = VIEWS_MATRIX[view_name]
        serializer_cls = self._serializer_for(view_name)
        payload = serializer_cls(instance).data  # type: ignore

        # Build fulltext value
        def _flatten_value(val: Any) -> str:
            if val is None:
                return ""
            if isinstance(val, (list, tuple, set)):
                return " ".join(_flatten_value(v) for v in val)
            if isinstance(val, dict):
                return " ".join(_flatten_value(v) for v in val.values())
            return str(val)

        fulltext_parts: List[str] = []
        for value in payload.values():
            fulltext_parts.append(_flatten_value(value))

        # FK label fields
        fk_labels = {}
        for fk_field, template in self._get_fk_label_fields(view_name).items():
            fk_obj = getattr(instance, fk_field, None)
            label = get_fk_display_label(fk_obj, template)
            if label:
                fk_labels[f"{fk_field}_label"] = label
                fulltext_parts.append(label)

        # Scope fields
        scope_data: Dict[str, Any] = {}
        for field_name in cfg.get("ownership_hierarchy", []):
            scope_value = getattr(instance, field_name, None)
            if scope_value is None:
                continue
            if hasattr(scope_value, "pk"):
                scope_value = getattr(scope_value, "pk")
            scope_data[field_name] = scope_value

        doc = {
            "id": str(payload.get("id") or getattr(instance, "pk")),
            "view": view_name,
            "data": payload,
            "__fulltext": " ".join(fulltext_parts).strip(),
            **fk_labels,
            **scope_data,
            "scope": scope_data,
        }
        return doc

    def index_instance(self, view_name: str, instance: Model) -> None:
        client = self._client_or_none()
        if not client:
            return
        try:
            doc = self._serialize_instance(view_name, instance)
            client.index(index=self.index_name(view_name), id=doc["id"], document=doc, refresh="wait_for")
            logger.debug("[Search] Indexed %s:%s", view_name, doc["id"])
        except Exception as exc:  # pragma: no cover - runtime path
            logger.warning("[Search] Index failed for %s:%s – %s", view_name, instance.pk, exc)
            # If ES je nedostupné (napr. connection refused), vypni indexovanie pre zvyšok procesu, aby sme nezdržiavali generovanie
            if "Connection refused" in str(exc) or "Failed to establish a new connection" in str(exc):
                self.disabled_after_error = True
                logger.warning("[Search] Disabling search indexing after connection failure")

    def delete_instance(self, view_name: str, instance: Model) -> None:
        client = self._client_or_none()
        if not client:
            return
        try:
            client.delete(index=self.index_name(view_name), id=str(getattr(instance, "pk")), ignore=[404])
            logger.debug("[Search] Deleted %s:%s", view_name, instance.pk)
        except Exception as exc:  # pragma: no cover - runtime path
            logger.warning("[Search] Delete failed for %s:%s – %s", view_name, instance.pk, exc)
            if "Connection refused" in str(exc) or "Failed to establish a new connection" in str(exc):
                self.disabled_after_error = True
                logger.warning("[Search] Disabling search indexing after connection failure")

    def recreate_index(self, view_name: str) -> Tuple[int, int]:
        """
        Drop & rebuild index for one view. Returns (indexed, failed).
        """
        client = self._client_or_none()
        if not client:
            return (0, 0)

        cfg = VIEWS_MATRIX.get(view_name)
        if not cfg:
            raise ValueError(f"View '{view_name}' nie je vo VIEWS_MATRIX")
        model: Model = cfg["model"]

        index_name = self.index_name(view_name)
        try:
            if client.indices.exists(index=index_name):
                client.indices.delete(index=index_name)
        except Exception as exc:  # pragma: no cover - runtime path
            logger.warning("[Search] Failed deleting index %s: %s", index_name, exc)

        mapping = self.build_mapping(view_name)
        client.indices.create(index=index_name, **mapping)

        def _gen():
            for obj in model.objects.all():
                doc = self._serialize_instance(view_name, obj)
                yield {
                    "_index": index_name,
                    "_id": doc["id"],
                    "_source": doc,
                }

        success, failed = helpers.bulk(client, _gen(), raise_on_error=False)  # type: ignore
        logger.info("[Search] Reindexed %s (%s ok, %s failed)", view_name, success, len(failed) if failed else 0)
        return (success, len(failed) if failed else 0)

    # ------------------------------------------------------------------ #
    # SCOPING FILTERS
    # ------------------------------------------------------------------ #
    def get_scope_filters(self, user, config: Dict[str, Any], request=None) -> Dict[str, List[str]]:
        """
        Build scope filters from ownership_hierarchy + scoping registry.
        """
        scope_filters: Dict[str, List[str]] = {}
        for level, field_name in enumerate(config.get("ownership_hierarchy", [])):
            selected = scoping_registry.get_scope_values(level, user, "selected", request) or []
            if not selected:
                # Fallback to accessible scope if nothing explicitly selected
                selected = scoping_registry.get_scope_values(level, user, "accessible", request) or []
            if selected:
                scope_filters[field_name] = [str(v) for v in selected]
        return scope_filters

    # ------------------------------------------------------------------ #
    # SEARCH (ES)
    # ------------------------------------------------------------------ #
    def search(
        self,
        view_name: str,
        query: str,
        mode: str,
        approximate: bool,
        page: int,
        page_size: int,
        ordering: Optional[str],
        scope_filters: Dict[str, List[str]],
    ) -> Optional[Dict[str, Any]]:
        client = self._client_or_none()
        if not client:
            return None

        body: Dict[str, Any] = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": [],
                }
            },
            "from": max(page - 1, 0) * page_size,
            "size": page_size,
            "track_total_hits": True,
        }

        # Query
        if query:
            if mode == "advanced":
                body["query"]["bool"]["must"].append(
                    {
                        "query_string": {
                            "query": query,
                            "default_operator": "AND",
                            "fields": ["__fulltext", "*"],
                        }
                    }
                )
            else:
                mm: Dict[str, Any] = {
                    "multi_match": {
                        "query": query,
                        "fields": ["__fulltext", "*"],
                    }
                }
                if approximate and getattr(settings, "SEARCH_ALLOW_APPROX", True):
                    mm["multi_match"]["fuzziness"] = "AUTO"
                body["query"]["bool"]["must"].append(mm)
        else:
            body["query"]["bool"]["must"].append({"match_all": {}})

        # Scope filters
        for field_name, values in scope_filters.items():
            if values:
                body["query"]["bool"]["filter"].append({"terms": {field_name: values}})

        # Highlight
        body["highlight"] = {
            "pre_tags": ["<mark>"],
            "post_tags": ["</mark>"],
            "fields": {
                "__fulltext": {"fragment_size": 150, "number_of_fragments": 3},
                "data.*": {"fragment_size": 150, "number_of_fragments": 3},
                "*_label": {"fragment_size": 150, "number_of_fragments": 3},
            },
            "require_field_match": False,
        }

        # Ordering (fallback to score)
        if ordering:
            field = ordering.lstrip("-")
            direction = "desc" if ordering.startswith("-") else "asc"
            body["sort"] = [{field: {"order": direction}}, {"_score": "desc"}]

        try:
            resp = client.search(index=self.index_name(view_name), body=body)
            hits = resp.get("hits", {})
            documents = []
            for hit in hits.get("hits", []):
                source = hit.get("_source", {})
                documents.append({
                    "id": source.get("id") or hit.get("_id"),
                    "score": hit.get("_score"),
                    "data": source.get("data", {}),
                    "highlight": hit.get("highlight"),
                    "source": "elastic",
                })
            total = hits.get("total", {}).get("value", len(documents))
            return {
                "results": documents,
                "count": total,
                "mode": mode,
                "approximate": approximate and getattr(settings, "SEARCH_ALLOW_APPROX", True),
                "source": "elastic",
                "took_ms": resp.get("took"),
            }
        except Exception as exc:  # pragma: no cover - runtime path
            logger.warning("[Search] ES search failed for %s: %s", view_name, exc)
            return None

    # ------------------------------------------------------------------ #
    # SEARCH (DB FALLBACK)
    # ------------------------------------------------------------------ #
    def db_search(
        self,
        view_name: str,
        query: str,
        mode: str,
        page: int,
        page_size: int,
        ordering: Optional[str],
        user,
        request=None,
        scope_filters: Optional[Dict[str, List[str]]] = None,
    ) -> Optional[Dict[str, Any]]:
        cfg = VIEWS_MATRIX.get(view_name)
        if not cfg:
            return None
        model: Model = cfg["model"]

        qs = model.objects.all()

        # Base filters
        base_filters = cfg.get("base_filters", {}) or {}
        if base_filters:
            qs = qs.filter(**base_filters)

        # Apply scope filters
        scope_filters = scope_filters or self.get_scope_filters(user, cfg, request)
        for field_name, values in scope_filters.items():
            if values:
                qs = qs.filter(**{f"{field_name}__in": values})

        # Global search across all fields
        if query:
            search_fields = cfg.get("search_fields") or []
            # Include fk label helpers if present in serializer
            search_q = Q()
            terms = [t for t in query.split() if t]
            if mode == "advanced" and terms:
                # Basic AND semantics for fallback
                for term in terms:
                    sub_q = Q()
                    for field_name in search_fields:
                        sub_q |= Q(**{f"{field_name}__icontains": term})
                    search_q &= sub_q
            else:
                for field_name in search_fields:
                    search_q |= Q(**{f"{field_name}__icontains": query})
            qs = qs.filter(search_q)

        # Ordering
        if ordering:
            qs = qs.order_by(ordering)

        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page)

        serializer_cls = self._serializer_for(view_name)
        results = [serializer_cls(obj).data for obj in page_obj.object_list]  # type: ignore

        return {
            "results": [{"id": r.get("id"), "data": r, "source": "db"} for r in results],
            "count": paginator.count,
            "mode": mode,
            "approximate": False,
            "source": "db_fallback",
        }


