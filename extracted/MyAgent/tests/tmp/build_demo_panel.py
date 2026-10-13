#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ساخت پیش‌نمایش استاتیک پنل برای وب‌سایت (public/panel.html)
   snapshotهای واقعی API + shim برای fetch/WebSocket — فقط برای پیش‌نمایش."""
import json, re
from pathlib import Path

SRC = Path("/home/z/my-project/parsagent/static/index.html")
DST = Path("/home/z/my-project/public/panel.html")
MOCKS = Path("/tmp/panel_mocks")

html = SRC.read_text(encoding="utf-8")

mocks = {}
for name, ep in [
    ("options", "/api/options"),
    ("state", "/api/state"),
    ("schedules", "/api/schedules"),
    ("settings", "/api/settings"),
    ("credentials", "/api/credentials"),
    ("media", "/api/media"),
    ("macro_list", "/api/macro/list"),
]:
    mocks[ep] = json.loads((MOCKS / f"{name}.json").read_text(encoding="utf-8"))

# کمی حیاتی‌تر کردن snapshot وضعیت: دو پلتفرم باز نشان بده
st = mocks["/api/state"]
if isinstance(st.get("platforms"), dict):
    if "instagram" in st["platforms"]:
        st["platforms"]["instagram"]["open"] = True
    if "telegram" in st["platforms"]:
        st["platforms"]["telegram"]["open"] = True

mock_js = json.dumps(mocks, ensure_ascii=False, separators=(",", ":"))

demo_logs = json.dumps([
    {"t": "22:10:01", "msg": "سرور ParsAgent روی 127.0.0.1:8765 بالا آمد — پیش‌نمایش استاتیک", "level": ""},
    {"t": "22:10:02", "msg": "پروفایل اینستاگرام با کانال msedge باز شد (profiles/instagram)", "level": ""},
    {"t": "22:10:05", "msg": "ضد شناسایی (Stealth) فعال — navigator.webdriver پنهان شد", "level": ""},
    {"t": "22:10:09", "msg": "زمان‌بند آماده است — وظیفه‌ها با jitter اجرا می‌شوند", "level": ""},
    {"t": "22:10:12", "msg": "این فقط پیش‌نمایش است؛ روی سیستم خودتان همهٔ دکمه‌ها واقعی‌اند ✅", "level": "warn"},
], ensure_ascii=False)

SHIM_TEMPLATE = """
<!-- DEMO SHIM — فقط برای پیش‌نمایش استاتیک روی وب‌سایت؛ در نسخهٔ اصلی وجود ندارد -->
<script>
(function () {
  var MOCKS = __MOCKS__;
  var REAL = window.fetch.bind(window);
  var DEMO_RESP = {"ok": true, "demo": true, "message": "پیش‌نمایش استاتیک است — روی سیستم خودتان واقعاً اجرا می‌شود"};
  window.fetch = function (url, opts) {
    var path;
    try { path = new URL(String(url), location.href).pathname; } catch (e) { path = String(url); }
    var m = (opts && (opts.method === "POST" || opts.method === "DELETE" || opts.method === "PUT"));
    if (MOCKS[path] && !m) {
      return Promise.resolve(new Response(JSON.stringify(MOCKS[path]), {status: 200, headers: {"Content-Type": "application/json"}}));
    }
    if (path.indexOf("/api/") === 0) {
      return Promise.resolve(new Response(JSON.stringify(DEMO_RESP), {status: 200, headers: {"Content-Type": "application/json"}}));
    }
    return REAL(url, opts);
  };
  function FakeWS() { this.readyState = 1; this.onmessage = null; }
  FakeWS.prototype.send = function () {};
  FakeWS.prototype.close = function () {};
  window.WebSocket = FakeWS;
  var LOGS = __DEMO_LOGS__;
  window.addEventListener("load", function () {
    setTimeout(function () {
      LOGS.forEach(function (e, i) {
        setTimeout(function () {
          var f = document.querySelector("#logfeed");
          if (!f) return;
          var d = document.createElement("div");
          d.innerHTML = '<span class="' + (e.level || "") + '">' + e.msg + '</span><span class="t">' + e.t + '</span>';
          f.appendChild(d);
          f.scrollTop = f.scrollHeight;
        }, i * 700);
      });
    }, 800);
  });
})();
</script>
<style>
#demo-banner{position:sticky;top:0;z-index:999;background:linear-gradient(90deg,#f59e0b,#f97316);
  color:#231400;text-align:center;font-size:12.5px;font-weight:700;padding:7px 14px;line-height:1.7}
</style>
"""

banner = '<div id="demo-banner">🔍 پیش‌نمایش استاتیک ظاهر پنل — دکمه‌ها اینجا اجرا نمی‌شوند؛ با دانلود و اجرای پروژه روی سیستم خودتان، همین پنل به سرور واقعی وصل می‌شود</div>'

shim = SHIM_TEMPLATE.replace("__MOCKS__", mock_js).replace("__DEMO_LOGS__", demo_logs)

html = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + banner, html, count=1)
html = html.replace("<script>", shim + "\n<script>", 1)

DST.write_text(html, encoding="utf-8")
print(f"OK -> {DST} ({len(html)//1024} KB)")
