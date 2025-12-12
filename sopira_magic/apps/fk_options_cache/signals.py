"""
Signal handlers to keep FK options cache in sync with source models.
"""

import logging
from functools import partial

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from sopira_magic.apps.api.view_configs import VIEWS_MATRIX
from .services import FKCacheService

logger = logging.getLogger(__name__)


def _invalidate_view(view_name: str, **kwargs):
    FKCacheService.invalidate_all(view_name)
    logger.debug("FK cache invalidated via signal for %s", view_name)


# Dynamically register signals for all FK-capable views
for view_name, cfg in VIEWS_MATRIX.items():
    model = cfg.get("model")
    if not model:
        continue

    # Consider view as FK source if it defines fk_display_template
    if not cfg.get("fk_display_template"):
        continue

    dispatch_uid = f"fk_cache_{view_name}"

    post_save.connect(
        receiver=partial(_invalidate_view, view_name),
        sender=model,
        weak=False,
        dispatch_uid=f"{dispatch_uid}_save",
    )
    post_delete.connect(
        receiver=partial(_invalidate_view, view_name),
        sender=model,
        weak=False,
        dispatch_uid=f"{dispatch_uid}_delete",
    )

