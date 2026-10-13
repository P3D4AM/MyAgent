# -*- coding: utf-8 -*-
"""تست‌های v2.13.0 — پروکسی سرویس‌های AI + پیام فارسی 403 + گروک.

اجرا:  cd parsagent && python ../tests/tmp/test_v213.py
"""
import asyncio
import json
import os
import socket
import sys
import threading
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "parsagent"))

import ai_agent  # noqa: E402
import ai_media  # noqa: E402

PASS = FAIL = 0


def check(name: str, cond: bool, extra: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {extra}")


# ─────────────────────────────────────────────────────── ۱) resolve_ai_proxy
print("۱) resolve_ai_proxy — اولویت‌ها و نرمال‌سازی")

# ① تنظیم پنل — بدون scheme
p = ai_agent.resolve_ai_proxy({"proxy": "127.0.0.1:10809"})
check("بدون scheme → http://", p == {"http": "http://127.0.0.1:10809", "https": "http://127.0.0.1:10809"}, str(p))

p = ai_agent.resolve_ai_proxy({"proxy": "http://127.0.0.1:7890"})
check("با scheme → همان", p == {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"})

# ① socks → خطای فارسی
try:
    ai_agent.resolve_ai_proxy({"proxy": "socks5://127.0.0.1:10808"})
    check("socks → AgentError فارسی", False)
except ai_agent.AgentError as e:
    check("socks → AgentError فارسی", "SOCKS" in str(e) and "10809" in str(e))

# ② متغیرهای محیط
os.environ["HTTP_PROXY"] = "http://10.0.0.5:3128"
os.environ.pop("HTTPS_PROXY", None)
p = ai_agent.resolve_ai_proxy({})
check("env HTTP_PROXY", p == {"http": "http://10.0.0.5:3128", "https": "http://10.0.0.5:3128"}, str(p))
os.environ.pop("HTTP_PROXY", None)

# هیچی نبود → مستقیم (در لینوکس رجیستری نیست)
p = ai_agent.resolve_ai_proxy({})
check("خالی → None (مستقیم)", p is None, str(p))

# ai_media._proxy_map هم همان را می‌دهد
os.environ["ALL_PROXY"] = "http://127.0.0.1:2080"
p = ai_media._proxy_map({})
check("ai_media env ALL_PROXY", p == {"http": "http://127.0.0.1:2080", "https": "http://127.0.0.1:2080"}, str(p))
os.environ.pop("ALL_PROXY", None)

try:
    ai_media._proxy_map({"proxy": "socks://x"})
    check("ai_media socks → MediaError فارسی", False)
except ai_media.MediaError as e:
    check("ai_media socks → MediaError فارسی", "SOCKS" in str(e))

# ─────────────────────────────────────────────────────── ۲) پیام‌های فارسی خطا
print("۲) _llm_error_fa — ترجمهٔ 403/401/429")

m = ai_agent._llm_error_fa(403, "Forbidden")
check("403 Forbidden → راهنمای پروکسی", "403" in m and "پروکسی" in m and "Z.ai" in m and "10809" in m, m[:80])

google_html = ('<!DOCTYPE html> <html lang=en> <meta charset=utf-8> '
               '<title>Error 403 (Forbidden)!!1</title> <p>Your client does not have permission')
m = ai_agent._llm_error_fa(403, google_html)
check("403 HTML گوگل → تشخیص صفحهٔ خطا", "HTML" in m and "پروکسی" in m, m[:80])

m = ai_agent._llm_error_fa(403, '{"error":{"code":403,"message":"User location is not supported for the API use."}}')
check("403 Gemini location → پیام اختصاصی", "Gemini" in m and "منطقه" in m and "پروکسی" in m, m[:80])

m = ai_agent._llm_error_fa(401, '{"error":{"message":"invalid api key"}}')
check("401 → کلید نامعتبر", "کلید" in m and "401" in m)

m = ai_agent._llm_error_fa(429, '{"error":{"message":"rate limited"}}')
check("429 → محدودیت نرخ", "429" in m)

m = ai_media._http_error_fa(403, "Forbidden")
check("ai_media 403 → راهنمای پروکسی", "403" in m and "پروکسی" in m)

# ─────────────────────────────────────────────────────── ۳) کاتالوگ: گروک
print("۳) سرویس جدید xAI Grok")
g = ai_agent.PROVIDERS.get("grok")
check("grok در PROVIDERS", bool(g) and g["base"] == "https://api.x.ai/v1" and g["kind"] == "openai")
check("مدل‌های grok", [m["id"] for m in (g["models"] if g else [])] == ["grok-4", "grok-3", "grok-3-mini"])
check("سرویس اولِ لیست هنوز Z.ai است", list(ai_agent.PROVIDERS.keys())[0] == "zai")
check("groq سر جایش است", "groq" in ai_agent.PROVIDERS)

# ─────────────────────────────────────────────────────── ۴) درخواست واقعی از راه پروکسی محلی
print("۴) llm_chat از راه پروکسیِ محلی (پروکسی واقعی، نه ماک)")

RESP = json.dumps({"choices": [{"message": {"content": "OK"}}]}).encode()


class FakeProxy(threading.Thread):
    """پروکسی HTTP کوچک — برای مقصد http درخواست کامل با URL مطلق می‌آید."""

    daemon = True
    last_request_line = ""
    mode = "ok"  # ok | 403 | html403

    def __init__(self):
        super().__init__()
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(4)
        self.port = self.sock.getsockname()[1]

    def run(self):
        while True:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            with conn:
                conn.settimeout(10)
                try:
                    data = b""
                    while b"\r\n\r\n" not in data:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break
                        data += chunk
                    line = data.split(b"\r\n", 1)[0].decode("utf-8", "ignore")
                    if line.startswith("POST "):
                        FakeProxy.last_request_line = line
                    if FakeProxy.mode == "ok":
                        body = RESP
                        head = ("HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n"
                                f"Content-Length: {len(body)}\r\n\r\n").encode()
                        conn.sendall(head + body)
                    elif FakeProxy.mode == "403":
                        conn.sendall(b"HTTP/1.0 403 Forbidden\r\nContent-Length: 9\r\n\r\nForbidden")
                    else:
                        page = ('<html lang=en><title>Error 403 (Forbidden)</title>'
                                '<p>User location is not supported</p></html>').encode()
                        head = "HTTP/1.0 403 Forbidden\r\nContent-Type: text/html\r\n" \
                               f"Content-Length: {len(page)}\r\n\r\n"
                        conn.sendall(head.encode() + page)
                except Exception:
                    pass


proxy = FakeProxy()
proxy.start()


async def _chat(mode: str):
    FakeProxy.mode = mode
    FakeProxy.last_request_line = ""
    cfg = {"custom_base": f"http://api.parsagent-test.internal/v1",
           "custom_model": "test-model",
           "api_keys": {"custom": "k"},
           "proxy": f"http://127.0.0.1:{proxy.port}"}
    return await ai_agent.llm_chat(cfg, "custom", "", [{"role": "user", "content": "hi"}])


reply = asyncio.run(_chat("ok"))
check("پاسخ از راه پروکسی آمد", reply == "OK", repr(reply))
check("درخواست با URL مطلق به پروکسی رفت", "api.parsagent-test.internal" in FakeProxy.last_request_line,
      FakeProxy.last_request_line)

try:
    asyncio.run(_chat("403"))
    check("403 Forbidden فارسی بلند می‌شود", False)
except ai_agent.AgentError as e:
    check("403 Forbidden فارسی بلند می‌شود", "پروکسی" in str(e) and "Z.ai" in str(e), str(e)[:80])

try:
    asyncio.run(_chat("html403"))
    check("403 HTML گوگل فارسی بلند می‌شود", False)
except ai_agent.AgentError as e:
    check("403 HTML گوگل فارسی بلند می‌شود", "پروکسی" in str(e), str(e)[:80])

# بدون پروکسی، آدرس لوکال مستقیم می‌رود (بدون تغییر رفتار قدیمی)
FakeProxy.mode = "ok"


async def _chat_local():
    cfg = {"custom_base": f"http://127.0.0.1:{proxy.port}/v1", "custom_model": "m",
           "api_keys": {"custom": "k"}}
    return await ai_agent.llm_chat(cfg, "custom", "", [{"role": "user", "content": "hi"}])


check("لوکال (Ollama) مستقیم — بدون پروکسی", asyncio.run(_chat_local()) == "OK")

# ─────────────────────────────────────────────────────── ۵) فیلم‌نامه: خطای دائمی، بدون retry
print("۵) _llm_scenes — خطای 403 دیگر retry نمی‌خورد")


class FakeLLM:
    calls = 0

    @staticmethod
    async def failing(cfg, provider, model, msgs, temperature=0.4):
        FakeLLM.calls += 1
        raise ai_agent.AgentError("سرویس درخواست شما را رد کرد (خطای 403 Forbidden). اگر کلید API درست است…")


async def _scenes_403():
    try:
        await ai_media._llm_scenes(FakeLLM.failing, {"proxy": ""}, "groq", "m", "تست", 3, "fa", 30)
        return "no-raise"
    except ai_media.MediaError as e:
        return str(e)


res = asyncio.run(_scenes_403())
check("403 → یک‌بار صدا زده شد (نه ۳ بار)", FakeLLM.calls == 1, f"calls={FakeLLM.calls}")
check("پیام با زمینهٔ فیلم‌نامه", res.startswith("نوشتن فیلم‌نامه ممکن نشد"), res[:60])


class FlakyLLM:
    calls = 0

    @staticmethod
    async def flaky(cfg, provider, model, msgs, temperature=0.4):
        FlakyLLM.calls += 1
        if FlakyLLM.calls == 1:
            raise OSError("[WinError 10054] connection reset")
        return {"scenes": [{"narration": "صحنهٔ اول", "image_prompt": "x"},
                           {"narration": "صحنهٔ دوم", "image_prompt": "y"}]}


ai_media._LLM_RETRY_WAITS = (0.01, 0.01)  # تست سریع
scenes = asyncio.run(ai_media._llm_scenes(FlakyLLM.flaky, {}, "zai", "m", "تست", 3, "fa", 30))
check("خطای اتصال (10054) هنوز retry می‌شود", FlakyLLM.calls == 2 and len(scenes) == 2, f"calls={FlakyLLM.calls}")

# ─────────────────────────────────────────────────────── ۶) DEFAULT_SETTINGS پنل
print("۶) panel_server — فیلد جدید تنظیمات")
import panel_server  # noqa: E402

st = panel_server.DEFAULT_SETTINGS
check("ai.proxy در پیش‌فرض‌ها", "proxy" in st["ai"], str(st["ai"].keys()))
check("کلید grok در پیش‌فرض‌ها", "grok" in st["ai"]["api_keys"])
check("مدل/سرویس پیش‌فرض دست‌نخورده", st["ai"]["provider"] == "zai" and st["ai"]["model"] == "glm-4.6")
check("video/image تنظیمات حفظ شد", "voice" in st["ai"]["video"] and "provider" in st["ai"]["image"])
check("۸ پلتفرم حفظ شد", len(panel_server.PLAT_IDS) == 8, str(panel_server.PLAT_IDS))

# تنظیمات ذخیره‌شدهٔ قدیمی (بدون proxy) با پیش‌فرض ادغام می‌شود → کلید grok اضافه می‌آید
merged = panel_server.settings()
check("merge: proxy بعد از ادغام هست", "proxy" in merged["ai"])
check("merge: کلید grok اضافه شد", "grok" in merged["ai"]["api_keys"])

print(f"\n{'='*50}\nنتیجه: {PASS} پاس / {FAIL} خطا")
sys.exit(1 if FAIL else 0)
