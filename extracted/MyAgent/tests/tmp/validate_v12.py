"""اعتبارسنجی ماژول‌های جدید (stealth / credentials / captcha / auto_login)
روی لینوکس سندباکس با stub — فقط برای wiring، روی ویندوز کاربر واقعی است.
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


# ---------- stubs ----------
pyautogui = mod("pyautogui")
for fn in ("moveTo", "click", "doubleClick", "rightClick", "middleClick",
           "dragTo", "scroll", "press", "hotkey", "typewrite", "keyDown",
           "keyUp", "mouseDown", "mouseUp", "screenshot"):
    setattr(pyautogui, fn, lambda *a, **k: None)

pynput = mod("pynput")
kb = mod("pynput.keyboard", Listener=mock.MagicMock(), Key=types.SimpleNamespace(name="x"))
ms = mod("pynput.mouse", Listener=mock.MagicMock())
pynput.keyboard = kb
pynput.mouse = ms
sys.modules["pynput.keyboard"] = kb
sys.modules["pynput.mouse"] = ms

pw = mod("playwright")
sapi = mod("playwright.sync_api")
sapi.BrowserContext = type("BrowserContext", (), {})
sapi.Page = type("Page", (), {})
sapi.TimeoutError = type("TimeoutError", (Exception,), {})
sapi.sync_playwright = mock.MagicMock()
pw.sync_api = sapi

mod("plyer", notification=types.SimpleNamespace(notify=lambda **k: None))
mod("pyperclip", copy=lambda t: None)

sys.path.insert(0, str(AGENT))

import json  # noqa: E402

cfg = json.loads((AGENT / "config.json").read_text(encoding="utf-8"))
assert "stealth" in cfg and "captcha" in cfg, "config sections missing"

from core.stealth import (LEVEL_PRESETS, build_stealth_js,  # noqa: E402
                           evaluate_probe, resolve_modules,
                           stealth_launch_args)

mods = resolve_modules(cfg["stealth"], cfg["browser"])
on = [k for k, v in mods.items() if v]
print("modules ON:", on)
assert set(LEVEL_PRESETS["standard"]) <= set(on), "standard level incomplete"
assert mods["webrtc_shield"] is False, "webrtc must be off without proxy"

js = build_stealth_js(cfg, "instagram")
assert js and "navigator" in js and "37446" in js
assert "__SEED__" not in js and "__CORES__" not in js and "__WEBGL" not in js
assert "SEED" in js  # مقدار عددی داخل اسکریپت
print("stealth js (instagram):", len(js), "chars")

# غیرفعال‌سازی با disable_for
cfg2 = json.loads(json.dumps(cfg))
cfg2["stealth"]["disable_for"] = ["instagram"]
assert build_stealth_js(cfg2, "instagram") == ""
# seed متفاوت برای پروفایل‌ها
assert build_stealth_js(cfg, "telegram") != js
# خاموش کلی
cfg3 = json.loads(json.dumps(cfg))
cfg3["stealth"]["enabled"] = False
assert build_stealth_js(cfg3, "instagram") == ""
# پروکسی → webrtc خودکار روشن
cfg4 = json.loads(json.dumps(cfg))
cfg4["browser"]["proxy"] = "http://127.0.0.1:8080"
mods4 = resolve_modules(cfg4["stealth"], cfg4["browser"])
assert mods4["webrtc_shield"] is True, "proxy must enable webrtc shield"
js4 = build_stealth_js(cfg4, "bale")
assert "RTCPeerConnection" in js4
# آرگومان‌های لانچ
args = stealth_launch_args(mods)
assert "--disable-blink-features=AutomationControlled" in args
print("launch args:", args)

# probe
checks = evaluate_probe({"webdriver": None, "plugins": 5, "chrome": True,
                         "platform": "Win32", "languages": "fa-IR,fa",
                         "renderer": "ANGLE (Intel, Intel(R) UHD Graphics 620)",
                         "cores": 8})
assert all(c["pass"] for c in checks), [c for c in checks if not c["pass"]]
checks2 = evaluate_probe({"webdriver": True, "plugins": 0, "chrome": False,
                          "platform": "", "languages": "",
                          "renderer": "SwiftShader", "cores": 2})
assert not any(c["pass"] for c in checks2)
print("probe: all-pass ✓ all-fail ✓")

from core.credentials import (FIELDS, clear_platform, get_platform,  # noqa: E402
                              masked, set_platform, totp_code)

code = totp_code("JBSWY3DPEHPK3PXP", t=1700000000)
assert len(code) == 6 and code.isdigit(), code
# تولید دوباره همان لحظه → همان کد (پایداری)
assert totp_code("JBSWY3DPEHPK3PXP", t=1700000000) == code
print("totp ok:", code)

rec = set_platform("instagram", {"username": "ped4am_test",
                                 "password": "secret123",
                                 "totp_secret": ""})
assert rec.get("username") == "ped4am_test" and "totp_secret" not in rec
assert get_platform("instagram").get("password") == "secret123"
m = masked()["instagram"]
assert m["username"] == "ped4am_test" and m["has_password"] is True \
       and "password" not in m, "رمز نباید لو برود"
# فرم خالی → username پاک می‌شود ولی رمز می‌ماند (merge semantics)
set_platform("instagram", {"username": "", "password": None})
m2 = masked()["instagram"]
assert m2["username"] == "" and m2["has_password"] is True
assert clear_platform("instagram") is True
assert clear_platform("instagram") is False
print("credentials store ok ✓")

from core.captcha import CaptchaSolver, detect_captcha  # noqa: E402

s = CaptchaSolver({"api_key": "", "provider": "2captcha"})
assert s.available is False
s2 = CaptchaSolver({"api_key": "K", "provider": "rucaptcha"})
assert s2.base == "https://rucaptcha.com" and s2.available
s3 = CaptchaSolver({"api_key": "K", "base_url": "https://x.example/"})
assert s3.base == "https://x.example"

# page ساختگی برای detect_captcha (بدون کپچا)
fake_page = mock.MagicMock()
fake_page.locator.return_value.count.return_value = 0
assert detect_captcha(fake_page) is None
# با iframe recaptcha → باید sitekey استخراج شود
fake_page2 = mock.MagicMock()
fake_page2.locator.return_value.count.return_value = 1
fake_page2.evaluate.return_value = "6Le-wvkSAAAAAPBMRTvw0Q4MuXq4"
cap = detect_captcha(fake_page2)
assert cap and cap["kind"] == "recaptcha" and cap["sitekey"].startswith("6Le")
print("captcha detect ok ✓")

# server.py import + route table
import server  # noqa: E402

routes = {r.path for r in server.app.routes}
for expected in ("/api/credentials", "/api/credentials/delete",
                 "/api/platform/login", "/api/stealth/probe",
                 "/api/stealth/test"):
    assert expected in routes, f"route missing: {expected}"
assert server.APP_VERSION == "1.2.0"
print("server routes ok ✓  version", server.APP_VERSION)

# platform catalog با has_creds
cat = server._platform_catalog()
assert len(cat) == 8 and all("has_creds" in p for p in cat)
print("catalog ok — sample:", cat[3]["id"], "has_creds:", cat[3]["has_creds"])

# auto_login: بدون اعتبارنامه باید خطای واضح بدهد
clear_platform("facebook")
clear_platform("instagram")
try:
    server._platform_auto_login("facebook")
    raise SystemExit("should have raised")
except RuntimeError as e:
    assert "ذخیره" in str(e)
print("auto_login no-creds error ok ✓")

# auto_login با اعتبارنامه + صفحهٔ stub — فلوی کامل
from platforms import PLATFORMS  # noqa: E402

set_platform("facebook", {"username": "me@test.com", "password": "pw1"})
calls = []


class StubPage:
    url = "https://www.facebook.com/"

    def __init__(self):
        self.context = mock.MagicMock()

    def goto(self, *a, **k):
        calls.append(("goto", a[0] if a else ""))

    def is_closed(self):
        return False

    def wait_for_selector(self, sel, *a, **k):
        if sel in ("input#email", "input#pass"):   # فیلدهای فرم فیسبوک
            return True
        raise Exception("no")


class StubEngine:
    def new_page(self):
        return StubPage()

    def goto(self, page, url, retries=3):
        calls.append(("goto", url))

    def exists(self, page, sel, timeout=0):
        # فرم کاربر هست؛ رمز هست؛ دکمهٔ submit هست؛ کد نه
        if sel.startswith("button#loginbutton"):
            return True
        if sel.startswith("button[type='submit']"):
            return False
        if "password" in sel:
            return True
        if "approval_code" in sel or "one-time-code" in sel:
            return False
        return sel.startswith("input#email")

    def type(self, page, sel, text, secret=False):
        calls.append(("type", sel, text[:4] + "…"))

    def click(self, page, sel, timeout=0):
        calls.append(("click", sel))

    def press(self, page, key):
        calls.append(("press", key))

    def human_pause(self, a=0, b=0):
        pass

    def export_session(self, page, name):
        calls.append(("export_session", name))

    def screenshot(self, page, tag):
        return "/tmp/x.png"


fb = PLATFORMS["facebook"](StubEngine(), cfg)
fb._page = StubPage()
fb.is_logged_in = lambda: False
result = fb.auto_login({"username": "me@test.com", "password": "pw1"}, None)
print("auto_login steps:", result["steps"])
assert any(c[0] == "type" and "email" in c[1] for c in calls), "user typed"
assert any(c[0] == "type" and "pass" in c[1] for c in calls), "pass typed"
submitted = any(c[0] == "click" and "loginbutton" in c[1] for c in calls) \
    or any(c[0] == "press" and c[1] == "Enter" for c in calls)
assert submitted, "form submitted"
assert result["needs"] is None
clear_platform("facebook")

# LOGIN_SELECTORS پوشش همهٔ ۸ پلتفرم
from platforms.base import LOGIN_SELECTORS  # noqa: E402

for pid in PLATFORMS:
    assert pid in LOGIN_SELECTORS, f"no login selectors: {pid}"
    assert LOGIN_SELECTORS[pid]["user"] and LOGIN_SELECTORS[pid]["submit"]
print("login selectors cover all 8 platforms ✓")

print("\nALL VALIDATION PASSED ✅")
