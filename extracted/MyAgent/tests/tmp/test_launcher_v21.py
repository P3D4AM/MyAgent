# -*- coding: utf-8 -*-
"""تست end-to-end لانچر ۲.۱.۰ — حتی با پروکسی/VPN ساختگی روشن"""
import importlib.util
import os
import sys

# ── شبیه‌سازی دقیق محیط کاربر: پروکسی سیستم روشن (همان چیزی که لانچر قدیمی را گیر می‌داد)
os.environ["http_proxy"] = "http://10.255.255.1:9"
os.environ["https_proxy"] = "http://10.255.255.1:9"
os.environ["no_proxy"] = ""

sys.path.insert(0, "/home/z/my-project/parsagent")
import launcher as L  # noqa: E402

# اگر ماژولی در سندباکس نصب نیست، فقط برای همین تست از چک حذف شود
# (روی ویندوز کاربر همه نصب‌اند؛ این تست مسیر اجرای سرور را می‌سنجد)
for m in list(L.REQUIRED):
    try:
        if importlib.util.find_spec(m) is None:
            del L.REQUIRED[m]
    except Exception:
        pass

captured = {}
app = L.Launcher()
app.after(700, app.start_server)


def check():
    if app.server_ready:
        app.after(900, lambda: (captured.update(
            log=app.txt.get("1.0", "end"),
            status=app.status_lbl.cget("text"),
            wsdot=app.ws_dot.cget("text")), app.destroy()))
        return
    app.after(300, check)


app.after(1500, check)
app.after(30000, lambda: (captured.update(
    log=app.txt.get("1.0", "end"), status=app.status_lbl.cget("text")), app.destroy()))
app.mainloop()

print("SERVER_READY:", app.server_ready)
print("STATUS_LABEL:", captured.get("status"))
print("PANEL_DOT:", captured.get("wsdot"))
print("---- LAUNCHER LOG ----")
print(captured.get("log", "(no log)"))
