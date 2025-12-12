#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/progress_state.py
#   Shared progress state storage (cache-backed) for SSE/status endpoints
#..............................................................

from __future__ import annotations

import time
import uuid
from typing import Dict, Any, Optional
from django.core.cache import caches

CACHE_KEY_PREFIX = "generator_progress:"
CACHE = caches["default"]
TTL_SECONDS = 60 * 60  # keep for 1h


def new_job_id() -> str:
    return uuid.uuid4().hex


def _key(job_id: str) -> str:
    return f"{CACHE_KEY_PREFIX}{job_id}"


def set_status(job_id: str, data: Dict[str, Any]):
    now = time.time()
    status = get_status(job_id) or {}
    status.update(data)
    status["updated_at"] = now
    CACHE.set(_key(job_id), status, TTL_SECONDS)


def get_status(job_id: str) -> Optional[Dict[str, Any]]:
    return CACHE.get(_key(job_id))


def mark_cancel(job_id: str):
    status = get_status(job_id) or {}
    status["cancel_requested"] = True
    set_status(job_id, status)


def is_cancel_requested(job_id: str) -> bool:
    status = get_status(job_id) or {}
    return bool(status.get("cancel_requested"))


def mark_done(job_id: str, note: str = "done"):
    status = get_status(job_id) or {}
    status.update({"done": True, "note": note})
    set_status(job_id, status)

