#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/progress.py
#   Progress logging helper - reusable across generator commands
#..............................................................

"""
Lightweight progress tracker for long-running generator operations.

Usage:
    tracker = ProgressTracker(name="generate_seed_data", total=500, logger=logger)
    tracker.start()
    ...
    tracker.step(n=created_count, note=f"model {model_key}")
    ...
    tracker.finish()
"""

from __future__ import annotations

import time
from typing import Callable, Optional, Dict, Any


def _fmt_seconds(seconds: float) -> str:
    """Return human-friendly duration (e.g., '1m 23s')."""
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    minutes, sec = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {sec}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m {sec}s"


class ProgressTracker:
    """
    Simple progress helper.

    - Reports percent, elapsed, ETA based on completed steps.
    - Logs via provided logger (info) and/or callable log_fn (e.g., BaseCommand.stdout.write).
    """

    def __init__(
        self,
        name: str,
        total: int,
        logger=None,
        log_fn: Optional[Callable[[str], None]] = None,
        status_fn: Optional[Callable[[Dict[str, Any]], None]] = None,
        job_id: Optional[str] = None,
        min_interval: float = 2.0,
    ):
        self.name = name
        self.total = max(int(total), 0)
        self.logger = logger
        self.log_fn = log_fn
        self.status_fn = status_fn
        self.job_id = job_id
        self.min_interval = min_interval
        self.start_time: Optional[float] = None
        self.last_log_time: float = 0.0
        self.completed = 0

    def start(self):
        self.start_time = time.time()
        self.last_log_time = self.start_time
        self._emit(f"[{self.name}] start | total={self.total}", done=False, note="start")

    def step(self, n: int = 1, note: Optional[str] = None):
        self.completed += n
        now = time.time()
        if now - self.last_log_time < self.min_interval:
            return
        self.last_log_time = now
        self._emit(self._build_msg(note, now), done=False, note=note)

    def finish(self):
        now = time.time()
        msg = self._build_msg("done", now, force_done=True)
        self._emit(msg, done=True, note="done")

    # -------------------------
    # Internal helpers
    # -------------------------
    def _build_msg(self, note: Optional[str], now: float, force_done: bool = False) -> str:
        elapsed = now - (self.start_time or now)
        pct = (self.completed / self.total * 100) if self.total else 0
        remaining = max(self.total - self.completed, 0)
        eta = (elapsed / self.completed * remaining) if self.completed else 0
        parts = [
            f"[{self.name}]",
            f"{self.completed}/{self.total}" if self.total else f"{self.completed}",
            f"({pct:.1f}%)" if self.total else "",
            f"elapsed={_fmt_seconds(elapsed)}",
            f"eta={_fmt_seconds(eta)}" if not force_done and self.total else "",
        ]
        if note:
            parts.append(f"| {note}")
        if force_done:
            parts.append("| done")
        return " ".join(filter(None, parts))

    def _emit(self, msg: str, done: bool = False, note: Optional[str] = None):
        if self.logger:
            try:
                self.logger.info(msg)
            except Exception:
                pass
        if self.log_fn:
            try:
                self.log_fn(msg)
            except Exception:
                pass
        if self.status_fn:
            try:
                payload = {
                    "job_id": self.job_id,
                    "name": self.name,
                    "completed": self.completed,
                    "total": self.total,
                    "pct": (self.completed / self.total * 100) if self.total else None,
                    "note": note,
                    "done": done,
                }
                # estimate eta
                if self.start_time and self.completed > 0:
                    elapsed = time.time() - self.start_time
                    remaining = max(self.total - self.completed, 0)
                    eta = (elapsed / self.completed * remaining) if self.total else None
                    payload["eta_seconds"] = eta
                    payload["elapsed_seconds"] = elapsed
                self.status_fn(payload)
            except Exception:
                pass

