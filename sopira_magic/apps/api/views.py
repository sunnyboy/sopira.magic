#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/api/views.py
#   API Views - API Gateway viewsets
#   REST API views for API key and version management
#..............................................................

"""
   API Views - API Gateway Viewsets.

   REST API viewsets for API Gateway functionality.
   Provides endpoints for API key management and API versioning.

   Viewsets:

   1. APIKeyViewSet (ModelViewSet)
      - Full CRUD operations for API keys
      - Custom action: regenerate (POST) - regenerates API key
      - TODO: Add serializer and permissions

   2. APIVersionViewSet (ReadOnlyModelViewSet)
      - Read-only access to API versions
      - Filters: enabled=True
      - TODO: Add serializer

   Endpoints:
   - /api/keys/ - API key management
   - /api/keys/{id}/regenerate/ - Regenerate API key
   - /api/versions/ - API version listing
"""

from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import APIKey, APIVersion, RateLimitConfig
from sopira_magic.apps.pdfviewer.services import PdfViewerService
from sopira_magic.apps.accessrights.services import (
    can_view_menu,
    get_access_matrix_for_user,
)
from sopira_magic.apps.api.view_configs import VIEWS_MATRIX


ASSIGN_FOCUSED_VIEW_PERMISSIONS = [
    # In local development we relax auth for the demo pdfviewer endpoint.
    AllowAny if getattr(settings, "ENV", "local") == "local" else IsAuthenticated,
]


class APIKeyViewSet(viewsets.ModelViewSet):
    """API Key management viewset."""
    queryset = APIKey.objects.all()
    # TODO: Add serializer and permissions
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate API key."""
        # TODO: Implement key regeneration
        return Response({'message': 'Key regenerated'})


class APIVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """API Version viewset."""
    queryset = APIVersion.objects.filter(enabled=True)
    # TODO: Add serializer


@csrf_exempt
@api_view(["POST"])
@permission_classes(ASSIGN_FOCUSED_VIEW_PERMISSIONS)
def assign_focused_view(request):
    """Assign or update a focused view for a generic source object.

    Expected JSON payload:
    - source_model_path: "app_label.ModelName" of the source entity
    - source_object_id: identifier of the source entity (string/int)
    - document_ref: PDF document reference (relative path or identifier)
    - page_number: page number (1-based)
    - x, y: normalized coordinates (0.0 - 1.0)
    - zoom: optional zoom value (float)
    - metadata: optional dict with extra info
    """

    payload = request.data or {}
    required_fields = [
        "source_model_path",
        "source_object_id",
        "document_ref",
        "page_number",
        "x",
        "y",
    ]
    missing = [f for f in required_fields if f not in payload]
    if missing:
        return Response(
            {"detail": f"Missing required fields: {', '.join(missing)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    focused_view = PdfViewerService.set_focused_view(
        source_model_path=payload["source_model_path"],
        source_object_id=str(payload["source_object_id"]),
        document_ref=payload["document_ref"],
        page_number=int(payload["page_number"]),
        x=float(payload["x"]),
        y=float(payload["y"]),
        zoom=float(payload.get("zoom")) if payload.get("zoom") is not None else None,
        metadata=payload.get("metadata") or {},
    )

    return Response(
        {
            "id": str(focused_view.id),
            "document_ref": focused_view.document_ref,
            "page_number": focused_view.page_number,
            "x": focused_view.x,
            "y": focused_view.y,
            "zoom": focused_view.zoom,
            "source_model_path": focused_view.source_model_path,
            "source_object_id": focused_view.source_object_id,
            "metadata": focused_view.metadata,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def accessrights_matrix_view(request):
    """
    Read-only endpoint pre FE: vráti menu + actions pre aktuálneho usera.
    """
    user = request.user

    # Zoznam menu položiek používaných vo FE
    menu_keys = [
        "dashboard",
        "measurements",
        "companies",
        "factories",
        "locations",
        "carriers",
        "drivers",
        "pots",
        "pits",
        "machines",
        "cameras",
        "users",
    ]

    # Actions pre všetky viewsety z VIEWS_MATRIX
    actions = get_access_matrix_for_user(user, VIEWS_MATRIX)

    # Menu viditeľnosť
    menu = {key: can_view_menu(key, user) for key in menu_keys}

    return Response(
        {
            "menu": menu,
            "actions": actions,
        },
        status=status.HTTP_200_OK,
    )

