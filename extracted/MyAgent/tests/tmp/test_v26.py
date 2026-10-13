# -*- coding: utf-8 -*-
"""تست E2E واقعی نسخهٔ ۲.۶.۰ — سه باگ گزارش‌شدهٔ کاربر:
۱) رفع خطای نصب نبودن کرومیوم / انتخاب مرورگر (کانال پاس داده شود + firefox/chromium)
۲) ورود خودکار کامل: نام کاربری + رمز + کلیک دکمهٔ ورود (هر ۷ پلتفرم؛ اینجا ۳ الگو)
۳) «باز کردن سایت» هم باید خودکار وارد شود اگر فرم ورود ببیند و اطلاعات ذخیره باشد

اجرا:  python3 tests/tmp/test_v26.py
"""
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PARS = os.path.join(ROOT, "parsagent")
PORT = 8799
BASE = f"http://127.0.0.1:{PORT}"

PASS, FAIL = [], []


def check(name: str, cond: bool, extra: str = ""):
    (PASS if cond else FAIL).append(name)
    print(("  ✅ " if cond else "  ❌ ") + name + (f"  ← {extra}" if extra and not cond else ""))


def api(path, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode())


def wait_ready(sec=30):
    for _ in range(sec * 4):
        try:
            api("/api/ready")
            return True
        except Exception:
            time.sleep(0.25)
    return False


def main():
    # ── پاک‌سازی وضعیت تست قبلی (پروفایل‌ها/کانفیگ) ───────────────
    for d in ("config", "profiles", "macros", "media"):
        p = os.path.join(PARS, d)
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)

    # ── صفحات لاگین شبیه‌سازی‌شده ──────────────────────────────────
    pages = subprocess.Popen([sys.executable, os.path.join(HERE, "v26_pages.py")])
    # ── سرور واقعی پنل (با URLهای ورود لوکال) ────────────────────
    env = {**os.environ, "PANEL_PORT": str(PORT), "PYTHONUNBUFFERED": "1"}
    server = subprocess.Popen([sys.executable, os.path.join(HERE, "v26_server.py")],
                               cwd=PARS, env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, encoding="utf-8", errors="replace")
    try:
        print("⏳ waiting for panel server …")
        ok = wait_ready()
        check("سرور پنل بالا آمد (/api/ready)", ok)
        if not ok:
            return

        st = api("/api/state")
        check("۷ پلتفرم در state", len(st.get("platforms", {})) == 7)

        # اندپوینت جدید ۲.۶.۰ — اعتبارسنجی ورودی
        try:
            api("/api/browser/install", "POST", {"browser": "chrome"})
            check("اندپوینت نصب مرورگر: chrome رد می‌شود (۴۰۰)", False)
        except Exception as e:
            check("اندپوینت نصب مرورگر: chrome رد می‌شود (۴۰۰)", "400" in str(e))

        # تنظیمات: headless برای تست
        r = api("/api/settings", "POST", {"general": {"headless": True, "channel": "auto"}})
        check("ذخیره تنظیمات (headless+auto)", r.get("ok") is True)

        # ── باگ ۲ — اینستاگرام: نام کاربری + رمز + کلیک دکمه ──────
        r = api("/api/credentials", "POST",
                {"platform": "instagram", "username": "pars_test_user", "password": "pars_test_pass"})
        check("ذخیره اعتبارنامهٔ اینستاگرام", r.get("ok") is True)

        r = api("/api/quickrun", "POST", {"platform": "instagram", "action": "login", "params": {}})
        msg = r.get("message", "")
        print("   نتیجهٔ لاگین اینستاگرام:", msg[:160])
        check("لاگین اینستاگرام ok", r.get("ok") is True, msg)
        check("نام کاربری پر شد", "نام کاربری پر شد" in msg, msg)
        check("رمز عبور پر شد", "رمز عبور پر شد" in msg, msg)
        check("دکمهٔ ورود کلیک شد", "دکمهٔ ورود کلیک شد" in msg or "Enter زده شد" in msg, msg)

        st = api("/api/state")
        url = (st.get("platforms", {}).get("instagram") or {}).get("url", "")
        check("بعد از ورود به صفحهٔ موفقیت رسید (submit واقعی کار کرد)", "/ok" in url and "pars_test_user" in url, url)

        # بستن نشست برای تست تمیز بعدی
        api("/api/platforms/instagram/close", "POST")

        # ── باگ ۳ — توییتر: فرم دومرحله‌ای (بعدی → رمز → Log in) ──
        api("/api/credentials", "POST",
            {"platform": "twitter", "username": "pars_tw_user", "password": "pars_tw_pass"})
        r = api("/api/quickrun", "POST", {"platform": "twitter", "action": "login", "params": {}})
        msg = r.get("message", "")
        print("   نتیجهٔ لاگین توییتر:", msg[:160])
        check("لاگین توییتر ok (دومرحله‌ای)", r.get("ok") is True, msg)
        check("دکمهٔ «بعدی» برای فرم دومرحله‌ای کلیک شد", "«بعدی» کلیک شد" in msg, msg)
        check("رمز توییتر بعد از مرحلهٔ دوم پر شد", "رمز عبور پر شد" in msg, msg)
        st = api("/api/state")
        url = (st.get("platforms", {}).get("twitter") or {}).get("url", "")
        check("توییتر به صفحهٔ موفقیت رسید", "/ok" in url and "pars_tw_user" in url, url)
        api("/api/platforms/twitter/close", "POST")

        # ── تلگرام: فقط شماره تلفن + بعدی ─────────────────────────
        api("/api/credentials", "POST", {"platform": "telegram", "username": "+989120000000"})
        r = api("/api/quickrun", "POST", {"platform": "telegram", "action": "login", "params": {}})
        msg = r.get("message", "")
        print("   نتیجهٔ لاگین تلگرام:", msg[:160])
        check("لاگین تلگرام ok (تلفنی)", r.get("ok") is True, msg)
        check("شماره تلفن پر شد", "شماره تلفن پر شد" in msg, msg)
        check("راهنمای OTP داده شد", "کد تأیید" in msg, msg)
        st = api("/api/state")
        url = (st.get("platforms", {}).get("telegram") or {}).get("url", "")
        check("تلگرام به صفحهٔ کد رسید", "/code" in url and "phone" in url, url)
        api("/api/platforms/telegram/close", "POST")

        # ── «باز کردن سایت» + فرم ورود = ورود خودکار (درخواست اصلی کاربر) ──
        r = api("/api/quickrun", "POST",
                {"platform": "instagram", "action": "open",
                 "params": {"url": "http://127.0.0.1:8971/login"}})
        check("«باز کردن سایت» ok", r.get("ok") is True, r.get("message", ""))
        # چند ثانیه صبر تا ورود خودکار تمام شود
        for _ in range(20):
            st = api("/api/state")
            url = (st.get("platforms", {}).get("instagram") or {}).get("url", "")
            if "/ok" in url:
                break
            time.sleep(1)
        check("«باز کردن سایت» خودکار وارد شد (فرم دید + پر کرد + کلیک کرد)", "/ok" in url and "pars_test_user" in url, url)
        api("/api/platforms/instagram/close", "POST")

        # ── «باز کردن سایت» بدون فرم ورود → نباید چیزی بترکد ──────
        r = api("/api/quickrun", "POST",
                {"platform": "instagram", "action": "open",
                 "params": {"url": "http://127.0.0.1:8971/home"}})
        check("«باز کردن سایت» صفحهٔ عادی ok", r.get("ok") is True, r.get("message", ""))
        api("/api/platforms/instagram/close", "POST")

        # ── بدون اطلاعات ذخیره → پیام راهنمای فارسی ────────────────
        api("/api/credentials", "POST", {"platform": "facebook", "username": "", "password": "", "clear_password": True})
        r = api("/api/quickrun", "POST", {"platform": "facebook", "action": "login", "params": {}})
        msg = r.get("message", "")
        check("بدون اطلاعات: پیام راهنما (نه خطای خام)", not r.get("ok") and "ذخیره نشده" in msg, msg)

        # ── انتخاب کانال chromium به‌صورت صریح (باگ پاس‌دادن کانال) ──
        api("/api/settings", "POST", {"general": {"channel": "chromium"}})
        r = api("/api/quickrun", "POST",
                {"platform": "instagram", "action": "open",
                 "params": {"url": "http://127.0.0.1:8971/home"}})
        check("کانال صریح «chromium» کار می‌کند (پاس داده شدن کانال)", r.get("ok") is True, r.get("message", ""))
        api("/api/platforms/instagram/close", "POST")

        # ── فایرفاکس: اندپوینت نصب فقط نام معتبر بپذیرد ─────────────
        try:
            r = api("/api/browser/install", "POST", {"browser": "firefox"})
            check("اندپوینت نصب firefox پذیرفته شد (در پس‌زمینه)", r.get("ok") is True, str(r))
        except Exception as e:
            check("اندپوینت نصب firefox پذیرفته شد (در پس‌زمینه)", False, str(e))

        # برگرداندن تنظیمات به وضعیت عادی
        api("/api/settings", "POST", {"general": {"headless": True, "channel": "auto"}})
    finally:
        print("\n⏳ shutting down …")
        server.terminate()
        pages.terminate()
        try:
            server.wait(timeout=10)
        except Exception:
            server.kill()
        out = server.stdout.read() if server.stdout else ""
        # ── پاک‌سازی وضعیت تست (دیتای شخصی وارد ZIP نشود) ──────────
        for d in ("config", "profiles", "macros", "media"):
            p = os.path.join(PARS, d)
            if os.path.isdir(p):
                shutil.rmtree(p, ignore_errors=True)
        if FAIL:
            print("\n===== SERVER LOG (tail) =====")
            print("\n".join(out.splitlines()[-40:]))

    print(f"\n{'=' * 52}\n  PASS: {len(PASS)}   FAIL: {len(FAIL)}")
    if FAIL:
        print("  FAILED:")
        for f in FAIL:
            print("   - " + f)
        sys.exit(1)
    print("  ALL TESTS PASSED ✅")


if __name__ == "__main__":
    main()
