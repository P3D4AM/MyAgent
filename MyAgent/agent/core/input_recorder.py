"""Global input recorder & macro player — record once, replay forever.

Listens to real mouse/keyboard activity with `pynput`, stores the event
timeline as a JSON macro, and replays it through PyAutoGUI while keeping
the original rhythm (or a scaled version of it).

Hotkeys while a recording is live:
    F9  → finish recording & save
    F10 → emergency abort without saving

Macro JSON format (one event per line concept, stored as a list):

    {
      "meta":    {"version": 1, "recorded_at": "...", "duration": 12.4},
      "events": [
        {"t": 0.000, "type": "move",    "x": 120, "y": 340},
        {"t": 0.812, "type": "click",   "x": 120, "y": 340, "button": "left", "pressed": true},
        {"t": 1.203, "type": "key",      "key": "a", "pressed": true},
        {"t": 1.301, "type": "scroll",   "dx": 0, "dy": -3}
      ]
    }
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pynput import keyboard, mouse

from core.logger import get_logger
from core.system_controller import SystemController

log = get_logger("recorder")

MOVE_SAMPLE_HZ = 40          # capture at most 40 move events per second


class InputRecorder:
    """Records global mouse & keyboard events into a JSON macro."""

    def __init__(self, out_path: str = "macros/macro.json"):
        self.out_path = Path(out_path)
        self.out_path.parent.mkdir(parents=True, exist_ok=True)
        self.events: List[Dict[str, Any]] = []
        self._t0 = 0.0
        self._last_move = 0.0
        self._running = False

    # -- pynput callbacks ------------------------------------------------
    def _now(self) -> float:
        return round(time.monotonic() - self._t0, 4)

    def _on_move(self, x: int, y: int) -> None:
        t = time.monotonic()
        if t - self._last_move < 1.0 / MOVE_SAMPLE_HZ:
            return
        self._last_move = t
        self.events.append({"t": self._now(), "type": "move", "x": x, "y": y})

    def _on_click(self, x: int, y: int, button, pressed: bool) -> None:
        self.events.append({
            "t": self._now(), "type": "click", "x": x, "y": y,
            "button": button.name, "pressed": pressed,
        })

    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        self.events.append({
            "t": self._now(), "type": "scroll", "x": x, "y": y, "dx": dx, "dy": dy,
        })

    def _on_key(self, key, pressed: bool) -> None:
        try:
            name = key.char if hasattr(key, "char") and key.char else key.name
        except Exception:
            name = str(key)
        self.events.append({"t": self._now(), "type": "key", "key": name, "pressed": pressed})

    # -- public API -------------------------------------------------------
    def record(self) -> Path:
        """Block until F9/F10, then write the macro file and return its path."""
        stop_flag = {"save": False}

        def _hotkey_save():
            stop_flag["save"] = True

        log.info("● RECORDING — press [F9] to stop & save, [F10] to abort")
        self._t0 = time.monotonic()
        self._running = True

        mouse_listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll,
        )
        key_listener = keyboard.Listener(on_press=lambda k: self._on_key(k, True),
                                          on_release=lambda k: self._on_key(k, False))
        hotkeys = keyboard.GlobalHotKeys({
            "<f9>": _hotkey_save,
            "<f10>": lambda: stop_flag.update(save=False, abort=True),
        })

        mouse_listener.start()
        key_listener.start()
        hotkeys.start()

        try:
            while not stop_flag.get("save") and not stop_flag.get("abort"):
                time.sleep(0.05)
        finally:
            self._running = False
            mouse_listener.stop()
            key_listener.stop()
            hotkeys.stop()

        if stop_flag.get("abort") or not self.events:
            log.warning("recording aborted (%s events discarded)", len(self.events))
            return self.out_path

        self._save()
        return self.out_path

    def _save(self) -> None:
        macro = {
            "meta": {
                "version": 1,
                "recorded_at": datetime.now().isoformat(timespec="seconds"),
                "duration": self._now(),
                "events": len(self.events),
            },
            "events": self.events,
        }
        self.out_path.write_text(json.dumps(macro, ensure_ascii=False, indent=2), encoding="utf-8")
        log.info("✔ saved %s events (%.1fs) → %s",
                 len(self.events), self._now(), self.out_path)


class MacroPlayer:
    """Replays a recorded macro through the SystemController."""

    def __init__(self, controller: Optional[SystemController] = None):
        self.ctrl = controller or SystemController()

    def load(self, path: str) -> Dict[str, Any]:
        return json.loads(Path(path).read_text(encoding="utf-8"))

    def play(self, path: str, speed: float = 1.0, loop: int = 1) -> None:
        """`speed=2.0` replays twice as fast; timing ratio is preserved."""
        macro = self.load(path)
        events: List[Dict[str, Any]] = macro["events"]
        if not events:
            log.warning("macro %s is empty — nothing to play", path)
            return

        for i in range(loop):
            log.info("▶ playing %s (round %s/%s, %s events, speed x%s)",
                     path, i + 1, loop, len(events), speed)
            self._run_timeline(events, speed)
        log.info("✔ macro finished — %s round(s)", loop)

    def _run_timeline(self, events: List[Dict[str, Any]], speed: float) -> None:
        prev_t = 0.0
        for ev in events:
            wait = (ev["t"] - prev_t) / max(speed, 0.05)
            if wait > 0:
                time.sleep(wait)
            prev_t = ev["t"]
            self._dispatch(ev)

    def _dispatch(self, ev: Dict[str, Any]) -> None:
        etype = ev["type"]
        if etype == "move":
            self.ctrl.move_to(ev["x"], ev["y"], duration=0)
        elif etype == "click":
            if ev.get("pressed"):
                self.ctrl.click(ev["x"], ev["y"], button=ev.get("button", "left"),
                                human=False)
        elif etype == "key":
            key = ev["key"]
            if key is None:
                return
            if len(key) == 1:
                self.ctrl.type_text(key, interval=0.0)
            else:  # special key: enter, space, ctrl_l ...
                self.ctrl.press(key)
        elif etype == "scroll":
            self.ctrl.scroll(int(ev.get("dy", 0)))
