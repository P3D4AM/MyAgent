# -*- coding: utf-8 -*-
"""
ParsAgent — چاپخانهٔ رسانه (تب «🧠 هوش مصنوعی» ← کارت‌های ساخت عکس و ویدیو)
==========================================================================

این ماژول الهام‌گرفته از پروژهٔ معروف چینیِ متن‌باز «MoneyPrinterTurbo»
(github.com/harry0703/MoneyPrinterTurbo) است: «با AI، با یک کلیک ویدیوی کوتاه
بساز» — آنجا موضوع را می‌دهید و خودش فیلم‌نامه می‌نویسد، صحنه‌ها را عکس‌گذاری
می‌کند، گویندگی، زیرنویس و موسیقی اضافه می‌کند و ویدیوی آمادهٔ انتشار تحویل
می‌دهد. ما همان زنجیره را برای پلتفرم‌های فارسی بازسازی کرده‌ایم:

  ۱) 🧠 فیلم‌نامه: مدل زبانی ماجرای صحنه‌به‌صحنه (گویندگی فارسی + پرامپت تصویر) می‌نویسد
  ۲) 🗣 گویندگی: edge-tts مایکروسافت — کاملاً رایگان، صدای طبیعی فارسی
     (فرید / دلارا) + زمان‌بندی کلمه‌به‌کلمه برای زیرنویس دقیق
  ۳) 🖼 تصویر هر صحنه: از AI تصویرساز (Z.ai GLM-Image / DALL·E 3) —
     و اگر کلید ندارید، به‌صورت خودکار روی Pollinations رایگانِ محدود می‌سازد
  ۴) 📝 زیرنویس: فارسیِ درست (رسم‌الخط + راست‌به‌چپ) روی نوار پایین تصویر حک می‌شود
  ۵) 🎬 ترکیب: ffmpeg (imageio-ffmpeg) — حرکت آرام دوربین (Ken Burns)،
     محوِ ورود/خروج، صدای گوینده و در صورت موجود بودن، موسیقی پس‌زمینهٔ ملایم
  ۶) 📦 خروجی: MP4 آمادهٔ انتشار در «رسانه‌ها» — همان‌جا که پست‌ها عکس می‌گیرند

ساخت عکس هم همین‌جاست: چند سرویس پولی و رایگان + زنجیرهٔ جایگزین خودکار.
اگر کتابخانهٔ لازم (مثل edge-tts یا Pillow) نصب نباشد، خودکار نصب می‌شود.

۲.۱۴.۰ — خطای 404 «مدل وجود ندارد» (Groq مدل‌های Llama 3.x را برای کلیدهای
معمولی بسته است): فیلم‌نامه‌نویسی حالا مدل حذف‌شده را بی‌صدا با جایگزین
رسمی عوض می‌کند (ai_agent.resolve_model) و خطای 404 دیگر ۳ بار تلاشِ
بی‌فایده نمی‌کند — همان لحظه با پیام فارسی «دکمهٔ 🔄 مدل‌های زنده» اعلام
می‌شود.

۲.۱۳.۰ — پروکسی سرویس‌های AI هم این‌جا اعمال می‌شود (تنظیمات ← هوش
مصنوعی ← «پروکسی فراخوانی سرویس‌ها»): خطای 403 سرویس‌هایی مثل Groq
و Gemini برای IP ایران است؛ حالا فیلم‌نامه، عکس‌سازی و دانلودها از
پروکسی شما عبور می‌کنند و پیام خطا فارسیِ راه‌حل‌دار است.
"""
from __future__ import annotations

import asyncio
import base64
import importlib
import json
import math
import os
import random
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

BASE = Path(__file__).resolve().parent
MEDIA_DIR = BASE / "media"
VIDEOS_DIR = MEDIA_DIR / "videos"
MUSIC_DIR = MEDIA_DIR / "music"      # اختیاری — فایل‌های mp3 خودتان را اینجا بگذارید
for _d in (MEDIA_DIR, VIDEOS_DIR, MUSIC_DIR):
    try:
        _d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

# برای سرویس‌های اینترنتی همان پروکسی سیستم (VPN کاربر)؛ لوکال بدون پروکسی.
_DIRECT = urllib.request.build_opener(urllib.request.ProxyHandler({}))

# ۲.۱۳.۰ — پروکسی مشترک سرویس‌های AI از ai_agent می‌آید (تنظیمات ←
# هوش مصنوعی ← «پروکسی فراخوانی سرویس‌ها»). ریشهٔ باگ: درخواست‌های پایتون
# به‌تنهایی از VPN مرورگر عبور نمی‌کنند و سرویس‌هایی مثل Groq/Gemini
# در ایران 403 «Forbidden» می‌دهند.
try:
    from ai_agent import resolve_ai_proxy as _resolve_proxy
except Exception:  # ماژول باید بدون ai_agent هم قابل استفاده بماند
    _resolve_proxy = None


def _proxy_map(ai_cfg: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """نقشهٔ پروکسی برای درخواست‌های این ماژول — خطای آن فارسی می‌شود."""
    if _resolve_proxy is None:
        return None
    try:
        return _resolve_proxy(ai_cfg)
    except Exception as e:
        raise MediaError(str(e))


class MediaError(Exception):
    """خطای قابل‌فهم برای کاربر."""


# ════════════════════════════════════════════════════════════════════ کاتالوگ تصویرسازها
# ترتیب مهم است: Z.ai اولِ لیست است (پیشنهاد ما). همه OpenAI-سازگارند.
# ⚠️ ۲.۱۲.۰ — طبق مستند رسمی docs.z.ai، تنها مدل تصویرسازِ معتبر روی
# api.z.ai کدِ «glm-image» است. مدل‌های CogView فقط روی پلتفرم چینی
# open.bigmodel.cn هستند و اینجا خطای 1211 «Unknown Model» می‌دهند.
IMAGE_PROVIDERS: Dict[str, Dict[str, Any]] = {
    "zai": {
        "name": "Z.ai — تصویرساز",
        "base": "https://api.z.ai/api/paas/v4",
        "key_field": "zai",
        "note": "پیشنهادی — مدل GLM-Image (کد: glm-image)؛ ارزان و باکیفیت — برای شارژ: z.ai/manage-apikey/apikey-list",
        "models": [
            {"id": "glm-image", "name": "GLM-Image", "tag": "پیشنهادی",
             "note": "تنها مدل تصویرسازِ معتبر روی api.z.ai (مستند رسمی docs.z.ai — بقیهٔ کدها خطای 1211 می‌گیرند)"},
        ],
    },
    "openai": {
        "name": "OpenAI — تصویرساز",
        "base": "https://api.openai.com/v1",
        "key_field": "openai",
        "note": "DALL·E 3 و gpt-image-1 — پولی",
        "models": [
            {"id": "gpt-image-1", "name": "GPT Image 1", "tag": "پیشرفته",
             "note": "نسل جدید OpenAI"},
            {"id": "dall-e-3", "name": "DALL·E 3", "tag": "پولی",
             "note": "کیفیت بالا، خلاق"},
        ],
    },
    "pollinations": {
        "name": "Pollinations — رایگانِ محدود",
        "base": "",
        "key_field": "pollinations",
        "note": "بدون کلید هم کار می‌کند ولی محدود (۱ درخواست هم‌زمان، فاصلهٔ ~۱۵ ثانیه — خطای 402 یعنی همین)؛ برای سهمیهٔ بهتر توکن رایگان auth.pollinations.ai را در تنظیمات ← کلید Pollinations بگذارید",
        "models": [
            {"id": "flux", "name": "Flux", "tag": "رایگان",
             "note": "رایگانِ محدود — کیفیت خوب"},
            {"id": "turbo", "name": "Turbo", "tag": "رایگان",
             "note": "سریع‌ترین حالت رایگانِ محدود"},
        ],
    },
}

# نسبت‌های تصویر — اندازهٔ api: مقادیر توصیه‌شدهٔ مستند رسمی Z.ai برای
# glm-image (1024x1024, 768x1344, 864x1152, 1344x768, 1152x864, 1440x720, 720x1440).
# w/h هم برای Pollinations استفاده می‌شود.
SIZES: Dict[str, Dict[str, Any]] = {
    "square":    {"name": "مربع ۱:۱ (پست اینستاگرام/لینکدین)", "api": "1024x1024", "w": 1024, "h": 1024},
    "portrait":  {"name": "عمودی ۹:۱۶ (استوری/ریلز)", "api": "768x1344", "w": 768, "h": 1344},
    "landscape": {"name": "افقی ۱۶:۹ (توییتر/یوتیوب)", "api": "1344x768", "w": 1344, "h": 768},
}

# نسبت‌های ویدیو
ASPECTS: Dict[str, Dict[str, Any]] = {
    "9:16": {"name": "عمودی ۹:۱۶ — ریلز/شورتس/استوری", "w": 1080, "h": 1920},
    "1:1":  {"name": "مربع ۱:۱ — پست فید", "w": 1080, "h": 1080},
    "16:9": {"name": "افقی ۱۶:۹ — یوتیوب/توییتر", "w": 1920, "h": 1080},
}

# صداهای edge-tts — رایگان و بدون کلید (فارسی + چند زبان پرکاربرد)
VOICES: List[Dict[str, str]] = [
    {"id": "fa-IR-FaridNeural", "name": "فرید — مرد، فارسی (ایران)", "lang": "fa"},
    {"id": "fa-IR-DilaraNeural", "name": "دلارا — زن، فارسی (ایران)", "lang": "fa"},
    {"id": "en-US-GuyNeural", "name": "Guy — مرد، انگلیسی (آمریکا)", "lang": "en"},
    {"id": "en-US-JennyNeural", "name": "Jenny — زن، انگلیسی (آمریکا)", "lang": "en"},
    {"id": "ar-SA-HamedNeural", "name": "حامد — مرد، عربی", "lang": "ar"},
    {"id": "tr-TR-AhmetNeural", "name": "Ahmet — مرد، ترکی استانبولی", "lang": "tr"},
]


def _http_error_fa(code: int, detail: str) -> str:
    """ترجمهٔ خطاهای رایج سرویس‌های تصویرساز به پیام فارسیِ قابل‌عمل (۲.۱۲.۰)."""
    raw = detail or ""
    d = raw.lower()
    if "1211" in raw or "unknown model" in d:
        return ("کد مدل نامعتبر است (خطای 1211) — روی Z.ai فقط مدل «glm-image» معتبر است؛ "
                "از دراپ‌داون «مدل» همان را انتخاب کنید (مدل‌های CogView فقط روی پلتفرم چینی bigmodel.cn کار می‌کنند)")
    if "1113" in raw or "insufficient balance" in d or "recharge" in d:
        return ("موجودی حساب Z.ai کافی نیست (خطای 1113) — از پنل کلیدهای Z.ai موجودی را چک و شارژ کنید: "
                "z.ai/manage-apikey/apikey-list — یا تصویرساز «Pollinations» را انتخاب کنید (رایگانِ محدود)")
    if code == 403:
        if "user location is not supported" in d:
            return ("سرویس Gemini منطقهٔ شما (ایران) را نمی‌پذیرد (خطای 403) — در «تنظیمات ← هوش مصنوعی ← "
                    "پروکسی فراخوانی سرویس‌ها» آدرس VPN را بدهید (مثلاً http://127.0.0.1:10809) یا "
                    "تصویرساز Z.ai را انتخاب کنید که از ایران مستقیم کار می‌کند")
        return ("سرویس درخواست را رد کرد (خطای 403 Forbidden) — اگر کلید درست است یعنی IP ایران نزد این سرویس "
                "مسدود است. راه حل: در «تنظیمات ← هوش مصنوعی ← پروکسی فراخوانی سرویس‌ها» آدرس VPN را بدهید "
                "(مثلاً http://127.0.0.1:10809) یا تصویرساز Z.ai/Pollinations را انتخاب کنید")
    if code == 401:
        return "کلید API نامعتبر یا منقضی است (خطای 401) — کلید را از «تنظیمات ← هوش مصنوعی» دوباره وارد کنید"
    if code == 402:
        return ("سهمیهٔ رایگان این سرویس فعلاً پر است (خطای 402) — خودش بعد از چند لحظه دوباره تلاش می‌کند؛ "
                "اگر تکرار شد از توکن رایگان Pollinations یا کلید شارژشدهٔ Z.ai استفاده کنید")
    if code == 429:
        return "تعداد درخواست‌ها زیاد است (خطای 429) — کمی صبر کنید و دوباره بسازید"
    return f"خطای {code} از سرویس تصویرساز{(' — ' + raw) if raw else ''}"


def _http_json(url: str, headers: Dict[str, str], payload: Dict[str, Any],
               timeout: int = 180, proxies: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": "ParsAgent/2.13", **headers})
    if "127.0.0.1" in url or "localhost" in url:
        opener = _DIRECT            # لوکال هرگز از پروکسی عبور نمی‌کند
    elif proxies:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxies))
    else:
        opener = _DIRECT            # پروکسی‌ای تنظیم نشده → مستقیم
    try:
        with opener.open(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", "ignore")[:400]
        except Exception:
            detail = ""
        raise MediaError(_http_error_fa(e.code, detail))
    except urllib.error.URLError as e:
        reason = str(getattr(e, "reason", e))
        if proxies:
            raise MediaError(f"از راه پروکسی به سرویس وصل نشد: {reason} — آدرس پروکسی و روشن بودن VPN را چک کنید")
        raise MediaError(f"ارتباط با سرویس تصویرساز برقرار نشد: {reason} — اینترنت/VPN را چک کنید")


def _download_bytes(url: str, timeout: int = 120, extra_headers: Optional[Dict[str, str]] = None,
                    proxies: Optional[Dict[str, str]] = None) -> bytes:
    headers = {"User-Agent": "Mozilla/5.0 ParsAgent/2.13"}
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, headers=headers)
    if "127.0.0.1" in url or "localhost" in url:
        opener = _DIRECT
    elif proxies:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxies))
    else:
        opener = _DIRECT
    with opener.open(req, timeout=timeout) as r:
        return r.read()


async def _download_bytes_retry(url: str, tries: int = 3,
                                proxies: Optional[Dict[str, str]] = None) -> bytes:
    """دانلود نتیجهٔ سرویس (لینک عکس) — با تلاش مجدد خودکار روی
    قطع‌شدن وسط کارِ اتصال (مثل WinError 10054)."""
    for attempt in range(tries):
        try:
            return await asyncio.to_thread(_download_bytes, url, proxies=proxies)
        except urllib.error.HTTPError:
            raise
        except Exception:  # noqa — اتصال ناپایدار: صبر و تلاش مجدد
            if attempt == tries - 1:
                raise
            await asyncio.sleep(2 + 2 * attempt)
    raise MediaError("دانلود تصویر ناموفق بود")  # غیرقابل‌رسیدن


# ─── ۲.۱۲.۰ — خودترمیمی: نصب خودکار وابستگی‌های رسانه ───────────────
# ریشهٔ باگ «کتابخانهٔ edge-tts نصب نیست»: کاربرانی که از نسخه‌های قدیمی
# ارتقا داده بودند ماژول‌های قدیمی نصب بود و لانچر نصبِ تازه را لازم
# نمی‌دید؛ حالا لانچر هم این‌ها را چک می‌کند و خودِ پنل هم در صورت
# نیاز یک‌بار (در هر اجرا) نصب خودکار می‌کند.
_DEPS_TRIED: set = set()


async def ensure_module(mod: str, pip_pkg: str, why: str,
                        report: Optional[Callable[[str], None]] = None) -> bool:
    """اگر ماژول import نشد، یک بار در طول اجرای سرور با pip نصبش می‌کند."""
    try:
        importlib.import_module(mod)
        return True
    except ImportError:
        pass
    if pip_pkg in _DEPS_TRIED:
        return False
    _DEPS_TRIED.add(pip_pkg)

    def _say(m: str) -> None:
        if report:
            try:
                report(m)
            except Exception:
                pass

    _say(f"📦 «{why}» نصب نیست — نصب خودکار {pip_pkg} شروع شد (یک بار؛ چند لحظه صبر کنید)…")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    indexes = [None, "https://pypi.tuna.tsinghua.edu.cn/simple"]  # PyPI، بعد آینهٔ چین (اینترنت ایران)
    try:
        for idx in indexes:
            cmd = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check",
                   "--only-binary=:all:", pip_pkg]
            if idx:
                cmd += ["-i", idx]
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT, env=env)
            out, _ = await asyncio.wait_for(proc.communicate(), timeout=420)
            if proc.returncode == 0:
                importlib.invalidate_caches()
                try:
                    importlib.import_module(mod)
                    _say(f"✅ {pip_pkg} نصب شد — ادامه می‌دهیم")
                    return True
                except ImportError:
                    pass
            text = (out or b"").decode("utf-8", "ignore")
            lines = [ln for ln in text.strip().splitlines() if ln.strip()]
            _say(f"⚠ نصب {pip_pkg} از {'آینهٔ Tsinghua' if idx else 'PyPI'} نشد: "
                 f"{lines[-1][:160] if lines else 'خطای نامشخص'}")
        _say(f"⌨ اگر دوباره نشد: در لانچر دکمهٔ «نصب پیش‌نیازها» را بزنید یا در خط فرمان: pip install {pip_pkg}")
    except Exception as e:
        _say(f"⚠ نصب خودکار {pip_pkg} ناموفق بود: {e}")
    return False


# ─── ۲.۱۲.۰ — Pollinations: تیر رایگان یعنی «۱ هم‌زمان + فاصلهٔ ~۱۵ ثانیه».
# بدون این صف‌بندی، درخواست‌های پشت‌سرهم (مثلاً صحنه‌های ویدیو) خطای 402 می‌گیرند.
_POLL_LOCK = asyncio.Lock()
_POLL_LAST = 0.0
_POLL_MIN_GAP = 16.0            # فاصلهٔ حداقلی بین دو درخواست (تیر رایگان)
_POLL_RETRY_WAITS = (20.0, 35.0)  # صبر بعد از 402/429 — سهمیهٔ IP فعلاً پر است
_TTS_RETRY_WAITS = (1.5, 3.0)     # صبر بین تلاش‌های گویندگی (اتصال ناپایدار)
_LLM_RETRY_WAITS = (2.0, 4.0)    # صبر بین تلاش‌های فیلم‌نامه (اتصال ناپایدار)


async def _pollinations_image(prompt: str, size: Dict[str, Any], model: str, token: str = "",
                             proxies: Optional[Dict[str, str]] = None) -> bytes:
    """ساخت عکس با Pollinations — صف سراسری + فاصلهٔ حداقلی + توکن اختیاری
    + تلاش مجدد خودکار وقتی سهمیهٔ رایگانِ IP فعلاً پر باشد (402/429)."""
    global _POLL_LAST
    q = urllib.parse.quote(prompt[:1500], safe="")
    url = (f"https://image.pollinations.ai/prompt/{q}"
           f"?width={size['w']}&height={size['h']}"
           f"&seed={random.randrange(1, 10**6)}&nologo=true&model={model}"
           f"&referrer=parsagent")  # referrer برای سهمیهٔ بهترِ تیر آزاد
    headers: Dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    async with _POLL_LOCK:
        loop = asyncio.get_running_loop()
        gap = _POLL_LAST + _POLL_MIN_GAP - loop.time()
        if gap > 0:
            await asyncio.sleep(gap)
        for attempt in range(3):
            try:
                _POLL_LAST = loop.time()
                return await asyncio.to_thread(_download_bytes, url, 150, headers, proxies)
            except urllib.error.HTTPError as e:
                if e.code in (402, 429, 403, 500, 502, 503) and attempt < 2:
                    await asyncio.sleep(_POLL_RETRY_WAITS[min(attempt, len(_POLL_RETRY_WAITS) - 1)])  # سهمیهٔ رایگان — صبر و تلاش مجدد
                    continue
                raise MediaError(_http_error_fa(e.code, ""))
            except Exception:  # noqa — اتصال ناپایدار (10054 و…)
                if attempt < 2:
                    await asyncio.sleep(3 + 2 * attempt)
                    continue
                raise
    raise MediaError("Pollinations پاسخ نداد — دوباره تلاش کنید")


def _slug(text: str, limit: int = 28) -> str:
    s = re.sub(r"[^A-Za-z0-9\-]+", "-", (text or "").strip()).strip("-").lower()
    return (s or "ai")[:limit]


def _now_stamped(kind: str, name: str) -> str:
    return f"{kind}-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{_slug(name)}.png"


# ════════════════════════════════════════════════════════════════════ ساخت عکس با AI
async def generate_image(ai_cfg: Dict[str, Any], prompt: str, *, provider: str = "zai",
                        model: str = "", size_key: str = "square", out_name: str = "",
                        progress: Optional[Callable[[int, str], None]] = None) -> Dict[str, Any]:
    """یک عکس با AI می‌سازد و در «رسانه‌ها» ذخیره می‌کند.

    زنجیرهٔ جایگزین: اگر سرویس انتخابی کلید نداشت یا خطا داد، خودکار به
    Pollinations (رایگان و بدون کلید) برمی‌گردد تا کارِ کاربر هرگز نیمه‌کاره نماند.
    """
    prompt = (prompt or "").strip()
    if not prompt:
        raise MediaError("متن توضیح عکس (پرامپت) خالی است")
    size = SIZES.get(size_key, SIZES["square"])
    px = _proxy_map(ai_cfg)  # ۲.۱۳.۰ — پروکسی سرویس‌های AI (برای ایران)
    keys = ai_cfg.get("api_keys") or {}
    tried: List[str] = []

    def _report(pct: int, msg: str) -> None:
        if progress:
            try:
                progress(pct, msg)
            except Exception:
                pass

    chain: List[Tuple[str, str]] = []
    if provider and provider in IMAGE_PROVIDERS and provider != "pollinations":
        ids = [m["id"] for m in IMAGE_PROVIDERS[provider]["models"]]
        m = model if model in ids else IMAGE_PROVIDERS[provider]["models"][0]["id"]
        if model and model not in ids:
            _report(22, f"⚠ مدل «{model}» روی این سرویس معتبر نیست — «{m}» جایگزین شد")
        chain.append((provider, m))
    chain.append(("pollinations", model if (provider == "pollinations" and model in ("flux", "turbo")) else "flux"))

    data_bytes: Optional[bytes] = None
    used = ""
    for prov, mdl in chain:
        info = IMAGE_PROVIDERS[prov]
        key = ""
        if prov == "pollinations":
            # توکن اختیاری است — بدون توکن هم (تیر رایگانِ محدود) کار می‌کند
            key = (keys.get("pollinations") or "").strip()
        elif info.get("key_field"):
            key = (keys.get(info["key_field"]) or "").strip()
            if not key:
                tried.append(f"{info['name']}: کلید API ندارد")
                continue
        _report(30, f"در حال ساخت عکس با {info['name']} ({mdl}) …")
        for attempt in range(1):  # تلاش مجدد داخلی خودش را دارد (Pollinations: صف + ۳ تلاش)
            try:
                if prov == "pollinations":
                    data_bytes = await _pollinations_image(prompt, size, mdl, key, proxies=px)
                else:
                    payload = {"model": mdl, "prompt": prompt[:3800], "size": size["api"], "n": 1}
                    if mdl == "dall-e-3":
                        payload["response_format"] = "url"
                    res = await asyncio.to_thread(
                        _http_json, info["base"] + "/images/generations",
                        {"Authorization": f"Bearer {key}"}, payload, proxies=px)
                    item = ((res.get("data") or [{}])[0])
                    if item.get("b64_json"):
                        data_bytes = base64.b64decode(item["b64_json"])
                    elif item.get("url"):
                        data_bytes = await _download_bytes_retry(item["url"], proxies=px)
                    if not data_bytes:
                        raise MediaError("سرویس تصویری برنگرداند (احتمالاً فیلتر محتوا) — پرامپت را عوض کنید")
                if data_bytes:
                    used = f"{info['name']} · {mdl}"
                    break
            except MediaError as e:
                tried.append(f"{info['name']}: {e}")
                data_bytes = None
                continue
            except Exception as e:  # noqa
                tried.append(f"{info['name']}: {e}")
                data_bytes = None
                continue
        if data_bytes:
            break
    if not data_bytes:
        raise MediaError("هیچ سرویس تصویرسازی جواب نداد — " + " | ".join(tried[:3]))

    # ذخیره در رسانه‌ها (فرمت واقعی را از بایت‌ها تشخیص می‌دهیم)
    kind = "png" if data_bytes[:8] == b"\x89PNG\r\n\x1a\n" else ("jpg" if data_bytes[:3] == b"\xff\xd8\xff" else "png")
    name = out_name or _now_stamped("ai-image", prompt)
    name = re.sub(r"\.(png|jpg|jpeg|webp)$", "", name, flags=re.I) + f".{kind}"
    path = MEDIA_DIR / name
    path.write_bytes(data_bytes)
    _report(100, f"✅ عکس ساخته شد: {name}")
    return {"ok": True, "file": name, "path": str(path), "provider": used,
            "url": f"/media/{urllib.parse.quote(name)}", "size": size["api"]}


# ════════════════════════════════════════════════════════════════════ ویدیوی خودکار (سبک MoneyPrinterTurbo)
async def _llm_scenes(llm_json: Callable, ai_cfg: Dict[str, Any], provider: str, model: str,
                      topic: str, n_scenes: int, lang: str, seconds: int) -> List[Dict[str, Any]]:
    """فیلم‌نامهٔ صحنه‌به‌صحنه — مثل MoneyPrinterTurbo: ماجرای هر صحنه + پرامپت تصویرش."""
    per = max(4, min(20, seconds // max(n_scenes, 1)))
    system = (
        "تو فیلم‌نامه‌نویس ویدیوهای کوتاه شبکه‌های اجتماعی هستی (سبک MoneyPrinterTurbo). "
        f"موضوع را به {n_scenes} صحنهٔ پیوسته تبدیل کن که مجموعاً حدود {seconds} ثانیه ویدیو شود. "
        f"زبان گویندگی: {'فارسی' if lang == 'fa' else 'انگلیسی'}. "
        "هر صحنه فقط یک جملهٔ کوتاه و طبیعی برای «بخواندن» دارد (۶ تا ۱۴ کلمه) و یک image_prompt انگلیسی "
        "برای تصویر همان صحنه (سبک سینمایی، نور خوب، بدون متن داخل تصویر). متن داخل تصویر ممنوع. "
        'خروجی فقط JSON: {"scenes":[{"narration":"...","image_prompt":"..."}]}'
    )
    data = None
    msgs = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"موضوع ویدیو: {topic}"},
    ]
    for attempt in range(3):  # اتصالِ ناپایدار (مثل WinError 10054) — خودکار تلاش مجدد
        try:
            data = await llm_json(ai_cfg, provider, model, msgs, temperature=0.7)
            break
        except Exception as e:  # noqa
            s = str(e)
            # ۲.۱۳.۰ — خطای دائمی (403/401) دوباره امتحان نمی‌شود؛ فقط وقتِ کاربر را می‌گرفت
            # ۲.۱۴.۰ — 404 (مدل حذف‌شده) هم دائمی است: سرویس مدل را بسته؛ تلاش مجدد بی‌فایده
            if "خطای 403" in s or "خطای 401" in s or "خطای 404" in s or "کلید API" in s \
                    or "does not exist or you do not have access" in s:
                raise MediaError("نوشتن فیلم‌نامه ممکن نشد — " + s)
            if attempt == 2:
                raise
            await asyncio.sleep(_LLM_RETRY_WAITS[min(attempt, len(_LLM_RETRY_WAITS) - 1)])
    scenes = []
    for s in ((data or {}).get("scenes") or [])[:n_scenes * 2]:
        nar = str(s.get("narration") or "").strip()
        img = str(s.get("image_prompt") or "").strip()
        if nar:
            scenes.append({"narration": nar, "image_prompt": img or topic})
    if len(scenes) < 2:
        raise MediaError("مدل، فیلم‌نامهٔ معتبری نساخت — دوباره تلاش کنید یا مدل بهتری انتخاب کنید")
    return scenes[:n_scenes]


async def _tts_scene(text: str, voice: str, out_mp3: Path) -> Dict[str, Any]:
    """گویندگی رایگان با edge-tts + جمع‌آوری زمان کلمات (برای زیرنویس دقیق).

    ۲.۱۲.۰ — اگر کتابخانه نصب نباشد یک‌بار خودکار نصب می‌شود؛ اگر اتصال
    وسط کار قطع شود (مثل WinError 10054) تا ۳ بار خودکار تلاش می‌شود.
    """
    try:
        import edge_tts
    except ImportError:
        ok = await ensure_module("edge_tts", "edge-tts>=6.1.0", "گویندگی ویدیو (edge-tts)")
        if not ok:
            raise MediaError("کتابخانهٔ edge-tts نصب نیست و نصب خودکار هم نشد — "
                             "در لانچر دکمهٔ «نصب پیش‌نیازها» را بزنید یا در خط فرمان: pip install edge-tts")
        import edge_tts

    async def _stream() -> Tuple[bytes, List[Dict[str, Any]]]:
        buf = bytearray()
        words: List[Dict[str, Any]] = []
        # boundary=WordBoundary — زمان دقیق هر کلمه برای زیرنویس (پیش‌فرض نسخهٔ 7+ جمله‌ای است)
        try:
            communicate = edge_tts.Communicate(text, voice, rate="+4%", boundary="WordBoundary")
        except TypeError:  # نسخه‌های قدیمی edge-tts — WordBoundary خودکار می‌آمد
            communicate = edge_tts.Communicate(text, voice, rate="+4%")
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buf.extend(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                words.append({"t": chunk["offset"] / 1e7, "d": chunk["duration"] / 1e7,
                              "w": chunk.get("text", "")})
        return bytes(buf), words

    data, words, last_err = b"", [], None
    for attempt in range(3):  # WinError 10054 و… — اتصالِ ناپایدار خودکار دوباره تلاش می‌شود
        try:
            data, words = await _stream()
            last_err = None
            break
        except Exception as e:  # noqa
            last_err = e
            if attempt < 2:
                await asyncio.sleep(_TTS_RETRY_WAITS[min(attempt, len(_TTS_RETRY_WAITS) - 1)])
    if last_err is not None:
        raise MediaError(f"گویندگی بعد از ۳ تلاش ناموفق بود (اتصال ناپایدار؟ اینترنت/VPN را چک کنید): {last_err}")
    if not data:
        raise MediaError("گویندهٔ edge-tts صدایی برنگرداند — دوباره تلاش کنید")
    out_mp3.parent.mkdir(parents=True, exist_ok=True)
    with open(out_mp3, "wb") as f:
        f.write(data)
    dur = (words[-1]["t"] + words[-1]["d"]) if words else max(3.0, len(text.split()) * 0.42)
    return {"words": words, "duration": round(dur, 3), "file": out_mp3}


def _ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        raise MediaError("کتابخانهٔ imageio-ffmpeg نصب نیست — در لانچر دکمهٔ «نصب پیش‌نیازها» را بزنید یا در خط فرمان: pip install imageio-ffmpeg")


def _run_ffmpeg(args: List[str], timeout: int = 900) -> None:
    # -threads 4: مصرف حافظه/سی‌پی‌یو محدود — روی سیستم‌های ضعیف هم پایدار
    cmd = [_ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y", "-threads", "4"] + args
    r = subprocess.run(cmd, capture_output=True, timeout=timeout)
    if r.returncode != 0:
        tail = r.stderr.decode("utf-8", "ignore")[-400:]
        raise MediaError(f"ترکیب ویدیو ناموفق بود (ffmpeg): {tail or 'خطای نامشخص'}")


# ---------- زیرنویس فارسی روی تصویر (رسم‌الخط + راست‌به‌چپ) ----------
_FONT_CANDIDATES = ["segoeui.ttf", "SegoeUI.ttf", "tahoma.ttf", "Tahoma.ttf",
                    "arial.ttf", "arialbd.ttf", "DejaVuSans.ttf", "arial.ttf"]

# اگر Pillow با موتور Raqm ساخته شده باشد، خودش رسم‌الخط و راست‌به‌چپ را
# درست انجام می‌دهد و باید متنِ خام + direction="rtl" بدهیم؛ وگرنه باید
# دستی شکل‌دهی (arabic_reshaper) و برگرداندن (bidi) کنیم و متن نمایشی بدهیم.
# (نکتهٔ حیاتی: دادن متنِ از-قبل-برگردانده به موتور raqm = دوبار برگرداندن!)
_RAQM: Optional[bool] = None


def _has_raqm() -> bool:
    global _RAQM
    if _RAQM is None:
        try:
            from PIL import features
            _RAQM = bool(features.check("raqm"))
        except Exception:
            _RAQM = False
    return _RAQM


def _draw_text(draw, xy, text, font, **kw):
    """رندر یک سطر فارسی — هر دو حالتِ موتور Pillow درست کار می‌کند."""
    if _has_raqm():
        return draw.text(xy, text, font=font, fill=kw.get("fill"),
                        direction="rtl", language="fa",
                        stroke_width=kw.get("stroke_width", 0),
                        stroke_fill=kw.get("stroke_fill"))
    return draw.text(xy, _shape_text(text), font=font, **kw)


def _text_width(draw, text, font) -> float:
    if _has_raqm():
        try:
            return draw.textlength(text, font=font, direction="rtl", language="fa")
        except Exception:
            pass
    return draw.textlength(_shape_text(text), font=font)

def _load_font(px: int):
    from PIL import ImageFont
    for name in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(name, px)
        except Exception:
            continue
    try:
        from PIL import ImageFont  # noqa
        return ImageFont.load_default()
    except Exception:
        raise MediaError("فونت مناسب برای زیرنویس پیدا نشد (Tahoma/Segoe UI نصب نیست؟)")


def _shape_text(text: str) -> str:
    """فارسی/عربی را برای رندر درست شکل‌دهی و جهت‌دهی می‌کند."""
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(text))
    except ImportError:
        return text  # بدون کتابخانه هم انگلیسی درست رندر می‌شود


def _compose_scene_image(material: Path, out_png: Path, w: int, h: int,
                         narration: str, accent: Tuple[int, int, int]) -> None:
    """تصویر صحنه + نوار زیرنویس فارسی → یک PNG آمادهٔ ویدیو."""
    from PIL import Image, ImageDraw, ImageEnhance
    if material and Path(material).exists():
        img = Image.open(material).convert("RGB")
        # برش مرکزی به نسبت هدف
        sr, tr = img.width / img.height, w / h
        if sr > tr:
            nw = int(img.height * tr)
            img = img.crop(((img.width - nw) // 2, 0, (img.width - nw) // 2 + nw, img.height))
        else:
            nh = int(img.width / tr)
            img = img.crop((0, (img.height - nh) // 2, img.width, (img.height - nh) // 2 + nh))
        img = img.resize((w, h), Image.LANCZOS)
        img = ImageEnhance.Color(img).enhance(1.08)
        canvas = img
    else:
        # پس‌زمینهٔ گرادیان — وقتی تصویر صحنه در دسترس نیست، صحنه هنوز قابل‌قبول بماند
        canvas = Image.new("RGB", (w, h))
        px = canvas.load()
        for y in range(h):
            t = y / max(1, h - 1)
            r = int(14 + (accent[0] // 12) * (1 - t))
            g = int(18 + (accent[1] // 12) * (1 - t))
            b = int(24 + (accent[2] // 12) * (1 - t))
            for x in range(0, w, 16):
                for dx in range(min(16, w - x)):
                    px[x + dx, y] = (r, g, b)
    draw = ImageDraw.Draw(canvas, "RGBA")
    # نوار نیمه‌شفاف پایین + متنِ شکل‌دهی‌شدهٔ راست‌به‌چپ
    band_h = max(140, h // 6)
    base = canvas.convert("RGBA")
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay.paste(Image.new("RGBA", (w, band_h), (8, 10, 14, 168)), (0, h - band_h))
    canvas = Image.alpha_composite(base, overlay)
    draw = ImageDraw.Draw(canvas, "RGBA")
    font = _load_font(max(34, h // 26))
    # شکستن سطر بر اساس پهنای واقعی — روی متنِ منطقی (راست‌به‌چپ خودش هنگام رندر اعمال می‌شود)
    max_w = int(w * 0.86)
    lines, cur = [], ""
    for word in (narration or "").split(" "):
        trial = (cur + " " + word).strip()
        if _text_width(draw, trial, font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    lines = lines[:3]
    lh = font.size + max(14, h // 90)
    total = lh * len(lines)
    y = h - band_h + (band_h - total) // 2 + h // 200
    for ln in lines:
        tw = _text_width(draw, ln, font)
        _draw_text(draw, ((w - tw) / 2, y), ln, font,
                   fill=(255, 255, 255, 245),
                   stroke_width=max(1, h // 900), stroke_fill=(0, 0, 0, 180))
        y += lh
    # خط تاکید بالای نوار (رنگ برند)
    draw.rectangle([0, h - band_h, w, h - band_h + max(4, h // 350)], fill=(*accent, 255))
    canvas.convert("RGB").save(out_png, "PNG")


def _srt_from_words(words: List[Dict[str, Any]], path: Path) -> None:
    """زیرنویس SRT جداگانه هم ذخیره می‌کنیم (برای پلتفرم‌هایی که فایل کپشن می‌گیرند)."""
    def _t(s: float) -> str:
        hh = int(s // 3600); mm = int(s % 3600 // 60); ss = int(s % 60); ms = int((s - int(s)) * 1000)
        return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"
    if not words:
        return
    cues, cur = [], []  # cur = لیست (t, d, w)
    for w in words:
        if cur and w["t"] - cur[0][0] > 3.5:
            cues.append((cur[0][0], cur[-1][0] + cur[-1][1], " ".join(x[2] for x in cur)))
            cur = []
        cur.append((w["t"], w["d"], w["w"]))
    if cur:
        cues.append((cur[0][0], cur[-1][0] + cur[-1][1], " ".join(x[2] for x in cur)))
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, txt) in enumerate(cues, 1):
            # SRT باید متنِ منطقیِ خام باشد — پلیرها خودشان رسم‌الخط می‌کنند
            f.write(f"{i}\n{_t(a)} --> {_t(b)}\n{txt}\n\n")


async def generate_video(llm_json: Callable, ai_cfg: Dict[str, Any], *, topic: str,
                         provider: str, model: str, voice: str = "fa-IR-FaridNeural",
                         aspect: str = "9:16", seconds: int = 45, material: str = "ai",
                         motion: str = "zoom", progress: Optional[Callable[[int, str], None]] = None,
                         images: Optional[List[str]] = None) -> Dict[str, Any]:
    """ویدیوی کامل با AI — سبک MoneyPrinterTurbo: موضوع بده، ویدیوی آمادهٔ انتشار بگیر."""
    topic = (topic or "").strip()
    if not topic:
        raise MediaError("موضوع ویدیو خالی است")
    asp = ASPECTS.get(aspect, ASPECTS["9:16"])
    w, h = asp["w"], asp["h"]
    seconds = max(15, min(180, int(seconds)))
    n_scenes = max(3, min(10, seconds // 8))
    lang = "fa" if str(voice).startswith("fa") else ("ar" if str(voice).startswith("ar") else "en")
    accent = (16, 185, 129)  # سبز پارس‌ایجنت

    work = VIDEOS_DIR / f"work-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    work.mkdir(parents=True, exist_ok=True)

    def _report(pct: int, msg: str) -> None:
        if progress:
            try:
                progress(pct, msg)
            except Exception:
                pass

    # ─── ۰) خودترمیمی (۲.۱۲.۰): اگر کتابخانهٔ رسانه نباشد همین‌جا نصب می‌شود
    _report(3, "🔎 بررسی کتابخانه‌های رسانه (edge-tts / Pillow / ffmpeg)…")
    await ensure_module("edge_tts", "edge-tts>=6.1.0", "گویندگی ویدیو (edge-tts)",
                        lambda m: _report(3, m))
    await ensure_module("PIL", "Pillow>=10.0", "رندر زیرنویس (Pillow)",
                        lambda m: _report(3, m))
    await ensure_module("imageio_ffmpeg", "imageio-ffmpeg>=0.4.8", "ترکیب ویدیو (ffmpeg)",
                        lambda m: _report(3, m))

    try:
        # ─── ۱) فیلم‌نامه
        _report(5, "🧠 فیلم‌نامهٔ صحنه‌ها نوشته می‌شود…")
        scenes = await _llm_scenes(llm_json, ai_cfg, provider, model, topic, n_scenes, lang, seconds)
        _report(15, f"📄 فیلم‌نامه آماده شد: {len(scenes)} صحنه")

        # ─── ۲) گویندگی رایگان (edge-tts)
        audios: List[Dict[str, Any]] = []
        for i, sc in enumerate(scenes):
            _report(15 + int(15 * (i + 1) / len(scenes)), f"🗣 گویندگی صحنهٔ {i + 1} از {len(scenes)} …")
            audios.append(await _tts_scene(sc["narration"], voice, work / f"voice-{i:02d}.mp3"))
        _report(32, "✅ گویندگی تمام شد")

        # ─── ۳) تصویر هر صحنه
        lib_images = [MEDIA_DIR / n for n in (images or []) if (MEDIA_DIR / n).exists()]
        scene_pngs: List[Path] = []
        for i, sc in enumerate(scenes):
            pct = 32 + int(40 * (i + 1) / len(scenes))
            mat: Optional[Path] = None
            if material in ("library", "mixed") and lib_images:
                mat = lib_images[i % len(lib_images)]
            if material == "library" and mat is None:
                raise MediaError("کتابخانهٔ رسانه خالی است — از تب «رسانه‌ها» عکس بگذارید یا منبع را «AI» کنید")
            if mat is None or material == "mixed" and random.random() < 0.6:
                _report(pct, f"🖼 تصویر صحنهٔ {i + 1} با AI ساخته می‌شود…")
                try:
                    # سقف زمانی سخت‌گیرانه — اگر تصویرساز گیر کرد، صحنه بدون عکس ادامه می‌دهد
                    res = await asyncio.wait_for(generate_image(
                        ai_cfg,
                        f"{sc['image_prompt']} — cinematic, high quality, no text, no watermark",
                        provider=ai_cfg.get("image", {}).get("provider", "zai"),
                        model=ai_cfg.get("image", {}).get("model", ""),
                        size_key="portrait" if aspect == "9:16" else ("landscape" if aspect == "16:9" else "square"),
                        out_name=f"scene-{i:02d}",
                        progress=None), timeout=300)
                    mat = MEDIA_DIR / res["file"]
                except (MediaError, asyncio.TimeoutError) as e:
                    _report(pct, f"⚠ تصویر صحنهٔ {i + 1} ساخته نشد ({str(e)[:60]}) — با پس‌زمینهٔ گرادیان ادامه می‌دهیم")
                    mat = None
                except Exception:
                    mat = None
                if mat is None:
                    mat = lib_images[i % len(lib_images)] if lib_images else None
            # ─── ۴) ترکیب تصویر + زیرنویس فارسی
            out_png = work / f"scene-{i:02d}.png"
            await asyncio.to_thread(_compose_scene_image, mat, out_png, w, h, sc["narration"], accent)
            scene_pngs.append(out_png)
            _report(pct, f"✅ صحنهٔ {i + 1} آماده شد")
        _report(74, "🎨 همهٔ صحنه‌ها آماده شد — ترکیب نهایی شروع می‌شود")

        # ─── ۵) ساخت کلیپ هر صحنه (تصویر + صدا) و به‌هم‌چسباندن
        clips: List[Path] = []
        for i, (png, au) in enumerate(zip(scene_pngs, audios)):
            _report(74 + int(18 * (i + 1) / len(scenes)), f"🎬 رندر صحنهٔ {i + 1} از {len(scenes)} …")
            dur = au["duration"] + 0.75  # نفس‌کشیدن بین صحنه‌ها
            clip = work / f"clip-{i:02d}.mp4"
            vf = (f"scale={int(w*1.18)}:{int(h*1.18)}:force_original_aspect_ratio=increase,"
                  f"crop={int(w*1.18)}:{int(h*1.18)},"
                  f"zoompan=z='min(zoom+{0.00055 if motion != 'static' else 0.0:.5f},1.12)':"
                  f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(dur*30)}:s={w}x{h}:fps=30,"
                  f"fade=t=in:st=0:d=0.35,fade=t=out:st={max(0.0, dur-0.35):.2f}:d=0.35")
            await asyncio.to_thread(
                _run_ffmpeg,
                ["-loop", "1", "-i", str(png), "-i", str(au["file"]),
                 "-vf", vf, "-t", f"{dur:.3f}",
                 "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage",
                 "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest",
                 "-threads", "4", str(clip)])
            clips.append(clip)

        concat_list = work / "list.txt"
        concat_list.write_text("\n".join(f"file '{c.name}'" for c in clips), encoding="utf-8")
        raw_out = work / "raw.mp4"
        await asyncio.to_thread(_run_ffmpeg, ["-f", "concat", "-safe", "0", "-i", str(concat_list),
                                              "-c", "copy", str(raw_out)])
        _report(93, "🎵 افزودن موسیقی پس‌زمینه (در صورت وجود) و خروجی نهایی…")

        # ─── ۶) موسیقی پس‌زمینهٔ اختیاری + خروجی نهایی در «رسانه‌ها»
        music = None
        if material != "nomusic":
            mp3s = [f for f in MUSIC_DIR.glob("*.mp3")]
            if mp3s:
                music = random.choice(mp3s)
        final_name = f"ai-video-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{_slug(topic)}.mp4"
        final_path = MEDIA_DIR / final_name
        if music:
            total = clips and sum(a["duration"] + 0.75 for a in audios) or 60
            await asyncio.to_thread(
                _run_ffmpeg,
                ["-i", str(raw_out), "-i", str(music),
                 "-filter_complex",
                 f"[1:a]volume=0.13,afade=t=out:st={max(0, total-3):.1f}:d=3,aloop=loop=-1:size=2e+09[bg];"
                 f"[0:a][bg]amix=inputs=2:duration=first:dropout_transition=3[a]",
                 "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                 str(final_path)])
        else:
            final_path.write_bytes(raw_out.read_bytes())

        # SRT کنار ویدیو + کاور از صحنهٔ اول
        _srt_from_words([w for a in audios for w in a["words"]], final_path.with_suffix(".srt"))
        cover = final_path.with_suffix(".cover.png")
        try:
            cover.write_bytes(scene_pngs[0].read_bytes())
        except Exception:
            pass
        _report(100, f"✅ ویدیو آماده است: {final_name}")
        return {
            "ok": True, "file": final_name, "url": f"/media/{urllib.parse.quote(final_name)}",
            "cover": f"/media/{urllib.parse.quote(cover.name)}",
            "scenes": [{"narration": s["narration"]} for s in scenes],
            "voice": voice, "aspect": aspect,
            "duration": round(sum(a["duration"] + 0.75 for a in audios), 1),
        }
    finally:
        # پوشهٔ کاری موقت را پاک می‌کنیم (خروجی نهایی در media/ است)
        try:
            import shutil
            shutil.rmtree(work, ignore_errors=True)
        except Exception:
            pass
