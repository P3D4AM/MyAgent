# -*- coding: utf-8 -*-
"""E2E واقعی v2.15.0 با Chromium هدلس:
  ۱) پخش کامل: goto صفحهٔ «اصلی پلتفرم» (ماک محلی) → اجرای رخدادها → بسته شدن خودکار مرورگر
  ۲) رزولوشن پلتفرم از فایل ماکرو (نه پارامتر)
  ۳) state.macro.playing حین پخش
  ۴) دکمهٔ توقف پخش (stop-run) → پیام متوقف‌شدن + بسته شدن مرورگر
  ۵) درمانِ خودکارِ پنجرهٔ دستی‌بسته‌شده (ensure)
"""
import asyncio, json, os, sys, threading, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, "/home/z/my-project/parsagent")
os.environ["PANEL_PORT"] = "8898"
import panel_server as ps

PASS = []
def ok(name, cond, extra=""):
    PASS.append(bool(cond))
    print(("✅" if cond else "❌"), name, extra if not cond else "")

HITS = []
MOCK = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>mock</title></head>
<body><input id="inp"><button id="btn" onclick="fetch('/hit?b=btn')">b1</button>
<button id="btn2" onclick="fetch('/hit?b=btn2')">b2</button>
<button id="btn3" onclick="fetch('/hit?b=btn3')">b3</button>
<button id="btn4" onclick="fetch('/hit?b=btn4')">b4</button></body></html>"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/hit"):
            HITS.append(urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("b", ["?"])[0])
            self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(MOCK.encode())
    def log_message(self, *a): pass

srv = ThreadingHTTPServer(("127.0.0.1", 8877), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
MOCK_URL = "http://127.0.0.1:8877/"

async def main():
    # پلتفرم تلگرام را برای این تست به صفحهٔ ماک می‌بریم (فقط در حافظه)
    for p in ps.PLATFORMS:
        if p["id"] == "telegram":
            p["url"] = MOCK_URL

    ev = lambda sel: {"t": "click", "sel": sel, "origin": MOCK_URL}
    f = ps.MACROS_DIR / "e2e-215.json"
    f.write_text(json.dumps({"platform": "telegram", "events": [
        {"t": "input", "sel": "#inp", "v": "سلام دنیا", "origin": MOCK_URL},
        ev("#btn"), ev("#btn2"), ev("#btn3"), ev("#btn4"),
    ]}, ensure_ascii=False), encoding="utf-8")

    # ---------- ۱+۲) پخش کامل با پلتفرمِ اشتباه در پارامتر (باید به تلگرام برود)
    r = await ps.macro_run({"platform": "instagram", "name": "e2e-215"})  # ← عمداً غلط
    ok("پخش ok", r.get("ok") is True, str(r))
    ok("هر ۵ رخداد اجرا شد", "5 از 5" in r.get("message", ""), r.get("message", ""))
    ok("بسته شدن مرورگر بعد از پخش", ps.SESSIONS["telegram"].context is None and ps.SESSIONS["telegram"].p is None)
    ok("رخدادها واقعاً اجرا شدند (سرور ماک)", set(HITS) == {"btn", "btn2", "btn3", "btn4"}, str(HITS))

    # ---------- ۳) state حین پخش + توقف mid-run
    HITS.clear()
    task = asyncio.create_task(ps.macro_run({"platform": "telegram", "name": "e2e-215"}))
    playing = None
    for _ in range(200):  # تا ۲۰ ثانیه صبر تا goto تمام و پخش شروع شود
        await asyncio.sleep(0.1)
        st = await ps.state()
        if st["macro"].get("playing"):
            playing = st["macro"]["playing"]
            break
    ok("state حین پخش: playing با platform/name", playing and playing["platform"] == "telegram" and playing["name"] == "e2e-215", str(playing))
    # حین پخش: دکمهٔ توقف
    r2 = await ps.macro_stop_run()
    ok("stop-run حین پخش ok", r2["ok"] is True, str(r2))
    r = await task
    ok("پیام توقف", r.get("stopped") is True and "متوقف شد" in r["message"], str(r))
    ok("مرورگر بعد از توقف هم بسته شد", ps.SESSIONS["telegram"].context is None)

    # ---------- ۴) پخش دوباره بعد از توقف (بدون خطا — درخواست کاربر)
    HITS.clear()
    r = await ps.macro_run({"platform": "telegram", "name": "e2e-215"})
    ok("پخش دوباره بعد از توقف کار می‌کند", r.get("ok") is True and "5 از 5" in r["message"], str(r))

    # ---------- ۵) درمان پنجرهٔ دستی‌بسته
    sess = ps.SESSIONS["telegram"]
    await sess.ensure()
    old_ctx = sess.context
    await old_ctx.close()          # شبیه‌سازی بستن دستی پنجره توسط کاربر
    ok("state کهنه: context هنوز None نیست (شرط باگ)", sess.context is not None)
    page = await sess.ensure()     # ← قبلاً همین‌جا Target closed می‌داد
    ok("ensure بعد از بستن دستی: بازگشایی", page is not None and sess.context is not None and sess.context is not old_ctx)
    ok("صفحهٔ بازگشایی سالم است", await page.evaluate("1 + 1") == 2)
    await sess.close()

    # ---------- ۶) پخش هم‌زمان دوم → پیام فارسی
    t1 = asyncio.create_task(ps.macro_run({"platform": "telegram", "name": "e2e-215"}))
    await asyncio.sleep(1.5)  # بگذار وارد goto شود
    r = await ps.macro_run({"platform": "telegram", "name": "e2e-215"})
    ok("پخش دوم رد شد با پیام", r.get("ok") is False and "هم اکنون یک ماکرو" in r["message"], str(r))
    await t1
    ok("پخش اول سالم تمام شد", ps.SESSIONS["telegram"].context is None)

    f.unlink(missing_ok=True)
    print("\n" + ("ALL E2E PASS ✅" if all(PASS) else "SOME E2E FAILED ❌"))
    sys.exit(0 if all(PASS) else 1)

asyncio.run(main())
