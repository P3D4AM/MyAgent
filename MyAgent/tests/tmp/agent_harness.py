"""Test harness — اجرای server.py پارس‌ایجنت روی لینوکس با ماژول‌های stub.

فقط برای اعتبارسنجی wiring در سندباکس؛ روی ویندوز کاربر، کتابخانه‌های
واقعی نصب‌اند و این فایل لازم نیست.
"""
import sys
import types
import unittest.mock as mock
from pathlib import Path

AGENT = Path("/home/z/my-project/agent")


def mod(name: str, **attrs):
    m = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(m, k, v)
    sys.modules[name] = m
    return m


# ---------- pyautogui ----------
class _Jpeg:
    def save(self, buf, format=None, quality=None):
        if hasattr(buf, "write"):
            buf.write(b"\xff\xd8\xff\xd9")  # fake jpeg marker
        return None


class _Img(_Jpeg):
    width, height = 800, 600


pyautogui = mod("pyautogui")
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05
pyautogui.screenshot = lambda *a, **k: _Img()
for fn in ("moveTo", "click", "doubleClick", "rightClick", "middleClick",
           "dragTo", "scroll", "press", "hotkey", "typewrite", "keyDown",
           "keyUp", "mouseDown", "mouseUp"):
    setattr(pyautogui, fn, lambda *a, **k: None)
pyautogui.position = lambda: types.SimpleNamespace(x=10, y=20)

# ---------- pynput ----------
pynput = mod("pynput")
kb = mod("pynput.keyboard", Listener=mock.MagicMock(), Key=types.SimpleNamespace(name="x"))
ms = mod("pynput.mouse", Listener=mock.MagicMock())
pynput.keyboard = kb
pynput.mouse = ms
sys.modules["pynput.keyboard"] = kb
sys.modules["pynput.mouse"] = ms

# ---------- playwright ----------
pw = mod("playwright")
sapi = mod("playwright.sync_api")
sapi.BrowserContext = type("BrowserContext", (), {})
sapi.Page = type("Page", (), {})
sapi.TimeoutError = type("TimeoutError", (Exception,), {})
sapi.sync_playwright = mock.MagicMock()
pw.sync_api = sapi

# ---------- plyer / pyperclip ----------
mod("plyer", notification=types.SimpleNamespace(notify=lambda **k: None))
mod("pyperclip", copy=lambda t: None)

# ---------- اجرای سرور ----------
sys.path.insert(0, str(AGENT))
import server  # noqa: E402

if __name__ == "__main__":
    import uvicorn
    print("HARNESS: serving on 127.0.0.1:8799")
    uvicorn.run(server.app, host="127.0.0.1", port=8799, log_level="warning")
