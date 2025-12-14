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

import logging
import time
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.renderers import BaseRenderer
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

from .models import APIKey, APIVersion, RateLimitConfig
from sopira_magic.apps.pdfviewer.services import PdfViewerService
from sopira_magic.apps.accessrights.services import (
    can_view_menu,
    get_access_matrix_for_user,
)
from sopira_magic.apps.api.view_configs import VIEWS_MATRIX
from sopira_magic.apps.m_user.models import UserPreference
# TEMP: TableState removed, zakomentované pre migráciu
# from sopira_magic.apps.mystate.models import TableState
TableState = None  # Placeholder
from sopira_magic.apps.generator.api import (
    generator_models_view_impl,
    generator_generate_view_impl,
    generator_clear_view_impl,
    generator_clear_all_view_impl,
    generator_clear_all_and_state_view_impl,
    generator_assign_tags_view_impl,
    generator_remove_tags_view_impl,
    generator_objects_view_impl,
    generator_progress_status_view_impl,
    generator_progress_cancel_view_impl,
)
from django.http import StreamingHttpResponse
import json
import time

logger = logging.getLogger(__name__)


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

class EventStreamRenderer(BaseRenderer):
    media_type = "text/event-stream"
    format = "event-stream"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def generator_progress_status_view(request, job_id: str):
    return generator_progress_status_view_impl(job_id)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generator_progress_cancel_view(request, job_id: str):
    # Agent debug log
    try:
        log_path = "/Users/sopira/sopira.magic/version_01/.cursor/debug.log"
        with open(log_path, "a") as f:
            f.write(
                '{{"sessionId":"debug-session","runId":"run1","hypothesisId":"H4","location":"generator_progress_cancel_view","message":"cancel request","data":{{"job_id":"{}","user":"{}"}},"timestamp":{}}}\\n'.format(
                    job_id, request.user.username, int(time.time() * 1000)
                )
            )
    except Exception:
        pass
    return generator_progress_cancel_view_impl(job_id)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@renderer_classes([EventStreamRenderer])
def generator_progress_stream_view(request, job_id: str):
    """
    SSE stream pre progress jobu.
    """
    from sopira_magic.apps.generator.progress_state import get_status

    def event_stream():
        last_payload = None
        while True:
            payload = get_status(job_id)
            if payload and payload != last_payload:
                yield f"data: {json.dumps(payload)}\n\n"
                last_payload = payload
                if payload.get("done") or payload.get("cancel_requested") or payload.get("error"):
                    break
            time.sleep(1)

    resp = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    resp["Cache-Control"] = "no-cache"
    return resp


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def accessrights_matrix_view(request):
    """
    Read-only endpoint pre FE: vráti menu + actions + dependencies pre aktuálneho usera.
    """
    from sopira_magic.apps.accessrights.services import check_menu_dependencies
    from sopira_magic.apps.accessrights.config import EMPTY_STATE_MESSAGES
    
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
    
    # Menu dependencies (has_companies, has_factories)
    menu_dependencies = check_menu_dependencies(user)

    return Response(
        {
            "menu": menu,
            "actions": actions,
            "menu_dependencies": menu_dependencies,
            "empty_state_messages": EMPTY_STATE_MESSAGES,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "POST", "PUT"])
@permission_classes([IsAuthenticated])
def user_preferences_view(request):
    """
    User preferences endpoint.
    GET: Returns user preferences for current user
    POST/PUT: Creates or updates user preferences
    """
    user = request.user
    
    if request.method == "GET":
        try:
            preference = UserPreference.objects.get(user=user)
            # Merge settings and preferences into a single response
            response_data = {
                **preference.settings,
                **preference.preferences,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except UserPreference.DoesNotExist:
            # Return empty preferences if none exist
            return Response(
                {
                    "general_settings": {},
                },
                status=status.HTTP_200_OK,
            )
    
    elif request.method in ["POST", "PUT"]:
        data = request.data or {}
        
        # Get or create UserPreference
        preference, created = UserPreference.objects.get_or_create(user=user)
        
        # Update settings and preferences
        if "general_settings" in data:
            preference.preferences["general_settings"] = data["general_settings"]
        
        # Merge any other fields into preferences
        for key, value in data.items():
            if key not in ["general_settings"]:
                preference.preferences[key] = value
        
        preference.save()
        
        # Return merged response
        response_data = {
            **preference.settings,
            **preference.preferences,
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def user_filters_view(request):
    """
    User filters endpoint.
    GET: Returns saved filters for storageKey
    POST: Saves a new filter
    DELETE: Deletes a filter
    """
    user = request.user
    
    if request.method == "GET":
        storage_key = request.GET.get("storageKey")
        if not storage_key:
            return Response(
                {"detail": "storageKey parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            filters = TableState.objects.using('state').filter(
                user_id=user.id,
                table_name=storage_key,
                component="filter",
                is_active=True,
            ).order_by("-updated")
            
            filters_list = [
                {
                    "name": f.state_data.get("name", f"Filter {f.id}"),
                    "timestamp": int(f.updated.timestamp() * 1000) if f.updated else 0,
                    "state": f.state_data.get("state", {}),
                    "storageKey": storage_key,
                    "storage_key": storage_key,  # Support both formats
                }
                for f in filters
            ]
            
            return Response({"filters": filters_list}, status=status.HTTP_200_OK)
        except Exception as e:
            # Graceful fallback: return empty filters to avoid FE crash when state DB missing
            logging.getLogger(__name__).warning(f"Filters fallback for storageKey={storage_key}: {e}")
            return Response({"filters": []}, status=status.HTTP_200_OK)
    
    elif request.method == "POST":
        data = request.data or {}
        name = data.get("name")
        state = data.get("state", {})
        storage_key = data.get("storageKey")
        
        if not name or not storage_key:
            return Response(
                {"detail": "name and storageKey are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Create or update filter
        # First try to find existing filter with this name
        try:
            existing_filters = TableState.objects.using('state').filter(
                user_id=user.id,
                table_name=storage_key,
                component="filter",
            )
            filter_state = None
            for f in existing_filters:
                if f.state_data.get("name") == name:
                    filter_state = f
                    break
            
            if filter_state:
                # Update existing
                filter_state.state_data = {
                    "name": name,
                    "state": state,
                }
                filter_state.is_active = True
                filter_state.save(using='state')
                created = False
            else:
                # Create new
                filter_state = TableState.objects.using('state').create(
                    user_id=user.id,
                    table_name=storage_key,
                    component="filter",
                    state_data={
                        "name": name,
                        "state": state,
                    },
                    is_active=True,
                )
                created = True
        except Exception as e:
            logging.getLogger(__name__).warning(f"Filters POST fallback for storageKey={storage_key}: {e}")
            # Graceful fallback: no-op but return success to keep FE functional
            return Response(
                {
                    "id": None,
                    "name": name,
                    "storageKey": storage_key,
                    "fallback": True,
                },
                status=status.HTTP_200_OK,
            )
        
        return Response(
            {
                "id": filter_state.id,
                "name": name,
                "storageKey": storage_key,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
    
    elif request.method == "DELETE":
        data = request.data or {}
        name = data.get("name")
        storage_key = data.get("storageKey")
        
        if not name or not storage_key:
            return Response(
                {"detail": "name and storageKey are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Delete filter
        # Find filters and delete those matching the name
        try:
            filters = TableState.objects.using('state').filter(
                user_id=user.id,
                table_name=storage_key,
                component="filter",
            )
            deleted_count = 0
            for f in filters:
                if f.state_data.get("name") == name:
                    f.delete(using='state')
                    deleted_count += 1
            
            if deleted_count > 0:
                return Response(
                    {"detail": "Filter deleted successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"detail": "Filter not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        except Exception as e:
            logging.getLogger(__name__).warning(f"Filters DELETE fallback for storageKey={storage_key}: {e}")
            return Response({"deleted": 0, "fallback": True}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def models_metadata_view(request):
    """
    Models metadata endpoint.
    Returns metadata from VIEWS_MATRIX (ownership_field, etc.)
    """
    metadata = {}
    
    for view_name, config in VIEWS_MATRIX.items():
        model_metadata = {}
        
        # Extract ownership_field from ownership_hierarchy
        ownership_hierarchy = config.get("ownership_hierarchy", [])
        if ownership_hierarchy:
            # First field in hierarchy is typically the ownership field
            model_metadata["ownership_field"] = ownership_hierarchy[0]
        
        # Add other metadata if needed
        if config.get("factory_scoped"):
            model_metadata["factory_scoped"] = True
        if config.get("soft_delete"):
            model_metadata["soft_delete"] = True
        
        if model_metadata:
            metadata[view_name] = model_metadata
    
    return Response(metadata, status=status.HTTP_200_OK)


@api_view(["GET", "POST", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def table_state_presets_view(request):
    """
    Table state presets endpoint.
    GET: Returns presets for preset_name and factory
    POST: Creates a new preset
    PUT: Updates an existing preset
    DELETE: Deletes a preset
    """
    user = request.user
    
    if request.method == "GET":
        preset_name = request.GET.get("preset_name", "__current__")
        factory = request.GET.get("factory")
        show_current = request.GET.get("show_current", "false").lower() == "true"
        
        try:
            presets = TableState.objects.using('state').filter(
                user_id=user.id,
                component="preset",
                is_active=True,
            ).order_by("-updated", "-id")
            
            filtered_presets = []
            for p in presets:
                preset_data = p.state_data or {}
                p_preset_name = preset_data.get("preset_name")
                p_factory = preset_data.get("factory")
                
                if p_preset_name != preset_name:
                    continue
                if factory and p_factory != factory:
                    continue
                if not show_current and p_preset_name == "__current__":
                    continue
                
                filtered_presets.append(p)
            
            presets_list = [
                {
                    "id": p.id,
                    "preset_name": p.state_data.get("preset_name", preset_name),
                    "factory": p.state_data.get("factory"),
                    "state": p.state_data.get("state", {}),
                    "updated": p.updated.isoformat() if p.updated else None,
                    "created": p.created.isoformat() if p.created else None,
                }
                for p in filtered_presets
            ]
            
            return Response(presets_list, status=status.HTTP_200_OK)
        except Exception as e:
            logging.getLogger(__name__).warning(f"TableState GET fallback preset_name={preset_name}: {e}")
            return Response([], status=status.HTTP_200_OK)
    
    elif request.method == "POST":
        data = request.data or {}
        preset_name = data.get("preset_name", "__current__")
        factory = data.get("factory")
        state = data.get("state", {})
        
        # Create or update preset
        preset_data = {
            "preset_name": preset_name,
            "state": state,
            "is_active": True,
        }
        if factory:
            preset_data["factory"] = factory
        
        try:
            presets = TableState.objects.using('state').filter(
                user_id=user.id,
                component="preset",
            )
            
            preset = None
            for p in presets:
                p_data = p.state_data or {}
                if p_data.get("preset_name") == preset_name:
                    if factory:
                        if p_data.get("factory") == factory:
                            preset = p
                            break
                    else:
                        # No factory specified, match any
                        preset = p
                        break
            
            if preset:
                preset.state_data = preset_data
                preset.is_active = True
                preset.save(using='state')
                created = False
            else:
                preset = TableState.objects.using('state').create(
                    user_id=user.id,
                    table_name="preset",  # Use preset as table_name
                    component="preset",
                    state_data=preset_data,
                    is_active=True,
                )
                created = True
            
            return Response(
                {
                    "id": preset.id,
                    "preset_name": preset_name,
                    "factory": factory,
                    "state": state,
                },
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )
        except Exception as e:
            logging.getLogger(__name__).warning(f"TableState POST fallback preset_name={preset_name}: {e}")
            return Response(
                {
                    "id": None,
                    "preset_name": preset_name,
                    "factory": factory,
                    "state": state,
                    "fallback": True,
                },
                status=status.HTTP_200_OK,
            )
    
    elif request.method == "PUT":
        data = request.data or {}
        preset_id = data.get("id")
        preset_name = data.get("preset_name", "__current__")
        factory = data.get("factory")
        state = data.get("state", {})
        
        if not preset_id:
            return Response(
                {"detail": "id is required for PUT"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            preset = TableState.objects.using('state').get(
                id=preset_id,
                user_id=user.id,
                component="preset",
            )
            
            # Update preset data
            preset_data = preset.state_data.copy()
            preset_data["preset_name"] = preset_name
            preset_data["state"] = state
            if factory:
                preset_data["factory"] = factory
            
            preset.state_data = preset_data
            preset.save(using='state')
            
            return Response(
                {
                    "id": preset.id,
                    "preset_name": preset_name,
                    "factory": factory,
                    "state": state,
                },
                status=status.HTTP_200_OK,
            )
        except TableState.DoesNotExist:
            return Response(
                {"detail": "Preset not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logging.getLogger(__name__).warning(f"TableState PUT fallback preset_id={preset_id}: {e}")
            return Response(
                {
                    "id": preset_id,
                    "preset_name": preset_name,
                    "factory": factory,
                    "state": state,
                    "fallback": True,
                },
                status=status.HTTP_200_OK,
            )
    
    elif request.method == "DELETE":
        preset_id = request.GET.get("id") or (request.data or {}).get("id")
        
        if not preset_id:
            return Response(
                {"detail": "id is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            preset = TableState.objects.using('state').get(
                id=preset_id,
                user_id=user.id,
                component="preset",
            )
            preset.delete(using='state')
            
            return Response(
                {"detail": "Preset deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except TableState.DoesNotExist:
            return Response(
                {"detail": "Preset not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logging.getLogger(__name__).warning(f"TableState DELETE fallback preset_id={preset_id}: {e}")
            return Response({"detail": "Preset delete fallback"}, status=status.HTTP_200_OK)


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def table_state_presets_detail_view(request, id):
    """
    Detail endpoint pre TableState (STATE DB) – používané useSnapshot pre PATCH.
    """
    user = request.user
    try:
        preset = TableState.objects.using('state').get(id=id, user_id=user.id, component="preset")
    except TableState.DoesNotExist:
        return Response({"detail": "Preset not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logging.getLogger(__name__).warning(f"TableState detail fallback id={id}: {e}")
        return Response({"detail": "Preset fallback", "fallback": True}, status=status.HTTP_200_OK)

    if request.method == "GET":
        try:
            return Response(
                {
                    "id": preset.id,
                    "preset_name": preset.state_data.get("preset_name"),
                    "factory": preset.state_data.get("factory"),
                    "state": preset.state_data.get("state", {}),
                    "updated": preset.updated.isoformat() if preset.updated else None,
                    "created": preset.created.isoformat() if preset.created else None,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logging.getLogger(__name__).warning(f"TableState detail GET fallback id={id}: {e}")
            return Response({"detail": "Preset fallback", "fallback": True}, status=status.HTTP_200_OK)

    if request.method == "DELETE":
        try:
            preset.delete(using='state')
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logging.getLogger(__name__).warning(f"TableState detail DELETE fallback id={id}: {e}")
            return Response(status=status.HTTP_200_OK)

    # PATCH
    data = request.data or {}
    state = data.get("state", {})
    try:
        preset.state_data["state"] = state
        preset.save(using='state')
        return Response(
            {
                "id": preset.id,
                "preset_name": preset.state_data.get("preset_name"),
                "factory": preset.state_data.get("factory"),
                "state": preset.state_data.get("state", {}),
                "updated": preset.updated.isoformat() if preset.updated else None,
                "created": preset.created.isoformat() if preset.created else None,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logging.getLogger(__name__).warning(f"TableState detail PATCH fallback id={id}: {e}")
        return Response(
            {
                "id": id,
                "preset_name": None,
                "factory": None,
                "state": state,
                "fallback": True,
            },
            status=status.HTTP_200_OK,
        )

# -----------------------------------------------------------------------------
# Generator Endpoints (config-driven, SSOT)
# -----------------------------------------------------------------------------


def _get_generator_dependency_graph():
    """Return configs, parents map, children map."""
    configs = get_all_generator_configs()
    parents_map = {key: cfg.get("depends_on", []) for key, cfg in configs.items()}
    children_map = {key: [] for key in configs.keys()}
    for child, cfg in configs.items():
        for parent in cfg.get("depends_on", []):
            if parent in children_map:
                children_map[parent].append(child)
    return configs, parents_map, children_map


def _topological_order(configs, parents_map):
    """Simple topological order based on depends_on for deletion (parents last)."""
    order = []
    visited = set()

    def dfs(node):
        if node in visited:
            return
        visited.add(node)
        for dep in parents_map.get(node, []):
            dfs(dep)
        order.append(node)

    for key in configs.keys():
        dfs(key)
    return order


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def generator_models_view(request):
    """List generator models with counts and dependencies."""
    user = request.user
    if not user.is_superuser:
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    return generator_models_view_impl(user)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generator_generate_view(request):
    """Generate N records for a model."""
    user = request.user
    if not user.is_superuser:
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    model_key = request.data.get("model_key")
    count = request.data.get("count")
    try:
        count = int(count) if count not in [None, ""] else None
    except Exception:
        return Response({"detail": "Invalid count"}, status=status.HTTP_400_BAD_REQUEST)

    if not model_key:
        return Response({"detail": "model_key is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        return generator_generate_view_impl(user, model_key, count)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generator_clear_view(request):
    """Clear Y records (or all) for a model; preserves superuser sopira for user model."""
    user = request.user
    if not user.is_superuser:
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    model_key = request.data.get("model_key")
    delete_count = request.data.get("delete_count")
    try:
        delete_count = int(delete_count) if delete_count not in [None, ""] else None
    except Exception:
        return Response({"detail": "Invalid delete_count"}, status=status.HTTP_400_BAD_REQUEST)

    if not model_key:
        return Response({"detail": "model_key is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        return generator_clear_view_impl(user, model_key, delete_count)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generator_clear_all_view(request):
    """Clear all generator models (children first), keep superuser 'sopira'."""
    user = request.user
    if not user.is_superuser:
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    return generator_clear_all_view_impl(user)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generator_clear_all_and_state_view(request):
    """Clear all generator data, state tables (except current), and user prefs (except sopira)."""
    user = request.user
    if not user.is_superuser:
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    return generator_clear_all_and_state_view_impl(user)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generator_assign_tags_view(request):
    """Assign tags to objects of a specific model."""
    user = request.user
    if not user.is_superuser:
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        data = request.data
        model_key = data.get("model_key")
        count_per_object = data.get("count_per_object", 1)
        object_ids = data.get("object_ids")
        
        if not model_key:
            return Response({"detail": "Model key is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        return generator_assign_tags_view_impl(user, model_key, count_per_object, object_ids)
        
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generator_remove_tags_view(request):
    """Remove tags from objects of a specific model."""
    user = request.user
    if not user.is_superuser:
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        data = request.data
        model_key = data.get("model_key")
        object_ids = data.get("object_ids")
        
        if not model_key:
            return Response({"detail": "Model key is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        return generator_remove_tags_view_impl(user, model_key, object_ids)
        
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generator_tags_assign_view(request):
    """Assign tags to objects for a given generator model (CUSTOM_ENDPOINTS mapping)."""
    return generator_assign_tags_view(request)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generator_tags_remove_view(request):
    """Remove tags from objects for a given generator model (CUSTOM_ENDPOINTS mapping)."""
    return generator_remove_tags_view(request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def generator_objects_view(request):
    """Lightweight list of objects for a generator model (for tag assignment UI)."""
    user = request.user
    if not user.is_superuser:
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    model_key = request.query_params.get("model_key")
    search = request.query_params.get("search")
    limit = request.query_params.get("limit")

    return generator_objects_view_impl(user, model_key, search=search, limit=limit)
