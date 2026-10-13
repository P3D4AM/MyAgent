"""Desktop-level input controller — real mouse & keyboard simulation on Windows.

Built on top of PyAutoGUI with production conveniences:

  * human-like jitter and randomized delays between every action
  * failsafe: slam the mouse into the top-left corner to abort instantly
  * image-based UI location (screenshot matching) for apps without APIs
  * screenshot helpers for debugging and vision pipelines

Use this engine when the target is a native Windows app, a game, or a website
that must be driven exactly like a human sits in front of the machine.
For pure web automation prefer the (faster, non-intrusive) BrowserEngine.
"""

import random
import time
from pathlib import Path
from typing import List, Optional, Tuple

import pyautogui

from core.logger import get_logger

log = get_logger("desktop")

# Global safety settings
pyautogui.FAILSAFE = True        # move mouse to screen corner (0,0) to panic-abort
pyautogui.PAUSE = 0.05           # default pause inserted between pyautogui calls


class SystemController:
    """The 'hands' of the agent — low-level desktop input automation."""

    def __init__(
        self,
        human: bool = True,
        min_delay: float = 0.25,
        max_delay: float = 0.9,
    ):
        self.human = human
        self.min_delay = min_delay
        self.max_delay = max_delay

    # ------------------------------------------------------------------ #
    # humanization helpers
    # ------------------------------------------------------------------ #
    def human_pause(self, min_s: Optional[float] = None, max_s: Optional[float] = None) -> None:
        """Sleep a random interval so actions don't fire at machine speed."""
        if not self.human:
            return
        lo = min_s if min_s is not None else self.min_delay
        hi = max_s if max_s is not None else self.max_delay
        time.sleep(random.uniform(lo, hi))

    @staticmethod
    def _jitter(x: int, y: int, amount: int = 4) -> Tuple[int, int]:
        """Tiny random offset so consecutive clicks never land on the same pixel."""
        return (
            x + random.randint(-amount, amount),
            y + random.randint(-amount, amount),
        )

    # ------------------------------------------------------------------ #
    # mouse
    # ------------------------------------------------------------------ #
    def move_to(self, x: int, y: int, duration: Optional[float] = None) -> None:
        """Move the cursor; duration=None + human mode gives natural easing."""
        if self.human and duration is None:
            duration = random.uniform(0.25, 0.7)
        pyautogui.moveTo(x, y, duration=duration)
        log.debug("move -> (%s, %s)", x, y)

    def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: str = "left",
        clicks: int = 1,
        interval: float = 0.12,
        human: bool = True,
    ) -> None:
        """Click at position (or current cursor when x is None) with jitter."""
        if x is not None and y is not None:
            if human:
                self.move_to(x, y)
                x, y = self._jitter(int(x), int(y))
            pyautogui.click(x=x, y=y, clicks=clicks, interval=interval, button=button)
        else:
            pyautogui.click(clicks=clicks, interval=interval, button=button)
        log.info("click (%s, %s) button=%s clicks=%s", x, y, button, clicks)
        self.human_pause(0.15, 0.5)

    def double_click(self, x: Optional[int] = None, y: Optional[int] = None) -> None:
        self.click(x, y, clicks=2)

    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> None:
        self.click(x, y, button="right")

    def drag(
        self,
        x1: int, y1: int, x2: int, y2: int,
        duration: float = 0.8,
        button: str = "left",
    ) -> None:
        """Press, drag and release — used for sliders, file drops, canvas apps."""
        pyautogui.moveTo(x1, y1, duration=duration / 3)
        pyautogui.drag(x2 - x1, y2 - y1, duration=duration, button=button)
        log.info("drag (%s,%s) -> (%s,%s)", x1, y1, x2, y2)

    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """Positive scrolls up, negative scrolls down."""
        pyautogui.scroll(clicks, x=x, y=y)
        log.info("scroll %s", clicks)

    @staticmethod
    def position() -> Tuple[int, int]:
        return pyautogui.position()

    @staticmethod
    def screen_size() -> Tuple[int, int]:
        return pyautogui.size()

    # ------------------------------------------------------------------ #
    # keyboard
    # ------------------------------------------------------------------ #
    def type_text(self, text: str, interval: Optional[float] = None) -> None:
        """Type as a human: randomized per-character delay."""
        if interval is None:
            interval = random.uniform(0.03, 0.09) if self.human else 0.01
        pyautogui.typewrite(text, interval=interval)
        log.info("typed %s chars", len(text))

    def hotkey(self, *keys: str) -> None:
        """e.g. hotkey('ctrl', 'shift', 't') — order preserved, released reversed."""
        pyautogui.hotkey(*keys)
        log.info("hotkey %s", "+".join(keys))

    def press(self, key: str, times: int = 1, interval: float = 0.15) -> None:
        pyautogui.press(key, presses=times, interval=interval)
        log.info("press %s x%s", key, times)

    # ------------------------------------------------------------------ #
    # vision-based location (works on ANY app — no API needed)
    # ------------------------------------------------------------------ #
    def screenshot(self, path: str = "data/shot.png", region: Optional[Tuple] = None) -> str:
        """Save a screenshot; used for debugging, logs and image matching."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        pyautogui.screenshot(str(p), region=region)
        log.info("screenshot -> %s", p)
        return str(p)

    def locate(
        self,
        image: str,
        confidence: float = 0.85,
        grayscale: bool = True,
    ) -> Optional[Tuple[int, int]]:
        """Find `image` (png of a UI element) on screen → center coordinates.

        Requires `pip install opencv-python` for confidence matching.
        Returns None when not found — never raises.
        """
        try:
            box = pyautogui.locateCenterOnScreen(
                image, confidence=confidence, grayscale=grayscale
            )
            return (int(box.x), int(box.y)) if box else None
        except Exception as exc:  # image missing / opencv absent
            log.debug("locate failed for %s: %s", image, exc)
            return None

    def locate_all(self, image: str, confidence: float = 0.85) -> List[Tuple[int, int]]:
        try:
            return [
                (int(b.x), int(b.y))
                for b in pyautogui.locateAllOnScreen(image, confidence=confidence)
            ]
        except Exception:
            return []

    def click_image(self, image: str, confidence: float = 0.85, retries: int = 3) -> bool:
        """Locate an element by picture and click it. Retries with fresh shots."""
        for attempt in range(1, retries + 1):
            pos = self.locate(image, confidence=confidence)
            if pos:
                self.click(*pos)
                return True
            log.warning("click_image: %s not found (try %s/%s)", image, attempt, retries)
            self.human_pause(0.5, 1.2)
        return False
