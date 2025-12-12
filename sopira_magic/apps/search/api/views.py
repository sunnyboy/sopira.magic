from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sopira_magic.apps.api.view_configs import VIEWS_MATRIX
from sopira_magic.apps.search.services import SearchService, TRUTHY


class SearchView(APIView):
    """
    Vyhľadávanie nad všetkými poľami + FK labelmi (ES + DB fallback).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        view_name = request.query_params.get("view")
        if not view_name:
            return Response({"detail": "Parameter 'view' je povinný."}, status=400)

        cfg = VIEWS_MATRIX.get(view_name)
        if not cfg:
            return Response({"detail": f"View '{view_name}' nie je definovaný vo VIEWS_MATRIX."}, status=404)

        query = (request.query_params.get("q") or "").strip()
        mode = (request.query_params.get("mode") or getattr(settings, "SEARCH_DEFAULT_MODE", "simple")).lower()
        approximate = (request.query_params.get("approximate") or request.query_params.get("approx") or "").lower() in TRUTHY

        try:
            page = max(int(request.query_params.get("page", "1")), 1)
        except ValueError:
            page = 1

        try:
            page_size = min(
                max(int(request.query_params.get("page_size", "25")), 1),
                getattr(settings, "SEARCH_MAX_PAGE_SIZE", 200),
            )
        except ValueError:
            page_size = 25

        ordering = request.query_params.get("ordering")

        service = SearchService()
        scope_filters = service.get_scope_filters(request.user, cfg, request)

        result = service.search(
            view_name=view_name,
            query=query,
            mode=mode,
            approximate=approximate,
            page=page,
            page_size=page_size,
            ordering=ordering,
            scope_filters=scope_filters,
        )

        # Fallback to DB if ES disabled/unavailable
        if result is None:
            result = service.db_search(
                view_name=view_name,
                query=query,
                mode=mode,
                page=page,
                page_size=page_size,
                ordering=ordering,
                user=request.user,
                request=request,
                scope_filters=scope_filters,
            )

        if result is None:
            return Response({"detail": "Search service je nedostupný."}, status=503)

        return Response(result)

