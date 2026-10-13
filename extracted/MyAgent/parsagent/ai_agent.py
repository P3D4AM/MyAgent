# -*- coding: utf-8 -*-
"""
ParsAgent — هستهٔ هوش مصنوعی (تب «🧠 هوش مصنوعی»)
=====================================================

یک ایجنت کاملاً خودمختار: شما فقط ایده یا ماموریت را می‌گویید؛ او:

  ۱) برنامهٔ اجرایی می‌سازد (با LLM)
  ۲) محتوای هر پلتفرم را با قوانین همان پلتفرم تولید می‌کند
  ۳) پست‌ها را در زمان‌بندی انتشار می‌گذارد (یا بلافاصله منتشر می‌کند)
  ۴) استراتژی فالو را تصمیم می‌گیرد: چند نفر، چه ساعتی، از کجا
  ۵) آخر کار گزارش مدیریتی فارسی می‌دهد (فوری یا در زمان مقرر)

نسخهٔ ۲.۴.۰ — دو بازوی جدید به ایجنت اضافه شد:
  • 🎨 ساخت عکس با AI (Z.ai GLM-Image / DALL·E / Pollinations رایگان)
  • 🎬 چاپخانهٔ ویدیو به سبک MoneyPrinterTurbo: موضوع بده، ویدیوی کامل
    (فیلم‌نامه + گوینده + تصویر + زیرنویس فارسی + موسیقی) تحویل بگیر
  • 💬 پاسخ‌گوی خودکار دایرکت در هر پلتفرم — طبیعی، با شخصیت شما (dm_reply.py)

نسخهٔ ۲.۱۳.۰ — رفع خطای 403 سرویس‌ها (گروک/Groq، جمینای، OpenAI…) در ایران:
  • همهٔ فراخوانی‌های AI حالا از «پروکسی فراخوانی سرویس‌ها» (تنظیمات ←
    هوش مصنوعی) عبور می‌کنند؛ اگر خالی باشد، پروکسی سیستم ویندوز
    (System Proxy ویندوز/VPN روشن) خودکار خوانده می‌شود — با رفع باگ
    قدیمی پایتون که برای اتصال https به پروکسیِ لوکال، آدرسِ https://
    می‌ساخت و v2rayN/Nekoray جواب نمی‌داد
  • پیام خطای 403/401/429 حالا فارسیِ راه‌حل‌دار است (به‌جای «Forbidden»
    خام یا صفحهٔ HTML گوگل): دقیقاً می‌گوید IP ایران مسدود است و پروکسی
    را از کجا روشن کند؛ Z.ai از ایران مستقیم کار می‌کند و پیشنهاد می‌ماند
  • سرویس جدید: xAI Grok (گروک) — از ایران فقط با پروکسی

نسخهٔ ۲.۱۴.۰ — رفع خطای 404 «مدل وجود ندارد» + ضبط/پخش ماکرو:
  • سرویس‌ها مدل‌های قدیمی را حذف می‌کنند: Groq در ۱۶ اوت ۲۰۲۶ مدل‌های
    llama-3.3-70b-versatile و llama-3.1-8b-instant را برای کلیدهای معمولی
    بست (فقط Enterprise) — کاتالوگ با مدل‌های رسمی جدید (GPT-OSS و Qwen)
    به‌روز شد؛ مدل مردهٔ ذخیره‌شده خودکار با جایگزین رسمی عوض می‌شود
  • دکمهٔ «🔄 مدل‌های زنده» در پنل: فهرست مدل‌ها مستقیم از خود سرویس
    (GET /models) خوانده می‌شود — دیگر هرگز مدل حذف‌شده‌ای در لیست نیست
  • خطای 404 حالا فارسیِ راه‌حل‌دار است (به‌جای متن خام سرویس)

سرویس‌های پشتیبانی‌شده (رایگان و پولی — همه از تب تنظیمات/هوش مصنوعی):
  • Z.ai (GLM) — پیشنهادی، مدل‌های Flash رایگان‌اند
  • Z.ai طرح Coding (GLM Coding Plan)
  • OpenAI · Anthropic Claude · Google Gemini · Groq · DeepSeek
  • OpenRouter (تجمیع‌کنندهٔ ده‌ها مدل رایگان/پولی)
  • هر اندپوینت سازگار با OpenAI (مثل Ollama لوکال)

فقط با کتابخانهٔ استاندارد پایتون — هیچ پیش‌نیاز جدیدی نصب نمی‌شود.
"""
from __future__ import annotations

import asyncio
import json
import random
import re
import sys
import threading
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

BASE = Path(__file__).resolve().parent
F_MISSIONS = BASE / "config" / "missions.json"

# برای آدرس‌های لوکال (Ollama و…) پروکسی نباید دخالت کند؛ برای APIهای
# اینترنتی همان تنظیم پروکسیِ سیستم (VPN کاربر) به کار می‌رود.
_DIRECT = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def resolve_ai_proxy(ai_cfg: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """پروکسی فراخوانی سرویس‌های هوش مصنوعی (۲.۱۳.۰).

    اولویت:
      ① فیلد «پروکسی فراخوانی سرویس‌ها» در تنظیمات ← هوش مصنوعی
      ② متغیرهای محیط (HTTP_PROXY / HTTPS_PROXY / ALL_PROXY)
      ③ پروکسی سیستم ویندوز (VPN با حالت System Proxy)

    چرا لازم است؟ سرویس‌هایی مثل Groq، Gemini، OpenAI، Anthropic و xAI
    درخواست از IP ایران را با خطای 403 «Forbidden» رد می‌کنند؛ درخواست‌های
    پایتون به‌تنهایی از VPNِ مرورگر عبور نمی‌کنند. خروجی این تابع به همهٔ
    فراخوانی‌ها (LLM/عکس/دانلود) داده می‌شود — Z.ai پروکسی لازم ندارد.

    نکتهٔ فنی: در ویندوز، urllib برای مقصد https آدرس پروکسی را «https://…»
    می‌سازد (باگ شناخته‌شدهٔ getproxies_registry) در حالی که v2rayN/
    Nekoray/Clash پروکسیِ HTTP لوکال‌اند و TLS روی آن‌ها بی‌معناست؛ این‌جا
    خودمان رجیستری را می‌خوانیم و همیشه http:// می‌دهیم.
    """
    raw = str((ai_cfg or {}).get("proxy") or "").strip()
    if raw:
        low = raw.lower()
        if low.startswith(("socks://", "socks4://", "socks5://", "socks5h://")):
            raise AgentError(
                "پروکسی SOCKS برای سرویس‌های هوش مصنوعی پشتیبانی نمی‌شود — پورت HTTP همان برنامه را "
                "وارد کنید (v2rayN: http://127.0.0.1:10809 · Nekoray/NekoBox پورت Mixed: "
                "http://127.0.0.1:2080 · Clash: http://127.0.0.1:7890)")
        if "://" not in raw:
            raw = "http://" + raw
        return {"http": raw, "https": raw}
    # ② متغیرهای محیط
    try:
        env = urllib.request.getproxies_environment()
        addr = env.get("https") or env.get("http") or env.get("all")
        if addr:
            return {"http": addr, "https": addr}
    except Exception:
        pass
    # ③ پروکسی سیستم ویندوز (رجیستری) — با رفع باگ scheme
    if sys.platform == "win32":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Internet Settings")
            try:
                enabled, _ = winreg.QueryValueEx(key, "ProxyEnable")
                server = ""
                if enabled:
                    server = str(winreg.QueryValueEx(key, "ProxyServer")[0] or "")
            finally:
                winreg.CloseKey(key)
            if "=" in server or ";" in server:  # http=h:p;https=h:p;…
                parts = dict(p.split("=", 1) for p in server.split(";") if "=" in p)
                server = parts.get("https") or parts.get("http") or parts.get("all") or ""
            if server:
                if "://" not in server:
                    server = "http://" + server
                return {"http": server, "https": server}
        except Exception:
            pass
    return None


class AgentError(Exception):
    """خطای قابل‌فهم برای کاربر."""


# ════════════════════════════════════════════════════════════════ کاتالوگ سرویس‌ها
# ترتیب مهم است: Z.ai اولِ لیست است (پیشنهاد ما). tag → چیپ نمایش در پنل.
PROVIDERS: Dict[str, Dict[str, Any]] = {
    "zai": {
        "name": "Z.ai (GLM)",
        "kind": "openai",
        "base": "https://api.z.ai/api/paas/v4",
        "docs": "https://z.ai",
        "note": "پیشنهادی — مدل‌های GLM؛ دو مدل Flash کاملاً رایگان‌اند",
        "key_field": "zai",
        "models": [
            {"id": "glm-5.3", "name": "GLM-5.3", "tag": "پیشرفته", "note": "پرچمدار جدید Z.ai — بهترین کیفیت"},
            {"id": "glm-4.6", "name": "GLM-4.6", "tag": "پیشرفته", "note": "نسل جدید — کیفیت عالی"},
            {"id": "glm-4.5", "name": "GLM-4.5", "tag": "پولی", "note": "نسخهٔ پایدار نسل قبل"},
            {"id": "glm-4.5-air", "name": "GLM-4.5-Air", "tag": "اقتصادی", "note": "سبک و ارزان"},
            {"id": "glm-4.5-flash", "name": "GLM-4.5-Flash", "tag": "رایگان", "note": "رایگان و سریع — برای شروع"},
            {"id": "glm-4-flash-250414", "name": "GLM-4-Flash", "tag": "رایگان", "note": "رایگان — نسل قبل"},
        ],
    },
    "zai_coding": {
        "name": "Z.ai — طرح Coding",
        "kind": "openai",
        "base": "https://api.z.ai/api/coding/paas/v4",
        "docs": "https://z.ai/subscribe",
        "note": "برای مشترکان GLM Coding Plan — همان کلید Z.ai",
        "key_field": "zai",
        "models": [
            {"id": "glm-4.6", "name": "GLM-4.6 (Coding)", "tag": "پولی", "note": "با اشتراک ماهانهٔ Coding Plan"},
            {"id": "glm-4.5", "name": "GLM-4.5 (Coding)", "tag": "پولی", "note": "با اشتراک ماهانهٔ Coding Plan"},
        ],
    },
    "openai": {
        "name": "OpenAI",
        "kind": "openai",
        "base": "https://api.openai.com/v1",
        "docs": "https://platform.openai.com",
        "note": "GPT — پولی",
        "key_field": "openai",
        "models": [
            {"id": "gpt-5", "name": "GPT-5", "tag": "پیشرفته", "note": "پرچمدار OpenAI"},
            {"id": "gpt-5-mini", "name": "GPT-5 mini", "tag": "اقتصادی", "note": "سریع و ارزان"},
            {"id": "gpt-4.1", "name": "GPT-4.1", "tag": "پولی", "note": "نسخهٔ پایدار"},
            {"id": "gpt-4.1-mini", "name": "GPT-4.1 mini", "tag": "اقتصادی", "note": "سبک"},
            {"id": "gpt-4o", "name": "GPT-4o", "tag": "پولی", "note": "چندوجهی نسل قبل"},
            {"id": "gpt-4o-mini", "name": "GPT-4o mini", "tag": "اقتصادی", "note": "کم‌هزینه"},
        ],
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "kind": "anthropic",
        "base": "https://api.anthropic.com/v1",
        "docs": "https://console.anthropic.com",
        "note": "کلود — پولی",
        "key_field": "anthropic",
        "models": [
            {"id": "claude-sonnet-4-5", "name": "Claude Sonnet 4.5", "tag": "پیشرفته", "note": "تعادل کیفیت/قیمت"},
            {"id": "claude-opus-4-1", "name": "Claude Opus 4.1", "tag": "پولی", "note": "بالاترین کیفیت"},
            {"id": "claude-haiku-4-5", "name": "Claude Haiku 4.5", "tag": "اقتصادی", "note": "سریع و ارزان"},
        ],
    },
    "gemini": {
        "name": "Google Gemini",
        "kind": "gemini",
        "base": "https://generativelanguage.googleapis.com/v1beta",
        "docs": "https://aistudio.google.com",
        "note": "جِمینی — رایگان در AI Studio؛ از ایران فقط با پروکسی",
        "key_field": "gemini",
        "models": [
            {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro", "tag": "پیشرفته", "note": "پرچمدار گوگل"},
            {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "tag": "رایگان", "note": "سریع و اقتصادی"},
            {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "tag": "رایگان", "note": "نسل قبل"},
        ],
    },
    # ۲.۱۳.۰ — گروک (xAI) به فهرست سرویس‌ها اضافه شد؛ از ایران فقط با
    # «پروکسی فراخوانی سرویس‌ها» کار می‌کند (خطای 403 یعنی بدون پروکسی رفته).
    "grok": {
        "name": "xAI Grok (گروک)",
        "kind": "openai",
        "base": "https://api.x.ai/v1",
        "docs": "https://console.x.ai",
        "note": "گروک — از ایران فقط با پروکسی فراخوانی سرویس‌ها",
        "key_field": "grok",
        "models": [
            {"id": "grok-4", "name": "Grok 4", "tag": "پیشرفته", "note": "پرچمدار xAI"},
            {"id": "grok-3", "name": "Grok 3", "tag": "پولی", "note": "نسل قبل"},
            {"id": "grok-3-mini", "name": "Grok 3 Mini", "tag": "اقتصادی", "note": "سریع و ارزان"},
        ],
    },
    "groq": {
        "name": "Groq",
        "kind": "openai",
        "base": "https://api.groq.com/openai/v1",
        "docs": "https://console.groq.com",
        "note": "سریع‌ترین اینترنت — با سطح رایگان سخاوتمندانه",
        "key_field": "groq",
        # ۲.۱۴.۰ — Groq در آگوست ۲۰۲۶ llama-3.3-70b-versatile و llama-3.1-8b-instant
        # را برای کلیدهای معمولی بست (فقط Enterprise) → کاتالوگ با جایگزین‌های رسمی
        # (GPT-OSS و Qwen) به‌روز شد؛ مستند رسمی: console.groq.com/docs/deprecations
        "models": [
            {"id": "openai/gpt-oss-120b", "name": "GPT-OSS 120B", "tag": "پیشنهادی", "note": "کیفیت بالا، ارزان — جایگزین رسمی Llama 3.3 70B"},
            {"id": "openai/gpt-oss-20b", "name": "GPT-OSS 20B", "tag": "سریع", "note": "سریع‌ترین و ارزان‌ترین — جایگزین رسمی Llama 3.1 8B"},
            {"id": "qwen/qwen3.8-27b", "name": "Qwen 3.8 27B", "tag": "پیش‌نمایش", "note": "چندزبانهٔ جدید — مدل پیش‌نمایش (ممکن است حذف شود)"},
        ],
    },
    "deepseek": {
        "name": "DeepSeek",
        "kind": "openai",
        "base": "https://api.deepseek.com/v1",
        "docs": "https://platform.deepseek.com",
        "note": "بسیار ارزان",
        "key_field": "deepseek",
        "models": [
            {"id": "deepseek-chat", "name": "DeepSeek V3", "tag": "اقتصادی", "note": "ارزان و توانمند"},
            {"id": "deepseek-reasoner", "name": "DeepSeek R1", "tag": "اقتصادی", "note": "استدلال گام‌به‌گام"},
        ],
    },
    "openrouter": {
        "name": "OpenRouter",
        "kind": "openai",
        "base": "https://openrouter.ai/api/v1",
        "docs": "https://openrouter.ai",
        "note": "تجمیع‌کنندهٔ صدها مدل — خیلی از مدل‌ها «:free» رایگان‌اند",
        "key_field": "openrouter",
        "models": [
            {"id": "deepseek/deepseek-chat-v3-0324:free", "name": "DeepSeek V3 (رایگان)", "tag": "رایگان", "note": "نسخهٔ رایگان OpenRouter"},
            {"id": "meta-llama/llama-3.3-70b-instruct:free", "name": "Llama 3.3 70B (رایگان)", "tag": "رایگان", "note": "نسخهٔ رایگان"},
            {"id": "qwen/qwen3-235b-a22b:free", "name": "Qwen3 235B (رایگان)", "tag": "رایگان", "note": "مدل بزرگ رایگان"},
            {"id": "google/gemini-2.0-flash-exp:free", "name": "Gemini 2.0 Flash (رایگان)", "tag": "رایگان", "note": "رایگان"},
            {"id": "openai/gpt-4o-mini", "name": "GPT-4o mini", "tag": "پولی", "note": "از طریق OpenRouter"},
            {"id": "anthropic/claude-sonnet-4.5", "name": "Claude Sonnet 4.5", "tag": "پولی", "note": "از طریق OpenRouter"},
        ],
    },
    "custom": {
        "name": "سرویس سفارشی (سازگار با OpenAI)",
        "kind": "openai",
        "base": "",
        "docs": "",
        "note": "هر اندپوینت OpenAI-سازگار — مثل Ollama لوکال (http://127.0.0.1:11434/v1)",
        "key_field": "custom",
        "models": [],  # از تنظیمات خوانده می‌شود
    },
}

# ════════════════════════════════════════════════════════════════ مدل‌های مرده (۲.۱۴.۰)
# سرویس‌ها مدل‌های قدیمی را می‌بندند و خطای 404 «The model … does not exist or
# you do not have access to it» می‌دهند (گزارش کاربر: llama-3.3-70b-versatile
# روی Groq). این جدولِ «مدل مرده ← جایگزین رسمی» است؛ llm_chat قبل از هر
# فراخوانی مدلِ ذخیره‌شده را از این جدول رد می‌کند تا کاربر هیچ‌وقت روی
# مدلِ حذف‌شده گیر نکند. منبع جایگزین‌ها: مستند رسمی خود سرویس
# (console.groq.com/docs/deprecations — ۱۶ اوت ۲۰۲۶).
DEAD_MODELS: Dict[str, Dict[str, str]] = {
    "groq": {
        "llama-3.3-70b-versatile": "openai/gpt-oss-120b",     # Enterprise-only شد
        "llama-3.1-8b-instant": "openai/gpt-oss-20b",         # Enterprise-only شد
        "qwen/qwen3-32b": "openai/gpt-oss-120b",
        "qwen/qwen3.6-27b": "qwen/qwen3.8-27b",
        "deepseek-r1-distill-llama-70b": "openai/gpt-oss-120b",
        "deepseek-r1-distill-llama-70b-specdec": "openai/gpt-oss-120b",
        "gemma2-9b-it": "openai/gpt-oss-20b",
        "moonshotai/kimi-k2-instruct": "openai/gpt-oss-120b",
        "moonshotai/kimi-k2-instruct-0905": "openai/gpt-oss-120b",
        "llama3-70b-8192": "openai/gpt-oss-120b",
        "llama3-8b-8192": "openai/gpt-oss-20b",
        "mixtral-8x7b-32768": "openai/gpt-oss-120b",
    },
    "gemini": {
        "gemini-1.5-pro": "gemini-2.5-flash",
        "gemini-1.5-flash": "gemini-2.5-flash",
        "gemini-1.5-flash-8b": "gemini-2.5-flash",
    },
}


def resolve_model(provider: str, model: str) -> str:
    """مدلِ حذف‌شده را به جایگزین رسمی همان سرویس تبدیل می‌کند (۲.۱۴.۰)."""
    return DEAD_MODELS.get(provider, {}).get((model or "").strip(), model)

# ════════════════════════════════════════════════════════════════ قوانین پلتفرم‌ها
PLATFORM_INFO: Dict[str, Dict[str, Any]] = {
    "instagram": {"name": "اینستاگرام", "max_chars": 2200, "hashtags": "۸ تا ۱۲", "style": "کپشن جذاب، سطرهای کوتاه، ایموجی",
                  "post_action": "post_photo", "needs_media": True, "is_messenger": False},
    "twitter": {"name": "توییتر (X)", "max_chars": 280, "hashtags": "۱ تا ۲", "style": "تند و کوتاه",
                "post_action": "tweet", "needs_media": False, "is_messenger": False},
    "telegram": {"name": "تلگرام", "max_chars": 4000, "hashtags": "۳ تا ۵", "style": "پیام کانال با CTA",
                 "post_action": "send_message", "needs_media": False, "is_messenger": True},
    "facebook": {"name": "فیسبوک", "max_chars": 2000, "hashtags": "۲ تا ۴", "style": "مطلب دوستانه",
                 "post_action": "post_photo", "needs_media": True, "is_messenger": False},
    "linkedin": {"name": "لینکدین", "max_chars": 1300, "hashtags": "۳ تا ۵", "style": "حرفه‌ای و مقاله‌وار",
                 "post_action": "post", "needs_media": False, "is_messenger": False},
    "bale": {"name": "بله", "max_chars": 4000, "hashtags": "۲ تا ۴", "style": "پیام کانال",
             "post_action": "send_message", "needs_media": False, "is_messenger": True},
    "rubika": {"name": "روبیکا", "max_chars": 4000, "hashtags": "۲ تا ۴", "style": "پیام کانال",
               "post_action": "send_message", "needs_media": False, "is_messenger": True},
    # ۲.۱۱.۰ — واتساپ: پیام‌رسان شخصی؛ برای مخاطبین/گروه‌های خودتان
    "whatsapp": {"name": "واتساپ", "max_chars": 3500, "hashtags": "بدون هشتگ (چت است)", "style": "پیام چت کوتاه و شخصی — بدون لینک‌بارانی",
                 "post_action": "send_message", "needs_media": False, "is_messenger": True},
}

# سقف امن فالو روزانه (از راهنمای طبیعی‌جلو کردن پنل) + شناسهٔ اکشن فالو
FOLLOW_CAPS: Dict[str, Dict[str, Any]] = {
    "instagram": {"cap": 150, "action": "follow", "name": "فالو اینستاگرام"},
    "twitter": {"cap": 100, "action": "follow", "name": "فالو توییتر"},
    "facebook": {"cap": 15, "action": "friend_request", "name": "درخواست دوستی فیسبوک"},
    "linkedin": {"cap": 20, "action": "connect", "name": "درخواست اتصال لینکدین"},
}

TOOL_NAMES = {
    "generate_content": "تولید محتوا",
    "generate_image": "🎨 ساخت عکس با AI",
    "generate_video": "🎬 ساخت ویدیو (چاپخانه)",
    "dm_autoreply": "💬 پاسخ‌گوی دایرکت",
    "schedule_publish": "زمان‌بندی انتشار",
    "publish_now": "انتشار فوری",
    "follow_strategy": "استراتژی فالو",
    "wait_report": "گزارش زمان‌دار",
    "report": "گزارش نهایی",
    "status_check": "بررسی وضعیت",
}

DEFAULT_HOURS = [10, 13, 16, 19, 21]


# ════════════════════════════════════════════════════════════════ ابزار HTTP و JSON
def _llm_error_fa(code: int, detail: str) -> str:
    """ترجمهٔ خطاهای سرویس‌های هوش مصنوعی به فارسیِ راه‌حل‌دار (۲.۱۳.۰).

    ریشهٔ باگ گزارش‌شدهٔ کاربر («خطای 403 — Forbidden» برای گروک و صفحهٔ
    HTML 403 برای جمینای، هنگام نوشتن فیلم‌نامهٔ ویدیو): این سرویس‌ها
    درخواست از IP ایران را کلاً رد می‌کنند و پیام قبلی («خطای 403 از سرویس
    هوش مصنوعی — Forbidden») هیچ راهنمایی نمی‌داد.

    ۲.۱۴.۰ — خطای 404 «The model … does not exist or you do not have access
    to it» هم فارسی شد: سرویس‌ها مدل‌های قدیمی را می‌بندند (مثل
    llama-3.3-70b-versatile روی Groq که ۱۶ اوت ۲۰۲۶ Enterprise-only شد).
    """
    raw = detail or ""
    d = raw.lower()
    m = re.search(r'"message"\s*:\s*"([^"\\]{3,240})"', raw)
    msg = m.group(1) if m else ""
    if code == 404 or "does not exist or you do not have access" in d or "model_not_found" in d:
        if "model" in d:
            return ("مدل در این سرویس موجود نیست یا کلید شما به آن دسترسی ندارد (خطای 404) — "
                    "سرویس‌ها مدل‌های قدیمی را حذف می‌کنند (مثلاً Groq مدل‌های Llama 3.x را بسته است). "
                    "راه حل: در پنل، کنار فیلد «مدل» دکمهٔ «🔄 مدل‌های زنده» را بزنید تا فهرست مدل‌های "
                    "معتبرِ همین لحظه از خود سرویس بیاید، بعد یکی را انتخاب و ذخیره کنید"
                    + (f" — پاسخ سرویس: {msg}" if msg else ""))
        return ("آدرس/مسیر سرویس پیدا نشد (خطای 404) — اگر «سرویس سفارشی» دارید، آدرس آن را در "
                "تنظیمات ← هوش مصنوعی بررسی کنید (مثلاً باید تا /v1 تمام شود)"
                + (f" — پاسخ سرویس: {msg}" if msg else ""))
    if code == 403 or "user location is not supported" in d:
        if "user location is not supported" in d or "location is not supported" in d:
            return ("سرویس Gemini منطقهٔ شما را نمی‌پذیرد (خطای 403 — «User location is not supported»): "
                    "گوگل IP ایران را برای Gemini API مسدود کرده است. راه حل: در «تنظیمات ← هوش مصنوعی ← "
                    "پروکسی فراخوانی سرویس‌ها» آدرس VPN خود را وارد کنید (مثلاً http://127.0.0.1:10809) "
                    "یا سرویس Z.ai را انتخاب کنید که از ایران مستقیم و بدون فیلترشکن کار می‌کند")
        if "<html" in d or "<!doctype" in d:
            return ("سرویس درخواست را کاملاً رد کرد (خطای 403 — صفحهٔ خطای HTML): تقریباً همیشه یعنی "
                    "IP شما نزد این سرویس مسدود است (ایران). راه حل: در «تنظیمات ← هوش مصنوعی ← پروکسی "
                    "فراخوانی سرویس‌ها» آدرس VPN را بدهید (مثلاً http://127.0.0.1:10809) یا Z.ai را "
                    "انتخاب کنید که از ایران مستقیم کار می‌کند")
        return ("سرویس درخواست شما را رد کرد (خطای 403 Forbidden). اگر کلید API درست است، شایع‌ترین علت این "
                "است که این سرویس IP ایران را نمی‌پذیرد (Groq، Gemini، OpenAI، Anthropic و xAI همه این‌طورند). "
                "راه حل: در «تنظیمات ← هوش مصنوعی ← پروکسی فراخوانی سرویس‌ها» آدرس VPN خود را بدهید "
                "(مثلاً http://127.0.0.1:10809) یا سرویس Z.ai را انتخاب کنید که از ایران بدون فیلترشکن "
                "کار می‌کند" + (f" — پاسخ سرویس: {msg}" if msg else ""))
    if code == 401:
        return ("کلید API نامعتبر یا منقضی است (خطای 401) — کلید را دوباره از سایت سرویس بگیرید و در "
                "«تنظیمات ← هوش مصنوعی» جایگزین کنید" + (f" — پاسخ سرویس: {msg}" if msg else ""))
    if "api key not valid" in d:
        return "کلید API معتبر نیست — از صفحهٔ کلید همان سرویس، کلید تازه بگیرید و دوباره بگذارید"
    if code == 429:
        return ("محدودیت نرخ درخواست (خطای 429) — چند ثانیه صبر کنید و دوباره تلاش کنید"
                + (f" — {msg}" if msg else ""))
    if code == 400 and msg:
        return f"درخواست قبول نشد (خطای 400) — {msg}"
    return f"خطای {code} از سرویس هوش مصنوعی{(' — ' + (msg or raw[:160])) if (msg or raw) else ''}"


def _http_json(url: str, headers: Dict[str, str], payload: Dict[str, Any],
               timeout: int = 180, proxies: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": "ParsAgent/2.14", **headers})
    if "127.0.0.1" in url or "localhost" in url:
        opener = _DIRECT            # لوکال (Ollama و…) هرگز از پروکسی عبور نمی‌کند
    elif proxies:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxies))
    else:
        opener = _DIRECT            # هیچ پروکسی‌ای تنظیم نشده → مستقیم
    try:
        with opener.open(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", "ignore")[:500]
        except Exception:
            detail = ""
        raise AgentError(_llm_error_fa(e.code, detail))
    except urllib.error.URLError as e:
        reason = str(getattr(e, "reason", e))
        if proxies:
            raise AgentError(f"از راه پروکسی به سرویس وصل نشد: {reason} — آدرس پروکسی و روشن بودن VPN را چک کنید")
        raise AgentError(f"ارتباط با سرویس برقرار نشد: {reason} — اینترنت/VPN را چک کنید")
    except json.JSONDecodeError:
        raise AgentError("پاسخ سرویس قابل خواندن نبود")


# ════════════════════════════════════════════════════════ فهرست مدل‌های زنده (۲.۱۴.۰)
# مدل‌هایی که کار گفتگو نیستند و در فهرست /models فقط شلوغی می‌کنند
_SKIP_MODEL_RE = re.compile(
    r"(embed|whisper|tts|guard|orpheus|dall-e|moderation|rerank|transcri|"
    r"safeguard|imagen|astra|veo|song|music|voice|audio|clip)", re.I)


def _http_get_json(url: str, headers: Dict[str, str], timeout: int = 30,
                   proxies: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """GET با همان منطق پروکسی/خطای فارسیِ _http_json (برای /models سرویس‌ها)."""
    req = urllib.request.Request(url, method="GET",
                                 headers={"User-Agent": "ParsAgent/2.14", **headers})
    if "127.0.0.1" in url or "localhost" in url:
        opener = _DIRECT
    elif proxies:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxies))
    else:
        opener = _DIRECT
    try:
        with opener.open(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", "ignore")[:500]
        except Exception:
            detail = ""
        raise AgentError(_llm_error_fa(e.code, detail))
    except urllib.error.URLError as e:
        reason = str(getattr(e, "reason", e))
        if proxies:
            raise AgentError(f"از راه پروکسی به سرویس وصل نشد: {reason} — آدرس پروکسی و روشن بودن VPN را چک کنید")
        raise AgentError(f"ارتباط با سرویس برقرار نشد: {reason} — اینترنت/VPN را چک کنید")
    except json.JSONDecodeError:
        raise AgentError("پاسخ سرویس قابل خواندن نبود")


async def fetch_models(ai_cfg: Dict[str, Any], provider: str) -> List[Dict[str, Any]]:
    """فهرست مدل‌های «همین لحظه» از خود سرویس — دکمهٔ «🔄 مدل‌های زنده» پنل (۲.۱۴.۰).

    چرا؟ کاتالوگ ایستا هر چند ماه کهنه می‌شود و سرویس‌ها مدل‌ها را حذف
    می‌کنند (خطای 404 گزارش‌شدهٔ کاربر). اینجا GET {base}/models با کلیدِ
    خود کاربر زده می‌شود — هر سرویسِ سازگار با OpenAI (و Gemini/Anthropic)
    این اندپوینت را دارد؛ پس فهرست همیشه با کلیدِ همان کاربر سازگار است.

    خروجی: [{id, name}] — مدل‌های آشنا (کاتالوگ ایستا) اول و بقیه بعدش.
    """
    p = PROVIDERS.get(provider)
    if not p:
        raise AgentError(f"سرویس نامعتبر: {provider}")
    if provider == "custom":
        base = (ai_cfg.get("custom_base") or "").strip().rstrip("/")
        if not base:
            raise AgentError("آدرس سرویس سفارشی در تنظیمات خالی است")
    else:
        base = p["base"]
    key = (ai_cfg.get("api_keys") or {}).get(p.get("key_field", provider), "")
    if not key and provider != "custom":
        raise AgentError(f"اول کلید API «{p['name']}» را در تنظیمات ← هوش مصنوعی وارد کنید")
    kind = p["kind"]
    if kind == "gemini":
        url = base + "/models?pageSize=1000"
        headers = {"x-goog-api-key": key}
    elif kind == "anthropic":
        url = base + "/models?limit=100"
        headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
    else:
        url = base + "/models"
        headers = {"Authorization": f"Bearer {key}"}
    proxies = resolve_ai_proxy(ai_cfg)
    data = await asyncio.to_thread(_http_get_json, url, headers, proxies=proxies)
    ids: List[str] = []
    if kind == "gemini":
        for m in (data.get("models") or []):
            mid = str(m.get("name") or "").removeprefix("models/")
            if mid:
                ids.append(mid)
    else:  # openai / anthropic — هر دو {data: [{id}]}
        for m in (data.get("data") or []):
            mid = str(m.get("id") or "")
            if mid:
                ids.append(mid)
    # فقط مدل‌های گفتگو؛ ترتیب کاتالوگ حفظ می‌شود تا مدل‌های آشنا اول باشند
    live = [i for i in ids if i and not _SKIP_MODEL_RE.search(i)]
    catalog_ids = [m["id"] for m in (p.get("models") or [])]
    ordered = [i for i in catalog_ids if i in live] + [i for i in live if i not in catalog_ids]
    return [{"id": i, "name": i} for i in ordered]


def extract_json(text: str) -> Optional[Any]:
    """اولین JSON متعادلِ داخل متن را بیرون می‌کشد (حتی اگر داخل ``` باشد)."""
    if not text:
        return None
    t = re.sub(r"```(?:json)?", "", text).strip()
    start = t.find("{")
    while start != -1:
        depth, in_str, esc = 0, False, False
        for i in range(start, len(t)):
            ch = t[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(t[start:i + 1])
                        except Exception:
                            break
        start = t.find("{", start + 1)
    return None


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ════════════════════════════════════════════════════════════════ کلاینت LLM
async def llm_chat(ai_cfg: Dict[str, Any], provider: str, model: str,
                   messages: List[Dict[str, str]], *, temperature: float = 0.7,
                   max_tokens: int = 4096, json_mode: bool = False) -> str:
    """گفتگو با هر سرویس — یکسان برای همه (رابط OpenAI/Anthropic/Gemini)."""
    p = PROVIDERS.get(provider)
    if not p:
        raise AgentError(f"سرویس نامعتبر: {provider}")
    if provider == "custom":
        base = (ai_cfg.get("custom_base") or "").strip().rstrip("/")
        model = (ai_cfg.get("custom_model") or "").strip() or model
        if not base:
            raise AgentError("آدرس سرویس سفارشی در تنظیمات خالی است")
    else:
        base = p["base"]
    key = (ai_cfg.get("api_keys") or {}).get(p.get("key_field", provider), "")
    if not key and provider != "custom":
        raise AgentError(f"کلید API «{p['name']}» در تنظیمات وارد نشده — از تب تنظیمات ← هوش مصنوعی")

    kind = p["kind"]
    # ۲.۱۴.۰ — مدلِ حذف‌شده توسط سرویس (مثل llama-3.3-70b-versatile روی Groq)
    # بی‌سروصدا با جایگزین رسمی عوض می‌شود تا کاربر روی مدل مرده گیر نکند
    model = resolve_model(provider, model)
    proxies = resolve_ai_proxy(ai_cfg)  # ۲.۱۳.۰ — پروکسی سرویس‌های AI (خطای socks فارسی می‌شود)
    if kind == "openai":
        payload: Dict[str, Any] = {"model": model, "messages": messages,
                                    "temperature": temperature, "max_tokens": max_tokens}
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        headers = {"Authorization": f"Bearer {key}"}
        if provider == "openrouter":
            headers["HTTP-Referer"] = "https://parsagent.local"
            headers["X-Title"] = "ParsAgent"
        url = base + "/chat/completions"
    elif kind == "anthropic":
        system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
        payload = {"model": model, "max_tokens": max(1024, min(max_tokens, 8000)),
                   "temperature": temperature,
                   "messages": [{"role": m["role"], "content": m["content"]}
                                for m in messages if m["role"] != "system"]}
        if system:
            payload["system"] = system
        headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
        url = base + "/messages"
    else:  # gemini
        system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
        payload = {"contents": [{"role": "model" if m["role"] == "assistant" else "user",
                                 "parts": [{"text": m["content"]}]}
                                for m in messages if m["role"] != "system"],
                   "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}}
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"
        headers = {"x-goog-api-key": key}
        url = f"{base}/models/{model}:generateContent"

    last_err: Optional[AgentError] = None
    for attempt in range(2):
        try:
            data = await asyncio.to_thread(_http_json, url, headers, payload, proxies=proxies)
            if kind == "openai":
                return data["choices"][0]["message"]["content"] or ""
            if kind == "anthropic":
                return "".join(b.get("text", "") for b in data.get("content", []))
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except AgentError as e:
            last_err = e
            if attempt == 0 and "خطای 429" in str(e):
                await asyncio.sleep(3)
                continue
            raise
        except (KeyError, IndexError, TypeError):
            raise AgentError("پاسخ سرویس ساختار مورد انتظار را نداشت (نام مدل درست است؟)")
    raise last_err or AgentError("خطای ناشناخته در سرویس هوش مصنوعی")


async def llm_json(ai_cfg: Dict[str, Any], provider: str, model: str,
                   messages: List[Dict[str, str]], *, temperature: float = 0.4) -> Dict[str, Any]:
    """گفتگو با خروجی تضمینی JSON — اگر پاسخ خراب بود یک‌بار تلاش مجدد."""
    for attempt in range(2):
        text = await llm_chat(ai_cfg, provider, model, messages,
                              temperature=temperature, json_mode=True)
        data = extract_json(text)
        if isinstance(data, dict):
            return data
        if attempt == 0:
            messages = messages + [
                {"role": "assistant", "content": text[:2000]},
                {"role": "user", "content": "پاسخ قبلی JSON معتبر نبود. فقط و فقط یک JSON درست و کامل بده — بدون هیچ متن اضافه."},
            ]
    raise AgentError("مدل پاسخ JSON درست نداد — دوباره تلاش کنید یا مدل بهتری انتخاب کنید")


# ════════════════════════════════════════════════════════════════ فروشگاه ماموریت‌ها
class MissionStore:
    def __init__(self, path: Path):
        self.path = path
        self.lock = threading.Lock()
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def load(self) -> List[Dict[str, Any]]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def save(self, missions: List[Dict[str, Any]]) -> None:
        with self.lock:
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(missions, ensure_ascii=False, indent=1), encoding="utf-8")
            tmp.replace(self.path)

    def get(self, mid: str) -> Optional[Dict[str, Any]]:
        return next((m for m in self.load() if m.get("id") == mid), None)

    def upsert(self, mission: Dict[str, Any]) -> None:
        missions = self.load()
        for i, m in enumerate(missions):
            if m.get("id") == mission["id"]:
                missions[i] = mission
                break
        else:
            missions.insert(0, mission)
        self.save(missions)


# ════════════════════════════════════════════════════════════════ ایجنت خودمختار
class AgentSystem:
    """مغز ParsAgent — ماموریت می‌گیرد، برنامه می‌سازد و تا گزارش نهایی اجرا می‌کند."""

    def __init__(self):
        self.store = MissionStore(F_MISSIONS)
        self.runners: Dict[str, "asyncio.Task[None]"] = {}
        self.ctx: Dict[str, Any] = {}

    # -------------------------------------------------- اتصال به پنل (تزریق وابستگی)
    def configure(self, *, run_action: Callable, add_schedule: Callable, get_settings: Callable,
                  save_settings: Callable, broadcast: Callable, log: Callable,
                  media_images: Callable, active_platforms: Callable,
                  generate_media_images: Optional[Callable] = None,
                  generate_media_video: Optional[Callable] = None,
                  dm_status: Optional[Callable] = None, dm_configure: Optional[Callable] = None,
                  dm_round: Optional[Callable] = None) -> None:
        self.ctx = {
            "run_action": run_action, "add_schedule": add_schedule,
            "get_settings": get_settings, "save_settings": save_settings,
            "broadcast": broadcast, "log": log, "media_images": media_images,
            "active_platforms": active_platforms,
            "generate_media_images": generate_media_images,
            "generate_media_video": generate_media_video,
            "dm_status": dm_status, "dm_configure": dm_configure, "dm_round": dm_round,
        }

    def _ai_cfg(self) -> Dict[str, Any]:
        return self.ctx["get_settings"]().get("ai", {})

    def _active_platforms(self) -> List[str]:
        try:
            return list(self.ctx["active_platforms"]())
        except Exception:
            return list(PLATFORM_INFO.keys())

    def _alog(self, m: Dict[str, Any], msg: str, level: str = "info", step: str = "") -> None:
        entry = {"t": datetime.now().strftime("%H:%M:%S"), "level": level,
                 "step": step or TOOL_NAMES.get("", ""), "msg": msg}
        m["log"].append(entry)
        m["log"] = m["log"][-80:]
        m["updated_at"] = _now_iso()
        try:
            self.ctx["log"](f"🧠 [{m.get('title') or m['id'][:8]}] {msg}", level if level in ("warn", "error") else "info")
        except Exception:
            pass

    async def _emit(self, m: Dict[str, Any]) -> None:
        self.store.upsert(m)
        try:
            await self.ctx["broadcast"]({"type": "agent", "mission": self.summarize(m)})
        except Exception:
            pass

    # -------------------------------------------------- کاتالوگ / تست / چت
    def catalog(self) -> Dict[str, Any]:
        ai = self._ai_cfg()
        keys = ai.get("api_keys") or {}
        cur_provider = ai.get("provider") or ""
        cur_model = ai.get("model") or ""
        out = []
        for pid, p in PROVIDERS.items():
            models = list(p["models"])
            if pid == "custom":
                cm = (ai.get("custom_model") or "").strip()
                models = [{"id": cm or "Custom Model", "name": cm or "مدل سفارشی",
                          "tag": "خودتان", "note": "از تنظیمات ← هوش مصنوعی تغییر دهید"}]
            out.append({
                "id": pid, "name": p["name"], "note": p["note"], "docs": p["docs"],
                "has_key": bool(keys.get(p.get("key_field", pid))),
                "models": models,
                # ۲.۱۴.۰ — آیا مدلِ ذخیره‌شدهٔ فعلی توسط سرویس حذف شده است؟
                "dead_current": bool(pid == cur_provider and cur_model
                                      and cur_model in DEAD_MODELS.get(pid, {})),
                "dead_replacement": DEAD_MODELS.get(pid, {}).get(cur_model, "") if pid == cur_provider else "",
            })
        return {"providers": out, "dead_current": bool(
            cur_provider and cur_model and cur_model in DEAD_MODELS.get(cur_provider, {}))}

    async def test(self, provider: str) -> Dict[str, Any]:
        name = PROVIDERS.get(provider, {}).get("name", provider)
        await llm_chat(self._ai_cfg(), provider, self._default_model(provider),
                       [{"role": "user", "content": "فقط یک کلمه بنویس: OK"}],
                       temperature=0.0, max_tokens=16)
        return {"ok": True, "message": f"✅ {name} وصل است و جواب می‌دهد"}

    def _default_model(self, provider: str) -> str:
        if provider == "custom":
            return (self._ai_cfg().get("custom_model") or "").strip() or "custom"
        models = PROVIDERS.get(provider, {}).get("models") or []
        return (models[0]["id"] if models else "glm-4.6")

    async def chat(self, provider: str, model: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        system = {"role": "system", "content":
                  "تو دستیار هوشمند ParsAgent هستی — نرم‌افزار اتوماسیون ۸ پلتفرم شبکهٔ اجتماعی "
                  "(اینستاگرام، توییتر، تلگرام، فیسبوک، لینکدین، بله، روبیکا، واتساپ). "
                  "جواب‌ها کوتاه، دقیق و فارسی؛ اگر از قابلیت‌های پنل می‌پرسند، به تب‌های پنل هم اشاره کن."}
        reply = await llm_chat(self._ai_cfg(), provider, model, [system] + messages[-14:])
        return {"ok": True, "reply": reply.strip()}

    # -------------------------------------------------- چرخهٔ حیات ماموریت
    async def create_mission(self, instruction: str, provider: Optional[str] = None,
                             model: Optional[str] = None, autonomy: Optional[str] = None) -> Dict[str, Any]:
        ai = self._ai_cfg()
        provider = provider or ai.get("provider", "zai")
        model = (model or "").strip() or (ai.get("model") if ai.get("provider") == provider else "") \
            or self._default_model(provider)
        autonomy = autonomy or ai.get("autonomy", "semi")
        if autonomy not in ("manual", "semi", "auto"):
            autonomy = "semi"
        m = {
            "id": "m" + uuid.uuid4().hex[:10], "title": "ماموریت جدید",
            "instruction": (instruction or "").strip(),
            "provider": provider, "model": model, "autonomy": autonomy,
            "status": "planning", "created_at": _now_iso(), "updated_at": _now_iso(),
            "plan": None, "step_index": 0, "approve_ok": False, "pause_flag": False,
            "posts": [], "scheduled": [], "published": [], "report": None, "log": [],
        }
        if not m["instruction"]:
            raise AgentError("متن ماموریت خالی است — ایده یا دستور خود را بنویسید")
        self._alog(m, f"ماموریت ساخته شد — مدل: {provider}/{model} · خودمختاری: {autonomy}")
        self.store.upsert(m)
        self._launch(m["id"])
        return m

    def _launch(self, mid: str) -> None:
        old = self.runners.get(mid)
        if old and not old.done():
            return
        self.runners[mid] = asyncio.create_task(self._runner(mid))

    async def control(self, mid: str, cmd: str) -> Dict[str, Any]:
        m = self.store.get(mid)
        if not m:
            raise AgentError("ماموریت پیدا نشد")
        if cmd == "approve":
            if m["status"] != "wait_approval":
                raise AgentError("این ماموریت منتظر تأیید نیست")
            m["approve_ok"] = True
            self._alog(m, "✅ کاربر برنامه را تأیید کرد — ادامه می‌دهم", "ok")
            self._launch(mid)
        elif cmd == "pause":
            if m["status"] in ("running", "planning"):
                m["pause_flag"] = True
                self._alog(m, "⏸ درخواست توقف ثبت شد — بین گام‌ها متوقف می‌شود", "warn")
        elif cmd == "resume":
            if m["status"] == "paused":
                m["status"] = "running"
                self._alog(m, "▶ ادامهٔ اجرا", "ok")
                self._launch(mid)
            else:
                raise AgentError("این ماموریت قابل ادامه نیست")
        elif cmd == "cancel":
            m["status"] = "cancelled"
            task = self.runners.pop(mid, None)
            if task and not task.done():
                task.cancel()
            self._alog(m, "🛑 ماموریت لغو شد", "warn")
        else:
            raise AgentError("فرمان ناشناخته")
        await self._emit(m)
        return {"ok": True, "status": m["status"]}

    def recover(self) -> None:
        """بعد از ری‌استارت سرور: ماموریت‌های ناتمام → paused تا کاربر ادامه دهد."""
        n = 0
        for m in self.store.load():
            if m.get("status") in ("planning", "running"):
                m["status"] = "paused"
                m["log"].append({"t": datetime.now().strftime("%H:%M:%S"), "level": "warn",
                                 "step": "", "msg": "سرور ری‌استارت شد — با دکمهٔ «ادامه» از همین‌جا ادامه دهید"})
                self.store.upsert(m)
                n += 1
        if n:
            try:
                self.ctx["log"](f"🧠 {n} ماموریت نیمه‌تمام پیدا شد — در حالت توقف", "warn")
            except Exception:
                pass

    async def finalize(self, mid: str) -> None:
        """زمان گزارش رسیده است (زمان‌بند صدایش می‌کند)."""
        m = self.store.get(mid)
        if not m or m["status"] in ("completed", "failed", "cancelled"):
            return
        self._alog(m, "🔔 زمان گزارش ماموریت رسید — گزارش نهایی ساخته می‌شود")
        await self._compile_report(m)
        m["status"] = "completed"
        await self._emit(m)

    # -------------------------------------------------- اجراکنندهٔ اصلی
    async def _runner(self, mid: str) -> None:
        try:
            while True:
                m = self.store.get(mid)
                if not m or m["status"] in ("completed", "failed", "cancelled", "paused", "waiting"):
                    return
                # ۱) اگر برنامه نیست → بساز
                if not m.get("plan"):
                    ok = await self._do_plan(m)
                    if not ok or m["status"] != "running":
                        return
                steps = m["plan"]["steps"]
                idx = m.get("step_index", 0)
                # ۲) تمام شد؟ → گزارش خودکار
                if idx >= len(steps):
                    if not m.get("report"):
                        await self._compile_report(m)
                    m["status"] = "completed"
                    await self._emit(m)
                    return
                step = steps[idx]
                # ۳) دروازهٔ تأیید
                if m["status"] == "wait_approval":
                    if not m.get("approve_ok"):
                        return
                    m["approve_ok"] = False
                    m["status"] = "running"
                # ۴) انتشار فوری در حالت غیر خودکار نیاز به تأیید دارد
                if step["action"] == "publish_now" and m["autonomy"] != "auto" and not m.get("publish_ok"):
                    m["publish_ok"] = False
                    m["status"] = "wait_approval"
                    self._alog(m, "⏳ انتشار فوری نیازمند تأیید شماست — دکمهٔ «تأیید» را بزنید", "warn", step["action"])
                    await self._emit(m)
                    return
                m["status"] = "running"
                self._alog(m, f"▶ گام {idx + 1} از {len(steps)}: {TOOL_NAMES.get(step['action'], step['action'])} — {step.get('reason') or ''}")
                await self._emit(m)
                try:
                    await self._exec_step(m, idx, step)
                    step["status"] = "done"
                except AgentError as e:
                    step["status"] = "failed"
                    step["error"] = str(e)
                    self._alog(m, f"⚠ این گام ناتمام ماند: {e} — به گام بعدی می‌رویم", "warn", step["action"])
                except asyncio.CancelledError:
                    raise
                except Exception as e:  # noqa
                    step["status"] = "failed"
                    step["error"] = str(e)
                    self._alog(m, f"⚠ خطای غیرمنتظره در گام: {e} — ادامه می‌دهیم", "warn", step["action"])
                m["publish_ok"] = False
                m["step_index"] = idx + 1
                await self._emit(m)
        except asyncio.CancelledError:
            pass
        except Exception as e:  # noqa
            try:
                m = self.store.get(mid)
                if m:
                    m["status"] = "failed"
                    self._alog(m, f"❌ ماموریت متوقف شد: {e}", "error")
                    await self._emit(m)
            except Exception:
                pass

    # -------------------------------------------------- برنامه‌ریزی
    async def _do_plan(self, m: Dict[str, Any]) -> bool:
        ai = self._ai_cfg()
        self._alog(m, "🧠 در حال فهمیدن ماموریت و ساخت برنامهٔ اجرایی…")
        await self._emit(m)
        active = self._active_platforms()
        budgets = ai.get("budgets", {})
        max_posts = int(budgets.get("posts_per_day", 4) or 4)
        rules = "\n".join(
            f"  - {pid} ({PLATFORM_INFO[pid]['name']}): حداکثر {PLATFORM_INFO[pid]['max_chars']} نویسه، "
            f"{PLATFORM_INFO[pid]['hashtags']} هشتگ، سبک: {PLATFORM_INFO[pid]['style']}"
            + (" — برای انتشار به عکس نیاز دارد (کتابخانهٔ رسانه)" if PLATFORM_INFO[pid]["needs_media"] else "")
            + (" — انتشار فقط به کانال (نام کانال لازم دارد)" if PLATFORM_INFO[pid]["is_messenger"] else "")
            for pid in active if pid in PLATFORM_INFO)
        caps = "، ".join(f"{pid} ≤ {c['cap']}" for pid, c in FOLLOW_CAPS.items() if pid in active)
        weekday = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه", "یکشنبه"][datetime.now().weekday()]
        system = f"""تو «مغزِ» ParsAgent هستی؛ ایجنت خودمختار شبکه‌های اجتماعی. ماموریت کاربر را به یک برنامهٔ اجرایی دقیق و واقع‌گرایانه تبدیل کن.

امروز: {datetime.now().strftime('%Y-%m-%d')} ({weekday}) — ساعت محلی: {datetime.now().strftime('%H:%M')}
پلتفرم‌های فعال کاربر: {', '.join(active) or 'هیچ‌کدام'}

ابزارهای موجود — فقط همین‌ها، نه بیشتر:
1) generate_content — تولید متن پست. params: {{"ideas": ["..."], "posts_per_idea": N, "platforms": ["instagram","twitter",...], "tone": "لحن", "note": "نکتهٔ اختیاری"}}
2) generate_image — با AI عکس می‌سازد (برای پست‌های عکس‌دار — اینستاگرام/فیسبوک/استوری). params: {{"prompts": ["توضیح عکس..."], "count": N, "purpose": "برای کدام پست/ایده"}}
3) generate_video — چاپخانهٔ ویدیو (سبک MoneyPrinterTurbo): موضوع را می‌دهد، فیلم کامل با گوینده و زیرنویس می‌سازد. params: {{"topic": "...", "seconds": 45, "voice": "fa-IR-FaridNeural", "aspect": "9:16", "note": "..."}}
4) dm_autoreply — پاسخ‌گوی خودکار دایرکت‌ها را روشن/تنظیم می‌کند. params: {{"platforms": ["instagram",...], "persona": "معرفی شما", "tone": "لحن", "faq": [{{"q":"...","a":"..."}}]}}
5) schedule_publish — پست‌های تولیدشده را زمان‌بندی و در صف انتشار می‌گذارد. params: {{"strategy": "spread_week" یا "best_times" یا "same_time", "per_day": N, "channels": {{"telegram": "نام کانال", "bale": "..."}}}}
6) publish_now — بلافاصله منتشر می‌کند (فقط وقتی کاربر صریحاً «همین حالا/فوری» گفته). params: {{"post_ids": []}}
7) follow_strategy — تصمیم فالو برای رشد: چند نفر در روز، از کجا (هشتگ) و در چه ساعاتی. params: {{"platform": "...", "daily_follows": N, "source": "hashtag:عکاسی یا user1,user2", "active_hours": [10, 14, 21]}}
8) wait_report — گزارش نهایی را به زمان مقرر موکول می‌کند (وقتی کاربر گفت «آخر هفته گزارش بده»). params: {{"at": "YYYY-MM-DDTHH:MM"}}
9) report — همین حالا گزارش نهایی می‌سازد. params: {{"include": ["posts","schedules","follows","media","dm"]}}
10) status_check — وضعیت پلتفرم‌ها را بررسی می‌کند. params: {{}}

نکته‌های مهم:
- اگر ماموریت «ویدیو» یا «ریلز» خواست، از generate_video استفاده کن و بعد خروجی‌اش را برای زمان‌بندی بگذار
- اگر برای پست اینستاگرام/فیسبوک عکس لازم است، به‌جای رهاکردن پست، گام generate_image بگذار
- اگر کاربر گفت «دایرکت‌ها را جواب بده»، dm_autoreply را با persona او تنظیم کن

قوانین پلتفرم‌ها (برای generate_content):
{rules}

محدودیت‌های امنی (نقض ممنوع):
- سقف پست روزانه: {max_posts} پست در روز
- سقف فالو روزانه: {caps or '—'}
- اینستاگرام و فیسبوک برای پستِ فید عکس لازم دارند؛ اگر کاربر رسانه نداده، برایشان محتوا تولید کن (پنل موقع زمان‌بندی هشدار می‌دهد)
- برای تلگرام/بله/روبیکا حتماً channels را پر کن؛ اگر کاربر کانالی نگفته، آن پلتفرم را از پست‌ها حذف کن
- گام آخر باید report یا wait_report باشد

خروجی: فقط یک JSON معتبر — بدون هیچ متن دیگر:
{{"title": "عنوان کوتاه ماموریت", "analysis": "۲ تا ۳ جمله تحلیل و استراتژی کلی", "steps": [{{"action": "...", "params": {{...}}, "reason": "دلیل کوتاه"}}]}}
حداکثر ۸ گام. منطقی و قابل اجرا؛ اعداد را محافظه‌کارانه انتخاب کن."""
        try:
            data = await llm_json(ai, m["provider"], m["model"], [
                {"role": "system", "content": system},
                {"role": "user", "content": "ماموریت من:\n" + m["instruction"]},
            ], temperature=0.3)
        except AgentError as e:
            m["status"] = "failed"
            self._alog(m, f"❌ ساخت برنامه ناموفق: {e}", "error")
            await self._emit(m)
            return False
        steps = []
        for s in (data.get("steps") or [])[:8]:
            act = str(s.get("action") or "").strip()
            if act in TOOL_NAMES and act != "status_check" or act == "status_check":
                steps.append({"action": act, "params": s.get("params") or {},
                              "reason": str(s.get("reason") or "")[:200], "status": "pending"})
        if not steps:
            steps = [{"action": "report", "params": {"include": ["posts", "schedules", "follows"]},
                      "reason": "برنامهٔ معتبری ساخته نشد؛ فقط گزارش", "status": "pending"}]
        m["title"] = str(data.get("title") or "ماموریت " + m["id"][1:6])[:80]
        m["plan"] = {"title": m["title"], "analysis": str(data.get("analysis") or "")[:600], "steps": steps}
        self._alog(m, f"📋 برنامه آماده شد: {len(steps)} گام — {m['title']}", "ok")
        if m["autonomy"] == "manual":
            m["status"] = "wait_approval"
            self._alog(m, "⏸ سطح «پیشنهادی» فعال است — برنامه را ببینید و «تأیید و اجرا» را بزنید", "warn")
            await self._emit(m)
            return False
        m["status"] = "running"
        await self._emit(m)
        return True

    # -------------------------------------------------- اجرای گام‌ها
    async def _exec_step(self, m: Dict[str, Any], idx: int, step: Dict[str, Any]) -> None:
        act, p = step["action"], step.get("params") or {}
        fn = getattr(self, "_tool_" + act, None)
        if not fn:
            raise AgentError(f"گام ناشناخته: {act}")
        await fn(m, p)

    # —— ۱) تولید محتوا
    async def _tool_generate_content(self, m: Dict[str, Any], p: Dict[str, Any]) -> None:
        ai = self._ai_cfg()
        active = set(self._active_platforms())
        ideas = [str(i).strip() for i in (p.get("ideas") or []) if str(i).strip()]
        if not ideas:
            ideas = [m["instruction"][:200]]
        per_idea = max(1, min(5, int(p.get("posts_per_idea") or 1)))
        platforms = [x for x in (p.get("platforms") or []) if x in PLATFORM_INFO and x in active]
        if not platforms:
            platforms = [x for x in PLATFORM_INFO if x in active and not PLATFORM_INFO[x]["needs_media"]]
        cap_total = int(ai.get("budgets", {}).get("posts_per_mission", 40) or 40)
        rules = "\n".join(f"- {pid} ({PLATFORM_INFO[pid]['name']}): حداکثر {PLATFORM_INFO[pid]['max_chars']} نویسه · "
                          f"{PLATFORM_INFO[pid]['hashtags']} هشتگ (ته‌متن، بعد از یک خط خالی) · سبک: {PLATFORM_INFO[pid]['style']}"
                          for pid in platforms)
        tone = p.get("tone") or "دوستانه و حرفه‌ای فارسی"
        note = p.get("note") or ""
        n_posts = 0
        for idea in ideas:
            if len(m["posts"]) >= cap_total:
                self._alog(m, f"⏹ سقف {cap_total} پست برای هر ماموریت پر شد — بقیهٔ ایده‌ها رد شد", "warn", "generate_content")
                break
            self._alog(m, f"✍️ تولید محتوا برای ایده: «{idea[:60]}»")
            await self._emit(m)
            data = await llm_json(ai, m["provider"], m["model"], [
                {"role": "system", "content":
                 f"تو نویسندهٔ حرفه‌ای شبکه‌های اجتماعی فارسی‌زبان هستی. برای این ایده، برای هر پلتفرمِ خواسته‌شده دقیقاً یک پست بنویس.\n\n"
                 f"قوانین پلتفرم‌ها:\n{rules}\n\nلحن: {tone}\n{('نکتهٔ کاربر: ' + note) if note else ''}\n\n"
                 "متن‌ها کاملاً فارسی و اصیل باشند؛ کلیشه ننویس. best_time = ساعت پیشنهادی انتشار برای مخاطب ایرانی (HH:MM).\n"
                 "برای هر پست یک image_prompt هم بنویس: توضیح انگلیسیِ کوتاه عکسِ پیشنهادی همان پست (برای تصویرسازی با AI).\n"
                 'خروجی فقط JSON: {"posts": [{"platform": "instagram", "text": "...", "hashtags": "#a #b", "best_time": "18:30", "image_prompt": "cinematic photo of ..."}]}'},
                {"role": "user", "content": f"ایده: {idea}\nپلتفرم‌ها: {', '.join(platforms)}"},
            ], temperature=0.8)
            got = 0
            for raw in (data.get("posts") or [])[:per_idea * len(platforms)]:
                pid = raw.get("platform")
                if pid not in platforms or len(m["posts"]) >= cap_total:
                    continue
                info = PLATFORM_INFO[pid]
                text = str(raw.get("text") or "").strip()[:info["max_chars"]]
                if not text:
                    continue
                m["posts"].append({
                    "id": f"p{len(m['posts']) + 1}", "idea": idea[:120], "platform": pid,
                    "text": text, "hashtags": str(raw.get("hashtags") or "").strip()[:200],
                    "best_time": str(raw.get("best_time") or "")[:5], "status": "draft",
                    "image_prompt": str(raw.get("image_prompt") or "").strip()[:400],
                    "media": "",
                })
                got += 1
            n_posts += got
            self._alog(m, f"✅ {got} پست برای «{idea[:40]}» تولید شد (مجموع: {len(m['posts'])})", "ok", "generate_content")
            await self._emit(m)
        if not m["posts"]:
            raise AgentError("هیچ پستی تولید نشد — ایده یا پلتفرم‌ها را واضح‌تر بنویسید")

    # —— ۱.۵) ساخت عکس با AI (۲.۴.۰)
    async def _tool_generate_image(self, m: Dict[str, Any], p: Dict[str, Any]) -> None:
        if not callable(self.ctx.get("generate_media_images")):
            raise AgentError("ماژول چاپخانهٔ رسانه آماده نیست (ai_media.py)")
        prompts = [str(x).strip() for x in (p.get("prompts") or []) if str(x).strip()]
        purpose = (p.get("purpose") or "").strip()
        if not prompts:
            raise AgentError("برای ساخت عکس، توضیح عکس (پرامپت) لازم است")
        count = max(1, min(6, int(p.get("count") or len(prompts))))
        prompts = (prompts * count)[:count]
        self._alog(m, f"🎨 ساخت {count} عکس با AI…" + (f" — {purpose[:80]}" if purpose else ""), "", "generate_image")
        await self._emit(m)
        res = await self.ctx["generate_media_images"](prompts, count, "square", m.get("id"))
        files = (res or {}).get("files") or []
        m.setdefault("media", []).extend(files)
        self._alog(m, f"✅ {len(files)} عکس ساخته و در «رسانه‌ها» ذخیره شد — از همان‌جا قابل انتشار است", "ok", "generate_image")

    # —— ۱.۶) چاپخانهٔ ویدیو (۲.۴.۰ — سبک MoneyPrinterTurbo)
    async def _tool_generate_video(self, m: Dict[str, Any], p: Dict[str, Any]) -> None:
        if not callable(self.ctx.get("generate_media_video")):
            raise AgentError("ماژول چاپخانهٔ رسانه آماده نیست (ai_media.py)")
        topic = (p.get("topic") or "").strip()
        if not topic:
            raise AgentError("موضوع ویدیو لازم است")
        seconds = max(15, min(180, int(p.get("seconds") or 45)))
        voice = str(p.get("voice") or "fa-IR-FaridNeural")
        aspect = str(p.get("aspect") or "9:16")
        note = (p.get("note") or "").strip()
        self._alog(m, f"🎬 چاپخانهٔ ویدیو روشن شد — «{topic[:60]}» ({seconds} ثانیه، {aspect})" +
                     (f" — نکته: {note[:80]}" if note else ""), "", "generate_video")
        await self._emit(m)
        res = await self.ctx["generate_media_video"](
            topic=topic + (f" — نکته: {note}" if note else ""), seconds=seconds, voice=voice, aspect=aspect)
        if not (res or {}).get("file"):
            raise AgentError("ساخت ویدیو ناموفق بود — جزئیات در لاگ")
        m.setdefault("media", []).append(res["file"])
        self._alog(m, f"✅ ویدیو آماده است: {res['file']} — در «رسانه‌ها» برای انتشار", "ok", "generate_video")

    # —— ۱.۷) پاسخ‌گوی دایرکت (۲.۴.۰)
    async def _tool_dm_autoreply(self, m: Dict[str, Any], p: Dict[str, Any]) -> None:
        if not callable(self.ctx.get("dm_configure")):
            raise AgentError("ماژول پاسخ‌گوی دایرکت آماده نیست (dm_reply.py)")
        active = set(self._active_platforms())
        platforms = [x for x in (p.get("platforms") or []) if x in active] or \
            [x for x in active if x in ("instagram", "telegram", "bale", "rubika", "twitter", "whatsapp")][:2]
        await self.ctx["dm_configure"]({
            "enabled": True, "platforms": {pid: (pid in platforms) for pid in active},
            "persona": str(p.get("persona") or "").strip(),
            "tone": str(p.get("tone") or "صمیمی و محترمانه — فارسی روان").strip(),
            "faq": p.get("faq") or [],
        })
        self._alog(m, f"💬 پاسخ‌گوی دایرکت برای {len(platforms)} پلتفرم فعال شد — جواب‌ها با شخصیت و لحن شما", "ok", "dm_autoreply")

    # —— ۲) زمان‌بندی انتشار
    async def _tool_schedule_publish(self, m: Dict[str, Any], p: Dict[str, Any]) -> None:
        ai = self._ai_cfg()
        strategy = p.get("strategy") or "spread_week"
        per_day = max(1, min(6, int(p.get("per_day") or ai.get("budgets", {}).get("posts_per_day", 3) or 3)))
        channels = p.get("channels") or {}
        images = list(self.ctx["media_images"]())
        posts = [x for x in m["posts"] if x.get("status") == "draft"]
        if not posts:
            self._alog(m, "پست آماده‌ای برای زمان‌بندی نیست (اول generate_content)", "warn", "schedule_publish")
            return
        # پخش زمان‌ها: از امروز، حداکثر per_day پست در روز، در ساعات پیشنهادی
        times: List[datetime] = []
        now = datetime.now()
        day_offset = 0
        hour_pool = list(DEFAULT_HOURS)
        for i in range(len(posts)):
            d = now + timedelta(days=day_offset)
            if strategy == "best_times":
                bt = (posts[i].get("best_time") or "").strip()
                try:
                    hh, mm = map(int, bt.split(":")[:2])
                except Exception:
                    hh, mm = hour_pool[i % len(hour_pool)], random.randint(2, 40)
            else:
                hh, mm = hour_pool[i % len(hour_pool)], random.randint(2, 40)
            if hh < 8 or hh >= 24:
                hh = 21
            when = d.replace(hour=hh, minute=mm, second=0, microsecond=0)
            if when <= now:
                when += timedelta(days=1)
            times.append(when)
            if (i + 1) % per_day == 0:
                day_offset += 1
        if strategy == "same_time":
            base_t = times[0]
            times = [base_t + timedelta(minutes=7 * i) for i in range(len(times))]
        n_ok, n_skip = 0, 0
        for post, when in zip(posts, times):
            pid = post["platform"]
            info = PLATFORM_INFO[pid]
            params: Dict[str, Any] = {"text": post["text"] + (
                "\n\n" + post["hashtags"] if post.get("hashtags") else "")}
            if info["is_messenger"]:
                target = (channels.get(pid) or "").strip()
                if not target:
                    n_skip += 1
                    post["status"] = "no_channel"
                    continue
                params["target"] = target
            elif info["needs_media"]:
                # ۲.۴.۰: اگر کتابخانه عکس ندارد، ایجنت خودش با AI عکس می‌سازد
                media = post.get("media") or ""
                if not media:
                    images = list(self.ctx["media_images"]())
                    media = images[0] if images else ""
                if media:
                    params["media"] = media
                elif callable(self.ctx.get("generate_media_images")):
                    try:
                        self._alog(m, f"🎨 عکس پست {post['id']} با AI ساخته می‌شود…", "", "generate_image")
                        await self._emit(m)
                        prompt = post.get("image_prompt") or (post["idea"] + " — high quality")
                        res = await self.ctx["generate_media_images"]([prompt], 1, "square", m.get("id"))
                        files = (res or {}).get("files") or []
                        if files:
                            params["media"] = files[0]
                            post["media"] = files[0]
                        else:
                            n_skip += 1
                            post["status"] = "needs_media"
                            continue
                    except Exception as e:  # noqa
                        self._alog(m, f"⚠ ساخت عکس ناموفق: {e}", "warn", "generate_image")
                        n_skip += 1
                        post["status"] = "needs_media"
                        continue
                else:
                    n_skip += 1
                    post["status"] = "needs_media"
                    continue
            entry = {
                "title": f"AI · پست {post['id']} — {info['name']}",
                "type": "action", "platform": pid, "action": info["post_action"],
                "params": params,
                "timing": {"type": "once", "at": when.isoformat(timespec="seconds")},
                "pacing": {}, "enabled": True, "mission_id": m["id"], "post_id": post["id"],
            }
            job = await self.ctx["add_schedule"](entry)
            post["status"] = "scheduled"
            m["scheduled"].append({"post_id": post["id"], "platform": pid,
                                   "at": when.isoformat(timespec="seconds"),
                                   "job_id": job.get("id"), "action": info["post_action"]})
            n_ok += 1
        msg = f"📅 {n_ok} پست در صف انتشار قرار گرفت" + (
            f" — {n_skip} مورد رد شد (عکس یا کانال ندارند؛ وضعیت‌شان در لیست پست‌ها مشخص است)" if n_skip else "")
        self._alog(m, msg, "ok" if n_ok else "warn", "schedule_publish")
        if n_skip:
            self._alog(m, "💡 برای پست‌های اینستاگرام/فیسبوک از تب «رسانه‌ها» عکس بگذارید؛ برای پیام‌رسان‌ها نام کانال را در ماموریت بگویید", "warn")

    # —— ۳) انتشار فوری
    async def _tool_publish_now(self, m: Dict[str, Any], p: Dict[str, Any]) -> None:
        ids = set(p.get("post_ids") or [])
        posts = [x for x in m["posts"] if (not ids or x["id"] in ids) and x.get("status") in ("draft", "no_channel")]
        targets = [x for x in posts if x["status"] == "draft"]
        if not targets:
            self._alog(m, "پست قابل انتشار فوری نیست", "warn", "publish_now")
            return
        images = list(self.ctx["media_images"]())
        for post in targets:
            info = PLATFORM_INFO[post["platform"]]
            params = {"text": post["text"] + ("\n\n" + post["hashtags"] if post.get("hashtags") else "")}
            if info["is_messenger"]:
                ch = ((p.get("channels") or {}).get(post["platform"]) or "").strip()
                if not ch:
                    self._alog(m, f"پست {post['id']} کانال ندارد — رد شد", "warn", "publish_now")
                    continue
                params["target"] = ch
            elif info["needs_media"]:
                media = post.get("media") or (images[0] if images else "")
                if not media and callable(self.ctx.get("generate_media_images")):
                    try:
                        prompt = post.get("image_prompt") or (post["idea"] + " — high quality")
                        res = await self.ctx["generate_media_images"]([prompt], 1, "square", m.get("id"))
                        media = ((res or {}).get("files") or [""])[0]
                    except Exception:
                        media = ""
                if not media:
                    self._alog(m, f"پست {post['id']} برای {info['name']} عکس لازم دارد — از تب رسانه‌ها اضافه کنید", "warn", "publish_now")
                    continue
                params["media"] = media
            self._alog(m, f"🚀 انتشار فوری پست {post['id']} در {info['name']} …")
            res = await self.ctx["run_action"](post["platform"], info["post_action"], params)
            m["published"].append({"post_id": post["id"], "platform": post["platform"],
                                   "ok": bool(res.get("ok")), "message": res.get("message", ""),
                                   "at": _now_iso()})
            post["status"] = "published" if res.get("ok") else "failed"

    # —— ۴) استراتژی فالو
    async def _tool_follow_strategy(self, m: Dict[str, Any], p: Dict[str, Any]) -> None:
        pid = p.get("platform")
        if pid not in FOLLOW_CAPS or pid not in PLATFORM_INFO:
            raise AgentError(f"برای «{pid}» استراتژی فالو پشتیبانی نمی‌شود "
                             f"(فقط: {', '.join(FOLLOW_CAPS)})")
        cap = FOLLOW_CAPS[pid]
        daily = max(1, min(cap["cap"], int(p.get("daily_follows") or 10)))
        source = (p.get("source") or "").strip()
        if not source:
            raise AgentError("منبع فالو مشخص نیست — هشتگ یا لیست کاربران لازم است")
        hours = [int(h) for h in (p.get("active_hours") or []) if 6 <= int(h) <= 23] or [10, 14, 21]
        hours = sorted(set(hours))[:4]
        per_run = max(1, daily // len(hours))
        plan = {"daily_follows": daily, "per_run": per_run, "hours": hours,
                "source": source, "created_at": _now_iso(), "mission_id": m["id"]}
        # ثبت در تنظیمات برای نمایش در پنل
        try:
            st = self.ctx["get_settings"]()
            st.setdefault("ai", {}).setdefault("follow_plans", {})[pid] = plan
            self.ctx["save_settings"](st)
        except Exception:
            pass
        # ساخت زمان‌بندی‌های روزانه
        for h in hours:
            entry = {
                "title": f"AI · فالو {PLATFORM_INFO[pid]['name']} ساعت {h}",
                "type": "action", "platform": pid, "action": cap["action"],
                "params": {"target": source, "count": per_run},
                "timing": {"type": "daily", "hours": [h], "minute": random.randint(2, 25)},
                "pacing": {"delay_min": 45, "delay_max": 140},
                "enabled": True, "mission_id": m["id"],
            }
            await self.ctx["add_schedule"](entry)
        self._alog(m, f"🎯 استراتژی فالو ثبت شد: {daily} نفر در روز ({per_run} نفر در {len(hours)} نوبت ساعت‌های "
                     f"{'، '.join(str(h) for h in hours)}) از «{source}» — سقف امن {cap['cap']}", "ok", "follow_strategy")

    # —— ۵) گزارش زمان‌دار
    async def _tool_wait_report(self, m: Dict[str, Any], p: Dict[str, Any]) -> None:
        at = (p.get("at") or "").strip()
        try:
            when = datetime.fromisoformat(at)
        except Exception:
            when = datetime.now() + timedelta(days=7)
        if when <= datetime.now():
            when = datetime.now() + timedelta(hours=1)
        entry = {
            "title": f"AI · گزارش نهایی «{m['title'][:30]}»",
            "type": "ai_report", "platform": "instagram", "action": "ai_report",
            "params": {}, "timing": {"type": "once", "at": when.isoformat(timespec="seconds")},
            "pacing": {}, "enabled": True, "mission_id": m["id"],
        }
        await self.ctx["add_schedule"](entry)
        m["status"] = "waiting"
        self._alog(m, f"⏰ گزارش نهایی برای {when.strftime('%Y-%m-%d ساعت %H:%M')} زمان‌بندی شد — تا آن زمان کار خودتان را بکنید", "ok", "wait_report")

    # —— ۶) گزارش فوری
    async def _tool_report(self, m: Dict[str, Any], p: Dict[str, Any]) -> None:
        await self._compile_report(m)
        m["status"] = "completed"

    # —— ۷) بررسی وضعیت
    async def _tool_status_check(self, m: Dict[str, Any], p: Dict[str, Any]) -> None:
        active = self._active_platforms()
        self._alog(m, f"🌐 پلتفرم‌های فعال: {', '.join(active) or '—'} | پست‌های تولیدشده: {len(m['posts'])} | "
                     f"در صف انتشار: {len(m['scheduled'])}", "ok", "status_check")

    # -------------------------------------------------- گزارش نهایی
    async def _compile_report(self, m: Dict[str, Any]) -> None:
        ai = self._ai_cfg()
        by_platform: Dict[str, int] = {}
        for post in m["posts"]:
            by_platform[post["platform"]] = by_platform.get(post["platform"], 0) + 1
        try:
            follow_plans = (self.ctx["get_settings"]().get("ai", {}).get("follow_plans") or {})
        except Exception:
            follow_plans = {}
        fp = {pid: v.get("daily_follows") for pid, v in follow_plans.items() if v.get("mission_id") == m["id"]}
        stats = {
            "ideas": len({post.get("idea") for post in m["posts"]}),
            "posts_generated": len(m["posts"]),
            "by_platform": by_platform,
            "scheduled": len(m["scheduled"]),
            "published_now": len([x for x in m["published"] if x.get("ok")]),
            "follow_plans": fp,
        }
        m["report"] = {"stats": stats, "summary": "", "created_at": _now_iso()}
        self._alog(m, "📝 در حال نوشتن گزارش مدیریتی…")
        await self._emit(m)
        try:
            text = await llm_chat(ai, m["provider"], m["model"], [
                {"role": "system", "content":
                 "تو گزارشگر مدیریتی ParsAgent هستی. با توجه به این آمار، یک گزارش کوتاه و کاربردی فارسی بنویس: "
                 "۴ تا ۶ بولت با اعداد، یک جمله دربارهٔ «گام بعدی پیشنهادی»، و یک جملهٔ جمع‌بندی. "
                 "از چرتکه و توضیح فنی بپرهیز؛ کارفرما وقت ندارد. فقط متن گزارش — بدون عنوان اضافه."},
                {"role": "user", "content":
                 f"ماموریت: {m['title']}\nدستور اولیه: {m['instruction'][:400]}\nآمار به JSON: {json.dumps(stats, ensure_ascii=False)}"},
            ], temperature=0.5, max_tokens=700)
            m["report"]["summary"] = text.strip()[:2500] or "گزارش ساخته شد (بدون متن خلاصه)"
        except AgentError as e:
            m["report"]["summary"] = f"گزارش آماری ساخته شد؛ خلاصه‌نویسی ناموفق بود ({e})"
        self._alog(m, "✅ گزارش نهایی آماده است — تب هوش مصنوعی ← کارت ماموریت", "ok", "report")
        await self._emit(m)

    # -------------------------------------------------- خلاصه برای پنل
    def summarize(self, m: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": m["id"], "title": m["title"], "instruction": m["instruction"][:300],
            "provider": m["provider"], "model": m["model"], "autonomy": m["autonomy"],
            "status": m["status"], "created_at": m["created_at"], "updated_at": m.get("updated_at"),
            "plan": m.get("plan"), "step_index": m.get("step_index", 0),
            "counts": {"posts": len(m.get("posts") or []), "scheduled": len(m.get("scheduled") or []),
                       "published": len(m.get("published") or [])},
            "report": m.get("report"),
            "log": (m.get("log") or [])[-25:],
            "media": (m.get("media") or [])[:12],
            "posts": [{"id": x["id"], "platform": x["platform"], "idea": x.get("idea", ""),
                       "text": x["text"][:280], "status": x.get("status", "draft"),
                       "media": x.get("media", "")} for x in (m.get("posts") or [])[:60]],
        }

    def list_missions(self) -> List[Dict[str, Any]]:
        return [self.summarize(m) for m in self.store.load()]
