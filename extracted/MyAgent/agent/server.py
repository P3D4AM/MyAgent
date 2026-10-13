#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ParsAgent Web Panel — سرور محلیِ پنل کنترل
================================================

همان ایجنت پارس‌ایجنت، اما با یک سرور وب محلی (فقط روی همین سیستم:
http://127.0.0.1:8765) که همهٔ قابلیت‌ها را از مرورگر قابل استفاده می‌کند:

  • پلتفرم‌ها   → باز کردن/بستن مرورگر هر پلتفرم (پروفایل ماندگار) + اکشن‌ها
  • وظایف      → اجرای فایل‌های تسک JSON + ویرایشگر + نمونه‌ها
  • ضبط ماکرو   → شروع/توقف از خود پنل (یا کلید F9/F10) + ذخیره/پخش با سرعت
  • سیستم      → اسکرین‌شات زنده، کلیک/تایپ/هاتکی/اسکرول، اعلان، دستور، خاموشی
  • لاگ‌ها      → استریم زندهٔ رویدادهای همهٔ موتورها (WebSocket)
  • تنظیمات     → ویرایش مستقیم config.json

اجرا (راه توصیه‌شده — از لانچر گرافیکی):
    python launcher.py          → دکمهٔ «اجرای سرور»

اجرا (دستی):
    python server.py
    python -m uvicorn server:app --host 127.0.0.1 --port 8765

نکتهٔ امنیتی: سرور فقط روی 127.0.0.1 گوش می‌دهد؛ از بیرونِ همین
سیستم قابل دسترسی نیست و نیازی به اینترنت هم ندارد.
"""

from __future__ import annotations

import asyncio
import base64
import importlib.util
import io
import itertools
import json
import logging
import os
import platform as _platform
import queue
import shutil
import subprocess
import sys
import threading
import time
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from fastapi import Body, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

APP_VERSION = "1.2.0"
HOST, PORT = "127.0.0.1", 8765
PANEL_URL = f"http://{HOST}:{PORT}"

WEB_DIR = ROOT / "web"
MACROS_DIR = ROOT / "macros"
TASKS_DIR = ROOT / "tasks"
SHOTS_DIR = ROOT / "logs" / "shots"
for _d in (WEB_DIR, MACROS_DIR, TASKS_DIR, SHOTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------- #
# ۱) قلاب لاگ — باید «قبل از» ایمپورت ماژول‌های ایجنت نصب شود تا لاگرهای
#    تازه (browser / desktop / recorder / platforms / …) هم به پنل بروند.
# --------------------------------------------------------------------------- #
import core.logger as _cl  # noqa: E402

log = _cl.get_logger("server")


class LogHub:
    """مرکز پخش رویداد به همهٔ کلاینت‌های متصل‌شده با WebSocket."""

    def __init__(self) -> None:
        self.clients: set = set()
        self.history: deque = deque(maxlen=300)
        self._lock = threading.Lock()

    def emit(self, name: str, level: str, msg: str) -> None:
        item = {
            "type": "log", "ts": datetime.now().strftime("%H:%M:%S"),
            "name": name, "level": level, "msg": str(msg)[:2000],
        }
        with self._lock:
            self.history.append(item)
        self.push(item)

    def push(self, item: dict) -> None:
        """پخش یک رویداد (log/job/record) به همه — امن از هر نخ."""
        loop = LOOP
        if loop is None:
            return
        try:
            asyncio.run_coroutine_threadsafe(self._broadcast(item), loop)
        except Exception:
            pass

    async def _broadcast(self, item: dict) -> None:
        data = json.dumps(item, ensure_ascii=False)
        dead = []
        for ws in list(self.clients):
            try:
                await ws.send_text(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.clients.discard(ws)


LOG = LogHub()
LOOP: Optional[asyncio.AbstractEventLoop] = None


class _WsHandler(logging.Handler):
    """هندلر logging که هر رکورد را به پنل می‌فرستد."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            LOG.emit(record.name, record.levelname.lower(), record.getMessage())
        except Exception:
            pass


_WS_HANDLER = _WsHandler()
_orig_get_logger = _cl.get_logger


def _patched_get_logger(name: str = "parsagent"):
    lg = _orig_get_logger(name)
    if _WS_HANDLER not in lg.handlers:
        lg.addHandler(_WS_HANDLER)
    return lg


_cl.get_logger = _patched_get_logger          # ماژول‌های بعدی نسخهٔ قلاب‌دار را می‌گیرند
log.addHandler(_WS_HANDLER)


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


# --------------------------------------------------------------------------- #
# ۲) ایمپورت ماژول‌های ایجنت — مقاوم به نبودِ بعضی وابستگی‌ها
# --------------------------------------------------------------------------- #
try:
    import pyautogui                                # noqa: E402
    try:
        import pyperclip                            # noqa: E402
    except Exception:
        pyperclip = None
    HAVE_INPUT = True
except Exception:
    pyautogui = None                                # type: ignore[assignment]
    pyperclip = None
    HAVE_INPUT = False

try:
    import psutil                                   # noqa: E402
except Exception:
    psutil = None                                   # type: ignore[assignment]

AGENT_IMPORT_ERROR: Optional[str] = None
try:
    from core.browser_engine import BrowserEngine   # noqa: E402
    from core.captcha import CaptchaSolver           # noqa: E402
    from core.credentials import (                    # noqa: E402
        FIELDS as CRED_FIELDS, clear_platform as cred_clear,
        get_platform as cred_get, masked as cred_masked,
        set_platform as cred_set)
    from core.notify import notify                  # noqa: E402
    from core.stealth import PROBE_JS, evaluate_probe   # noqa: E402
    from core.system_controller import SystemController  # noqa: E402
    from core.task_engine import TaskEngine         # noqa: E402
    from platforms import PLATFORMS                 # noqa: E402
except Exception as _exc:                          # pragma: no cover
    AGENT_IMPORT_ERROR = str(_exc)
    CRED_FIELDS = {}
    cred_clear = cred_get = cred_masked = cred_set = None
    CaptchaSolver = None                            # type: ignore[assignment]
    eval_probe = None
    PROBE_JS = None


def _require_agent() -> None:
    if AGENT_IMPORT_ERROR:
        raise RuntimeError(
            "ماژول‌های ایجنت در دسترس نیستند: " + AGENT_IMPORT_ERROR +
            " — با دکمهٔ «نصب پیش‌نیازها» در لانچر نصبشان کنید")


def _require_input() -> None:
    if not HAVE_INPUT:
        raise RuntimeError("pyautogui نصب نیست — از لانچر «نصب پیش‌نیازها» را بزنید")


def _require_pynput() -> None:
    try:
        import pynput                               # noqa: F401
    except Exception as exc:
        raise RuntimeError(f"pynput نصب نیست: {exc}")


# --------------------------------------------------------------------------- #
# ۳) نخِ تک‌نفرهٔ ایجنت — Playwright سینک فقط از داخل همین نخ باید استفاده شود
# --------------------------------------------------------------------------- #
class AgentWorker:
    """صف تک‌نخمی برای هر عملیات ایجنت (مرورگر، تسک، ورود، …).

    sync-API پایتونِ Playwright بین‌نخ امن نیست؛ همهٔ کارهای مرورگری از
    این نخ عبور می‌کنند تا هیچ‌وقت دو نخ هم‌زمان کانتکست را لمس نکنند.
    """

    def __init__(self) -> None:
        self._q: "queue.Queue" = queue.Queue()
        threading.Thread(target=self._loop, name="parsagent-worker",
                         daemon=True).start()

    def _loop(self) -> None:
        while True:
            fn, args, done, slot = self._q.get()
            try:
                slot["result"] = fn(*args)
            except BaseException as exc:            # noqa: BLE001
                slot["error"] = exc
            finally:
                done.set()

    def run(self, fn: Callable, *args: Any) -> Any:
        done = threading.Event()
        slot: Dict[str, Any] = {"result": None, "error": None}
        self._q.put((fn, args, done, slot))
        done.wait()
        if slot["error"] is not None:
            raise slot["error"]
        return slot["result"]


AGENT = AgentWorker()

# --------------------------------------------------------------------------- #
# ۴) موتورهای سینگلتون (داخل نخِ AgentWorker ساخته می‌شوند)
# --------------------------------------------------------------------------- #
_task_engine = None        # TaskEngine مشترک
_direct_desktop = None     # SystemController بدون تأخیر انسانی برای کنترل مستقیم


def _load_config() -> dict:
    path = ROOT / "config.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _get_engine():
    """TaskEngine سینگلتون — همیشه از داخل AgentWorker صدا زده شود."""
    global _task_engine, _direct_desktop
    if _task_engine is None:
        _require_agent()
        config = _load_config()
        browser = BrowserEngine(config).start(lazy=True)
        _direct_desktop = SystemController(human=False)
        desktop_task = SystemController(human=config.get("human", {}).get("enabled", True))
        _task_engine = TaskEngine(config, lambda: browser, desktop_task, PLATFORMS)
        LOG.emit("server", "info", "موتور ایجنت آماده شد (مرورگر lazy)")
    return _task_engine


def _browser_state() -> Optional[dict]:
    if _task_engine is None:
        return None
    b = getattr(_task_engine, "_browser", None)
    if b is None:
        return None
    try:
        return {"channel": b.channel, "profiles": list(b.open_profiles())}
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# ۵) سیستم کارها (job) — هر عملیات زمان‌بر یک شناسه می‌گیرد و از WebSocket
#    وضعیتش پخش می‌شود.
# --------------------------------------------------------------------------- #
class _Cancelled(Exception):
    pass


JOBS: Dict[str, dict] = {}
_JOB_ORDER: List[str] = []
_JOB_LOCK = threading.Lock()
_job_seq = itertools.count(1)


def _job_cancelled(jid: str) -> bool:
    with _JOB_LOCK:
        return bool(JOBS.get(jid, {}).get("cancel"))


def _job_public(job: dict, include_result: bool = True) -> dict:
    base = {
        "id": job["id"], "kind": job["kind"], "label": job["label"],
        "status": job["status"], "started_at": job["started_at"],
        "finished_at": job["finished_at"], "error": job["error"],
        "cancellable": job["cancellable"],
    }
    if include_result and job.get("result") is not None:
        try:
            s = json.dumps(job["result"], ensure_ascii=False, default=str)
            if len(s) < 4000:
                base["result"] = job["result"]
            else:
                base["result_omitted"] = True
        except Exception:
            base["result_omitted"] = True
    return base


def _recent_jobs(n: int = 20) -> List[dict]:
    with _JOB_LOCK:
        return [JOBS[j] for j in _JOB_ORDER[-n:]][::-1]


def _new_job(kind: str, label: str, fn: Callable, *args: Any,
             via_worker: bool = True, inject_id: bool = False) -> dict:
    jid = f"j{next(_job_seq)}"
    job = {
        "id": jid, "kind": kind, "label": label, "status": "running",
        "started_at": _now_iso(), "finished_at": None,
        "result": None, "error": None, "cancel": False,
        "cancellable": kind == "macro",
    }
    with _JOB_LOCK:
        JOBS[jid] = job
        _JOB_ORDER.append(jid)
        while len(_JOB_ORDER) > 80:
            JOBS.pop(_JOB_ORDER.pop(0), None)

    def _run() -> None:
        call_args = (jid,) + args if inject_id else args
        try:
            if via_worker:
                job["result"] = AGENT.run(fn, *call_args)
            else:
                job["result"] = fn(*call_args)
            job["status"] = "cancelled" if job["cancel"] else "done"
        except _Cancelled as exc:
            job["status"] = "cancelled"
            job["error"] = str(exc)
        except Exception as exc:                   # noqa: BLE001
            job["status"] = "failed"
            job["error"] = str(exc)[:600]
            LOG.emit("server", "error", f"کار «{label}» شکست خورد: {str(exc)[:220]}")
        finally:
            job["finished_at"] = _now_iso()
            LOG.push({"type": "job", "job": _job_public(job)})

    threading.Thread(target=_run, daemon=True, name=f"job-{jid}").start()
    LOG.push({"type": "job", "job": _job_public(job)})
    return job


# --------------------------------------------------------------------------- #
# ۶) ضبط‌کنندهٔ تحت وب — همان فرمت ماکروی InputRecorder (سازگار با CLI)
#    F9 = پایان و ذخیره، F10 = لغو — یا از خود پنل.
# --------------------------------------------------------------------------- #
class WebRecorder:
    def __init__(self) -> None:
        self.events: List[dict] = []
        self.active = False
        self.last_macro: Optional[dict] = None
        self._t0 = 0.0
        self._last_move = 0.0
        self._m = None
        self._k = None

    def _now(self) -> float:
        return round(time.monotonic() - self._t0, 4)

    def start(self) -> None:
        if self.active:
            return
        from pynput import keyboard, mouse
        self.events = []
        self.last_macro = None
        self._t0 = time.monotonic()
        self._last_move = 0.0
        self.active = True
        self._m = mouse.Listener(on_move=self._om, on_click=self._oc,
                                 on_scroll=self._os)
        self._k = keyboard.Listener(on_press=self._ok_press,
                                    on_release=self._ok_rel)
        self._m.start()
        self._k.start()
        threading.Thread(target=self._tick, daemon=True).start()
        LOG.emit("recorder", "info", "● ضبط شروع شد — پایان: دکمهٔ پنل یا کلید F9")

    def _tick(self) -> None:
        while self.active:
            LOG.push({"type": "record", "active": True,
                      "count": len(self.events), "duration": self._now()})
            time.sleep(0.8)

    def _om(self, x: int, y: int) -> None:
        if not self.active:
            return
        t = time.monotonic()
        if t - self._last_move < 0.025:            # حداکثر ~۴۰ نمونه در ثانیه
            return
        self._last_move = t
        self.events.append({"t": self._now(), "type": "move", "x": x, "y": y})

    def _oc(self, x: int, y: int, button, pressed: bool) -> None:
        if not self.active:
            return
        self.events.append({"t": self._now(), "type": "click", "x": x, "y": y,
                            "button": button.name, "pressed": pressed})

    def _os(self, x: int, y: int, dx: int, dy: int) -> None:
        if not self.active:
            return
        self.events.append({"t": self._now(), "type": "scroll",
                            "x": x, "y": y, "dx": dx, "dy": dy})

    @staticmethod
    def _key_of(key) -> Optional[str]:
        ch = getattr(key, "char", None)
        if ch:
            return ch
        return getattr(key, "name", None) or str(key)

    def _ok_press(self, key) -> None:
        if not self.active:
            return
        name = getattr(key, "name", None)
        if name in ("f9", "f10"):                   # کلیدهای کنترلی ضبط
            self.stop(save=(name == "f9"))
            return
        self.events.append({"t": self._now(), "type": "key",
                            "key": self._key_of(key), "pressed": True})

    def _ok_rel(self, key) -> None:
        if not self.active:
            return
        ch = getattr(key, "char", None)
        if ch:                                      # برای حروف، press کافی است
            return
        self.events.append({"t": self._now(), "type": "key",
                            "key": self._key_of(key), "pressed": False})

    def stop(self, save: bool = True) -> Optional[dict]:
        self.active = False
        for listener in (self._m, self._k):
            try:
                listener.stop()
            except Exception:
                pass
        self._m = self._k = None
        macro = {
            "meta": {
                "version": 1,
                "recorded_at": datetime.now().isoformat(timespec="seconds"),
                "duration": self._now(),
                "events": len(self.events),
            },
            "events": self.events,
        }
        if save and self.events:
            self.last_macro = macro
            LOG.emit("recorder", "info",
                     f"■ ضبط تمام شد — {len(self.events)} رخداد "
                     f"({macro['meta']['duration']:.1f}s)")
        else:
            LOG.emit("recorder", "warning",
                     f"■ ضبط لغو شد — {len(self.events)} رخداد دور ریخته شد")
        LOG.push({"type": "record", "active": False,
                  "count": len(self.events), "duration": macro["meta"]["duration"]})
        return self.last_macro

    def status(self) -> dict:
        dur = self._now() if self.active else \
            (self.last_macro or {}).get("meta", {}).get("duration", 0)
        return {"active": self.active, "count": len(self.events),
                "duration": round(dur, 1)}


REC = WebRecorder()


# --------------------------------------------------------------------------- #
# ۷) پخش‌کنندهٔ ماکرو — قابل لغو + تایپ فارسی (کلیپ‌بورد)
# --------------------------------------------------------------------------- #
_MODIFIERS = {"ctrl_l", "ctrl_r", "alt_l", "alt_r", "alt_gr", "shift_l",
              "shift_r", "cmd", "cmd_r", "win", "win_l", "win_r"}

_PAGUI_KEY = {
    "ctrl_l": "ctrl", "ctrl_r": "ctrlright", "alt_l": "alt", "alt_r": "altright",
    "alt_gr": "altgr", "shift_l": "shift", "shift_r": "shiftright",
    "cmd": "win", "cmd_r": "winright", "win": "win", "win_l": "winleft",
    "win_r": "winright", "page_up": "pgup", "page_down": "pgdown",
    "esc": "escape", "return": "enter", "enter": "enter", "space": "space",
    "tab": "tab", "backspace": "backspace", "delete": "delete",
    "insert": "insert", "home": "home", "end": "end", "up": "up",
    "down": "down", "left": "left", "right": "right",
    "caps_lock": "capslock", "num_lock": "numlock",
    "print_screen": "printscreen", "volume_mute": "volumemute",
    "volume_down": "volumedown", "volume_up": "volumeup",
}
for _i in range(1, 13):
    _PAGUI_KEY[f"f{_i}"] = f"f{_i}"


def _type_text_direct(text: str) -> None:
    """تایپ متن — متن فارسی از طریق کلیپ‌بورد (typewrite فقط ASCII است)."""
    if not text:
        return
    if all(ord(c) < 128 for c in text):
        pyautogui.typewrite(text, interval=0.012)
        return
    if pyperclip is None:
        raise RuntimeError("برای متن فارسی، پکیج pyperclip لازم است")
    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.05)


def _run_macro(job_id: str, events: List[dict], speed: float, loop: int) -> dict:
    _require_input()
    speed = max(0.1, min(float(speed), 10.0))
    rounds = max(1, int(loop))
    played = 0
    for rnd in range(1, rounds + 1):
        buf = ""
        prev_t = 0.0
        for ev in events:
            if _job_cancelled(job_id):
                raise _Cancelled(f"ماکرو در دور {rnd} لغو شد")
            wait = (ev["t"] - prev_t) / speed
            prev_t = ev["t"]
            if wait > 0:
                time.sleep(min(wait, 30.0))        # حداکثر ۳۰ ثانیه مکث در هر گام
            et = ev.get("type")
            if et == "move":
                if buf:
                    _type_text_direct(buf)
                    buf = ""
                pyautogui.moveTo(ev["x"], ev["y"], duration=0)
            elif et == "click":
                if buf:
                    _type_text_direct(buf)
                    buf = ""
                if ev.get("pressed"):
                    pyautogui.click(x=ev["x"], y=ev["y"],
                                    button=ev.get("button", "left"),
                                    clicks=1, interval=0.05)
            elif et == "scroll":
                if buf:
                    _type_text_direct(buf)
                    buf = ""
                pyautogui.scroll(int(ev.get("dy", 0)))
            elif et == "key":
                key = ev.get("key")
                if not key:
                    continue
                if len(key) == 1:                  # کاراکتر معمولی
                    if ev.get("pressed", True):
                        buf += key
                else:                              # کلید ویژه
                    if buf:
                        _type_text_direct(buf)
                        buf = ""
                    mapped = _PAGUI_KEY.get(key, key)
                    if key in _MODIFIERS:
                        if ev.get("pressed", True):
                            pyautogui.keyDown(mapped)
                        else:
                            pyautogui.keyUp(mapped)
                    elif ev.get("pressed", True):
                        pyautogui.press(mapped)
            played += 1
        if buf:
            _type_text_direct(buf)
    return {"events_played": played, "rounds": rounds, "speed": speed}


# --------------------------------------------------------------------------- #
# ۸) کاتالوگ پلتفرم‌ها و اکشن‌ها برای پنل
# --------------------------------------------------------------------------- #
PLATFORM_META = {
    "instagram": {"fa": "اینستاگرام", "color": "#e1306c"},
    "twitter": {"fa": "توییتر (X)", "color": "#9aa7b8"},
    "telegram": {"fa": "تلگرام", "color": "#229ed9"},
    "facebook": {"fa": "فیسبوک", "color": "#1877f2"},
    "linkedin": {"fa": "لینکدین", "color": "#0a66c2"},
    "bale": {"fa": "بله", "color": "#20c997"},
    "rubika": {"fa": "روبیکا", "color": "#e0457b"},
    "eitaa": {"fa": "ایتا", "color": "#f0a52e"},
}

_F = {
    "image": {"key": "image", "fa": "مسیر فایل عکس", "type": "text",
              "placeholder": "assets/photo.jpg"},
    "image_opt": {"key": "image", "fa": "مسیر عکس (اختیاری)", "type": "text",
                  "optional": True, "placeholder": "assets/photo.jpg"},
    "caption": {"key": "caption", "fa": "کپشن", "type": "textarea",
                "placeholder": "متن کپشن..."},
    "text": {"key": "text", "fa": "متن", "type": "textarea", "placeholder": "متن..."},
    "username": {"key": "username", "fa": "یوزرنیم", "type": "text",
                 "placeholder": "username"},
    "message": {"key": "message", "fa": "پیام", "type": "textarea",
                "placeholder": "متن پیام..."},
    "chat": {"key": "chat", "fa": "نام چت / مخاطب", "type": "text",
             "placeholder": "نام ذخیره‌شدهٔ چت"},
    "channel": {"key": "channel", "fa": "نام کانال", "type": "text",
                "placeholder": "نام کانال"},
    "group": {"key": "group", "fa": "نام گروه", "type": "text"},
    "post_url": {"key": "post_url", "fa": "لینک پست", "type": "text",
                 "placeholder": "https://..."},
    "profile_url": {"key": "profile_url", "fa": "لینک پروفایل", "type": "text",
                    "placeholder": "https://..."},
    "note": {"key": "note", "fa": "یادداشت (اختیاری)", "type": "textarea",
             "optional": True},
    "count": {"key": "count", "fa": "تعداد", "type": "number", "value": 3},
}

ACTIONS: Dict[str, List[dict]] = {
    "instagram": [
        {"id": "post_photo", "fa": "انتشار عکس با کپشن",
         "fields": [_F["image"], _F["caption"]]},
        {"id": "upload_story", "fa": "آپلود استوری", "fields": [_F["image"]]},
        {"id": "send_dm", "fa": "ارسال دایرکت",
         "fields": [_F["username"], _F["message"]]},
        {"id": "follow", "fa": "فالو کردن", "fields": [_F["username"]]},
        {"id": "like_latest", "fa": "لایک پست‌های جدید فید", "fields": [_F["count"]]},
        {"id": "comment", "fa": "کامنت روی پست",
         "fields": [_F["post_url"], _F["text"]]},
    ],
    "twitter": [
        {"id": "post_tweet", "fa": "ارسال توییت",
         "fields": [_F["text"], _F["image_opt"]]},
        {"id": "send_dm", "fa": "ارسال دایرکت",
         "fields": [_F["username"], _F["message"]]},
        {"id": "follow", "fa": "فالو کردن", "fields": [_F["username"]]},
        {"id": "like", "fa": "لایک توییت", "fields": [_F["post_url"]]},
        {"id": "retweet", "fa": "ریتوییت", "fields": [_F["post_url"]]},
    ],
    "telegram": [
        {"id": "send_message", "fa": "ارسال پیام", "fields": [_F["chat"], _F["text"]]},
        {"id": "post_channel", "fa": "ارسال در کانال",
         "fields": [_F["channel"], _F["text"], _F["image_opt"]]},
        {"id": "send_group_message", "fa": "پیام در گروه",
         "fields": [_F["group"], _F["text"]]},
    ],
    "facebook": [
        {"id": "post_status", "fa": "انتشار پست",
         "fields": [_F["text"], _F["image_opt"]]},
        {"id": "like_post", "fa": "لایک پست", "fields": [_F["post_url"]]},
        {"id": "comment", "fa": "کامنت", "fields": [_F["post_url"], _F["text"]]},
    ],
    "linkedin": [
        {"id": "post", "fa": "انتشار پست", "fields": [_F["text"], _F["image_opt"]]},
        {"id": "connect", "fa": "درخواست اتصال",
         "fields": [_F["profile_url"], _F["note"]]},
        {"id": "send_dm", "fa": "پیام مستقیم",
         "fields": [_F["profile_url"], _F["message"]]},
    ],
    "bale": [
        {"id": "send_message", "fa": "ارسال پیام", "fields": [_F["chat"], _F["text"]]},
        {"id": "post_channel", "fa": "ارسال در کانال",
         "fields": [_F["channel"], _F["text"]]},
    ],
    "rubika": [
        {"id": "send_message", "fa": "ارسال پیام", "fields": [_F["chat"], _F["text"]]},
        {"id": "post_channel", "fa": "ارسال در کانال",
         "fields": [_F["channel"], _F["text"]]},
    ],
    "eitaa": [
        {"id": "send_message", "fa": "ارسال پیام", "fields": [_F["chat"], _F["text"]]},
        {"id": "post_channel", "fa": "ارسال در کانال",
         "fields": [_F["channel"], _F["text"]]},
    ],
}


def _platform_catalog() -> List[dict]:
    out = []
    open_profiles = (_browser_state() or {}).get("profiles", [])
    have_creds = set(cred_masked()) if cred_masked else set()
    if AGENT_IMPORT_ERROR is None:
        for pid, cls in PLATFORMS.items():
            meta = PLATFORM_META.get(pid, {"fa": pid, "color": "#888"})
            out.append({
                "id": pid, "fa": meta["fa"], "color": meta["color"],
                "url": getattr(cls, "base_url", ""),
                "open": pid in open_profiles,
                "has_creds": pid in have_creds,
                "actions": ACTIONS.get(pid, []),
            })
    else:                                          # حالت نیمه‌قابل‌استفاده
        for pid, meta in PLATFORM_META.items():
            out.append({"id": pid, "fa": meta["fa"], "color": meta["color"],
                        "url": "", "open": False, "has_creds": pid in have_creds,
                        "actions": ACTIONS.get(pid, [])})
    return out


def _modules_state() -> dict:
    mods = ["pyautogui", "pynput", "playwright", "rich", "plyer",
            "psutil", "pyperclip", "PIL"]
    out = {}
    for m in mods:
        try:
            out[m] = importlib.util.find_spec(m) is not None
        except Exception:
            out[m] = m in sys.modules
    out["fastapi"] = True
    out["uvicorn"] = True
    return out


# --------------------------------------------------------------------------- #
# ۹) عملیات پلتفرم (همه از داخل نخ ایجنت)
# --------------------------------------------------------------------------- #
def _platform_open(platform: str) -> dict:
    eng = _get_engine()
    if platform not in PLATFORMS:
        raise ValueError(f"پلتفرم ناشناخته: {platform}")
    mod = eng.platform(platform)                    # پروفایل ماندگار + لانچ تنبل
    page = getattr(mod, "_page", None)
    if page is not None:
        try:
            if not page.is_closed():
                page.goto(mod.base_url, wait_until="domcontentloaded",
                          timeout=45_000)
                try:
                    page.bring_to_front()
                except Exception:
                    pass
                return {"already_open": True, "url": page.url}
        except Exception:
            pass
    page = mod.open()                               # صفحهٔ تازه + رفتن به سایت
    return {"already_open": False, "url": page.url,
            "channel": eng._browser.channel}


def _platform_close(platform: str) -> dict:
    eng = _get_engine()
    browser = getattr(eng, "_browser", None)
    closed = browser.close_profile(platform) if browser else False
    getattr(eng, "_platform_instances", {}).pop(platform, None)
    return {"platform": platform, "closed": closed}


def _platform_logged_in(platform: str) -> dict:
    eng = _get_engine()
    mod = eng.platform(platform)
    try:
        ok = bool(mod.is_logged_in())
    except Exception as exc:
        return {"platform": platform, "logged_in": False, "error": str(exc)[:200]}
    return {"platform": platform, "logged_in": ok}


def _platform_screenshot(platform: str) -> dict:
    eng = _get_engine()
    mod = getattr(eng, "_platform_instances", {}).get(platform) \
        or eng.platform(platform)
    page = getattr(mod, "_page", None)
    if page is None:
        raise RuntimeError("صفحه‌ای باز نیست — اول پلتفرم را باز کنید")
    if page.is_closed():
        raise RuntimeError("صفحه بسته شده — دوباره پلتفرم را باز کنید")
    path = Path(eng._browser.screenshot(page, platform))
    data = path.read_bytes()
    return {"image": base64.b64encode(data).decode(),
            "path": str(path), "url": page.url}


def _platform_auto_login(platform: str) -> dict:
    """ورود خودکار: اعتبارنامه‌ها + حل کپچا + کد دومرحله‌ای (در نخ ایجنت)."""
    _require_agent()
    if not cred_get:
        raise RuntimeError("ماژول اعتبارنامه‌ها در دسترس نیست")
    if platform not in PLATFORMS:
        raise ValueError(f"پلتفرم ناشناخته: {platform}")
    creds = cred_get(platform)
    if not any(creds.get(f) for f in ("username", "email", "phone")):
        raise RuntimeError(
            "برای این پلتفرم چیزی ذخیره نشده — از «تنظیمات ← حساب‌ها و ورود "
            "خودکار» نام کاربری/شماره و رمز را پر کن و ذخیره بزن")
    cfg = _load_config()
    solver = None
    cap_cfg = cfg.get("captcha") or {}
    if cap_cfg.get("api_key") and CaptchaSolver is not None:
        solver = CaptchaSolver(cap_cfg, (cfg.get("browser") or {}).get("proxy"))
    eng = _get_engine()
    mod = eng.platform(platform)
    return mod.auto_login(creds, solver)


def _stealth_probe(platform: str) -> dict:
    """تست سریع اثر انگشت در پروفایل پلتفرم — بدون خروج از سیستم."""
    _require_agent()
    if evaluate_probe is None or PROBE_JS is None:
        raise RuntimeError("ماژول stealth در دسترس نیست")
    eng = _get_engine()
    mod = eng.platform(platform)
    page = getattr(mod, "_page", None)
    if page is None or page.is_closed():
        page = mod.open()
    probe_html = (ROOT / "data" / "stealth-probe.html").resolve()
    page.goto(probe_html.as_uri(), wait_until="domcontentloaded", timeout=20_000)
    time.sleep(0.4)                                 # فرصت اجرای init-script
    raw = page.evaluate(PROBE_JS)
    checks = evaluate_probe(raw or {})
    passed = sum(1 for c in checks if c["pass"])
    LOG.emit("stealth", "info",
             f"تست اثر انگشت {platform}: {passed}/{len(checks)} مورد سالم")
    return {"platform": platform, "checks": checks,
            "passed": passed, "total": len(checks), "raw": raw}


def _stealth_open_test_site(platform: str) -> dict:
    """باز کردن سایت‌های تست بات در پروفایل پلتفرم (آزمون واقعی)."""
    _require_agent()
    eng = _get_engine()
    mod = eng.platform(platform)
    page = getattr(mod, "_page", None)
    if page is None or page.is_closed():
        page = mod.open()
    page.goto("https://bot.sannysoft.com/", wait_until="domcontentloaded",
              timeout=45_000)
    try:
        ctx = page.context
        p2 = ctx.new_page()
        p2.goto("https://browserleaks.com/javascript", wait_until="domcontentloaded",
                timeout=45_000)
    except Exception:
        pass
    return {"ok": True, "url": page.url,
            "hint": "ردیف‌های قرمز = مشکل؛ سبز = سالم. با پروفایل واقعی مقایسه کن."}


# --------------------------------------------------------------------------- #
# ۱۰) فایل‌های تسک و ماکرو
# --------------------------------------------------------------------------- #
def _safe_name(name: str) -> str:
    safe = "".join(c for c in str(name).strip()
                   if c.isalnum() or c in " _-") or "macro"
    return safe[:60]


def _safe_file(name: str) -> Path:
    if "/" in name or "\\" in name or ".." in name:
        raise HTTPException(400, "نام فایل نامعتبر است")
    path = TASKS_DIR / name
    if not str(path).startswith(str(TASKS_DIR)):
        raise HTTPException(400, "نام فایل نامعتبر است")
    return path


def _tasks_list() -> List[dict]:
    out = []
    for f in sorted(TASKS_DIR.glob("*.json")):
        item = {"file": f.name, "names": [], "description": "", "count": 0}
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            tasks = data.get("tasks", [data]) if isinstance(data, dict) else []
            names = [t.get("name", "?") for t in tasks if isinstance(t, dict)]
            item["names"] = names
            item["count"] = len(names)
            item["description"] = data.get("description", "") if isinstance(data, dict) else ""
        except Exception:
            item["description"] = "خطای JSON"
        out.append(item)
    return out


def _macros_list() -> List[dict]:
    out = []
    for f in sorted(MACROS_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            meta = data.get("meta", {})
            out.append({"name": f.stem, "file": f.name,
                        "events": len(data.get("events", [])),
                        "duration": meta.get("duration", 0),
                        "recorded_at": meta.get("recorded_at", "")})
        except Exception:
            continue
    return out


# --------------------------------------------------------------------------- #
# ۱۱) FastAPI app
# --------------------------------------------------------------------------- #
@asynccontextmanager
async def _lifespan(app: FastAPI):
    global LOOP
    LOOP = asyncio.get_running_loop()
    LOG.emit("server", "info",
             f"🚀 سرور پنل پارس‌ایجنت v{APP_VERSION} روشن شد — {PANEL_URL}")
    if AGENT_IMPORT_ERROR:
        LOG.emit("server", "warning",
                 f"بعضی ماژول‌های ایجنت در دسترس نیستند: {AGENT_IMPORT_ERROR[:160]}")
    yield
    try:
        if REC.active:
            REC.stop(save=False)
    except Exception:
        pass
    try:
        if _task_engine is not None:
            AGENT.run(_task_engine.finish)
    except Exception:
        pass
    LOG.emit("server", "info", "سرور پنل خاموش شد")


app = FastAPI(title="ParsAgent Panel", version=APP_VERSION, lifespan=_lifespan)


# ---------- سلامت و وضعیت کلی ----------
@app.get("/api/health")
async def health():
    return {"ok": True, "version": APP_VERSION, "time": _now_iso(),
            "agent_ok": AGENT_IMPORT_ERROR is None,
            "modules": _modules_state(),
            "recording": REC.status()["active"],
            "browser": _browser_state(),
            "url": PANEL_URL}


@app.get("/api/state")
async def panel_state():
    return {
        "version": APP_VERSION,
        "agent_ok": AGENT_IMPORT_ERROR is None,
        "modules": _modules_state(),
        "platforms": _platform_catalog(),
        "browser": _browser_state(),
        "recording": REC.status(),
        "macros": _macros_list(),
        "task_files": _tasks_list(),
        "credentials": (cred_masked() if cred_masked else {}),
        "jobs": [_job_public(j, include_result=False) for j in _recent_jobs(12)],
    }


# ---------- پلتفرم‌ها ----------
@app.post("/api/platform/open")
async def platform_open(payload: dict = Body(...)):
    pid = payload.get("platform")
    if not pid:
        raise HTTPException(400, "platform الزامی است")
    job = _new_job("platform", f"🌐 باز کردن {PLATFORM_META.get(pid, {}).get('fa', pid)}",
                   _platform_open, pid)
    return _job_public(job)


@app.post("/api/platform/close")
async def platform_close(payload: dict = Body(...)):
    pid = payload.get("platform")
    if not pid:
        raise HTTPException(400, "platform الزامی است")
    job = _new_job("platform", f"⛔ بستن {PLATFORM_META.get(pid, {}).get('fa', pid)}",
                   _platform_close, pid)
    return _job_public(job)


@app.post("/api/platform/logged_in")
async def platform_logged_in(payload: dict = Body(...)):
    pid = payload.get("platform")
    if not pid:
        raise HTTPException(400, "platform الزامی است")
    job = _new_job("platform",
                   f"🔑 بررسی ورود {PLATFORM_META.get(pid, {}).get('fa', pid)}",
                   _platform_logged_in, pid)
    return _job_public(job)


@app.post("/api/platform/screenshot")
async def platform_screenshot(payload: dict = Body(...)):
    pid = payload.get("platform")
    if not pid:
        raise HTTPException(400, "platform الزامی است")
    job = _new_job("screenshot",
                   f"📸 اسکرین‌شات صفحهٔ {PLATFORM_META.get(pid, {}).get('fa', pid)}",
                   _platform_screenshot, pid)
    return _job_public(job)


@app.post("/api/platform/login")
async def platform_login(payload: dict = Body(...)):
    """ورود خودکار — اعتبارنامه + حل کپچا + TOTP (پنل ← تنظیمات ← حساب‌ها)."""
    pid = payload.get("platform")
    if not pid:
        raise HTTPException(400, "platform الزامی است")
    if pid not in PLATFORM_META:
        raise HTTPException(404, "پلتفرم ناشناخته")
    try:
        _require_agent()
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
    job = _new_job("login",
                   f"🔑 ورود خودکار {PLATFORM_META.get(pid, {}).get('fa', pid)}",
                   _platform_auto_login, pid)
    return _job_public(job)


# ---------- حساب‌ها و اعتبارنامه‌ها ----------
@app.get("/api/credentials")
async def credentials_index():
    if cred_masked is None:
        raise HTTPException(503, "ماژول اعتبارنامه‌ها در دسترس نیست")
    return {"platforms": cred_masked(),
            "path": "data/credentials.json"}


@app.post("/api/credentials")
async def credentials_save(payload: dict = Body(...)):
    if cred_set is None:
        raise HTTPException(503, "ماژول اعتبارنامه‌ها در دسترس نیست")
    pid = payload.get("platform")
    if not pid or pid not in CRED_FIELDS:
        raise HTTPException(400, "platform نامعتبر است")
    fields = {k: payload.get(k) for k in CRED_FIELDS.get(pid, [])
              if k in payload}
    if not any(str(v or "").strip() for v in fields.values()):
        raise HTTPException(400, "حداقل یک فیلد را پر کن")
    rec = cred_set(pid, fields)
    LOG.emit("credentials", "info",
             f"اعتبارنامهٔ {PLATFORM_META.get(pid, {}).get('fa', pid)} ذخیره شد "
             f"(رمز: {'✓' if rec.get('password') else '—'})")
    return {"ok": True, "platform": pid, "saved": sorted(rec.keys())}


@app.post("/api/credentials/delete")
async def credentials_delete(payload: dict = Body(...)):
    if cred_clear is None:
        raise HTTPException(503, "ماژول اعتبارنامه‌ها در دسترس نیست")
    pid = payload.get("platform")
    if not pid or pid not in CRED_FIELDS:
        raise HTTPException(400, "platform نامعتبر است")
    existed = cred_clear(pid)
    if existed:
        LOG.emit("credentials", "warning",
                 f"اعتبارنامهٔ {PLATFORM_META.get(pid, {}).get('fa', pid)} حذف شد")
    return {"ok": True, "existed": existed}


# ---------- ضد شناسایی ----------
@app.post("/api/stealth/probe")
async def stealth_probe(payload: dict = Body(...)):
    """تست سریع اثر انگشت در پروفایل پلتفرم (صفحهٔ محلی، بدون اینترنت)."""
    pid = payload.get("platform")
    if not pid or pid not in PLATFORM_META:
        raise HTTPException(400, "platform نامعتبر است")
    try:
        _require_agent()
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
    job = _new_job("stealth",
                   f"🛡️ تست اثر انگشت {PLATFORM_META.get(pid, {}).get('fa', pid)}",
                   _stealth_probe, pid)
    return _job_public(job)


@app.post("/api/stealth/test")
async def stealth_test_site(payload: dict = Body(...)):
    """باز کردن سایت‌های آزمون بات در مرورگر پلتفرم (تست واقعی)."""
    pid = payload.get("platform")
    if not pid or pid not in PLATFORM_META:
        raise HTTPException(400, "platform نامعتبر است")
    try:
        _require_agent()
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
    job = _new_job("stealth",
                   f"🌍 سایت تست بات ({PLATFORM_META.get(pid, {}).get('fa', pid)})",
                   _stealth_open_test_site, pid)
    return _job_public(job)


# ---------- اجرای اکشن پلتفرم ----------
@app.post("/api/action/run")
async def action_run(payload: dict = Body(...)):
    pid, action = payload.get("platform"), payload.get("action")
    args = payload.get("args") or {}
    if not pid or not action:
        raise HTTPException(400, "platform و action الزامی‌اند")

    def _run():
        eng = _get_engine()
        mod = eng.platform(pid)
        method = getattr(mod, action, None)
        if method is None:
            raise ValueError(f"اکشن ناشناخته: {pid}.{action}")
        method(**args)
        return {"ok": True}

    label = f"⚡ {PLATFORM_META.get(pid, {}).get('fa', pid)} · {action}"
    job = _new_job("action", label, _run)
    return _job_public(job)


# ---------- وظایف ----------
@app.get("/api/tasks")
async def tasks_index():
    return _tasks_list()


@app.get("/api/tasks/content")
async def task_content(file: str):
    path = _safe_file(file)
    if not path.exists():
        raise HTTPException(404, "فایل پیدا نشد")
    return {"file": file, "content": path.read_text(encoding="utf-8")}


@app.post("/api/tasks/save")
async def task_save(payload: dict = Body(...)):
    fname = payload.get("file") or "my-task.json"
    if not fname.endswith(".json"):
        fname += ".json"
    path = _safe_file(fname)
    content = payload.get("content", "")
    try:
        json.loads(content)
    except Exception as exc:
        raise HTTPException(400, f"JSON نامعتبر: {exc}")
    path.write_text(content, encoding="utf-8")
    LOG.emit("server", "info", f"تسک ذخیره شد → tasks/{fname}")
    return {"ok": True, "file": fname}


@app.post("/api/tasks/load_samples")
async def tasks_load_samples():
    """ساخت tasks/examples.json در صورت نبود (از نسخهٔ داخلی)."""
    path = TASKS_DIR / "examples.json"
    if path.exists():
        return {"ok": True, "created": False, "file": "examples.json"}
    data = json.loads((ROOT / "tasks" / "examples.json").read_text(encoding="utf-8")) \
        if (ROOT / "tasks" / "examples.json").exists() else {"tasks": []}
    if not data.get("tasks"):
        data = {"tasks": [{
            "name": "hello_panel",
            "description": "نمونهٔ ساخته‌شده از پنل — یک اعلان ویندوز",
            "steps": [{"type": "notify", "message": "سلام از پنل پارس‌ایجنت 👋"}],
        }]}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                    encoding="utf-8")
    return {"ok": True, "created": True, "file": "examples.json"}


@app.post("/api/tasks/run")
async def task_run(payload: dict = Body(...)):
    if payload.get("file"):
        path = _safe_file(payload["file"])
        if not path.exists():
            raise HTTPException(404, "فایل تسک پیدا نشد")
        data = json.loads(path.read_text(encoding="utf-8"))
        tasks = data.get("tasks", [data]) if "tasks" in data else [data]
        if payload.get("name"):
            tasks = [t for t in tasks if t.get("name") == payload["name"]] or tasks[:1]
        label = f"⚙ {payload['file']}" + (f" · {payload['name']}" if payload.get("name") else "")
    elif payload.get("task"):
        tasks = [payload["task"]]
        label = f"⚙ {tasks[0].get('name', 'تسک')}"
    else:
        raise HTTPException(400, "یا file بده یا task")

    for t in tasks:                                 # متغیرهای تعاملی از پنل نه
        t.pop("interactive_vars", None)

    def _run_all():
        eng = _get_engine()
        return [eng.run(t) for t in tasks]

    job = _new_job("task", label, _run_all)
    return _job_public(job)


# ---------- ضبط و ماکرو ----------
@app.post("/api/record/start")
async def record_start():
    try:
        _require_pynput()
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
    REC.start()
    return {"recording": True}


@app.post("/api/record/stop")
async def record_stop():
    macro = REC.stop()
    return {"recording": False,
            "macro": (macro or {}).get("meta", {})}


@app.get("/api/record/status")
async def record_status():
    return REC.status()


@app.get("/api/macros")
async def macros_index():
    return _macros_list()


@app.post("/api/macros/save")
async def macros_save(payload: dict = Body(...)):
    if REC.active:
        REC.stop()
    macro = REC.last_macro
    if not macro or not macro.get("events"):
        raise HTTPException(400, "رویدادی برای ذخیره نیست — اول ضبط کن")
    name = _safe_name(payload.get("name") or
                      f"macro-{datetime.now():%Y%m%d-%H%M%S}")
    (MACROS_DIR / f"{name}.json").write_text(
        json.dumps(macro, ensure_ascii=False, indent=2), encoding="utf-8")
    LOG.emit("recorder", "info", f"ماکرو «{name}» ذخیره شد "
                                 f"({len(macro['events'])} رخداد)")
    return {"ok": True, "name": name}


@app.post("/api/macros/delete")
async def macros_delete(payload: dict = Body(...)):
    name = _safe_name(payload.get("name") or "")
    path = MACROS_DIR / f"{name}.json"
    if not path.exists():
        raise HTTPException(404, "ماکرو پیدا نشد")
    path.unlink()
    LOG.emit("recorder", "info", f"ماکرو «{name}» حذف شد")
    return {"ok": True}


@app.post("/api/macros/play")
async def macros_play(payload: dict = Body(...)):
    name = _safe_name(payload.get("name") or "")
    path = MACROS_DIR / f"{name}.json"
    if not path.exists():
        raise HTTPException(404, "ماکرو پیدا نشد")
    try:
        macro = json.loads(path.read_text(encoding="utf-8"))
        events = macro.get("events", [])
    except Exception as exc:
        raise HTTPException(400, f"فایل ماکرو خراب است: {exc}")
    if not events:
        raise HTTPException(400, "این ماکرو خالی است")
    speed = float(payload.get("speed", 1.0))
    loop = int(payload.get("loop", 1))
    job = _new_job("macro", f"▶ پخش ماکرو «{name}» ×{speed:g}",
                   _run_macro, events, speed, loop,
                   via_worker=False, inject_id=True)
    return _job_public(job)


# ---------- کارها ----------
@app.get("/api/jobs")
async def jobs_index():
    return [_job_public(j, include_result=False) for j in _recent_jobs(20)]


@app.get("/api/jobs/{jid}")
async def job_get(jid: str):
    with _JOB_LOCK:
        job = JOBS.get(jid)
    if not job:
        raise HTTPException(404, "کار پیدا نشد")
    return _job_public(job, include_result=True)


@app.post("/api/jobs/cancel")
async def job_cancel(payload: dict = Body(...)):
    jid = payload.get("id")
    with _JOB_LOCK:
        job = JOBS.get(jid or "")
        if not job:
            raise HTTPException(404, "کار پیدا نشد")
        if not job["cancellable"]:
            raise HTTPException(400, "این کار قابل لغو نیست (تسک‌ها تا پایان اجرا می‌شوند)")
        job["cancel"] = True
    return {"ok": True}


# ---------- سیستم و دسکتاپ ----------
def _desktop_screenshot() -> dict:
    _require_input()
    img = pyautogui.screenshot()
    SHOTS_DIR.mkdir(parents=True, exist_ok=True)
    path = SHOTS_DIR / f"desktop_{datetime.now():%Y%m%d_%H%M%S}.png"
    img.save(path)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=68)
    return {"width": img.width, "height": img.height,
            "image": base64.b64encode(buf.getvalue()).decode(),
            "path": str(path)}


@app.post("/api/system/screenshot")
async def system_screenshot():
    try:
        return await asyncio.to_thread(_desktop_screenshot)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))


@app.post("/api/system/mouse")
async def system_mouse(payload: dict = Body(...)):
    if not HAVE_INPUT:
        raise HTTPException(503, "pyautogui نصب نیست")

    def _do():
        act = payload.get("action", "click")
        x, y = payload.get("x"), payload.get("y")
        btn = payload.get("button", "left")
        if act == "move":
            pyautogui.moveTo(int(x or 0), int(y or 0),
                              duration=float(payload.get("duration", 0.15)))
        elif act == "click":
            pyautogui.click(x=x, y=y, button=btn,
                            clicks=int(payload.get("clicks", 1)), interval=0.08)
        elif act == "double":
            pyautogui.doubleClick(x=x, y=y)
        elif act == "right":
            pyautogui.rightClick(x=x, y=y)
        elif act == "middle":
            pyautogui.middleClick(x=x, y=y)
        elif act == "drag":
            pyautogui.dragTo(int(x or 0), int(y or 0),
                             duration=float(payload.get("duration", 0.6)),
                             button=btn)
        elif act == "scroll":
            pyautogui.scroll(int(payload.get("clicks", -3)))
        elif act == "position":
            p = pyautogui.position()
            return {"x": p.x, "y": p.y}
        else:
            raise ValueError(f"action نامعتبر: {act}")
        p = pyautogui.position()
        return {"x": p.x, "y": p.y}

    return await asyncio.to_thread(_do)


@app.post("/api/system/keyboard")
async def system_keyboard(payload: dict = Body(...)):
    if not HAVE_INPUT:
        raise HTTPException(503, "pyautogui نصب نیست")

    def _do():
        act = payload.get("action", "type")
        if act == "type":
            _type_text_direct(payload.get("text", ""))
        elif act == "press":
            key = payload.get("key", "enter")
            pyautogui.press(_PAGUI_KEY.get(key, key),
                            presses=int(payload.get("times", 1)), interval=0.12)
        elif act == "hotkey":
            keys = payload.get("keys") or []
            if not keys:
                raise ValueError("keys خالی است")
            pyautogui.hotkey(*[_PAGUI_KEY.get(k, k) for k in keys])
        else:
            raise ValueError(f"action نامعتبر: {act}")
        return {"ok": True}

    try:
        return await asyncio.to_thread(_do)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))


def _sysinfo() -> dict:
    info = {
        "computer": _platform.node() or "-",
        "os": f"{_platform.system()} {_platform.release()}",
        "processor": _platform.processor() or _platform.machine(),
        "python": _platform.python_version(),
        "cpu_cores": os.cpu_count(),
        "agent_ok": AGENT_IMPORT_ERROR is None,
    }
    if psutil is not None:
        vm = psutil.virtual_memory()
        info.update({
            "ram_total_gb": round(vm.total / 1024 ** 3, 1),
            "ram_used_gb": round(vm.used / 1024 ** 3, 1),
            "ram_percent": vm.percent,
            "cpu_percent": psutil.cpu_percent(interval=0.4),
        })
        try:
            du = shutil.disk_usage(str(Path(os.path.abspath(os.sep))))
            info.update({"disk_total_gb": round(du.total / 1024 ** 3, 1),
                         "disk_free_gb": round(du.free / 1024 ** 3, 1)})
        except Exception:
            pass
    return info


@app.get("/api/system/info")
async def system_info():
    return await asyncio.to_thread(_sysinfo)


@app.post("/api/system/notify")
async def system_notify(payload: dict = Body(...)):
    title = payload.get("title") or "ParsAgent"
    message = payload.get("message") or ""
    if not message:
        raise HTTPException(400, "پیام خالی است")
    try:
        notify(title, message)
        return {"ok": True}
    except Exception as exc:
        raise HTTPException(500, f"اعلان نمایش داده نشد: {exc}")


@app.post("/api/system/open")
async def system_open(payload: dict = Body(...)):
    target = (payload.get("target") or "").strip()
    if not target:
        raise HTTPException(400, "مسیر/آدرس خالی است")
    try:
        if os.name == "nt":
            os.startfile(target)                     # noqa: S606
        else:
            subprocess.Popen(["xdg-open", target])
        return {"ok": True}
    except Exception as exc:
        raise HTTPException(500, f"باز نشد: {exc}")


@app.post("/api/system/cmd")
async def system_cmd(payload: dict = Body(...)):
    cmd = (payload.get("cmd") or "").strip()
    if not cmd:
        raise HTTPException(400, "دستور خالی است")

    def _do():
        p = subprocess.run(cmd, shell=True, capture_output=True,
                            timeout=min(int(payload.get("timeout", 60)), 300))
        out = (p.stdout or b"").decode("utf-8", "replace")
        err = (p.stderr or b"").decode("utf-8", "replace")
        return {"code": p.returncode,
                "output": (out + (("\n" + err) if err else "")).strip()[:20000]}

    return await asyncio.to_thread(_do)


@app.post("/api/system/lock")
async def system_lock():
    try:
        if os.name == "nt":
            import ctypes
            ctypes.windll.user32.LockWorkStation()
            return {"ok": True}
        raise RuntimeError("فقط روی ویندوز")
    except Exception as exc:
        raise HTTPException(500, f"قفل نشد: {exc}")


@app.post("/api/system/shutdown")
async def system_shutdown(payload: dict = Body(...)):
    delay_min = max(int(payload.get("delay_min", 1)), 1)
    p = subprocess.run(["shutdown", "/s", "/t", str(delay_min * 60)],
                       capture_output=True)
    LOG.emit("server", "warning",
             f"⏻ خاموشی سیستم تا {delay_min} دقیقهٔ دیگر زمان‌بندی شد")
    return {"ok": p.returncode == 0, "delay_min": delay_min}


@app.post("/api/system/abort_shutdown")
async def system_abort_shutdown():
    p = subprocess.run(["shutdown", "/a"], capture_output=True)
    LOG.emit("server", "info", "خاموشی لغو شد")
    return {"ok": p.returncode == 0}


# ---------- تنظیمات ----------
@app.get("/api/config")
async def config_get():
    path = ROOT / "config.json"
    content = path.read_text(encoding="utf-8") if path.exists() else "{}"
    return {"content": content, "path": str(path)}


@app.post("/api/config/save")
async def config_save(payload: dict = Body(...)):
    content = payload.get("content", "")
    try:
        json.loads(content)
    except Exception as exc:
        raise HTTPException(400, f"JSON نامعتبر: {exc}")
    (ROOT / "config.json").write_text(content, encoding="utf-8")
    LOG.emit("server", "info", "config.json ذخیره شد "
             "(برای اعمال کامل روی موتورهای باز، سرور را ری‌استارت کنید)")
    return {"ok": True}


# ---------- WebSocket لاگ زنده ----------
@app.websocket("/ws/logs")
async def ws_logs(ws: WebSocket):
    await ws.accept()
    LOG.clients.add(ws)
    try:
        await ws.send_text(json.dumps({
            "type": "hello", "version": APP_VERSION,
            "logs": list(LOG.history)[-120:],
            "jobs": [_job_public(j, include_result=False)
                     for j in _recent_jobs(15)],
            "recording": REC.status(),
        }, ensure_ascii=False))
        while True:
            await ws.receive_text()                 # keep-alive
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        LOG.clients.discard(ws)


# ---------- فایل‌های پنل (web/index.html) ----------
app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")


# --------------------------------------------------------------------------- #
# اجرای مستقیم: python server.py
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
