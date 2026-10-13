# -*- coding: utf-8 -*-
"""سرور تست نسخهٔ ۲.۶.۰ — panel_server واقعی با URLهای ورود لوکال."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "parsagent"))
import panel_server as ps  # noqa: E402

BASE = "http://127.0.0.1:8971"
# شبیه‌سازی صفحات ورود (سلکتورها همان سلکتورهای واقعی هر پلتفرم‌اند)
ps.LOGIN_URLS["instagram"] = BASE + "/login"
ps.LOGIN_URLS["twitter"] = BASE + "/login2"
ps.LOGIN_URLS["telegram"] = BASE + "/login3"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(ps.app, host="127.0.0.1", port=int(os.environ.get("PANEL_PORT", "8799")),
                log_level="warning")
