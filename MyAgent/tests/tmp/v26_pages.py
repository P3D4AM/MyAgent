# -*- coding: utf-8 -*-
"""صفحات ورود شبیه‌سازی‌شده برای تست ورود خودکار ۲.۶.۰.

- /login  : سبک اینستاگرام — تک‌صفحه (username + password + submit)
- /login2 : سبک توییتر — دومرحله‌ای (username → Next → password → Log in)
- /login3 : سبک تلگرام — تلفن → Next → صفحهٔ کد
- /ok     : صفحهٔ موفقیت    /code : صفحهٔ کد تأیید
"""
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote

HEAD = ("<!doctype html><html><head><meta charset='utf-8'>"
        "<style>body{font-family:sans-serif;padding:40px}input,button{padding:8px 14px;"
        "font-size:16px;display:block;margin:8px 0}</style></head><body>")
TAIL = "</body></html>"

PAGE_LOGIN = HEAD + """
<h2>Instagram Login (TEST)</h2>
<form action="/ok" method="get">
  <input name="username" aria-label="Phone number, username, or email" placeholder="username">
  <input type="password" name="password" placeholder="password">
  <button type="submit">Log in</button>
</form>""" + TAIL

PAGE_LOGIN2 = HEAD + """
<h2>Twitter Login (TEST — two step)</h2>
<form action="/ok" method="get" onsubmit="return go2()">
  <div id="step1">
    <input autocomplete="username" name="text" placeholder="username">
    <div data-testid="nextButton" role="button" onclick="step2()" style="padding:8px 20px;
         background:#1d9bf0;color:#fff;border-radius:20px;cursor:pointer">Next</div>
  </div>
  <div id="step2" style="display:none">
    <input type="password" name="password" placeholder="password">
    <div data-testid="LoginForm_Login_Button" role="button" onclick="go2()" style="padding:8px
         20px;background:#1d9bf0;color:#fff;border-radius:20px;cursor:pointer">Log in</div>
  </div>
</form>
<script>
function step2(){document.getElementById('step1').style.display='none';
  document.getElementById('step2').style.display='block';return false;}
function go2(){document.forms[0].submit();return false;}
</script>""" + TAIL

PAGE_LOGIN3 = HEAD + """
<h2>Telegram Login (TEST)</h2>
<form action="/code" method="get">
  <input name="phone" type="tel" placeholder="Phone number">
  <button type="submit">Next</button>
</form>""" + TAIL

PAGE_OK = HEAD + "<h2>SUCCESS</h2><p id='who'></p>" + TAIL
PAGE_CODE = HEAD + "<h2>Enter code</h2><input placeholder='Code'><p>کد را وارد کنید</p>" + TAIL


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/dump":  # برای دیدن مقدار فرم ارسالی (query)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(unquote(self.path).encode())
            return
        page = {"/login": PAGE_LOGIN, "/login2": PAGE_LOGIN2, "/login3": PAGE_LOGIN3,
                "/ok": PAGE_OK, "/code": PAGE_CODE}.get(path, HEAD + "<h1>home</h1>" + TAIL)
        body = page.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def start(port: int = 8971):
    srv = HTTPServer(("127.0.0.1", port), H)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv


if __name__ == "__main__":
    print("fake login pages on :8971")
    start()
    threading.Event().wait()
