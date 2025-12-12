from datetime import timedelta

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..serializers import FKOptionsCacheSerializer
from ..services import FKCacheService


def _format_cache_age(updated) -> str | None:
    if not updated:
        return None
    delta: timedelta = timezone.now() - updated
    total_seconds = int(delta.total_seconds())
    if total_seconds < 60:
        return f"{total_seconds}s"
    if total_seconds < 3600:
        return f"{total_seconds // 60}m"
    return f"{total_seconds // 3600}h"


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def fk_options_cache_view(request):
    field = request.GET.get("field")
    if not field:
        return Response({"detail": "Missing 'field' parameter"}, status=status.HTTP_400_BAD_REQUEST)

    data = FKCacheService.get_fk_options(field, user=request.user, request=request, force_refresh=False)
    payload = {
        "field": field,
        "options": data.get("options", []),
        "count": data.get("count", 0),
        "cache_age": _format_cache_age(data.get("updated")),
        "factories_count": data.get("factories_count", 0),
    }
    serializer = FKOptionsCacheSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def fk_options_cache_rebuild_view(request):
    field = request.data.get("field")
    if not field:
        return Response({"detail": "Missing 'field' parameter"}, status=status.HTTP_400_BAD_REQUEST)

    data = FKCacheService.rebuild_cache(field, user=request.user, request=request)
    payload = {
        "field": field,
        "options": data.get("options", []),
        "count": data.get("count", 0),
        "cache_age": _format_cache_age(data.get("updated")),
        "factories_count": data.get("factories_count", 0),
    }
    serializer = FKOptionsCacheSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def fk_options_cache_rebuild_scope_view(request):
    """
    Rebuild cache for all FK-capable fields.
    Intended for scope changes; keeps interface aligned with Thermal Eye.
    """
    from sopira_magic.apps.api.view_configs import VIEWS_MATRIX

    results = {}
    for view_name, cfg in VIEWS_MATRIX.items():
        if not cfg.get("fk_display_template"):
            continue
        data = FKCacheService.rebuild_cache(view_name, user=request.user, request=request)
        results[view_name] = {
            "count": data.get("count", 0),
            "cache_age": _format_cache_age(data.get("updated")),
            "factories_count": data.get("factories_count", 0),
        }
    return Response({"results": results}, status=status.HTTP_200_OK)

