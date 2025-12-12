"""
Signals pre automatickú indexáciu (create/update/delete).
"""

from django.db.models.signals import post_delete, post_save

from sopira_magic.apps.api.view_configs import VIEWS_MATRIX
from sopira_magic.apps.search.services import SearchService

_service = SearchService()
_registered = False


def _make_save_handler(view_name: str):
    def _handler(sender, instance, **kwargs):
        _service.index_instance(view_name, instance)
    return _handler


def _make_delete_handler(view_name: str):
    def _handler(sender, instance, **kwargs):
        _service.delete_instance(view_name, instance)
    return _handler


def register_model_signals():
    """
    Pre každý view z VIEWS_MATRIX (dynamic_search=True) zaregistruje post_save/post_delete.
    """
    global _registered
    if _registered:
        return

    for view_name, cfg in VIEWS_MATRIX.items():
        if not cfg.get("dynamic_search", True):
            continue
        model = cfg.get("model")
        if not model:
            continue

        post_save.connect(_make_save_handler(view_name), sender=model, dispatch_uid=f"search_index_save_{view_name}", weak=False)
        post_delete.connect(_make_delete_handler(view_name), sender=model, dispatch_uid=f"search_index_delete_{view_name}", weak=False)

    _registered = True

