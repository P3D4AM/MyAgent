# -*- coding: utf-8 -*-
"""اعتبارسنجی v2.7.0 — جریان ورود، ناوبری مقاوم و زنجیرهٔ مرورگر (با ماک، بدون مرورگر واقعی)."""
import asyncio
import sys
import time as _time
import types
from pathlib import Path

sys.path.insert(0, "/home/z/my-project/parsagent")

import panel_server as ps  # noqa

PASS, FAIL = [], []


def check(name, cond, extra=""):
    (PASS if cond else FAIL).append(name)
    print(("✅" if cond else "❌") + f" {name}" + (f"  [{extra}]" if extra and not cond else ""))


# ---------------------------------------------------------------- ماک‌ها
class FakeLoc:
    def __init__(self, page, sel):
        self.page, self.sel = page, sel

    @property
    def first(self):
        return self

    async def count(self):
        return 1 if self.page._visible(self.sel) else 0

    async def is_visible(self):
        return self.page._visible(self.sel)

    async def click(self, timeout=3000):
        await self.page._click(self.sel)

    async def fill(self, value, timeout=3000):
        self.page.typed.append((self.sel, value))

    async def bounding_box(self):
        return {"x": 100.0, "y": 100.0, "width": 120.0, "height": 30.0}


class FakeMouse:
    async def move(self, x, y):
        pass

    async def wheel(self, dx, dy):
        pass


class FakeKeyboard:
    def __init__(self, page):
        self.page = page

    async def type(self, text):
        self.page.typed.append((self.page.current_sel, text))


def go_to(url):
    async def _f(page):
        page.url = url
    return _f


class FakePage:
    """صفحهٔ ساختگی — رفتار با اسکریپت set_script تعیین می‌شود."""

    def __init__(self, script):
        self.script = script  # {"goto": Exc|None, "fields": {sel: bool}, "on_click": {sel: fn}, "start_url": ...}
        self.url = script.get("start_url", "about:blank")
        self.typed = []
        self.mouse = FakeMouse()
        self.keyboard = FakeKeyboard(self)
        self.current_sel = None
        self.goto_calls = 0

    def _visible(self, sel):
        f = self.script.get("fields", {})
        return bool(f.get(sel, False))

    async def _click(self, sel):
        fn = self.script.get("on_click", {}).get(sel)
        if fn:
            await fn(self)

    def locator(self, sel):
        return FakeLoc(self, sel)

    async def goto(self, url, wait_until=None, timeout=None):
        self.goto_calls += 1
        self.url = self.script.get("after_goto", self.url)
        beh = self.script.get("goto")
        if beh is not None:
            raise beh

    async def click(self, sel, timeout=None):
        self.current_sel = sel
        await self._click(sel)

    async def title(self):
        return self.script.get("title", "Instagram")

    async def inner_text(self, sel):
        return self.script.get("body", "")


def make_sess(platform, page):
    s = types.SimpleNamespace()
    s.platform = platform
    async def ensure():
        return page
    s.ensure = ensure
    return s


# ---------------------------------------------------------------- زمان فشرده
real_sleep = asyncio.sleep
real_monotonic = _time.monotonic
_n = {"i": 0}


def fake_monotonic():
    _n["i"] += 1
    return 1000.0 + _n["i"] * 5.0


async def fake_sleep(s):
    return None


CREDS = {"instagram": {"username": "myuser", "password": "mypass"},
         "twitter": {"username": "twuser", "password": "twpass"},
         "telegram": {"username": "+989120000000"}}
ps.creds = lambda: CREDS

IG_LOGIN = "https://www.instagram.com/accounts/login/"


async def run(name, platform, script, creds_patch=None):
    page = FakePage(script)
    old = ps.creds
    if creds_patch is not None:
        ps.creds = lambda: creds_patch
    try:
        res = await ps._generic_login(make_sess(platform, page), {})
        return res
    except Exception as e:
        return {"ok": False, "message": f"EXC: {e}"}
    finally:
        ps.creds = old


async def main():
    _time.monotonic = fake_monotonic
    asyncio.sleep = fake_sleep
    try:
        await all_tests()
    finally:
        _time.monotonic = real_monotonic
        asyncio.sleep = real_sleep


async def all_tests():
    # ---------- ۱) goto مقاوم
    class PG:
        def __init__(self, fails):
            self.n = fails
            self.url = "x"

        async def goto(self, url, **kw):
            if self.n > 0:
                self.n -= 1
                raise Exception("Page.goto: net::ERR_CONNECTION_CLOSED at https://www.instagram.com/")
    pg = PG(2)
    try:
        await ps.goto(pg, "https://www.instagram.com/")
        check("goto: دو خطا → تلاش سوم موفق", True)
    except Exception as e:
        check("goto: دو خطا → تلاش سوم موفق", False, str(e))
    pg = PG(99)
    try:
        await ps.goto(pg, "https://www.instagram.com/")
        check("goto: همیشه خطا → RuntimeError با راهنما", False, "no raise")
    except RuntimeError as e:
        m = str(e)
        check("goto: همیشه خطا → پیام فارسی (تحریم/پروکسی/10809)",
              "ERR_CONNECTION_CLOSED" in m and "تحریم" in m and "پروکسی" in m and "10809" in m, m)
    # ---------- ۲) اینستاگرام — مسیر موفق
    script = {"start_url": IG_LOGIN, "after_goto": IG_LOGIN,
              "fields": {"input[name='username']": True, "input[type='password']": True,
                         "button[type='submit']": True},
              "on_click": {"button[type='submit']": go_to("https://www.instagram.com/")}}
    r = await run("ig-happy", "instagram", script)
    check("اینستاگرام موفق: ورود انجام شد", r.get("ok") and "ورود انجام شد" in r["message"], str(r))
    page = FakePage(script)
    await ps._generic_login(make_sess("instagram", page), {})
    joined = "".join(t[1] for t in page.typed)
    check("اینستاگرام موفق: یوزرنیم و رمز واقعاً تایپ شدند", "myuser" in joined and "mypass" in joined, joined)

    # ---------- ۳) خطای شبکهٔ کاربر (ERR_CONNECTION_CLOSED) — همان باگ امروز
    script = {"start_url": IG_LOGIN, "goto": Exception("Page.goto: net::ERR_CONNECTION_CLOSED at https://www.instagram.com/ Call log: - navigating")}
    r = await run("ig-conn", "instagram", script)
    check("باگ کاربر: ERR_CONNECTION_CLOSED → پیام راهنما (نه «فیلد دیده نشد»)",
          not r.get("ok") and "تحریم" in r["message"] and "پروکسی" in r["message"], str(r))

    # ---------- ۴) صفحه می‌آید ولی فیلد نیست (با عنوان صفحه)
    script = {"start_url": IG_LOGIN, "after_goto": IG_LOGIN, "fields": {},
              "title": "Login • Instagram", "body": ""}
    r = await run("ig-nofield", "instagram", script)
    check("فیلد نیست → پیام «فیلد ورود دیده نشد» + عنوان صفحه",
          not r.get("ok") and "فیلد ورود دیده نشد" in r["message"] and "عنوان صفحه" in r["message"], str(r))

    # ---------- ۵) از قبل وارد شده
    script = {"start_url": "https://www.instagram.com/", "after_goto": "https://www.instagram.com/",
              "fields": {"button:has-text('Log in')": True}}
    r = await run("ig-loggedin", "instagram", script)
    check("از قبل وارد شده → تشخیص و پیام", r.get("ok") and "از قبل وارد" in r["message"], str(r))

    # ---------- ۶) بنر کوکی
    state = {"cookie_open": True}

    async def close_banner(page):
        state["cookie_open"] = False
        page.script["fields"]["input[name='username']"] = True
    script = {"start_url": IG_LOGIN, "after_goto": IG_LOGIN,
              "fields": {"button:has-text('Allow all cookies')": True, "input[name='username']": False,
                          "input[type='password']": True, "button[type='submit']": True},
              "on_click": {"button:has-text('Allow all cookies')": close_banner,
                           "button[type='submit']": go_to("https://www.instagram.com/")}}
    r = await run("ig-cookie", "instagram", script)
    check("بنر کوکی بسته شد و ورود ادامه یافت",
          r.get("ok") and "ورود انجام شد" in r["message"] and not state["cookie_open"], str(r))

    # ---------- ۷) رمز نادرست
    script = {"start_url": IG_LOGIN, "after_goto": IG_LOGIN,
              "fields": {"input[name='username']": True, "input[type='password']": True, "button[type='submit']": True},
              "body": "Sorry, your password was incorrect. Please try again."}
    r = await run("ig-badpass", "instagram", script)
    check("رمز نادرست → پیام مشخص", not r.get("ok") and "درست نیست" in r["message"], str(r))

    # ---------- ۸) توییتر دومرحله‌ای
    async def next_step(page):
        page.script["fields"]["input[type='password']"] = True
    script = {"start_url": "https://x.com/i/flow/login", "after_goto": "https://x.com/i/flow/login",
              "fields": {"input[autocomplete='username']": True, "button:has-text('Next')": True,
                         "input[type='password']": False, "button[data-testid='LoginForm_Login_Button']": True},
              "on_click": {"button:has-text('Next')": next_step,
                           "button[data-testid='LoginForm_Login_Button']": go_to("https://x.com/home")}}
    r = await run("tw", "twitter", script)
    check("توییتر: یوزرنیم → بعدی → رمز → ورود", r.get("ok") and "فرم X پر شد" in r["message"] and "دکمهٔ ورود زده شد" in r["message"], str(r))

    # ---------- ۹) تلگرام (OTP)
    script = {"start_url": "https://web.telegram.org", "after_goto": "https://web.telegram.org",
              "fields": {"input[name='phone_number']": True, "button:has-text('Next')": True}}
    r = await run("tg", "telegram", script)
    check("تلگرام: شماره تایپ + پیام کد پیامکی", r.get("ok") and "شماره تلفن تایپ شد" in r["message"] and "کد پیامکی" in r["message"], str(r))

    # ---------- ۱۰) بدون اطلاعات ذخیره‌شده
    r = await run("nocred", "instagram", {"start_url": IG_LOGIN, "after_goto": IG_LOGIN, "fields": {}},
                  creds_patch={})
    check("بدون اطلاعات ذخیره‌شده → راهنمای تنظیمات", r.get("ok") and "ذخیره نشده" in r["message"], str(r))

    # ---------- ۱۱) زنجیرهٔ مرورگر — با Playwright ماک (قطعی)
    class FakeCtx:
        pages = []

        async def add_init_script(self, s):
            pass

        async def new_page(self):
            return types.SimpleNamespace(url="about:blank")

    class FakeEngine:
        def __init__(self, fail_for=()):
            self.fail_for = fail_for
            self.kws = []

        async def launch_persistent_context(self, **kw):
            self.kws.append(kw)
            ch = kw.get("channel", "chromium")
            if ch in self.fail_for:
                raise Exception(f"BrowserType.launch_persistent_context: Executable doesn't exist at ...\\{ch}-1243\\...")
            return FakeCtx()

    class FakePW:
        def __init__(self, chromium, firefox):
            self.chromium, self.firefox = chromium, firefox

        async def start(self):
            return self

        async def stop(self):
            pass

    import sys as _sys
    real_pw_mod = _sys.modules.get("playwright.async_api")
    fake_pw_mod = types.ModuleType("playwright.async_api")
    _sys.modules["playwright.async_api"] = fake_pw_mod

    calls = []

    async def no_install(which):
        calls.append(which)
        return "شبیه‌سازی: اینترنت نیست"

    async def ok_install(which):
        calls.append(which)
        return None

    real_ai = ps._auto_install_browser
    st = {"general": {"headless": True, "channel": "chrome", "proxy": "", "start_maximized": False},
          "stealth": {"enabled": False, "per_platform": {}}}
    ps.settings = lambda: st
    ps._auto_install_browser = no_install
    try:
        # الف) chrome غایب → msedge باز می‌شود
        eng = FakeEngine(("chrome",))
        fake_pw_mod.async_playwright = lambda: FakePW(eng, FakeEngine())
        s = ps.BotSession("instagram")
        page = await s.ensure()
        check("زنجیرهٔ مرورگر: chrome غایب → جایگزین باز شد", page is not None and s.context is not None)
        check("زنجیرهٔ مرورگر: پس از شکست chrome، msedge امتحان شد", len(eng.kws) == 2 and eng.kws[1].get("channel") == "msedge",
              str([k.get("channel", "chromium") for k in eng.kws]))
        # ب) همه غایب و اینترنت نیست → خطای راهنمای فارسی + تلاش نصب خودکار
        eng2 = FakeEngine(("msedge", "chrome", "chromium"))
        fake_pw_mod.async_playwright = lambda: FakePW(eng2, FakeEngine())
        st["general"]["channel"] = "auto"
        s2 = ps.BotSession("instagram")
        try:
            await s2.ensure()
            check("همه غایب → خطای راهنما", False, "no raise")
        except RuntimeError as e:
            check("همه غایب → خطای راهنمای فارسی",
                  "باز شدن مرورگر ممکن نشد" in str(e) and "خودکار" in str(e) and "npmmirror" in str(e), str(e))
        check("نصب خودکار chromium با آینه صدا زده شد", calls and calls[-1] == "chromium", str(calls))
        # ج) همه غایب ولی نصب خودکار موفق → دوباره تلاش و موفق
        eng3 = FakeEngine(("msedge", "chrome"))
        eng3.attempt = 0
        async def launch2(**kw):
            eng3.kws.append(kw)
            eng3.attempt += 1
            ch = kw.get("channel", "chromium")
            if ch in eng3.fail_for:
                raise Exception("BrowserType.launch_persistent_context: Executable doesn't exist at ...chromium-1243...")
            return FakeCtx()
        eng3.launch_persistent_context = launch2
        ps._auto_install_browser = ok_install
        fake_pw_mod.async_playwright = lambda: FakePW(eng3, FakeEngine())
        s3 = ps.BotSession("instagram")
        p3 = await s3.ensure()
        check("نصب خودکار موفق → دوباره باز و موفق", p3 is not None and s3.context is not None and "chromium" in calls)
        # د) پروکسی دستی → kw
        eng4 = FakeEngine()
        fake_pw_mod.async_playwright = lambda: FakePW(eng4, FakeEngine())
        st["general"]["channel"] = "auto"
        st["general"]["proxy"] = "127.0.0.1:8080"
        await ps.BotSession("instagram").ensure()
        check("پروکسی بدون اسکیم → http در kw",
              eng4.kws and eng4.kws[-1].get("proxy") == {"server": "http://127.0.0.1:8080"}, str(eng4.kws[-1].get("proxy")))
        # هـ) فایرفاکس از p.firefox و locale
        eng5 = FakeEngine()
        fake_pw_mod.async_playwright = lambda: FakePW(FakeEngine(), eng5)
        st["general"]["channel"] = "firefox"
        st["general"]["proxy"] = ""
        await ps.BotSession("instagram").ensure()
        check("firefox → از p.firefox باز شد", eng5.kws and "channel" not in eng5.kws[-1], str(eng5.kws[-1].get("channel")))
        # و) پروکسی نرمال
        check("پروکسی بدون اسکیم → http", ps._norm_proxy("127.0.0.1:8080") == "http://127.0.0.1:8080")
        check("پروکسی socks دست‌نخورده", ps._norm_proxy("socks5://127.0.0.1:10808") == "socks5://127.0.0.1:10808")
        check("پروکسی خالی → None", ps._norm_proxy("") is None)
    finally:
        ps._auto_install_browser = real_ai
        if real_pw_mod is not None:
            _sys.modules["playwright.async_api"] = real_pw_mod
        else:
            _sys.modules.pop("playwright.async_api", None)

    # ---------- ۱۲) جدول LOGIN_FLOW کلیدها
    ok = True
    for pid in ps.PLAT_IDS:
        f = ps.LOGIN_FLOW.get(pid)
        ok = ok and f and f.get("user")
    check("LOGIN_FLOW برای هر ۷ پلتفرم تعریف شده", ok)
    check("زنجیره‌ها: auto=msedge→chrome→chromium", ps.BROWSER_CHAINS["auto"] == ["msedge", "chrome", "chromium"])

    print(f"\n===== {len(PASS)} PASS / {len(FAIL)} FAIL =====")
    if FAIL:
        print("FAILED:", *FAIL, sep="\n  - ")
        sys.exit(1)


asyncio.run(main())
