# -*- coding: utf-8 -*-
"""
تست v2.12.0 — رفع «سازنده و چاپ پول» (ساخت عکس/ویدیو)
======================================================
موردِ گزارش‌شدهٔ کاربر:
  ❌ video: «کتابخانهٔ edge-tts نصب نیست» + [WinError 10054] اتصال بسته شد
  ❌ image: Z.ai خطای 400 کد 1211 «Unknown Model»
  ❌ image: Z.ai خطای 429 کد 1113 «Insufficient balance»
  ❌ image: Pollinations دو بار HTTP 402 Payment Required

این تست بدون اینترنت، همهٔ این مسیرها را با ماک شبیه‌سازی و اثبات می‌کند.
اجرا:  python tests/tmp/test_media_v212.py
"""
import asyncio
import io
import sys
import types
import urllib.error
from pathlib import Path

BASE = Path(__file__).resolve().parents[2] / "parsagent"
sys.path.insert(0, str(BASE))

import ai_media  # noqa: E402

real_ensure = ai_media.ensure_module  # ذخیرهٔ نسخهٔ واقعی قبل از هر ماکی

# صبرهای backoff را برای تست کوچک می‌کنیم (در تولید: 20/35 و 1.5/3 و 2/4 ثانیه)
ai_media._POLL_RETRY_WAITS = (0.01, 0.01)
ai_media._TTS_RETRY_WAITS = (0.01, 0.01)
ai_media._LLM_RETRY_WAITS = (0.01, 0.01)

PASS, FAIL = [], []


def check(name: str, cond: bool, extra: str = ""):
    (PASS if cond else FAIL).append(name)
    print(("  ✅ " if cond else "  ❌ ") + name + (f"  [{extra}]" if extra and not cond else ""))


# ─────────────────────────── ۱) کاتالوگ و مدل Z.ai (خطای 1211) ───────────────────────────
print("\n۱) مدل Z.ai — خطای 1211 «Unknown Model»:")
ids = [m["id"] for m in ai_media.IMAGE_PROVIDERS["zai"]["models"]]
check("zai فقط glm-image را دارد (cogview حذف شد)", ids == ["glm-image"], str(ids))
check("پلتفرم openai دست‌نخورده است", "dall-e-3" in [m["id"] for m in ai_media.IMAGE_PROVIDERS["openai"]["models"]])
check("pollinations توکن اختیاری دارد (key_field)", ai_media.IMAGE_PROVIDERS["pollinations"]["key_field"] == "pollinations")
check("نام pollinations دیگر «کاملاً رایگان» نیست", "محدود" in ai_media.IMAGE_PROVIDERS["pollinations"]["name"])

# ─────────────────────────── ۲) پیام فارسی خطاها (1113/1211/402) ───────────────────────────
print("\n۲) پیام فارسی خطاها:")
m = ai_media._http_error_fa(400, '{"error":{"code":"1211","message":"Unknown Model, please check the model code."}}')
check("1211 → پیام شامل «glm-image» و «1211»", "1211" in m and "glm-image" in m, m)
m = ai_media._http_error_fa(429, '{"error":{"code":"1113","message":"Insufficient balance or no resource package. Please recharge."}}')
check("1113 → پیام شامل «شارژ» و لینک z.ai", "1113" in m and "شارژ" in m and "z.ai" in m, m)
m = ai_media._http_error_fa(402, "")
check("402 → پیام «سهمیهٔ رایگان»", "402" in m and "سهمیه" in m, m)
m = ai_media._http_error_fa(401, "bad key")
check("401 → راهنمای کلید", "کلید" in m, m)
m = ai_media._http_error_fa(500, "boom")
check("خطای نامشخص → کد + جزئیات حفظ می‌شود", "500" in m and "boom" in m, m)

# ─────────────────────────── ۳) سایزها مطابق مستند رسمی ───────────────────────────
print("\n۳) سایزهای عکس (مستند docs.z.ai):")
check("مربع 1024x1024", ai_media.SIZES["square"]["api"] == "1024x1024")
check("عمودی 768x1344 (قبلاً 1024x1792ِ غیرمجاز بود)", ai_media.SIZES["portrait"]["api"] == "768x1344")
check("افقی 1344x768 (قبلاً 1792x1024 بود)", ai_media.SIZES["landscape"]["api"] == "1344x768")

# ─────────────────────────── ۴) generate_image — زنجیره و اعتبارسنجی ───────────────────────────
print("\n۴) generate_image — مدل کهنه/نامعتبر خودکار جایگزین می‌شود (رفع 1211):")
captured = {}
ai_cfg = {"api_keys": {"zai": "KEY-TEST"}}


async def fake_install(mod, pkg, why, report=None):
    check("نصب خودکار برای edge_tts خواسته شد", mod == "edge_tts")
    sys.modules["edge_tts"] = types.SimpleNamespace(Communicate=FakeCommunicate)
    return True


def fake_http_json_sync(url, headers, payload, timeout=180):  # sync — مثل واقعی، چون asyncio.to_thread است
    captured["url"], captured["payload"] = url, payload
    return {"data": [{"b64_json": "iVBORw0KGgoAAAANSUhEUg=="}]}


ai_media._http_json = fake_http_json_sync

async def t4():
    return await ai_media.generate_image(ai_cfg, "یک گربه روی پنجره", provider="zai",
                                          model="cogview-3-flash",  # ← مدل کهنهٔ ذخیره‌شدهٔ کاربر
                                          size_key="portrait")

res = asyncio.run(t4())
check("با مدل کهنه هم کار کرد (جایگزین خودکار)", res.get("ok") is True, str(res))
check("پرامپت به endpoint رسمی Z.ai رفت", "api.z.ai/api/paas/v4/images/generations" in captured.get("url", ""), str(captured.get("url")))
check("کد مدل ارسالی glm-image است (نه cogview)", captured["payload"].get("model") == "glm-image", str(captured["payload"]))
check("سایز ارسالی 768x1344 است", captured["payload"].get("size") == "768x1344", str(captured["payload"]))
check("فایل در media/ ذخیره شد", res.get("file", "").startswith("ai-image-") and (ai_media.MEDIA_DIR / res["file"]).exists())
(ai_media.MEDIA_DIR / res["file"]).unlink(missing_ok=True)  # پاک‌سازی تست

# ─────────────────────────── ۵) Z.ai موجودی ناکافی → پیام فارسی در «tried» ───────────────────────────
print("\n۵) خطای 1113 از Z.ai در زنجیرهٔ جایگزین:")
ai_cfg2 = {"api_keys": {"zai": "KEY", "pollinations": ""}}


def fake_http_json_1113(url, headers, payload, timeout=180):  # sync — مثل واقعی
    raise ai_media.MediaError(ai_media._http_error_fa(429, '{"error":{"code":"1113","message":"Insufficient balance or no resource package. Please recharge."}}'))


ai_media._http_json = fake_http_json_1113
real_poll = ai_media._pollinations_image
ai_media._pollinations_image = lambda *a, **k: (_ for _ in ()).throw(ai_media.MediaError("Pollinations: 402 سهمیه پر است"))

async def t5():
    try:
        await ai_media.generate_image(ai_cfg2, "گربه", provider="zai", model="glm-image")
        return None
    except ai_media.MediaError as e:
        return str(e)

err = asyncio.run(t5())
check("پیام فارسی 1113 به کاربر رسید (نه JSON خام)", err is not None and "1113" in err and "شارژ" in err, str(err))

# ─────────────────────────── ۶) Pollinations: توکن + صف + 402 ───────────────────────────
print("\n۶) Pollinations — توکن، فاصلهٔ صف، تلاش مجدد روی 402:")
ai_media._pollinations_image = real_poll  # برگرداندن تابع واقعی برای این بخش
poll_calls = []


def fake_poll_dl(url, timeout=120, extra_headers=None):
    poll_calls.append({"url": url, "headers": extra_headers or {}})
    if len(poll_calls) <= 2:
        raise urllib.error.HTTPError(url, 402, "Payment Required", hdrs=None, fp=None)
    return b"\x89PNG\r\n\x1a\nPOLLIMG"


ai_media._download_bytes = fake_poll_dl
ai_media._POLL_MIN_GAP = 0.25
ai_media._POLL_LAST = 0.0
ai_media._POLL_LOCK = asyncio.Lock()

async def t6a():
    t0 = asyncio.get_running_loop().time()
    b1 = await ai_media._pollinations_image("عکس اول", ai_media.SIZES["square"], "flux", "TOKEN123")
    t1 = asyncio.get_running_loop().time()
    b2 = await ai_media._pollinations_image("عکس دوم", ai_media.SIZES["square"], "flux", "TOKEN123")
    t2 = asyncio.get_running_loop().time()
    return b1, b2, (t1 - t0), (t2 - t1)

b1, b2, d1, d2 = asyncio.run(t6a())
check("بعد از دو بار 402، سومین تلاش موفق شد", b1 == b"\x89PNG\r\n\x1a\nPOLLIMG" and b2 == b1)
check("عکس اول: ۳ درخواست (۲ شکست + ۱ موفق)؛ عکس دوم: فقط ۱ درخواست موفق", len(poll_calls) == 4, str(len(poll_calls)))
check("توکن به‌عنوان Bearer فرستاده شد", all(c["headers"].get("Authorization") == "Bearer TOKEN123" for c in poll_calls))
check("referrer=parsagent در URL هست (سهمیهٔ بهتر تیر آزاد)", all("referrer=parsagent" in c["url"] for c in poll_calls))
check("فاصلهٔ صفِ دو عکسِ پشت‌سرهم رعایت شد (≥ 0.2s)", d2 >= 0.2, f"{d2:.3f}s")

# 402 پایدار → پیام فارسی
ai_media._download_bytes = lambda url, timeout=120, extra_headers=None: (
    (_ for _ in ()).throw(urllib.error.HTTPError(url, 402, "Payment Required", hdrs=None, fp=None)))
ai_media._POLL_LAST = 0.0
try:
    asyncio.run(ai_media._pollinations_image("x", ai_media.SIZES["square"], "flux", ""))
    check("402 پایدار باید MediaError می‌داد", False)
except ai_media.MediaError as e:
    check("402 پایدار → پیام فارسی «سهمیهٔ رایگان»", "402" in str(e) and "سهمیه" in str(e), str(e))

# ─────────────────────────── ۷) edge-tts: نصب خودکار + retry اتصال ───────────────────────────
print("\n۷) edge-tts — نصب خودکار و retry سه‌مرحله‌ای (WinError 10054):")

# ۷-الف) وقتی نصب نیست و نصب خودکار هم شکست می‌خورد → پیام راهنمای لانچر
saved_edge = sys.modules.pop("edge_tts", None)
ai_media._DEPS_TRIED.clear()


async def _coro_false():
    return False


ai_media.ensure_module = lambda *a, **k: _coro_false()  # نصب ناموفق

async def t7a():
    try:
        await ai_media._tts_scene("سلام", "fa-IR-FaridNeural", ai_media.MEDIA_DIR / "t.mp3")
        return None
    except ai_media.MediaError as e:
        return str(e)

err = asyncio.run(t7a())
check("نبود edge-tts → پیام شامل «نصب پیش‌نیازها» (لانچر)", err is not None and "نصب پیش‌نیازها" in err, str(err))

# ۷-ب) نصب خودکار موفق → ماژول تزریق‌شده استفاده می‌شود
class FakeCommunicate:
    def __init__(self, text, voice, rate=None, boundary=None): pass
    async def stream(self):
        yield {"type": "audio", "data": b"AUDIO-CHUNK-1"}
        yield {"type": "WordBoundary", "offset": 1e7, "duration": 5e6, "text": "سلام"}
        yield {"type": "audio", "data": b"-CHUNK-2"}

async def fake_install(mod, pkg, why, report=None):
    check("نصب خودکار برای edge_tts خواسته شد", mod == "edge_tts")
    sys.modules["edge_tts"] = types.SimpleNamespace(Communicate=FakeCommunicate)
    return True

ai_media.ensure_module = fake_install
sys.modules.pop("edge_tts", None)
ai_media._DEPS_TRIED.clear()
out_mp3 = ai_media.MEDIA_DIR / "voice-test.mp3"
r = asyncio.run(ai_media._tts_scene("سلام دنیا", "fa-IR-FaridNeural", out_mp3))
check("بعد از نصب خودکار، گویندگی موفق شد", out_mp3.exists() and out_mp3.read_bytes() == b"AUDIO-CHUNK-1-CHUNK-2")
check("زمان‌بندی کلمات جمع شد (برای زیرنویس)", len(r["words"]) == 1 and r["duration"] == 1.5)
out_mp3.unlink(missing_ok=True)

# ۷-ج) قطع‌شدن اتصال وسط استریم (WinError 10054) → ۳ بار تلاش، سومی موفق
attempts = {"n": 0}


class FlakyCommunicate:
    def __init__(self, text, voice, rate=None, boundary=None): pass
    async def stream(self):
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise ConnectionResetError(10054, "An existing connection was forcibly closed by the remote host")
        yield {"type": "audio", "data": b"OK-AFTER-RETRY"}
        yield {"type": "WordBoundary", "offset": 2e7, "duration": 5e6, "text": "دوباره"}

sys.modules["edge_tts"] = types.SimpleNamespace(Communicate=FlakyCommunicate)
ai_media.ensure_module = lambda *a, **k: _coro_false()  # دیگر لازم نیست — ماژول هست
out2 = ai_media.MEDIA_DIR / "voice-retry.mp3"
r2 = asyncio.run(ai_media._tts_scene("تست", "fa-IR-FaridNeural", out2))
check("دو بار 10054 → سومی موفق (retry خودکار)", attempts["n"] == 3 and out2.read_bytes() == b"OK-AFTER-RETRY",
      f"attempts={attempts['n']}")
out2.unlink(missing_ok=True)

# ۷-د) سه بار شکست پیاپی → خطای فارسیِ قابل‌فهم
class DeadCommunicate:
    def __init__(self, *a, **k): pass

    async def stream(self):
        raise ConnectionResetError(10054, "forcibly closed")
        yield  # تبدیل به async-generator تا با async for سازگار باشد

sys.modules["edge_tts"] = types.SimpleNamespace(Communicate=DeadCommunicate)
try:
    asyncio.run(ai_media._tts_scene("تست", "fa-IR-FaridNeural", out2))
    check("شکست پیاپی باید خطا می‌داد", False)
except ai_media.MediaError as e:
    check("۳ شکست → «بعد از ۳ تلاش ناموفق» فارسی", "۳ تلاش" in str(e) and "10054" in str(e), str(e))

# ─────────────────────────── ۸) ensure_module واقعی — گارد «فقط یک بار pip» ───────────────────────────
print("\n۸) ensure_module — یک‌بار بودنِ تلاش pip در هر اجرا:")
ai_media.ensure_module = real_ensure  # برگرداندن تابع واقعی (از بخش ۷)
ai_media._DEPS_TRIED.clear()
sys.modules.pop("edge_tts", None)
pip_calls = {"n": 0}


class _FakeProc:
    returncode = 1  # نصب «ناموفق» تا تابع False برگرداند

    async def communicate(self):
        return b"ERROR: no matching distribution found", b""


async def _fake_exec(*args, **kwargs):
    pip_calls["n"] += 1
    return _FakeProc()


_real_exec = asyncio.create_subprocess_exec
asyncio.create_subprocess_exec = _fake_exec
ok1 = asyncio.run(ai_media.ensure_module("edge_tts", "edge-tts>=6.1.0", "تست"))
ok2 = asyncio.run(ai_media.ensure_module("edge_tts", "edge-tts>=6.1.0", "تست"))
asyncio.create_subprocess_exec = _real_exec
check("اولین فراخوانی → تلاش pip (ناموفق) → False", ok1 is False)
check("گارد _DEPS_TRIED: دومین فراخوانی بدون pip → False", ok2 is False)
check("pip فقط در اولین فراخوانی زده شد — دوبار (PyPI + آینهٔ Tsinghua) و دیگر هرگز",
      pip_calls["n"] == 2, str(pip_calls))

# ─────────────────────────── ۹) llm_scenes — retry اتصال ───────────────────────────
print("\n۹) فیلم‌نامه با اتصال ناپایدار:")
llm_calls = {"n": 0}


async def flaky_llm(cfg, provider, model, msgs, temperature=0.7):
    llm_calls["n"] += 1
    if llm_calls["n"] < 3:
        raise ConnectionResetError(10054, "forcibly closed")
    return {"scenes": [{"narration": "صحنهٔ یک", "image_prompt": "scene one"},
                        {"narration": "صحنهٔ دو", "image_prompt": "scene two"}]}


scenes = asyncio.run(ai_media._llm_scenes(flaky_llm, {}, "zai", "glm-4.6", "تست", 3, "fa", 24))
check("دو بار قطع اتصال → سومی موفق", llm_calls["n"] == 3 and len(scenes) == 2, f"n={llm_calls['n']}")

# ─────────────────────────── ۱۰) launcher — REQUIRED کامل ───────────────────────────
print("\n۱۰) launcher — ماژول‌های رسانه در REQUIRED:")
import launcher  # noqa: E402
for mod in ("edge_tts", "PIL", "arabic_reshaper", "bidi", "imageio_ffmpeg"):
    check(f"launcher REQUIRED «{mod}» را چک می‌کند", mod in launcher.REQUIRED)
for mod in ("fastapi", "uvicorn", "multipart", "playwright"):
    check(f"ماژول قدیمی «{mod}» حذف نشده", mod in launcher.REQUIRED)
check("APP_VERSION = 2.12.0", launcher.APP_VERSION == "2.12.0")

# ─────────────────────────── جمع‌بندی ───────────────────────────
print(f"\n{'═' * 60}\nنتیجه: {len(PASS)} پاس / {len(FAIL)} خطا")
for f in FAIL:
    print("  ❌ " + f)
sys.exit(1 if FAIL else 0)
