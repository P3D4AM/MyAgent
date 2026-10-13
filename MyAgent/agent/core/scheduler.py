"""Cron-like scheduler — run task files on intervals or at a daily time.

Examples:
    sched = Scheduler(config)
    sched.every("tasks/post.json", minutes=30)
    sched.daily("tasks/report.json", at="09:30")
    sched.run_forever()          # blocks, logs each execution
"""

import random
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, List, Optional

from core.logger import get_logger

log = get_logger("scheduler")


class _Entry:
    def __init__(self, task_path: str, run: Callable[[], object]):
        self.task_path = task_path
        self.run = run
        self.last_run: Optional[datetime] = None
        self.next_due: Optional[datetime] = None

    def __repr__(self) -> str:
        return f"<{self.task_path} next={self.next_due:%H:%M}>"


class Scheduler:
    """Background task runner — thread-safe, single worker by default."""

    def __init__(self, config: Optional[dict] = None):
        self._entries: List[_Entry] = []
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self.max_concurrent = (config or {}).get("scheduler", {}).get("max_concurrent", 1)
        self._active = 0

    # -- declaration API ---------------------------------------------------
    def every(self, task_path: str, seconds: int = 0, minutes: int = 0,
              hours: int = 0, jitter_s: int = 30) -> None:
        """Run the task at a fixed interval (with small random jitter)."""
        interval = seconds + minutes * 60 + hours * 3600
        if interval <= 0:
            raise ValueError("interval must be positive")

        def _runner():
            return self._load_and_run(task_path)

        entry = _Entry(task_path, _runner)
        entry.next_due = datetime.now() + timedelta(seconds=interval)

        entry.tick = lambda: setattr(          # type: ignore[attr-defined]
            entry, "next_due", entry.next_due + timedelta(
                seconds=interval + random.randint(0, jitter_s)))
        with self._lock:
            self._entries.append(entry)
        log.info("scheduled %s → every %ss (+%ss jitter)", task_path, interval, jitter_s)

    def daily(self, task_path: str, at: str = "09:00") -> None:
        """Run the task once per day at `at` (HH:MM, 24h)."""

        def _runner():
            return self._load_and_run(task_path)

        entry = _Entry(task_path, _runner)
        hh, mm = (int(x) for x in at.split(":"))
        now = datetime.now()
        due = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if due <= now:
            due += timedelta(days=1)
        entry.next_due = due
        entry.tick = lambda: setattr(          # type: ignore[attr-defined]
            entry, "next_due", entry.next_due + timedelta(days=1))
        with self._lock:
            self._entries.append(entry)
        log.info("scheduled %s → daily at %02d:%02d", task_path, hh, mm)

    # -- execution ----------------------------------------------------------
    def _load_and_run(self, task_path: str):
        """Delegate to a runner injected by main.py (keeps the scheduler generic)."""
        if self._runner is None:
            raise RuntimeError("no runner attached — call attach_runner() first")
        return self._runner(task_path)

    _runner: Optional[Callable[[str], object]] = None

    def attach_runner(self, runner: Callable[[str], object]) -> None:
        """runner(task_path) → executes the task (wired in main.py)."""
        self._runner = runner

    def run_forever(self, tick_seconds: float = 1.0) -> None:
        log.info("⏰ scheduler live — %s entr%s watching",
                 len(self._entries), "y" if len(self._entries) == 1 else "ies")
        while not self._stop.is_set():
            now = datetime.now()
            with self._lock:
                due = [e for e in self._entries
                       if e.next_due and e.next_due <= now and self._active < self.max_concurrent]
            for entry in due:
                self._active += 1
                threading.Thread(target=self._safe_run, args=(entry,), daemon=True).start()
            time.sleep(tick_seconds)

    def _safe_run(self, entry: _Entry) -> None:
        try:
            log.info("⏰ firing %s", entry.task_path)
            entry.run()
            entry.last_run = datetime.now()
        except Exception as exc:
            log.error("scheduled run of %s failed: %s", entry.task_path, exc)
        finally:
            entry.tick()                       # schedule next occurrence
            self._active -= 1

    def stop(self) -> None:
        self._stop.set()

    def status(self) -> List[Dict[str, str]]:
        with self._lock:
            return [
                {
                    "task": e.task_path,
                    "next_due": e.next_due.strftime("%Y-%m-%d %H:%M:%S") if e.next_due else "-",
                    "last_run": e.last_run.strftime("%Y-%m-%d %H:%M:%S") if e.last_run else "never",
                }
                for e in self._entries
            ]
