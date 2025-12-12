def generator_assign_tags_view_impl(user, model_key: str, count_per_object: int | None = 1, object_ids=None):
    """
    Priraď tagy k vybraným objektom (alebo ku všetkým pre daný model).
    count_per_object: koľko nových tagov vygenerovať na objekt (default 1)
    object_ids: zoznam ID; ak None → všetky objekty modelu
    """
    from django.contrib.contenttypes.models import ContentType
    from sopira_magic.apps.m_tag.models import Tag, TaggedItem
    from sopira_magic.apps.generator.datasets import generate_tags

    if not model_key:
        return Response({"error": "model_key is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        count_int = max(1, int(count_per_object or 1))
    except Exception:
        count_int = 1

    cfg = get_generator_config(model_key)
    if not cfg:
        return Response({"error": f"Generator config '{model_key}' not found"}, status=status.HTTP_404_NOT_FOUND)

    model_class = GeneratorService.get_model_class(cfg["model"])
    qs = model_class.objects.all()
    if object_ids:
        try:
            qs = qs.filter(pk__in=object_ids)
        except Exception:
            pass
    objects = list(qs)

    ctype = ContentType.objects.get_for_model(model_class)
    tagged_items = 0
    tags_created = 0
    for obj in objects:
        tag_names = generate_tags(count_int)
        for name in tag_names:
            tag, created_tag = Tag.objects.get_or_create(name=name)
            tags_created += 1 if created_tag else 0
            _, created_item = TaggedItem.objects.get_or_create(
                tag=tag,
                content_type=ctype,
                object_id=obj.pk,
            )
            tagged_items += 1 if created_item else 0

    return Response(
        {
            "model_key": model_key,
            "objects_tagged": len(objects),
            "tags_requested": len(objects) * count_int,
            "tag_records_created": tags_created,
            "tagged_links_created": tagged_items,
        },
        status=status.HTTP_200_OK,
    )


def generator_remove_tags_view_impl(user, model_key: str, object_ids=None):
    """
    Odstráni všetky tagy z vybraných objektov (alebo všetkých objektov modelu).
    """
    from django.contrib.contenttypes.models import ContentType
    from sopira_magic.apps.m_tag.models import TaggedItem

    if not model_key:
        return Response({"error": "model_key is required"}, status=status.HTTP_400_BAD_REQUEST)

    cfg = get_generator_config(model_key)
    if not cfg:
        return Response({"error": f"Generator config '{model_key}' not found"}, status=status.HTTP_404_NOT_FOUND)

    model_class = GeneratorService.get_model_class(cfg["model"])
    qs = model_class.objects.all()
    if object_ids:
        try:
            qs = qs.filter(pk__in=object_ids)
        except Exception:
            pass
    obj_ids = [obj.pk for obj in qs]

    ctype = ContentType.objects.get_for_model(model_class)
    deleted, _ = TaggedItem.objects.filter(content_type=ctype, object_id__in=obj_ids).delete()

    return Response(
        {"model_key": model_key, "objects_processed": len(obj_ids), "tag_links_deleted": deleted},
        status=status.HTTP_200_OK,
    )
"""
Generator API helpers - separation of concerns from api/views.py

Tenká vrstva vo views.py má iba delegovať na tieto helpery, aby sa
api/views.py nezväčšoval. Obsahuje:
- _get_generator_dependency_graph
- _topological_order
- generator_models_view_impl
- generator_generate_view_impl
- generator_clear_view_impl
- generator_clear_all_view_impl
"""

import logging
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from sopira_magic.apps.generator.config import (
    get_all_generator_configs,
    get_generator_config,
)
from sopira_magic.apps.generator.services import GeneratorService

logger = logging.getLogger(__name__)


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


def generator_objects_view_impl(user, model_key: str, search: str | None = None, limit: int | None = 100):
    """
    Return lightweight list of existing objects for a given generator model.
    Used by FE tag management to target specific objects.
    """
    if not model_key:
        return Response({"error": "model_key is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        limit_int = max(1, min(int(limit or 100), 500))
    except Exception:
        limit_int = 100

    cfg = get_generator_config(model_key)
    if not cfg:
        return Response({"error": f"Generator config '{model_key}' not found"}, status=status.HTTP_404_NOT_FOUND)

    model_class = GeneratorService.get_model_class(cfg["model"])
    qs = model_class.objects.all()

    if search:
        search_fields = ["name", "code", "title", "human_id"]
        query = Q()
        for field in search_fields:
            if hasattr(model_class, field):
                query |= Q(**{f"{field}__icontains": search})
        if query:
            qs = qs.filter(query)

    qs = qs.order_by("id")[:limit_int]

    def get_label(obj):
        for field in ["name", "code", "title", "human_id"]:
            if hasattr(obj, field):
                value = getattr(obj, field, None)
                if value:
                    return str(value)
        return f"{model_class.__name__} {obj.pk}"

    objects = [{"id": str(obj.pk), "label": get_label(obj)} for obj in qs]
    return Response(
        {"model_key": model_key, "objects": objects, "total_returned": len(objects)},
        status=status.HTTP_200_OK,
    )


def generator_models_view_impl(user):
    """List generator models with counts and dependencies."""
    configs, parents_map, children_map = _get_generator_dependency_graph()

    # Precompute counts
    counts = {}
    for key, cfg in configs.items():
        model_path = cfg.get("model")
        model_class = GeneratorService.get_model_class(model_path)
        counts[key] = model_class.objects.count()

    response = []
    for key, cfg in configs.items():
        model_path = cfg.get("model")
        model_class = GeneratorService.get_model_class(model_path)
        parents = parents_map.get(key, [])
        children = children_map.get(key, [])
        can_generate = all(counts.get(p, 0) > 0 for p in parents)

        response.append(
            {
                "id": key,
                "key": key,
                "model": model_path,
                "label": model_class._meta.verbose_name.title(),
                "count": counts.get(key, 0),
                "parents": parents,
                "children": children,
                "can_generate": can_generate,
                "default_count": cfg.get("count", 0),
            }
        )

    return Response(response, status=status.HTTP_200_OK)


def generator_generate_view_impl(user, model_key: str, count):
    """
    Spustí generovanie asynchrónne a hneď vráti job_id, aby FE mohlo otvoriť modal a počúvať SSE.
    """
    import threading
    from sopira_magic.apps.generator.progress_state import new_job_id, set_status, mark_done
    from sopira_magic.apps.generator.progress import ProgressTracker

    job_id = new_job_id()
    cfg = get_generator_config(model_key)
    model_class = GeneratorService.get_model_class(cfg["model"])
    total_target = count or cfg.get("count", 0)

    # Inicializuj stav hneď, aby SSE malo čo streamovať
    set_status(
        job_id,
        {
            "job_id": job_id,
            "name": f"generate_{model_key}",
            "completed": 0,
            "total": total_target,
            "note": "Starting",
            "done": False,
        },
    )

    def run_generation():
        def status_fn(snapshot):
            set_status(job_id, snapshot)

        tracker = ProgressTracker(
            name=f"generate_{model_key}",
            total=total_target,
            status_fn=status_fn,
            job_id=job_id,
        )
        created = []
        try:
            tracker.start()
            created = GeneratorService.generate_data(
                model_key, count=count, user=user, progress=tracker, job_id=job_id
            )
            tracker.finish()
            mark_done(job_id)
            set_status(
                job_id,
                {
                    "job_id": job_id,
                    "name": f"generate_{model_key}",
                    "completed": len(created),
                    "total": total_target or len(created),
                    "done": True,
                    "note": "done",
                },
            )
        except Exception as e:
            set_status(
                job_id,
                {"job_id": job_id, "name": f"generate_{model_key}", "error": str(e), "done": True},
            )

    threading.Thread(target=run_generation, daemon=True).start()

    return Response(
        {
            "job_id": job_id,
            "model_key": model_key,
            "accepted": True,
        },
        status=status.HTTP_202_ACCEPTED,
    )


def generator_clear_view_impl(user, model_key: str, delete_count):
    from sopira_magic.apps.generator.progress_state import new_job_id, set_status, mark_done
    job_id = new_job_id()

    cfg = get_generator_config(model_key)
    model_class = GeneratorService.get_model_class(cfg["model"])
    qs = model_class.objects.all()
    total_before = qs.count()

    deleted = 0

    # Preserve superuser sopira for user model
    if model_key == "user":
        qs = qs.exclude(username="sopira")

    try:
        if delete_count and delete_count > 0:
            ids = list(qs.order_by("id").values_list("id", flat=True)[:delete_count])
            deleted = len(ids)
            if ids:
                model_class.objects.filter(id__in=ids).delete()
        else:
            if model_key == "user":
                deleted = qs.count()
                qs.delete()
            else:
                deleted = GeneratorService.clear_data(model_key, keep_count=0)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    total_after = model_class.objects.count()
    set_status(job_id, {
        "job_id": job_id,
        "name": f"clear_{model_key}",
        "completed": deleted,
        "total": total_before,
        "done": True,
    })
    mark_done(job_id)
    return Response(
        {
            "job_id": job_id,
            "model_key": model_key,
            "deleted": deleted,
            "total": total_after,
            "total_before": total_before,
        },
        status=status.HTTP_200_OK,
    )


def generator_clear_all_view_impl(user, skip_users: bool = False):
    from sopira_magic.apps.generator.progress_state import new_job_id, set_status, mark_done, is_cancel_requested
    job_id = new_job_id()
    configs, parents_map, _ = _get_generator_dependency_graph()
    order = _topological_order(configs, parents_map)  # parents last
    deleted_summary = {}

    delete_order = list(reversed(order))  # children first, parents last

    total_target = sum(get_generator_config(k).get("count", 0) for k in delete_order)
    completed = 0

    for key in delete_order:
        if is_cancel_requested(job_id):
            deleted_summary["cancelled"] = True
            break
        try:
            cfg = get_generator_config(key)
            model_class = GeneratorService.get_model_class(cfg["model"])

            if key == "user":
                if skip_users:
                    deleted_summary[key] = "skipped"
                    continue
                
                # First, clear state records for users to be deleted (cross-database CASCADE)
                try:
                    from sopira_magic.apps.state.models import TableState, SavedWorkspace, EnvironmentState
                    from sopira_magic.apps.m_user.models import UserPreference
                    
                    # Get IDs of users to delete (all except sopira)
                    user_ids_to_delete = list(
                        model_class.objects.exclude(username="sopira").values_list("id", flat=True)
                    )
                    
                    if user_ids_to_delete:
                        # Clear state DB records for these users
                        TableState.objects.using("state").filter(user_id__in=user_ids_to_delete).delete()
                        SavedWorkspace.objects.using("state").filter(user_id__in=user_ids_to_delete).delete()
                        EnvironmentState.objects.using("state").filter(user_id__in=user_ids_to_delete).delete()
                        
                        # Clear UserPreference (PRIMARY DB)
                        UserPreference.objects.filter(user_id__in=user_ids_to_delete).delete()
                except Exception as state_err:
                    logger.warning("Failed to clear state data for users: %s", state_err)
                
                # Now delete users
                qs = model_class.objects.exclude(username="sopira")
                deleted = qs.count()
                try:
                    qs.delete()
                    deleted_summary[key] = deleted
                except Exception as e:
                    # Log error but still report how many we tried to delete
                    deleted_summary[key] = f"error: {str(e)} (attempted {deleted})"
                continue

            deleted = GeneratorService.clear_data(key, keep_count=0)
            deleted_summary[key] = deleted
            completed += deleted
            set_status(job_id, {
                "job_id": job_id,
                "name": "clear_all",
                "completed": completed,
                "total": total_target,
                "note": f"cleared {key}",
            })
        except Exception as e:
            deleted_summary[key] = f"error: {str(e)}"

    mark_done(job_id)
    return Response({"job_id": job_id, "deleted": deleted_summary}, status=status.HTTP_200_OK)


def generator_clear_all_and_state_view_impl(user):
    """
    Clear generator data (children -> parents), keep sopira, and also clear state/user preferences safely.
    - state tables: keep only current preset (if any)
    - user preferences: remove all except sopira
    """
    from sopira_magic.apps.state.models import TableState
    from sopira_magic.apps.m_user.models import UserPreference
    from sopira_magic.apps.generator.progress_state import new_job_id, set_status, mark_done

    job_id = new_job_id()
    set_status(
        job_id,
        {
            "job_id": job_id,
            "name": "clear_all_state",
            "completed": 0,
            "total": 3,
            "note": "starting",
            "done": False,
        },
    )

    # 1) Clear generator data (skip users to avoid cross-db state cascade issues; sopira stays)
    generator_result = generator_clear_all_view_impl(user, skip_users=False).data
    set_status(
        job_id,
        {
            "job_id": job_id,
            "name": "clear_all_state",
            "completed": 1,
            "total": 3,
            "note": "generator cleared",
            "done": False,
        },
    )

    # 2) Clear state tables (keep current)
    state_deleted = {}
    try:
        qs = TableState.objects.using("state").all()
        deleted_count = qs.delete()[0]
        state_deleted["tablestate_deleted"] = deleted_count
    except Exception as e:
        state_deleted["error"] = str(e)
    set_status(
        job_id,
        {
            "job_id": job_id,
            "name": "clear_all_state",
            "completed": 2,
            "total": 3,
            "note": "state cleared",
            "done": False,
        },
    )

    # 3) Clear user preferences except sopira
    preferences_deleted = {}
    try:
        qs = UserPreference.objects.exclude(user__username="sopira")
        deleted_count = qs.delete()[0]
        preferences_deleted["userpreferences_deleted"] = deleted_count
    except Exception as e:
        preferences_deleted["error"] = str(e)

    mark_done(job_id, note="done")
    set_status(
        job_id,
        {
            "job_id": job_id,
            "name": "clear_all_state",
            "completed": 3,
            "total": 3,
            "note": "done",
            "done": True,
        },
    )

    return Response(
        {
            "job_id": job_id,
            "generator": generator_result.get("deleted", generator_result),
            "state": state_deleted,
            "preferences": preferences_deleted,
        },
        status=status.HTTP_200_OK,
    )


# =============================================================================
# PROGRESS API - status / cancel / stream
# =============================================================================

def generator_progress_status_view_impl(job_id: str):
    from sopira_magic.apps.generator.progress_state import get_status
    status_data = get_status(job_id)
    if not status_data:
        return Response({"detail": "job not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(status_data, status=status.HTTP_200_OK)


def generator_progress_cancel_view_impl(job_id: str):
    from sopira_magic.apps.generator.progress_state import mark_cancel
    mark_cancel(job_id)
    return Response({"job_id": job_id, "cancel_requested": True}, status=status.HTTP_200_OK)


# =============================================================================
# TAG API HELPERS - Wrapper functions for tag operations
# =============================================================================

def generator_assign_tags_view_impl(user, model_key, count_per_object=2, object_ids=None):
    """
    API helper for assigning tags to existing objects.
    
    Args:
        user: request.user (must be superuser validated upstream)
        model_key: generator model key (required)
        count_per_object: how many tags per object (default 2)
        object_ids: optional list of specific object IDs
    """
    from ..services import GeneratorService

    if not model_key:
        return Response({"error": "model_key is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        result = GeneratorService.assign_tags_to_objects(
            user=user,
            model_key=model_key,
            count_per_object=count_per_object,
            object_ids=object_ids,
        )
        return Response(result, status=status.HTTP_200_OK)

    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": f"Internal server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def generator_remove_tags_view_impl(user, model_key, count_per_object=None, object_ids=None):
    """
    API helper for removing tags from objects.
    
    Args:
        user: request.user (must be superuser validated upstream)
        model_key: generator model key (required)
        count_per_object: optional number of tags to remove per object (None => remove all)
        object_ids: optional list of specific object IDs
    """
    from ..services import GeneratorService

    if not model_key:
        return Response({"error": "model_key is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        result = GeneratorService.remove_tags_from_objects(
            user=user,
            model_key=model_key,
            count_per_object=count_per_object,
            object_ids=object_ids,
        )
        return Response(result, status=status.HTTP_200_OK)

    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": f"Internal server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Backward-compatible wrappers (request-based signature)
def generator_tags_assign_view_impl(request):
    data = request.data or {}
    return generator_assign_tags_view_impl(
        user=request.user,
        model_key=data.get("model_key"),
        count_per_object=data.get("count_per_object", 2),
        object_ids=data.get("object_ids"),
    )


def generator_tags_remove_view_impl(request):
    data = request.data or {}
    return generator_remove_tags_view_impl(
        user=request.user,
        model_key=data.get("model_key"),
        count_per_object=data.get("count_per_object"),
        object_ids=data.get("object_ids"),
    )

