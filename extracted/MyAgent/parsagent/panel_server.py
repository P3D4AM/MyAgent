# -*- coding: utf-8 -*-
"""
ParsAgent — پنل مدیریت محلی (بک‌اند)
اجرا:  python panel_server.py
نیازمندی‌ها:  pip install fastapi uvicorn python-multipart playwright

تغییرهای این نسخه:
  - اجرای سریع: نتیجه از طریق state برگردانده می‌شود؛ فرم هرگز بازسازی خودکار نمی‌شود
  - آپلود رسانه از سیستم (پوشه media) برای انتشار عکس/استوری/پست
  - زمان‌بند کامل: هر X دقیقه / ساعت‌های مشخص روزانه / یک‌بار
  - ضبط ماکرو فقط با دکمه «شروع ضبط» آغاز می‌شود — با بالا آمدن سرور شروع نمی‌شود
  - تست بات + تنظیمات ضد شناسایی + ذخیره نام کاربری/رمز + حل کپچا
  - ۲.۱.۰: لانچر — رفع گیرکردن روی «در حال راه‌اندازی سرور» (بررسی سلامت
    بدون پروکسی/VPN + نمایش زندهٔ خطاهای سرور در لاگ لانچر)
  - ۲.۲.۰: ضد شناسایی v3 «پیشرفته» بر اساس متد روز دنیا:
    اثر انگشت پایدار per-profile (نویز تصادفیِ هر بار خودش پرچم قرمز است!)،
    ۴ گروه تنظیم (هویت مرورگر / اثر انگشت دیجیتال / رفتار انسانی / هر پلتفرم)،
    ماژول‌های جدید: window.chrome کامل، نویز پایدار Audio، ماسک فونت،
    مشخصات سخت‌افزار واقع‌نما، شیلد WebRTC، کلاک native بودن توابع،
    حرکت موس منحنی، اسکرول تصادفی، سرعت تایپ، مکث شبانه
  - ۲.۲.۰: زمان‌بندی پخش ماکرو — پخش ماکروها هم مثل اکشن‌ها قابل
    زمان‌بندی شد (تکرارشونده / روزانه / یک‌بار + مکث شبانه)
  - ۲.۳.۰: تب «🧠 هوش مصنوعی» — ایجنت خودمختار!
    فقط ایده را می‌گویید؛ خودش برنامه می‌سازد، برای هر پلتفرم محتوا
    تولید می‌کند، زمان انتشار می‌چیند، استراتژی فالو (چند نفر/چه ساعتی)
    تصمیم می‌گیرد و آخر کار گزارش فارسی می‌دهد.
    سرویس‌ها (رایگان و پولی): Z.ai (GLM) — اول لیست، OpenAI،
    Anthropic Claude، Google Gemini، Groq، DeepSeek، OpenRouter و
    هر اندپوینت سازگار با OpenAI (مثل Ollama) — ماژول ai_agent.py
  - ۲.۴.۰: چاپخانهٔ رسانه + پاسخ‌گوی دایرکت:
    • 🎨 ساخت عکس با AI (ai_media.py) — Z.ai GLM-Image (کد: glm-image)،
      OpenAI و Pollinations (رایگانِ محدود) با زنجیرهٔ جایگزین خودکار
    • 🎬 چاپخانهٔ ویدیو به سبک پروژهٔ متن‌باز MoneyPrinterTurbo
      (github.com/harry0703/MoneyPrinterTurbo): موضوع ← فیلم‌نامهٔ AI ←
      گویندهٔ رایگان edge-tts ← تصویر AI برای هر صحنه ← زیرنویس فارسی
      حک‌شده ← ترکیب MP4 با ffmpeg + موسیقی اختیاری
    • 💬 پاسخ‌گوی خودکار دایرکت (dm_reply.py) — جواب طبیعی در هر
      پلتفرم با شخصیت و لحن شما، سقف روزانه، ساعت‌های فعال و پیش‌نمایش
  - ۲.۵.۰: نصب آفلاین بدون اینترنت (همه‌چیز داخل launcher.py):
    • «💾 ساخت بستهٔ آفلاین» — همهٔ پیش‌نیازها به‌صورت wheel آماده +
      (اختیاری) کرومیوم، داخل پوشهٔ پروژه در offline_bundle/ ذخیره می‌شوند
    • «📀 نصب آفلاین» — روی هر سیستم بدون اینترنت، نصب کامل فقط از
      همان پوشه؛ با محافظ سازگاری پایتون (خطای free-threaded مثل
      cp313t با پیام فارسی گفته می‌شود، نه خطای کامپایلر Rust)
  - ۲.۶.۰: تعمیر مرورگر و ورود خودکار:
    • زنجیرهٔ مرورگر هوشمند — Edge → Chrome → Chromiumِ داخل Playwright؛
      اگر Chromium داخل Playwright نصب نباشد، خودکار با آینهٔ npmmirror
      دانلود می‌شود (رفع «Executable doesn't exist …chromium-…»)
    • Firefox هم به «مرورگر ترجیحی» تنظیمات اضافه شد
    • پروکسی سیستم ویندوز (v2rayN و مثل آن) خودکار خوانده و روی
      مرورگر اعمال می‌شود — همان کاری که Edge با آن می‌کند
  - ۲.۷.۰: ناوبری و ورود مقاوم:
    • goto با تلاش مجدد — خطاهای شبکه (net::ERR_CONNECTION_CLOSED و…)
      دوباره امتحان و در پایان با راهنمای فارسی پروکسی/VPN اعلام می‌شوند
    • ورود خودکار همهٔ ۷ پلتفرم از نو: بستن بنر کوکی، چند سلکتور برای
      هر فیلد، فلو دومرحله‌ای X (یوزرنیم → بعدی → رمز → ورود)،
      تشخیص «از قبل وارد شده»، و پیام دقیق برای OTP/کپچا/رمز نادرست؛
      «فیلد دیده نشد» فقط وقتی گفته می‌شود که صفحه واقعاً آمده باشد
  - ۲.۸.۰: نصب هوشمند روی سیستم خام (تغییرات در launcher.py):
    • اگر لانچر با پایتون free-threaded (مثل python3.13t) باز شود، خودش را
      با پایتون استانداردِ سیستم بازگشایی می‌کند؛ اگر هیچ نبود، دکمهٔ
      «🐍 پایتون استاندارد» نسخهٔ ۳.۱۲ را از python.org دانلود و خاموش
      نصب می‌کند — دیگر خطای کامپایل Rust/C++ (maturin / link.exe /
      «Microsoft Visual C++ 14.0 or greater is required») پیش نمی‌آید
    • نصب اینترنتی فقط از wheel آماده (--only-binary) و در صورت نیاز
      خودکار با آینه‌های جایگزین (Tsinghua / Aliyun) دوباره تلاش می‌کند
  - ۲.۹.۰: تعمیر دو باگ گزارش‌شده (گروه ۴ + فیلد ورود اینستاگرام):
    • «گروه ۴ — فعال برای کدام پلتفرم‌ها؟» در تنظیمات عملاً کار نمی‌کرد:
      کلیک روی چیپ‌ها دوبار تاگل می‌شد (رفتار پیش‌فرض <label> + کد دستی)
      و نتیجه همیشه به حالت اول برمی‌گشت — با preventDefault رفع شد.
    • «فیلد ورود دیده نشد» روی اینستاگرام وقتی صفحه و فرم واقعاً باز بود:
      ۱) موتور پیدا کردن فیلد فقط «اولین» نتیجهٔ هر سلکتور را چک می‌کرد و
         نسخهٔ مخفیِ فیلد (تغییر حساب) بالای نسخهٔ مرئی نشسته بود؛
         حالا همهٔ نتایج چک و اولین فیلدِ «مرئی» برمی‌خورد.
      ۲) سلکتورها فقط انگلیسی بودند؛ ولی ضد شناسایی خودمان زبان مرورگر
         را fa-IR می‌گذارد و سایت لیبل‌ها را فارسی رندر می‌کند — سلکتورهای
         فارسی (aria-label/placeholder) برای همهٔ ۷ پلتفرم اضافه شد.
      ۳) آخرین راه همیشه: «اولین فیلد متنیِ مرئی داخل فرم» — حتی اگر
         ساختار کل سایت عوض شود، فرم ورود فیلد متن + رمز دارد.
      ۴) اگر باز هم فیلد پیدا نشد، صفات همهٔ فیلدهای صفحه در «لاگ‌ها»
         ثبت می‌شود تا ساختار جدید سایت سریع شناسایی شود.
      ۵) «از قبل وارد شده» دیگر مثبت کاذب نمی‌گوید (اینستاگرام گاهی
         از /accounts/login/ به صفحهٔ اصلی هدایت می‌کند ولی فرم همان‌جاست).
  - ۲.۱۰.۰: سه درخواست کاربر — موتور لایک، استوریِ واقعی، راهنمای کلیدها:
    • ❤ موتور لایک همهٔ ۴ پلتفرم (اینستاگرام/توییتر/فیسبوک/لینکدین) از نو:
      چک ورود قبل از هر چیز (پیام واضح به‌جای «لایک انجام شد: ۰»)، جست‌وجوی
      دکمهٔ لایک فقط «داخل همان پست» (نه کل صفحه — قبلاً لایکِ کامنت/دکمهٔ
      جانبی زده می‌شد)، سلکتور دقیق به‌جای «شاملِ Like» (قبلاً دکمهٔ «Liked»
      پستِ قبلاً لایک‌شده را می‌گرفت و لایک را برمی‌داشت!)، فارسی+انگلیسی،
      تأیید بعد از کلیک (تغییر دکمه به «برداشتن پسند/Unlike»)، انتظار برای
      بارگیری فید و اسکرول تدریجی برای پست‌های بعدی.
    • 📸 اکشن «انتشار استوری» بعد از تحقیق اصلاح شد: اینستاگرام اجازهٔ
      استوری از نسخهٔ وب را نمی‌دهد → حذف شد؛ فیسبوک تنها پلتفرمی است که
      استوری عکس از وب را می‌پذیرد → اکشن «انتشار استوری» برایش اضافه شد.
      (توییتر اصلاً استوری ندارد، لینکدین از ۲۰۲۱ حذف کرد، تلگرام فقط
      پریمیوم و فقط از اپ، بله/روبیکا نسخهٔ وب استوری ندارند.)
    • 🔑 زیر هر فیلد کلید API در «تنظیمات ← هوش مصنوعی» دکمهٔ «؟» با
      آموزش گام‌به‌گام و لینک مستقیم ساختن کلید برای همان سرویس.
  - ۲.۱۱.۰: دو درخواست کاربر — واتساپ وب + تغییرات شفاف نسخه‌ها:
    • 🟢 پلتفرم هشتم: واتساپ وب (web.whatsapp.com):
      - ورود مخصوص واتساپ: باز کردن صفحه و «صبر هوشمند برای اسکن QR» —
        راهنمای فارسی گام‌به‌گام (گوشی ← تنظیمات ← دستگاه‌های متصل ←
        اتصال دستگاه) و تا ۳ دقیقه منتظر مانده و بعد اعلام نتیجه؛
        تشخیص «از قبل وارد شده» (فهرست چت‌ها آماده است).
      - اکشن «ارسال پیام»: جستجوی مخاطب/گروه، باز شدن چت، تایپ انسانی و
        ارسال با Enter/دکمهٔ ارسال — با پشتیبانی از چند گیرنده (با ویرگول)،
        فاصلهٔ انسانی بین گیرنده‌ها و پیام فارسی روشن برای هر خطا.
      - پاسخ‌گوی دایرکت واتساپ (dm_reply) و تولید محتوای AI برای واتساپ.
      - نکتهٔ ایران: واتساپ هم مثل اینستاگرام از IP ایران باز نمی‌شود →
        راهنمای پروکسی/VPN همان پیام‌های فارسی قبل را می‌گیرد.
    • 📜 «چه چیز تازه است؟» — کادر تغییرات هر نسخه در بالای پنل:
      کاربر فرمود «۲.۱۰ همون ۲.۹ بود، تغییری ندیدم» — تغییرها بودند ولی
      دیده نمی‌شدند (موتور لایک داخل کد است، «؟» کوچک است…). از این به
      بعد هر نسخه فهرست تغییراتش را همین‌جا، به چشم، نشان می‌دهد.
  - ۲.۱۳.۰: رفع خطای 403 سرویس‌های AI در ایران (گزارش کاربر: خطای 403
    «Forbidden» از گروک/Groq و صفحهٔ HTML 403 از جمینای، هنگام «نوشتن
    فیلم‌نامهٔ صحنه‌ها» در چاپخانهٔ ویدیو):
    • 🛡 «پروکسی فراخوانی سرویس‌ها» — فیلد جدید در تنظیمات ← هوش مصنوعی:
      همهٔ فراخوانی‌های AI (فیلم‌نامه/چت/عکس/دانلود) از آن عبور می‌کنند.
      اگر خالی باشد، پروکسی سیستم ویندوز (System Proxy / VPN روشن)
      خودکار خوانده می‌شود — با رفع باگ قدیمی urllib که برای مقصدِ https
      آدرسِ https:// به پروکسیِ HTTP لوکال (v2rayN/Nekoray) می‌داد.
      علت خطا: درخواست‌های پایتون به‌تنهایی از VPN مرورگر عبور نمی‌کنند
      و این سرویس‌ها IP ایران را 403 می‌کنند؛ Z.ai پروکسی لازم ندارد.
    • 🔌 دکمهٔ «تست اتصال» کنار فیلد پروکسی — تنظیمات را ذخیره و سرویس
      انتخابی را با یک پیام فارسی وصل/غیروصل آزمایش می‌کند.
    • 📢 پیام خطای 403/401/429 سرویس‌ها فارسیِ راه‌حل‌دار شد (به‌جای
      «Forbidden» خام یا HTML گوگل) و خطای دائمی دیگر ۳ بار تلاش مجددِ
      بی‌فایده نمی‌کند.
    • ➕ سرویس جدید: xAI Grok (گروک) — رابط OpenAI، از ایران فقط با پروکسی.
  - ۲.۱۴.۰: رفع خطای 404 مدل‌ها + تعمیر کامل ضبط/پخش ماکرو:
    • ♻️ خطای 404 «The model … does not exist or you do not have access»
      (گزارش کاربر: llama-3.3-70b-versatile روی Groq): سرویس‌ها مدل‌های
      قدیمی را می‌بندند — Groq در ۱۶ اوت ۲۰۲۶ llama-3.3-70b-versatile و
      llama-3.1-8b-instant را فقط Enterprise کرد. سه لایهٔ رفع:
      ۱) کاتالوگ با مدل‌های رسمی جدید (GPT-OSS 120B/20B، Qwen 3.8)؛
      ۲) مدلِ مردهٔ ذخیره‌شده در startup خودکار با جایگزین رسمی عوض می‌شود؛
      ۳) دکمهٔ «🔄 مدل‌های زنده» — فهرست مدل‌ها مستقیم از خود سرویس
      (GET /models) با کلید کاربر؛ اندپوینت جدید /api/ai/models.
    • 🎬 ماکرو (درخواست کاربر: «ضبط و پخش درست کار نمی‌کند؛ هنگام خاموش
      کردن ضبط نشود؛ فقط در پنجرهٔ مرورگرِ شبکهٔ اجتماعی ضبط شود»):
      ۱) متنِ تایپ‌شده در جعبه‌های چت contentEditable (اینستاگرام/واتساپ/
      تلگرام) قبلاً هرگز ضبط نمی‌شد → پخش، ارسالِ خالی می‌زد؛ حالا ضبط
      می‌شود (رویداد focusout + Enter).
      ۲) ضبط فقط در دامنهٔ خودِ پلتفرم (PLATFORM_DOMAINS) — کلیک روی
      پنلِ باز‌شده داخل همان مرورگر یا سایت‌های دیگر نادیده گرفته می‌شود؛
      دکمهٔ «توقف» دیگر هرگز داخل ماکرو نمی‌نشیند (چک در مرورگر + سرور).
      ۳) پخش مقاوم: تبِ درست از روی دامنهٔ هر رخداد پیدا می‌شود، عنصر در
      همهٔ فریم‌ها (iframe) جستجو می‌شود و رخداد ناموفق با دلیل اعلام
      می‌شود (قبلاً بی‌صدا رد می‌شد و «کار نمی‌کند» فقط تعداد کم بود).
  - ۲.۱۵.۰: کنترل کامل پخش ماکرو (چهار درخواست کاربر):
    • ⏹ دکمهٔ «توقف پخش» — اندپوینت جدید POST /api/macro/stop-run: پرچم
      توقف بین رخدادها و داخل مکث‌ها (چانک ۰.۲ ثانیه) چک می‌شود و پخش
      همان‌جا قطع می‌شود؛ وضعیت پخشِ جاری هم در /api/state می‌آید.
    • 🎯 پلتفرم هر ماکرو از لحظهٔ ضبط داخل فایل ذخیره می‌شود و پخش روی
      همان اجرا می‌شود — دراپ‌داونِ پخش از رابط حذف شد (باگ: انتخاب
      پلتفرم، وسطِ پُل ۳ ثانیه‌ای state و بازسازی لیست، به گزینهٔ اول
      برمی‌گشت). ماکروهای قدیمی (فرمت لیست) هنوز با دراپ‌داونِ همان ردیف
      کار می‌کنند.
    • 🌐 شروع پخش = رفتن تبِ مرورگر به صفحهٔ اصلی همان پلتفرم — قبلاً
      صفحهٔ about:blank می‌ماند و هیچ رخدادی پیدا نمی‌شد.
    • 🔒 پایان یا توقف پخش = بسته شدن خودکار پنجرهٔ مرورگرِ همان
      پلتفرم؛ و اگر کاربر خودش مرورگر را بسته باشد، ensure() حالا
      سلامتِ واقعیِ context را چک می‌کند و به‌جای خطای «Target … has
      been closed» تا ری‌استارت، دوباره بازش می‌کند.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from ai_agent import AgentSystem, llm_chat, llm_json
import ai_media
from dm_reply import DMAuto

# ---------------------------------------------------------------- مسیرها
BASE = Path(__file__).resolve().parent
PORT = int(os.environ.get("PANEL_PORT", "8765"))
MEDIA_DIR = BASE / "media"
CONFIG_DIR = BASE / "config"
MACROS_DIR = BASE / "macros"
PROFILES_DIR = BASE / "profiles"
STATIC_DIR = BASE / "static"
for d in (MEDIA_DIR, CONFIG_DIR, MACROS_DIR, PROFILES_DIR, STATIC_DIR):
    d.mkdir(parents=True, exist_ok=True)

F_SETTINGS = CONFIG_DIR / "settings.json"
F_CREDS = CONFIG_DIR / "credentials.json"
F_SCHED = CONFIG_DIR / "schedules.json"

# ---------------------------------------------------------------- پلتفرم‌ها
PLATFORMS: List[Dict[str, str]] = [
    {"id": "instagram", "name": "اینستاگرام", "icon": "📸", "url": "https://www.instagram.com"},
    {"id": "twitter",   "name": "توییتر (X)",  "icon": "🐦", "url": "https://x.com"},
    {"id": "telegram",  "name": "تلگرام",      "icon": "✈️", "url": "https://web.telegram.org"},
    {"id": "whatsapp",  "name": "واتساپ",      "icon": "🟢", "url": "https://web.whatsapp.com"},
    {"id": "facebook",  "name": "فیسبوک",      "icon": "📘", "url": "https://www.facebook.com"},
    {"id": "linkedin",  "name": "لینکدین",     "icon": "💼", "url": "https://www.linkedin.com"},
    {"id": "bale",      "name": "بله",         "icon": "💬", "url": "https://ble.ir"},
    {"id": "rubika",    "name": "روبیکا",      "icon": "🟣", "url": "https://web.rubika.ir"},
]
PLAT_IDS = [p["id"] for p in PLATFORMS]

LOGIN_URLS = {
    "instagram": "https://www.instagram.com/accounts/login/",
    "twitter": "https://x.com/i/flow/login",
    "telegram": "https://web.telegram.org",
    "whatsapp": "https://web.whatsapp.com",
    "facebook": "https://www.facebook.com/login",
    "linkedin": "https://www.linkedin.com/login",
    "bale": "https://ble.ir",
    "rubika": "https://web.rubika.ir",
}

# ۲.۱۴.۰ — دامنه‌های مجازِ ضبط ماکرو (درخواست کاربر: «ماکرو فقط در پنجرهٔ
# مرورگرِ شبکهٔ اجتماعی ضبط شود، نه بقیهٔ پنجره‌ها/سایت‌ها»): رویدادهایی
# که از دامنهٔ خودِ پلتفرم نمی‌آیند (مثل کلیک روی پنلِ باز‌شده داخل همان
# مرورگر، یا سایت‌های دیگری که کاربر وسط ضبط باز می‌کند) نادیده گرفته
# می‌شوند تا ماکرو تمیز بماند و پخشش نشکند.
PLATFORM_DOMAINS: Dict[str, List[str]] = {
    "instagram": ["instagram.com", "cdninstagram.com", "facebook.com", "fb.com", "fbcdn.net"],
    "twitter": ["x.com", "twitter.com", "twimg.com", "t.co"],
    "telegram": ["telegram.org", "t.me", "telesco.pe"],
    "whatsapp": ["whatsapp.com", "whatsapp.net"],
    "facebook": ["facebook.com", "fb.com", "fbcdn.net"],
    "linkedin": ["linkedin.com", "lnkd.in", "licdn.net"],
    "bale": ["ble.ir", "bale.ai"],
    "rubika": ["rubika.ir", "rubico.ir"],
}

# ---------------------------------------------------------------- ورود خودکار (۲.۶/۲.۷)
# جریان ورود هر پلتفرم — لیست سلکتورها به‌ترتیب تلاش. صفحه‌های اینستاگرام/X
# روی VPN کند باز می‌شوند؛ برای همین همه با نظرسنجی و مهلت بلند صبر می‌شوند.
# otp=True یعنی پیام‌رسان با شماره تلفن + کد پیامکی (کد را فقط خود کاربر می‌زند).
#
# ۲.۹.۰ — چرا سلکتورها این‌قدر زیاد شدند؟ سه دلیل:
#   ۱) ضد شناسایی خودمان زبان مرورگر را fa-IR می‌گذارد ⇒ سایت‌ها لیبل/placeholder
#      فیلدها را «فارسی» رندر می‌کنند و سلکتورهای انگلیسیِ aria-label دیگر نمی‌گیرند.
#   ۲) ساختار جدید صفحهٔ ورود اینستاگرام (۲۰۲۵) ممکن است name/autocomplete نداشته باشد.
#   ۳) همه‌جا آخرین راه، «اولین فیلد متنیِ مرئی داخل فرم» است — حتی اگر سایت
#      کل ساختارش عوض شده باشد، فرم ورود همیشه یک فیلد متن + یک فیلد رمز دارد.
# ضمناً همهٔ نتایجِ هر سلکتور چک می‌شوند (نه فقط اولی) — چون سایت‌ها گاهی
# یک نسخهٔ «مخفی» از فیلد (برای تغییر حساب و…) بالاتر از نسخهٔ مرئی می‌گذارند.
GENERIC_USER = [
    "form input[type='text']", "form input[type='email']", "form input:not([type])",
    "input[type='email']:visible",
]
GENERIC_TEL = [
    "input[type='tel']", "input[autocomplete='tel']", "input[inputmode='tel']",
    "input[placeholder*='Phone' i]", "input[placeholder*='شماره']",
    "input[placeholder*='موبایل']", "input[aria-label*='Phone' i]",
    "input[aria-label*='شماره']",
] + GENERIC_USER
LOGIN_FLOW: Dict[str, Dict[str, Any]] = {
    "instagram": {
        "user": [
            "input[name='username']", "input[autocomplete='username']",
            "input[aria-label*='username' i]", "input[aria-label*='Phone number' i]",
            "input[placeholder*='username' i]", "input[placeholder*='Phone number' i]",
            "input[placeholder*='phone number' i]",
            # فارسی — چون زبان مرورگرِ خودمان fa-IR است
            "input[aria-label*='نام کاربری']", "input[aria-label*='شماره تلفن']",
            "input[placeholder*='نام کاربری']", "input[placeholder*='شماره تلفن']",
        ] + GENERIC_USER,
        "pass": ["input[type='password']", "input[name='password']",
                 "input[autocomplete='current-password']",
                 "input[aria-label*='Password' i]", "input[aria-label*='رمز']",
                 "input[placeholder*='Password' i]", "input[placeholder*='رمز']"],
        "submit": ["button[type='submit']",
                   "form button:not([type='reset']):not([type='button'])",
                   "button:has-text('Log in')", "button:has-text('ورود')",
                   "div[role='button']:has-text('Log in')", "div[role='button']:has-text('ورود')"],
        "otp_field": "input[name='verificationCode'], input[autocomplete='one-time-code']",
    },
    "twitter": {  # فلو دومرحله‌ای: یوزرنیم → «بعدی» → رمز → «ورود»
        "user": ["input[autocomplete='username']", "input[name='text']",
                 "input[aria-label*='username' i]", "input[placeholder*='Phone' i]",
                 "input[placeholder*='username' i]", "input[placeholder*='شماره تلفن']",
                 "input[aria-label*='نام کاربری']"] + GENERIC_USER,
        "pass": ["input[type='password']", "input[name='password']",
                 "input[aria-label*='Password' i]", "input[aria-label*='رمز']"],
        "next": ["button:has-text('بعدی')", "button:has-text('Next')",
                 "div[role='button']:has-text('Next')"],
        "submit": ["button[data-testid='LoginForm_Login_Button']",
                   "button:has-text('Log in')", "button:has-text('ورود')",
                   "div[role='button']:has-text('Log in')", "button[type='submit']"],
        "otp_field": "input[name='verification_code'], input[autocomplete='one-time-code']",
    },
    "telegram": {"user": GENERIC_TEL, "otp": True, "submit": []},
    "facebook": {
        "user": ["#email", "input[name='email']", "input[id='email']",
                 "input[autocomplete='username']", "input[autocomplete='email']",
                 "input[type='email']",
                 "input[aria-label*='Email' i]", "input[aria-label*='email' i]",
                 "input[placeholder*='Email' i]", "input[placeholder*='موبایل']",
                 "input[placeholder*='ایمیل']", "input[aria-label*='ایمیل']"] + GENERIC_USER,
        "pass": ["#pass", "input[name='password']", "input[type='password']",
                 "input[aria-label*='Password' i]", "input[aria-label*='رمز']"],
        "submit": ["button[name='login']", "#loginbutton", "button[type='submit']",
                   "button:has-text('Log in')", "button:has-text('ورود')",
                   "form button:not([type='reset']):not([type='button'])"],
        "otp_field": "input[autocomplete='one-time-code'], input[name='approvals_code']",
    },
    "linkedin": {
        "user": ["#username", "input[name='session_key']", "input[autocomplete='username']",
                 "input[type='email']", "input[placeholder*='Email' i]",
                 "input[placeholder*='ایمیل']", "input[aria-label*='Email' i]"] + GENERIC_USER,
        "pass": ["#password", "input[name='session_password']", "input[type='password']",
                 "input[aria-label*='Password' i]", "input[aria-label*='رمز']"],
        "submit": ["button[type='submit']", "button:has-text('Sign in')", "button:has-text('ورود')",
                   "form button:not([type='reset']):not([type='button'])"],
        "otp_field": "input[id='verification-code'], input[autocomplete='one-time-code']",
    },
    "bale": {"user": GENERIC_TEL, "otp": True, "submit": []},
    "rubika": {"user": GENERIC_TEL, "otp": True, "submit": []},
    # ۲.۱۱.۰ — واتساپ: نه نام کاربری دارد نه رمز؛ ورود فقط با اسکن QR از
    # گوشی است. فلگِ qr یعنی _generic_login به‌جای فرم، راهنمای اسکن +
    # «صبر هوشمند» را اجرا می‌کند (تا ۳ دقیقه منتظر می‌ماند و بعد نتیجه می‌دهد).
    "whatsapp": {"qr": True},
}

# بنرهای «اجازهٔ کوکی» — قبل از دنبال کردن فیلد ورود بسته می‌شوند (اینستاگرام/فیسبوک اولشان می‌آید)
COOKIE_CONSENT = [
    "button:has-text('اجازهٔ همهٔ کوکی‌ها')", "button:has-text('اجازه همه کوکی‌ها')",
    "button:has-text('Allow all cookies')", "button:has-text('Allow essential and optional cookies')",
    "button:has-text('Accept all cookies')", "button:has-text('Accept all')",
    "button:has-text('تأیید همه')", "button:has-text('پذیرش همه')",
    "div[role='button']:has-text('Accept all')", "div[role='button']:has-text('Allow all cookies')",
    "#onetrust-accept-btn-handler", "button[data-cookiebanner='accept_button']",
]

# دکمه‌های تأیید شماره برای پیام‌رسان‌ها
OTP_SUBMIT_HINTS = ["button:has-text('Next')", "button:has-text('بعدی')", "button:has-text('ورود')",
                    "button:has-text('Log in')", "button:has-text('تأیید')", "button:has-text('ادامه')",
                    "button[type='submit']", "a:has-text('Next')"]

# زنجیرهٔ مرورگرها (۲.۶/۲.۷) — انتخاب کاربر اول امتحان می‌شود و اگر نشد، جایگزین‌ها
BROWSER_CHAINS = {
    "auto": ["msedge", "chrome", "chromium"],
    "msedge": ["msedge", "chromium"],
    "chrome": ["chrome", "msedge", "chromium"],
    "firefox": ["firefox"],
    "chromium": ["chromium", "msedge", "chrome"],
}
VALID_CHANNELS = tuple(BROWSER_CHAINS.keys())
BROWSER_LABEL = {"msedge": "Edge", "chrome": "Chrome",
                 "chromium": "Chromium داخلی Playwright", "firefox": "Firefox"}

# ---------------------------------------------------------------- راهنمای طبیعی جلوه دادن
GUIDE: Dict[str, Dict[str, Any]] = {
    "instagram": {
        "name": "اینستاگرام",
        "rows": [("فالو در ساعت", "۲۰ تا ۳۰ نفر"), ("فالو در روز", "۱۵۰ تا ۲۰۰ نفر"),
                 ("لایک در ساعت", "۶۰ تا ۱۰۰"), ("کامنت در روز", "۲۰ تا ۳۰"),
                 ("پست عکس در روز", "۱ تا ۲"), ("استوری در روز (فقط اپ موبایل)", "تا ۱۰")],
        "delay": (35, 120), "active": "۹ صبح تا ۱۱ شب",
        "tips": ["برای حساب تازه، ۲ هفتهٔ اول فقط نصفِ محدودیت‌ها (گرم کردن حساب).",
                 "بین هر اکشن فاصلهٔ تصادفی بگذارید؛ عدد ثابت = رفتار رباتیک.",
                 "متن کامنت‌ها را تنوع بدهید؛ کامنت تکراری علامت اسپم است.",
                 "هر روز چند دقیقه تعامل دستی و طبیعی هم داشته باشید."],
    },
    "twitter": {
        "name": "توییتر (X)",
        "rows": [("فالو در ساعت", "۱۵ تا ۲۰ نفر"), ("فالو در روز", "تا ۱۰۰ نفر"),
                 ("توییت در روز", "۲۰ تا ۵۰"), ("لایک در روز", "۳۰۰ تا ۵۰۰")],
        "delay": (30, 90), "active": "۱۰ صبح تا ۱۲ شب",
        "tips": ["توییت‌ها را با فاصلهٔ چند ساعتی منتشر کنید نه پشت‌سرهم.",
                 "ریتوییت و لایک را با توییت دستی خودتان ترکیب کنید.",
                 "اکانت تازه: هفتهٔ اول حداکثر ۱۰ فالو در روز."],
    },
    "telegram": {
        "name": "تلگرام",
        "rows": [("پیام به افراد ناشناس", "با احتیاط — ریسک ریپورت"), ("عضویت در کانال در روز", "۱۰ تا ۱۵")],
        "delay": (45, 120), "active": "۱۰ صبح تا ۱۱ شب",
        "tips": ["برای ارسال گروهی حتماً تأخیر طولانی بگذارید؛ تلگرام در پیام‌های سریع محدود می‌کند.",
                 "کد ورود تلگرام وب را از اپ موبایل خود تأیید کنید."],
    },
    "facebook": {
        "name": "فیسبوک",
        "rows": [("درخواست دوستی در روز", "۱۰ تا ۱۵"), ("کامنت در روز", "۲۰ تا ۳۰"), ("پست در روز", "۱ تا ۳")],
        "delay": (40, 120), "active": "۹ صبح تا ۱۱ شب",
        "tips": ["فیسبوک نسبت به دوستی‌های سریع حساس است؛ تعداد را کم نگه دارید.",
                 "قبل از اتوماسیون، اکانت باید حداقل چند ماه فعالیت دستی داشته باشد."],
    },
    "linkedin": {
        "name": "لینکدین",
        "rows": [("درخواست اتصال در روز", "۱۵ تا ۲۰"), ("اتصال در هفته", "حداکثر ۸۰ تا ۱۰۰"), ("پست در هفته", "۲ تا ۵")],
        "delay": (60, 180), "active": "۸ صبح تا ۶ عصر (روزهای کاری)",
        "tips": ["لینکدین خارج از ساعت کاری فعالیت زیاد را عجیب می‌بیند.",
                 "همیشه هنگام اتصال، یادداشت شخصی اضافه کنید.",
                 "آخر هفته (پنجشنبه/جمعه ایرانی) کمتر فعالیت کنید."],
    },
    "bale": {
        "name": "بله",
        "rows": [("پیام در روز", "۵۰ تا ۸۰"), ("عضویت در کانال در روز", "۱۰ تا ۱۵")],
        "delay": (30, 90), "active": "۹ صبح تا ۱۱ شب",
        "tips": ["برای ارسال به کاربران ناشناس، فاصلهٔ طولانی بگذارید.",
                 "ترکیب پیام‌های یکسان گروهی، ریسک محدودیت را بالا می‌برد."],
    },
    "rubika": {
        "name": "روبیکا",
        "rows": [("پیام در روز", "۵۰ تا ۸۰"), ("عضویت در کانال در روز", "۱۰ تا ۱۵")],
        "delay": (30, 90), "active": "۹ صبح تا ۱۱ شب",
        "tips": ["مثل هر پیام‌رسان، ارسال انبوه بدون فاصله باعث محدودیت می‌شود.",
                 "برای کانال‌های عمومی، عضویت‌ها را در طول روز پخش کنید."],
    },
    # ۲.۱۱.۰ — واتساپ: پیام‌رسان شخصی؛ سخت‌گیرترین پلتفرم نسبت به پیام انبوه
    "whatsapp": {
        "name": "واتساپ",
        "rows": [("پیام به مخاطبین آشنا در روز", "۳۰ تا ۶۰"),
                 ("پیام به ناشناس‌ها در روز", "۰ — واتساپ تحمل نمی‌کند"),
                 ("پیام گروهی (هر گروه)", "۳ تا ۵")],
        "delay": (45, 150), "active": "۹ صبح تا ۱۰ شب",
        "tips": ["واتساپ سخت‌گیرترین پیام‌رسان نسبت به اسپم است: فقط به مخاطبینی پیام بدهید که شمارهٔ شما را ذخیره دارند.",
                 "رساندن پیام به افراد ناشناس = گزارش اسپم → بن سریع. برای مشتری، اول پیام معرفی کوتاه و سپس ادامهٔ گفت‌وگو.",
                 "گروه‌های خودتان (مشتریان/همکاران) بهترین جای پیام دوره‌ای است — عضوها اجازهٔ خروج دارند و ریسک نزدیک صفر است.",
                 "بین پیام‌های گروهی فاصلهٔ طولانی بگذارید؛ ارسال هم‌زمان به چند گروه پرچم قرمز است."],
    },
}

# فاصلهٔ ایمن بین زیر-اکشن‌ها بر اساس نوع اکشن (ثانیه)
SAFE_DELAY = {
    "follow": (35, 120), "friend_request": (45, 150), "connect": (60, 180),
    "like": (20, 60), "comment": (60, 180), "retweet": (60, 180),
    "send_message": (45, 120), "join_channel": (60, 180),
    "post_photo": (120, 300), "post_story": (120, 300), "tweet": (180, 420), "post": (180, 420),
}

# ---------------------------------------------------------------- اکشن‌ها (برای فرانت‌اند)
ACTIONS: Dict[str, List[Dict[str, Any]]] = {
    "instagram": [
        {"id": "open", "name": "باز کردن سایت", "params": []},
        {"id": "login", "name": "ورود (تکمیل خودکار نام/رمز)", "params": []},
        {"id": "follow", "name": "فالو کردن", "params": [
            {"key": "target", "name": "کاربر یا هشتگ (مثل hashtag:عکس) — چند مورد با ویرگول", "type": "text"},
            {"key": "count", "name": "تعداد", "type": "number", "default": 1}]},
        {"id": "like", "name": "لایک پست‌های فید", "params": [
            {"key": "count", "name": "تعداد لایک", "type": "number", "default": 5}]},
        {"id": "comment", "name": "کامنت گذاشتن", "params": [
            {"key": "target", "name": "نام کاربری صاحب پست", "type": "text"},
            {"key": "text", "name": "متن کامنت", "type": "textarea"},
            {"key": "count", "name": "تعداد کامنت (روی پست‌های اخیر)", "type": "number", "default": 1}]},
        {"id": "post_photo", "name": "انتشار عکس (پست)", "params": [
            {"key": "media", "name": "فایل رسانه", "type": "media"},
            {"key": "text", "name": "کپشن", "type": "textarea"}]},
        # ۲.۱۰.۰ — اکشن «انتشار استوری» از اینستاگرام حذف شد: اینستاگرام اجازهٔ
        # انتشار استوری از نسخهٔ وب را نمی‌دهد (فقط اپ موبایل / Meta Business
        # Suite برای اکانت تجاری). استوری از وب فقط در فیسبوک ممکن است.
        {"id": "search", "name": "جستجو", "params": [{"key": "query", "name": "عبارت", "type": "text"}]},
    ],
    "twitter": [
        {"id": "open", "name": "باز کردن سایت", "params": []},
        {"id": "login", "name": "ورود (تکمیل خودکار نام/رمز)", "params": []},
        {"id": "follow", "name": "فالو کردن", "params": [
            {"key": "target", "name": "نام کاربری (ها) با ویرگول", "type": "text"},
            {"key": "count", "name": "تعداد", "type": "number", "default": 1}]},
        {"id": "like", "name": "لایک توییت‌های فید", "params": [
            {"key": "count", "name": "تعداد", "type": "number", "default": 5}]},
        {"id": "tweet", "name": "انتشار توییت", "params": [
            {"key": "media", "name": "فایل رسانه (اختیاری)", "type": "media"},
            {"key": "text", "name": "متن توییت", "type": "textarea"}]},
        {"id": "retweet", "name": "ریتوییت", "params": [
            {"key": "target", "name": "لینک توییت", "type": "text"}]},
        {"id": "search", "name": "جستجو", "params": [{"key": "query", "name": "عبارت", "type": "text"}]},
    ],
    "telegram": [
        {"id": "open", "name": "باز کردن تلگرام وب", "params": []},
        {"id": "login", "name": "ورود (شماره تلفن خودکار)", "params": []},
        {"id": "join_channel", "name": "عضویت در کانال", "params": [
            {"key": "target", "name": "آدرس یا نام کانال", "type": "text"}]},
        {"id": "send_message", "name": "ارسال پیام", "params": [
            {"key": "target", "name": "نام کاربری یا کانال", "type": "text"},
            {"key": "text", "name": "متن پیام", "type": "textarea"}]},
        {"id": "search", "name": "جستجوی جهانی", "params": [{"key": "query", "name": "عبارت", "type": "text"}]},
    ],
    "facebook": [
        {"id": "open", "name": "باز کردن سایت", "params": []},
        {"id": "login", "name": "ورود (تکمیل خودکار نام/رمز)", "params": []},
        {"id": "friend_request", "name": "درخواست دوستی", "params": [
            {"key": "target", "name": "لینک پروفایل یا نام", "type": "text"},
            {"key": "count", "name": "تعداد (برای جستجو)", "type": "number", "default": 1}]},
        {"id": "like", "name": "لایک پست‌های فید", "params": [
            {"key": "count", "name": "تعداد", "type": "number", "default": 5}]},
        {"id": "comment", "name": "کامنت گذاشتن", "params": [
            {"key": "target", "name": "لینک پست", "type": "text"},
            {"key": "text", "name": "متن کامنت", "type": "textarea"}]},
        {"id": "post_photo", "name": "انتشار عکس (پست)", "params": [
            {"key": "media", "name": "فایل رسانه", "type": "media"},
            {"key": "text", "name": "متن پست", "type": "textarea"}]},
        # ۲.۱۰.۰ — فیسبوک تنها پلتفرمی است که استوری (عکس) از نسخهٔ وب می‌پذیرد
        {"id": "post_story", "name": "انتشار استوری (عکس)", "params": [
            {"key": "media", "name": "فایل رسانه (عکس — ویدیو از وب ممکن نیست)", "type": "media"}]},
    ],
    "linkedin": [
        {"id": "open", "name": "باز کردن سایت", "params": []},
        {"id": "login", "name": "ورود (تکمیل خودکار نام/رمز)", "params": []},
        {"id": "connect", "name": "درخواست اتصال", "params": [
            {"key": "target", "name": "لینک پروفایل یا نام", "type": "text"},
            {"key": "count", "name": "تعداد (برای جستجو)", "type": "number", "default": 1}]},
        {"id": "like", "name": "لایک پست‌های فید", "params": [
            {"key": "count", "name": "تعداد", "type": "number", "default": 5}]},
        {"id": "comment", "name": "کامنت گذاشتن", "params": [
            {"key": "target", "name": "لینک پست", "type": "text"},
            {"key": "text", "name": "متن کامنت", "type": "textarea"}]},
        {"id": "post", "name": "انتشار پست", "params": [
            {"key": "media", "name": "فایل رسانه (اختیاری)", "type": "media"},
            {"key": "text", "name": "متن پست", "type": "textarea"}]},
    ],
    "bale": [
        {"id": "open", "name": "باز کردن بله", "params": []},
        {"id": "login", "name": "ورود (شماره تلفن خودکار)", "params": []},
        {"id": "join_channel", "name": "عضویت در کانال", "params": [
            {"key": "target", "name": "نام کانال", "type": "text"}]},
        {"id": "send_message", "name": "ارسال پیام", "params": [
            {"key": "target", "name": "نام کاربری یا کانال", "type": "text"},
            {"key": "text", "name": "متن پیام", "type": "textarea"}]},
    ],
    "rubika": [
        {"id": "open", "name": "باز کردن روبیکا", "params": []},
        {"id": "login", "name": "ورود (شماره تلفن خودکار)", "params": []},
        {"id": "join_channel", "name": "عضویت در کانال", "params": [
            {"key": "target", "name": "نام کانال", "type": "text"}]},
        {"id": "send_message", "name": "ارسال پیام", "params": [
            {"key": "target", "name": "نام کاربری یا کانال", "type": "text"},
            {"key": "text", "name": "متن پیام", "type": "textarea"}]},
    ],
    # ۲.۱۱.۰ — واتساپ وب: ورود با QR (نه رمز) + ارسال پیام به مخاطب/گروه
    "whatsapp": [
        {"id": "open", "name": "باز کردن واتساپ وب", "params": []},
        {"id": "login", "name": "ورود با اسکن QR (راهنمای گام‌به‌گام)", "params": []},
        {"id": "send_message", "name": "ارسال پیام به مخاطب/گروه", "params": [
            {"key": "target", "name": "نام مخاطب یا گروه (ذخیره‌شده در واتساپ شما) — چند مورد با ویرگول", "type": "text"},
            {"key": "text", "name": "متن پیام", "type": "textarea"}]},
    ],
}

DEFAULT_SETTINGS: Dict[str, Any] = {
    "general": {"headless": False, "channel": "auto", "proxy": "", "start_maximized": True},
    "stealth": {
        "enabled": True,
        "level": "standard",
        # —— گروه ۱: هویت مرورگر
        "hide_webdriver": True, "spoof_languages": True, "plugins_mimic": True,
        "chrome_runtime": True, "permissions_fix": True, "ua_fix": True,
        "spoof_ua": False, "user_agent": "",
        # —— گروه ۲: اثر انگشت دیجیتال
        "webgl_mask": True, "canvas_noise": True, "audio_noise": True,
        "font_mask": True, "hardware_specs": True, "webrtc_shield": False,
        # —— گروه ۳: رفتار انسانی
        "human_typing": True, "human_delays": True, "typing_speed": "human",
        "mouse_curves": True, "random_scrolls": True, "page_dwell": True,
        "night_pause": True,
        "per_platform": {pid: True for pid in PLAT_IDS},
    },
    "auto_fill": True,
    "captcha": {"mode": "notify", "provider": "2captcha", "api_key": "", "manual_wait_seconds": 180},
    "ai": {
        "provider": "zai",
        "model": "glm-4.6",
        "autonomy": "semi",
        "temperature": 0.7,
        # ۲.۱۳.۰ — پروکسی مخصوص فراخوانی سرویس‌های هوش مصنوعی (مهم برای
        # ایران): Groq/Gemini/OpenAI/xAI درخواست از IP ایران را 403 می‌کنند.
        # خالی = مستقیم؛ اگر System Proxy ویندوز روشن باشد خودکار خوانده می‌شود.
        "proxy": "",
        "api_keys": {k: "" for k in ("zai", "openai", "anthropic", "gemini",
                                       "groq", "grok", "deepseek", "openrouter", "custom")},
        "custom_base": "",
        "custom_model": "",
        "budgets": {"posts_per_day": 4, "posts_per_mission": 40},
        "follow_plans": {},
        # ۲.۴.۰ — چاپخانهٔ رسانه و پاسخ‌گوی دایرکت
        "image": {"provider": "zai", "model": ""},
        "video": {"voice": "fa-IR-FaridNeural", "aspect": "9:16", "seconds": 45,
                   "material": "ai", "motion": "zoom"},
        "dm_reply": {},
    },
}

# ---------------------------------------------------------------- ابزار فایل/حالت
def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def settings() -> Dict[str, Any]:
    s = load_json(F_SETTINGS, {})
    merged = json.loads(json.dumps(DEFAULT_SETTINGS))  # deep copy
    for k, v in s.items():
        if k == "stealth":
            merged["stealth"].update({kk: vv for kk, vv in v.items() if kk != "per_platform"})
            merged["stealth"]["per_platform"].update(v.get("per_platform", {}))
        elif isinstance(v, dict):
            # ۲.۱۳.۰ — کلیدهای سرویس‌های جدید (مثل grok) در فایل تنظیماتِ قدیمی نیستند؛
            # ادغام api_keys زیر-کلیدی است تا فیلدهای تازه از پیش‌فرض گم نشوند.
            if k == "ai" and isinstance(v.get("api_keys"), dict) and isinstance(merged[k].get("api_keys"), dict):
                saved = v["api_keys"]
                rest = {kk: vv for kk, vv in v.items() if kk != "api_keys"}
                merged[k].update(rest)
                merged[k]["api_keys"].update(saved)
            else:
                merged[k].update(v)
        else:
            merged[k] = v
    return merged

def creds() -> Dict[str, Any]:
    return load_json(F_CREDS, {})

def load_schedules() -> List[Dict[str, Any]]:
    return load_json(F_SCHED, [])

def save_schedules(data: List[Dict[str, Any]]) -> None:
    save_json(F_SCHED, data)

LOGS: List[Dict[str, str]] = []
WS_CLIENTS: set = set()
STATS: Dict[str, Any] = {"date": datetime.now().strftime("%Y-%m-%d"), "runs": 0, "success": 0, "fail": 0}
CURRENT_RUN: Optional[Dict[str, Any]] = None
LAST_RESULT: Optional[Dict[str, Any]] = None
RUNNING_SCHED: set = set()

async def broadcast(obj: Dict[str, Any]) -> None:
    dead = set()
    msg = json.dumps(obj, ensure_ascii=False)
    for ws in list(WS_CLIENTS):
        try:
            await ws.send_text(msg)
        except Exception:
            dead.add(ws)
    WS_CLIENTS.difference_update(dead)

def log(message: str, level: str = "info") -> None:
    entry = {"t": datetime.now().strftime("%H:%M:%S"), "msg": message, "level": level}
    LOGS.append(entry)
    if len(LOGS) > 400:
        del LOGS[:200]
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(broadcast({"type": "log", **entry}))
    except RuntimeError:
        pass

def media_list() -> List[Dict[str, Any]]:
    out = []
    for f in sorted(MEDIA_DIR.iterdir(), key=lambda x: -x.stat().st_mtime):
        if f.is_file() and not f.name.startswith("."):
            out.append({"name": f.name, "size": f.stat().st_size,
                        "image": f.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"),
                        "video": f.suffix.lower() in (".mp4", ".mov", ".webm")})
    return out

def macro_names() -> List[Dict[str, Any]]:
    """فهرست ماکروها به‌شکل [{name, events, platform}] — هماهنگ با /api/macro/list و رندر پنل.

    ۲.۱۵.۰ — پلتفرمِ هر ماکرو (از لحظهٔ ضبط) هم برگردانده می‌شود تا پخش
    خودش بداند روی کدام پلتفرم اجرا شود (دراپ‌داون پخش حذف شد) و ردیفِ
    ماکرو در پنل بنویسد این ضبط متعلق به کدام پلتفرم است.
    """
    out: List[Dict[str, Any]] = []
    for f in sorted(MACROS_DIR.glob("*.json")):
        try:
            raw = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            raw = []
        if isinstance(raw, dict):  # فرمت ۲.۱۵.۰+
            out.append({"name": f.stem, "events": len(raw.get("events") or []),
                        "platform": str(raw.get("platform") or "")})
        else:  # فرمت قدیمی: لیستِ خالی رخدادها (پلتفرم نامشخص)
            out.append({"name": f.stem, "events": len(raw), "platform": ""})
    return out

# ---------------------------------------------------------------- رفتار انسانی
def _stealth() -> Dict[str, Any]:
    return settings()["stealth"]

async def hdelay(lo: float = 0.8, hi: float = 2.8) -> None:
    if not _stealth().get("human_delays", True):
        lo, hi = min(lo, 0.5), min(hi, 0.9)
    await asyncio.sleep(random.uniform(lo, hi))

_TYPE_SPEEDS: Dict[str, tuple] = {"off": (0.0, 0.0), "fast": (0.03, 0.09), "human": (0.06, 0.19), "slow": (0.14, 0.38)}

def _night_now() -> bool:
    """مکث شبانه (۱ تا ۷ بامداد) — ساعت‌هایی که هیچ انسانی فعال نیست."""
    try:
        return bool(_stealth().get("night_pause", True)) and datetime.now().hour in (1, 2, 3, 4, 5, 6)
    except Exception:
        return False

# ---------------------------------------------------------------- ناوبری مقاوم (۲.۷.۰)
# خطاهایی که با تلاش مجدد بهتر می‌شوند (قطعی لحظه‌ای، VPN که هنوز بالا نمی‌آید و…)
NET_RETRY_ERRORS = (
    "ERR_CONNECTION_CLOSED", "ERR_CONNECTION_RESET", "ERR_CONNECTION_REFUSED",
    "ERR_TIMED_OUT", "ERR_NAME_NOT_RESOLVED", "ERR_EMPTY_RESPONSE",
    "ERR_ADDRESS_UNREACHABLE", "ERR_NETWORK_CHANGED", "ERR_INTERNET_DISCONNECTED",
    "ERR_PROXY_CONNECTION_FAILED", "ERR_TUNNEL_CONNECTION_FAILED",
    "ERR_SSL_PROTOCOL_ERROR", "ERR_HTTP2_PROTOCOL_ERROR",
)
# سایت‌هایی که اتصال از IP ایران را نمی‌پذیرند
SANCTIONED_HOSTS = ("instagram.com", "cdninstagram.com", "x.com", "twitter.com",
                    "twimg.com", "facebook.com", "fbcdn.net", "linkedin.com", "licdn.net",
                    # ۲.۱۱.۰ — واتساپ هم از IP ایران فیلتر است؛ پیام راهنمای
                    # پروکسی/VPN باید برایش هم ظاهر شود (net::ERR_CONNECTION_…)
                    "whatsapp.com", "whatsapp.net")

def _short_err(e: Exception) -> str:
    """کد خطای کوتاه و خوانا از متن استثنا."""
    m = re.search(r"net::(ERR_[A-Z_]+)", str(e))
    if m:
        return "net::" + m.group(1)
    return str(e).split("\n")[0][:170]

def _net_hint(url: str) -> str:
    """راهنمای فارسی خطای شبکه — به‌ویژه برای سایت‌های تحریمی."""
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    g = settings().get("general", {})
    if any(s in host for s in SANCTIONED_HOSTS):
        why = f"«{host}» اتصال از IP ایران را نمی‌پذیرد (تحریم)"
    else:
        why = "اتصال به اینترنت/سایت برقرار نشد"
    if g.get("proxy"):
        return (f"{why} — پروکسی فعلی: {g['proxy']}؛ اگر VPN خاموش است روشن کنید یا آدرس درست "
                "را در «تنظیمات ← عمومی ← پروکسی» بگذارید")
    return (f"{why} — VPN سیستم را روشن کنید و آدرسش را در «تنظیمات ← عمومی ← پروکسی» وارد کنید "
            "(مثلاً http://127.0.0.1:10809 یا socks5://127.0.0.1:10808 برای v2rayN/Nekoray؛ "
            "اگر پروکسی سیستم روشن باشد، خودکار برداشته می‌شود)")

async def goto(page, url: str, attempts: int = 3) -> None:
    """ناوبری با تلاش مجدد — خطاهای شبکه دو بار دیگر امتحان و در پایان با راهنمای فارسی خطا می‌دهد."""
    last: Optional[Exception] = None
    for i in range(max(1, attempts)):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            last = None
            break
        except Exception as e:  # noqa
            last = e
            retryable = any(c in str(e) for c in NET_RETRY_ERRORS) or "Timeout" in str(e)
            if not retryable or i == attempts - 1:
                break
            log(f"… اتصال برقرار نشد ({_short_err(e)}) — تلاش مجدد ({i + 2}/{attempts})", "warn")
            await asyncio.sleep(1.5 + 1.6 * i)
    if last is not None:
        raise RuntimeError(f"باز شدن {url} ممکن نشد ({_short_err(last)}) — {_net_hint(url)}")
    await hdelay(1.2, 2.6)
    # اسکرول تصادفی کوتاه — انسان‌ها بعد از باز شدن صفحه کمی اسکرول می‌کنند
    if _stealth().get("random_scrolls", True) and random.random() < 0.45:
        try:
            await page.mouse.wheel(0, random.randint(140, 520))
            await asyncio.sleep(random.uniform(0.5, 1.4))
            await page.mouse.wheel(0, -random.randint(30, 140))
        except Exception:
            pass

async def hclick(page, sel: str, timeout: int = 8000) -> bool:
    st = _stealth()
    if st.get("human_delays", True):
        await asyncio.sleep(random.uniform(0.3, 0.9))
    # حرکت موس با مسیر منحنی (بازیجی) به‌جای پرش ناگهانی — امضای موس ربات‌ها خط راست است
    if st.get("mouse_curves", True):
        try:
            box = await page.locator(sel).first.bounding_box()
            if box:
                tx = box["x"] + box["width"] * random.uniform(0.25, 0.75)
                ty = box["y"] + box["height"] * random.uniform(0.3, 0.7)
                sx = tx - random.uniform(110, 300)
                sy = ty + random.uniform(30, 150)
                cx = tx + random.uniform(-70, 70)
                cy = ty - random.uniform(20, 80)
                steps = random.randint(12, 24)
                for i in range(1, steps + 1):
                    t = i / steps
                    mt = 1 - t
                    x = mt * mt * sx + 2 * mt * t * cx + t * t * tx
                    y = mt * mt * sy + 2 * mt * t * cy + t * t * ty
                    await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.04, 0.15))
        except Exception:
            pass
    await page.click(sel, timeout=timeout)
    return True

async def htype(page, sel: Optional[str], text: str) -> None:
    if sel:
        await page.click(sel, timeout=8000)
    st = _stealth()
    if not st.get("human_typing", True):
        await page.keyboard.type(text)
        return
    lo, hi = _TYPE_SPEEDS.get(st.get("typing_speed", "human"), _TYPE_SPEEDS["human"])
    for ch in text:
        await page.keyboard.type(ch)
        if lo:
            await asyncio.sleep(random.uniform(lo, hi))
            if random.random() < 0.04:  # مکث «فکر کردن» انسانی وسط تایپ
                await asyncio.sleep(random.uniform(0.25, 0.7))

async def click_first(page, sels: List[str], timeout: int = 6000) -> bool:
    for sel in sels:
        try:
            locs = page.locator(sel)
            n = min(await locs.count(), _SEL_CAP)
            for i in range(n):
                try:
                    if await locs.nth(i).is_visible():
                        await hclick(page, f"{sel} >> nth={i}", timeout=timeout)
                        return True
                except Exception:
                    continue
        except Exception:
            continue
    return False

# ---------------------------------------------------------------- ضد شناسایی v3 (متد روز دنیا)
# اصل طلایی: «اثر انگشت پایدار». نویز تصادفیِ هر بار، خودش توسط سیستم‌های
# ضد ربات (مثل CreepJS) شناسایی می‌شود؛ ما برای هر پروفایل یک seed دائمی
# می‌سازیم تا GPU/CPU/Canvas/صدا بین اجراها ثابت بماند — یعنی شما یک
# «انسانِ همیشگی» با یک سیستم مشخص باشید، نه یک رباتِ هر بار متفاوت.
GPU_POOL = [
    ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 SUPER Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) UHD Graphics 630 (0x00003E92) Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (AMD)", "ANGLE (AMD, AMD Radeon(TM) Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"),
]
CORES_POOL = [4, 6, 8, 12, 16]
MEM_POOL = [4, 8, 8, 16]

def fp_values(platform: str) -> Dict[str, Any]:
    """مقادیر اثر انگشت پایدار برای هر پلتفرم (seed دائمی در پروفایل ذخیره می‌شود)."""
    pdir = PROFILES_DIR / platform
    try:
        pdir.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    f = pdir / ".fpseed"
    seed = 0
    try:
        seed = int(f.read_text(encoding="utf-8").strip())
    except Exception:
        seed = random.randrange(1, 2 ** 31)
        try:
            f.write_text(str(seed), encoding="utf-8")
        except Exception:
            pass
    h = hashlib.sha256(f"parsagent:{platform}:{seed}".encode()).digest()
    gpu = GPU_POOL[h[0] % len(GPU_POOL)]
    return {
        "seed": seed,
        "vendor": gpu[0], "renderer": gpu[1],
        "cores": CORES_POOL[h[1] % len(CORES_POOL)],
        "mem": MEM_POOL[h[2] % len(MEM_POOL)],
        # جابجایی پیکسل ثابت Canvas (پایدار — نه تصادفی)
        "d1": (h[3] % 3) - 1, "d2": (h[4] % 3) - 1,
    }

STEALTH_JS = r"""
(() => {
  try {
    const C = window.__PA_CFG__ || {};
    /* —— ضد تشخیصِ تشخیص: همهٔ تابع‌های وصله‌شده «native» به نظر می‌رسند (toString cloak) */
    const NATIVE = new Map();
    const _ts = Function.prototype.toString;
    Function.prototype.toString = function () {
      const n = NATIVE.get(this);
      if (n) return "function " + n + "() { [native code] }";
      return _ts.call(this);
    };
    NATIVE.set(Function.prototype.toString, "toString");
    const cloak = (fn, name) => { try { NATIVE.set(fn, name); } catch (e) {} };
    const def = (obj, prop, value) => {
      try { Object.defineProperty(obj, prop, { get: () => value, configurable: true }); } catch (e) {}
    };

    /* ============ گروه ۱: هویت مرورگر ============ */
    if (C.hide_webdriver !== false) {
      try { delete Object.getPrototypeOf(navigator).webdriver; } catch (e) {}
      def(navigator, "webdriver", undefined);
    }
    if (C.spoof_languages !== false) {
      def(navigator, "languages", ["fa-IR", "fa", "en-US", "en"]);
      def(navigator, "language", "fa-IR");
    }
    if (C.plugins_mimic !== false) {
      const names = ["PDF Viewer", "Chrome PDF Viewer", "Chromium PDF Viewer", "Microsoft Edge PDF Viewer", "WebKit built-in PDF"];
      const pl = names.map((n) => ({ name: n, filename: "internal-pdf-viewer", description: "Portable Document Format", length: 1 }));
      def(navigator, "plugins", pl);
      def(navigator, "mimeTypes", [{ type: "application/pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: pl[0] }]);
    }
    if (C.chrome_runtime !== false) {
      /* window.chrome کامل — حالت خالی/ناقص خودش نشانهٔ اتوماسیون است */
      window.chrome = window.chrome || {};
      const ch = window.chrome;
      ch.app = ch.app || { isInstalled: false };
      ch.runtime = ch.runtime || { OnInstalledReason: {}, PlatformOs: {}, connect: function () {}, sendMessage: function () {} };
      ch.loadTimes = ch.loadTimes || function () {};
      ch.csi = ch.csi || function () {};
    }
    if (C.permissions_fix !== false) {
      try {
        const q = navigator.permissions.query.bind(navigator.permissions);
        navigator.permissions.query = (p) => (p && p.name === "notifications")
          ? Promise.resolve({ state: Notification.permission }) : q(p);
        cloak(navigator.permissions.query, "query");
      } catch (e) {}
    }
    if (C.ua_fix !== false || C.spoof_ua) {
      try {
        let ua = navigator.userAgent.replace(/Headless(Chrome)/g, "$1");
        if (C.spoof_ua && C.user_agent) ua = C.user_agent;
        def(navigator, "userAgent", ua);
      } catch (e) {}
    }

    /* ============ گروه ۲: اثر انگشت دیجیتال (پایدار از seed پروفایل) ============ */
    if (C.hardware_specs !== false) {
      def(navigator, "hardwareConcurrency", C.cores || 8);
      try { def(navigator, "deviceMemory", C.mem || 8); } catch (e) {}
      def(navigator, "maxTouchPoints", 0);
    }
    if (C.webgl_mask !== false) {
      for (const proto of [window.WebGLRenderingContext, window.WebGL2RenderingContext]) {
        if (!proto) continue;
        try {
          const gp = proto.prototype.getParameter;
          proto.prototype.getParameter = function (a) {
            if (a === 37445) return C.vendor;
            if (a === 37446) return C.renderer;
            return gp.apply(this, [a]);
          };
          cloak(proto.prototype.getParameter, "getParameter");
        } catch (e) {}
      }
    }
    if (C.canvas_noise !== false) {
      /* نویز پایدار: مقدار ثابت d1/d2 از seed — دو بار خواندن Canvas همان
         نتیجه را می‌دهد. نویز تصادفیِ هر بار، الگوریتم CreepJS فوراً لو می‌دهد. */
      try {
        const done = new WeakSet();
        const td = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function (...args) {
          try {
            if (this.width > 1 && this.height > 1 && !done.has(this)) {
              const c = this.getContext("2d");
              if (c) {
                const x = c.getImageData(0, 0, Math.min(this.width, 8), 1);
                x.data[0] += (C.d1 || 1); x.data[1] += (C.d2 || 1);
                c.putImageData(x, 0, 0);
                done.add(this);
              }
            }
          } catch (e) {}
          return td.apply(this, args);
        };
        cloak(HTMLCanvasElement.prototype.toDataURL, "toDataURL");
      } catch (e) {}
    }
    if (C.audio_noise !== false) {
      try {
        const gd = AudioBuffer.prototype.getChannelData;
        AudioBuffer.prototype.getChannelData = function (ch) {
          const d = gd.apply(this, [ch]);
          try { if (d && d.length) d[Math.min(3, d.length - 1)] += 1e-7 * ((C.seed % 7) + 1); } catch (e) {}
          return d;
        };
        cloak(AudioBuffer.prototype.getChannelData, "getChannelData");
      } catch (e) {}
    }
    if (C.font_mask !== false) {
      /* شمارش فونت‌ها: فونت‌های رایج ویندوز = بله؛ فونت ساختگی = نه */
      try {
        if (document.fonts && document.fonts.check) {
          const COMMON = ["Arial", "Calibri", "Cambria", "Consolas", "Courier New", "Georgia",
                          "Impact", "Segoe UI", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana"];
          document.fonts.check = (font, text) => {
            try {
              const fam = String(font || "").toLowerCase();
              if (COMMON.some((fn) => fam.includes(fn.toLowerCase()))) return true;
            } catch (e) {}
            return false;
          };
          cloak(document.fonts.check, "check");
        }
      } catch (e) {}
    }
    if (C.webrtc_shield) {
      /* جلوگیری از لو رفتن IP محلی از طریق WebRTC (پیش‌فرض خاموش —
         تماس صوتی/تصویری پیام‌رسان‌ها ممکن است به هم بریزد) */
      try {
        const OC = window.RTCPeerConnection;
        if (OC) {
          const NW = function RTCPeerConnection() {
            const pc = new OC(...arguments);
            pc.addEventListener("icecandidate", (e) => {
              if (e.candidate && e.candidate.candidate && !/typ relay/.test(e.candidate.candidate)) {
                e.stopImmediatePropagation();
              }
            }, true);
            return pc;
          };
          NW.prototype = OC.prototype;
          window.RTCPeerConnection = NW;
        }
      } catch (e) {}
    }
  } catch (e) {}
})();
"""

def build_stealth_init(st: Dict[str, Any], platform: str) -> str:
    """اسکریپت راه‌اندازی کامل ضد شناسایی برای تزریق در نشست مرورگر."""
    s = st["stealth"]
    fp = fp_values(platform)
    cfg: Dict[str, Any] = {k: bool(s.get(k, True)) for k in (
        "hide_webdriver", "spoof_languages", "plugins_mimic", "chrome_runtime", "permissions_fix",
        "ua_fix", "webgl_mask", "canvas_noise", "audio_noise", "font_mask", "hardware_specs")}
    cfg["webrtc_shield"] = bool(s.get("webrtc_shield", False))
    cfg["spoof_ua"] = bool(s.get("spoof_ua", False))
    cfg["user_agent"] = (s.get("user_agent") or "").strip()
    cfg.update(vendor=fp["vendor"], renderer=fp["renderer"], cores=fp["cores"],
               mem=fp["mem"], d1=fp["d1"], d2=fp["d2"], seed=fp["seed"])
    return "window.__PA_CFG__ = %s;\n%s" % (json.dumps(cfg), STEALTH_JS)

RECORDER_JS = """
(() => {
  if (window.__PA_REC_ACTIVE__) return;
  window.__PA_REC_ACTIVE__ = true;
  // ۲.۱۴.۰ — پنل خودمان هرگز ضبط نمی‌شود (درخواست کاربر: کلیک روی دکمهٔ
  // «توقف» ماکرو نباید داخل ماکرو ضبط شود)؛ چک دوم هم در سرور انجام می‌شود.
  const hn = (location.hostname || '').toLowerCase();
  if (hn === 'localhost' || hn === '127.0.0.1' || hn === '0.0.0.0' || hn === '[::1]') return;
  const emit = (ev) => { try { window.__pa_rec(JSON.stringify(ev)); } catch (e) {} };
  const q = (el) => {
    if (!el || el === document.documentElement) return 'body';
    let n = el, path = [];
    while (n && n.nodeType === 1 && n !== document.body) {
      let s = n.tagName.toLowerCase();
      if (n.id) { path.unshift('#' + (window.CSS && CSS.escape ? CSS.escape(n.id) : n.id)); break; }
      const nm = n.getAttribute && n.getAttribute('name');
      if (nm) s += '[name="' + nm + '"]';
      const sib = Array.from(n.parentNode ? n.parentNode.children : []).filter(x => x.tagName === n.tagName);
      if (sib.length > 1) s += ':nth-of-type(' + (sib.indexOf(n) + 1) + ')';
      path.unshift(s);
      n = n.parentElement;
    }
    if (!path.length) path = ['body'];
    return path.join(' > ');
  };
  const origin = location.origin;
  // ۲.۱۴.۰ — هر مقدار فقط یک‌بار ضبط می‌شود (اگر Enter بعد از تایپ زده شود و
  // بعد blur هم بیاید، همان متن دوباره ضبط نمی‌شود تا پخش، پیام را دوبار نفرستد)
  const lastVal = new WeakMap();
  const emitCE = (t) => {
    const txt = (t.innerText || '').trim();
    if (lastVal.get(t) === txt) return;
    lastVal.set(t, txt);
    emit({t: 'input', sel: q(t), v: txt, origin: origin, ts: Date.now()});
  };
  const emitInput = (t) => {
    if (lastVal.get(t) === (t.value || '')) return;
    lastVal.set(t, t.value || '');
    emit({t: 'input', sel: q(t), v: t.value || '', origin: origin, ts: Date.now()});
  };
  const isTextInput = (t) => t && (t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' ||
    (t.tagName === 'INPUT' && ['text','password','email','tel','number','search','url'].includes(t.type)));
  document.addEventListener('click', (e) => {
    try {
      let t = e.target;
      if (t && t.closest) t = t.closest('a,button,input,textarea,select,[role=button],[onclick],label,svg,path') || t;
      emit({t: 'click', sel: q(t), origin: origin, ts: Date.now()});
    } catch(err) {}
  }, true);
  document.addEventListener('change', (e) => {
    try {
      if (isTextInput(e.target)) emitInput(e.target);
    } catch(err) {}
  }, true);
  // ۲.۱۴.۰ — جعبه‌های چت اینستاگرام/واتساپ/تلگرام contentEditable اند و رویداد
  // change ندارند؛ بدون این بلوک، متنِ تایپ‌شده هرگز ضبط نمی‌شد و پخش ماکرو
  // دکمهٔ «ارسال» را خالی می‌زد (ریشهٔ اصلی «ضبط و پخش درست کار نمی‌کند»).
  // focusout برای input های معمولی هم هست (خروج از فیلد = مقدار نهایی).
  document.addEventListener('focusout', (e) => {
    try {
      const t = e.target;
      if (t && t.isContentEditable) emitCE(t);
      else if (isTextInput(t)) emitInput(t);
    } catch(err) {}
  }, true);
  // ۲.۱۴.۰ — Enter هم ضبط می‌شود (ارسال پیام با Enter در چت‌ها)؛ برای textarea
  // نه، چون آنجا Enter یعنی «خط جدید» و مقدار کامل با change/focusout ضبط می‌شود.
  document.addEventListener('keydown', (e) => {
    try {
      if (e.key !== 'Enter' || e.isComposing || e.ctrlKey || e.altKey || e.metaKey) return;
      const t = e.target;
      if (!t) return;
      if (t.isContentEditable) {
        emitCE(t);
        emit({t: 'key', k: 'Enter', sel: q(t), origin: origin, ts: Date.now()});
      } else if (t.tagName === 'INPUT' && !['checkbox','radio','file'].includes(t.type)) {
        emitInput(t);
        emit({t: 'key', k: 'Enter', sel: q(t), origin: origin, ts: Date.now()});
      }
    } catch(err) {}
  }, true);
})();
"""

# ---------------------------------------------------------------- نشست مرورگر (۲.۶/۲.۷)
def _norm_proxy(raw: str) -> Optional[str]:
    """نرمال‌سازی آدرس پروکسی — بدون اسکیم، http فرض می‌شود؛ socks هم پذیرفته است."""
    p = (raw or "").strip()
    if not p:
        return None
    if p.startswith(("socks5://", "socks4://", "http://", "https://")):
        return p
    return "http://" + p

def _sys_proxy() -> Optional[str]:
    """پروکسی سیستم ویندوز (v2rayN/Nekoray آن را ست می‌کنند) — تا مرورگر ما هم مثل Edge از همان VPN استفاده کند."""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings")
        try:
            enable, _ = winreg.QueryValueEx(key, "ProxyEnable")
            server, _ = winreg.QueryValueEx(key, "ProxyServer")
        finally:
            winreg.CloseKey(key)
        if enable and server:
            if "=" in server and ";" in server:  # شکل http=127.0.0.1:8080;https=…
                server = server.split(";")[0].split("=", 1)[-1]
            return _norm_proxy(server)
    except Exception:
        pass
    return None

async def _auto_install_browser(which: str) -> Optional[str]:
    """نصب خودکار مرورگر داخل Playwright با آینهٔ npmmirror (ایران) — None یعنی موفق."""
    mirror = "https://cdn.npmmirror.com/binaries/playwright"
    env = dict(os.environ)
    env["PLAYWRIGHT_DOWNLOAD_HOST"] = mirror
    env["PLAYWRIGHT_DOWNLOAD_HOST_CN"] = mirror
    log(f"⬇️ {BROWSER_LABEL.get(which, which)} نصب نیست — دانلود خودکار با آینهٔ npmmirror … (چند دقیقه ممکن است طول بکشد)", "warn")
    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "playwright", "install", which,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT, env=env)
    except Exception as e:
        return f"اجرای دستور نصب ممکن نشد: {e}"
    tail: List[str] = []
    while True:
        try:
            line = await proc.stdout.readline()
        except Exception:
            break
        if not line:
            break
        txt = line.decode("utf-8", "replace").strip()
        if txt:
            tail.append(txt)
    await proc.wait()
    if proc.returncode == 0:
        log(f"✅ {BROWSER_LABEL.get(which, which)} نصب شد — دوباره باز می‌کنیم…")
        return None
    return " | ".join(tail[-2:])[-280:] or f"کد خروج {proc.returncode}"

class BotSession:
    def __init__(self, platform: str):
        self.platform = platform
        self.p = None
        self.context = None
        self.page = None
        self.recording = False
        self.rec_events: List[Dict[str, Any]] = []
        self._exposed = False
        # ۲.۱۴.۰ — آمار رویدادهای نادیده‌گرفته‌شده (خارج از دامنهٔ پلتفرم/کلیک روی پنل)
        self.rec_dropped_panel = 0
        self.rec_dropped_foreign = 0

    @property
    def open(self) -> bool:
        return self.context is not None

    async def ensure(self):
        if self.context:
            # ۲.۱۵.۰ — اگر کاربر پنجرهٔ مرورگر را دستی بسته باشد، context
            # کهنه «زنده» به‌نظر می‌رسید و صفحهٔ بسته‌شده برگردانده می‌شد →
            # هر اجرای بعدی خطای «Target page, context or browser has been
            # closed» می‌داد و تا ری‌استارتِ سرور هیچ ماکرویی دوباره پخش
            # نمی‌شد. حالا سلامتِ واقعی چک می‌شود و مرورگر خودش دوباره
            # باز می‌شود.
            try:
                pages = list(self.context.pages)
                alive = None
                for pg in pages:
                    try:
                        if not pg.is_closed():
                            alive = pg
                            break
                    except Exception:
                        continue
                if alive is not None:
                    self.page = alive
                    return self.page
                if not pages:
                    raise RuntimeError("مرورگر بسته است")
                # context زنده است ولی همهٔ تب‌ها بسته‌اند → تبِ تازه
                self.page = await self.context.new_page()
                return self.page
            except Exception:
                log(f"🔄 پنجرهٔ مرورگر {self.platform} از قبل بسته شده بود — دوباره باز می‌شود", "warn")
                await self.close()
        from playwright.async_api import async_playwright  # noqa
        self.p = await async_playwright().start()
        st = settings()
        g = st["general"]
        stealth_on = st["stealth"]["enabled"] and st["stealth"].get("per_platform", {}).get(self.platform, True)
        args = ["--disable-blink-features=AutomationControlled", "--no-first-run",
                "--no-default-browser-check", "--disable-notifications"]
        if g.get("start_maximized", True):
            args.append("--start-maximized")
        if stealth_on:
            args.append("--lang=fa-IR")

        # --- پروکسی (۲.۷.۰): تنظیم دستی مقدم است؛ وگرنه پروکسی سیستم ویندوز (v2rayN و مثل آن) خودکار اعمال می‌شود
        manual = _norm_proxy(g.get("proxy") or "")
        proxy = manual or _sys_proxy()
        if proxy and not manual:
            log(f"🔄 پروکسی سیستم ویندوز پیدا و اعمال شد: {proxy} — مرورگر ما هم مثل Edge از VPN شما استفاده می‌کند")
        if proxy and stealth_on and not st["stealth"].get("webrtc_shield"):
            log("💡 پیشنهاد: «شیلد WebRTC» را هم در تنظیمات روشن کنید تا IP اصلی از راه WebRTC لو نرود (اگر تماس صوتی/تصویری لازم ندارید)", "warn")

        # --- زنجیرهٔ مرورگر (۲.۶/۲.۷): انتخاب کاربر اول؛ اگر باز نشد، جایگزین‌ها با پیام
        chosen = (g.get("channel") or "auto").strip().lower()
        if chosen not in VALID_CHANNELS:
            chosen = "auto"
        chain = list(BROWSER_CHAINS[chosen])

        last_err: Optional[Exception] = None
        used = chain[0]
        for ch in chain:
            try:
                kw: Dict[str, Any] = dict(
                    user_data_dir=str(PROFILES_DIR / self.platform),
                    headless=bool(g.get("headless", False)),
                    args=(args if ch != "firefox" else []),
                    viewport=None,
                )
                if ch == "firefox":
                    if stealth_on:
                        kw["locale"] = "fa-IR"  # فایرفاکس آرگومان‌های کرومیوم را نمی‌فهمد
                else:
                    kw["ignore_default_args"] = ["--enable-automation"]
                    if ch != "chromium":
                        kw["channel"] = ch
                if proxy:
                    kw["proxy"] = {"server": proxy}
                mod = self.p.firefox if ch == "firefox" else self.p.chromium
                self.context = await mod.launch_persistent_context(**kw)
                used = ch
                break
            except Exception as e:  # noqa
                last_err = e
                self.context = None
                log(f"… باز شدن {BROWSER_LABEL[ch]} ناموفق: {_short_err(e)}", "warn")
                # مرورگرِ داخل Playwright غایب است → نصب خودکار با آینه (رفع «Executable doesn't exist …chromium-…»)
                if ch in ("chromium", "firefox") and "Executable doesn't exist" in str(e):
                    err = await _auto_install_browser(ch)
                    if err is None:
                        try:
                            mod2 = self.p.firefox if ch == "firefox" else self.p.chromium
                            self.context = await mod2.launch_persistent_context(**kw)
                            used = ch
                            break
                        except Exception as e2:  # noqa
                            last_err = e2
                            log(f"… بعد از نصب هم باز نشد: {_short_err(e2)}", "warn")
                    else:
                        log(f"نصب خودکار {BROWSER_LABEL[ch]} نشد: {err} — از لانچر، «نصب پیش‌نیازها» یا «📀 نصب آفلاین» را بزنید", "warn")
        if not self.context:
            raise RuntimeError(
                f"باز شدن مرورگر ممکن نشد: {_short_err(last_err)} — راهنما: «تنظیمات ← عمومی ← مرورگر ترجیحی» را روی «خودکار» "
                "بگذارید (Edge → Chrome → Chromium)؛ Chromium که نباشد، خودش با آینهٔ npmmirror نصب می‌شود")
        if used != chosen and chosen != "auto":
            log(f"⚠️ «{BROWSER_LABEL.get(chosen, chosen)}» انتخاب شما باز نشد — این بار با «{BROWSER_LABEL[used]}» ادامه می‌دهیم؛ "
                "اگر می‌خواهید همان باشد، نصب بودنش را بررسی کنید", "warn")
        if stealth_on:
            st_js = st
            if used == "firefox":
                st_js = json.loads(json.dumps(st))
                st_js["stealth"]["chrome_runtime"] = False  # فایرفاکس واقعی window.chrome ندارد
            await self.context.add_init_script(build_stealth_init(st_js, self.platform))
            fp = fp_values(self.platform)
            log(f"🥷 ضد شناسایی v3 روی {self.platform} فعال شد — اثر انگشت پایدار #{fp['seed'] % 10000} (GPU: {fp['vendor'].split('(')[-1][:-1]})")
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
        return self.page

    async def close(self) -> None:
        try:
            if self.context:
                await self.context.close()
        except Exception:
            pass
        try:
            if self.p:
                await self.p.stop()
        except Exception:
            pass
        self.context = None
        self.page = None
        self.p = None

SESSIONS: Dict[str, BotSession] = {pid: BotSession(pid) for pid in PLAT_IDS}
LOCKS: Dict[str, asyncio.Lock] = {pid: asyncio.Lock() for pid in PLAT_IDS}

async def get_session(platform: str) -> BotSession:
    sess = SESSIONS[platform]
    if not sess.open:
        log(f"🚀 در حال باز کردن مرورگر برای {platform} …")
    await sess.ensure()
    return sess

# ---------------------------------------------------------------- کپچا
CAPTCHA_SEL = ("iframe[src*='recaptcha'], iframe[title*='reCAPTCHA' i], iframe[src*='hcaptcha'], "
               "iframe[data-hcaptcha-widget], iframe[src*='funcaptcha'], iframe[src*='arcade'], "
               "div.g-recaptcha, div.h-captcha")

async def captcha_present(page) -> bool:
    try:
        return await page.locator(CAPTCHA_SEL).count() > 0
    except Exception:
        return False

def _http_json(url: str, data: Optional[Dict[str, str]] = None, timeout: int = 40) -> Dict[str, Any]:
    if data:
        body = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, data=body)
    else:
        req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

async def _extract_sitekey(page) -> Optional[str]:
    js = """() => {
        const el = document.querySelector('.g-recaptcha[data-sitekey], .h-captcha[data-sitekey]');
        if (el) return el.getAttribute('data-sitekey');
        const m = document.documentElement.innerHTML.match(/data-sitekey="([^"]+)"/);
        if (m) return m[1];
        const s = document.querySelector('script[src*="recaptcha/api.js"]');
        if (s) { const r = s.src.match(/render=([^&]+)/); if (r) return r[1]; }
        return null;
    }"""
    try:
        return await page.evaluate(js)
    except Exception:
        return None

async def solve_with_provider(page) -> str:
    st = settings()["captcha"]
    sitekey = await _extract_sitekey(page)
    if not sitekey:
        log("⚠ sitekey کپچا پیدا نشد", "warn")
        return "failed"
    pageurl = page.url
    hcaptcha = "hcaptcha" in (page.content()[:200000] if False else "") or await page.evaluate(
        "() => !!document.querySelector('iframe[src*=hcaptcha], .h-captcha')")
    provider, key = st.get("provider", "2captcha"), st.get("api_key", "")
    if not key:
        log("⚠ کلید سرویس کپچا در تنظیمات خالی است", "warn")
        return "failed"
    try:
        import urllib.request as _u
        if provider == "capsolver":
            payload = json.dumps({
                "clientKey": key,
                "task": {"type": "HCaptchaTaskProxyLess" if hcaptcha else "ReCaptchaV2TaskProxyLess",
                         "websiteURL": pageurl, "websiteKey": sitekey},
            }).encode()
            req = _u.Request("https://api.capsolver.com/createTask", data=payload,
                            headers={"Content-Type": "application/json"})
            with _u.urlopen(req, timeout=40) as r:
                res = json.loads(r.read().decode())
            task_id = res.get("taskId")
            if not task_id:
                log(f"⚠ capsolver خطا: {res.get('errorId')} {res.get('errorDescription')}", "error")
                return "failed"
            for _ in range(40):
                await asyncio.sleep(5)
                payload = json.dumps({"clientKey": key, "taskId": task_id}).encode()
                req = _u.Request("https://api.capsolver.com/getTaskResult", data=payload,
                                headers={"Content-Type": "application/json"})
                with _u.urlopen(req, timeout=40) as r:
                    res = json.loads(r.read().decode())
                if res.get("status") == "ready":
                    token = res["solution"].get("gRecaptchaResponse", "")
                    break
            else:
                return "timeout"
        else:  # 2captcha
            method = "hcaptcha" if hcaptcha else "userrecaptcha"
            res = await asyncio.to_thread(
                _http_json,
                f"https://2captcha.com/in.php?key={urllib.parse.quote(key)}&method={method}"
                f"&googlekey={urllib.parse.quote(sitekey)}&pageurl={urllib.parse.quote(pageurl)}&json=1")
            task_id = res.get("request") if res.get("status") == 1 else None
            if not task_id:
                log(f"⚠ 2captcha خطا: {res.get('request')}", "error")
                return "failed"
            token = ""
            for _ in range(40):
                await asyncio.sleep(5)
                res = await asyncio.to_thread(
                    _http_json,
                    f"https://2captcha.com/res.php?key={urllib.parse.quote(key)}&action=get&id={urllib.parse.quote(task_id)}&json=1")
                if res.get("status") == 1:
                    token = res.get("request", "")
                    break
            if not token:
                return "timeout"
        # تزریق توکن
        await page.evaluate("""(token) => {
            const set = (id) => { const el = document.getElementById(id) || document.querySelector('textarea[name="' + id + '"]'); if (el) { el.style.display = 'block'; el.value = token; } };
            ['g-recaptcha-response', 'h-captcha-response'].forEach(set);
            document.querySelectorAll('textarea[name=g-recaptcha-response],textarea[name=h-captcha-response]').forEach(t => { t.style.display='block'; t.value = token; });
        }""", token)
        log("🔓 توکن کپچا تزریق شد؛ در حال تلاش برای ادامه…")
        await asyncio.sleep(2)
        return "solved"
    except Exception as e:
        log(f"⚠ خطای سرویس کپچا: {e}", "error")
        return "failed"

async def handle_captcha(page) -> str:
    st = settings()["captcha"]
    mode = st.get("mode", "notify")
    if mode == "off":
        return "none"
    if not await captcha_present(page):
        return "none"
    log("🤖 کپچا شناسایی شد!", "warn")
    if mode == "auto" and st.get("api_key"):
        res = await solve_with_provider(page)
        if res == "solved":
            return "solved"
        log("حل خودکار موفق نبود؛ منتظر حل دستی می‌مانم…", "warn")
    wait = int(st.get("manual_wait_seconds", 180))
    log(f"⏳ کپچا را دستی حل کنید — حداکثر {wait} ثانیه منتظر می‌مانم.", "warn")
    for _ in range(wait):
        await asyncio.sleep(1)
        if not await captcha_present(page):
            log("✅ کپچا حل شد (دستی)")
            return "manual"
    return "timeout"

# ---------------------------------------------------------------- اکشن‌ها
ACTION_IMPL: Dict[tuple, Any] = {}

def action(pid: str, name: str):
    def deco(fn):
        ACTION_IMPL[(pid, name)] = fn
        return fn
    return deco

def _media_path(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    f = MEDIA_DIR / Path(name).name
    return str(f.resolve()) if f.exists() else None

async def _collect_users_from_links(page, url: str, pattern: str, count: int, skip=()) -> List[str]:
    await goto(page, url)
    hrefs = await page.eval_on_selector_all("a[href]", "els => els.map(e => e.getAttribute('href'))")
    users, seen = [], set()
    for h in hrefs:
        if not h:
            continue
        m = re.match(pattern, h)
        if m:
            u = m.group(1)
            if u.lower() not in seen and u.lower() not in skip:
                seen.add(u.lower())
                users.append(u)
        if len(users) >= count:
            break
    return users

for _pid, _url in ((p["id"], p["url"]) for p in PLATFORMS):

    async def _make_open(sess, p, _url=_url):
        page = await sess.ensure()
        url = p.get("url") or _url
        await goto(page, url)
        return {"ok": True, "message": f"باز شد: {url}"}
    ACTION_IMPL[(_pid, "open")] = _make_open

# ---------------------------------------------------------------- ورود خودکار (۲.۶/۲.۷)
_SEL_CAP = 10  # حداکثر تعداد نتیجهٔ هر سلکتور که برای «مرئی بودن» چک می‌شود

async def _first_visible(page, sels: List[str]) -> Optional[str]:
    """اولین المانِ مرئی بین همهٔ سلکتورها — «همهٔ» نتایج هر سلکتور چک می‌شوند،
    نه فقط اولی؛ چون سایت‌ها (اینستاگرام!) گاهی یک نسخهٔ مخفی از فیلد را
    بالاتر از نسخهٔ مرئی می‌گذارند و `.first` همان مخفی را برمی‌داشت (باگ ۲.۸.۰).
    خروجی: رشتهٔ سلکتورِ آمادهٔ کلیک/tایپ با سینتکس «sel >> nth=i»."""
    for sel in sels or []:
        try:
            locs = page.locator(sel)
            n = min(await locs.count(), _SEL_CAP)
            for i in range(n):
                try:
                    if await locs.nth(i).is_visible():
                        return f"{sel} >> nth={i}"
                except Exception:
                    continue
        except Exception:
            continue
    return None

async def _wait_visible(page, sels: List[str], timeout_s: float = 30.0) -> Optional[str]:
    """صبر برای اولین سلکتورِ مرئی — با نظرسنجی؛ برای صفحه‌های سنگین که دیر فیلد می‌آورند (اینستاگرام/X روی VPN)."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        target = await _first_visible(page, sels)
        if target:
            return target
        await asyncio.sleep(0.7)
    return None

async def _dismiss_cookie_walls(page) -> bool:
    """بستن بنر «اجازهٔ کوکی» که اینستاگرام/فیسبوک قبل از فرم ورود نشان می‌دهند."""
    for sel in COOKIE_CONSENT:
        try:
            target = await _first_visible(page, [sel])
            if target:
                await hclick(page, target, timeout=2500)
                await asyncio.sleep(0.9)
                log("🍪 بنر «اجازهٔ کوکی» بسته شد تا فرم ورود پیدا شود")
                return True
        except Exception:
            continue
    return False

async def _fill_first(page, sels: List[str], value: str) -> bool:
    """پر کردن اولین فیلدِ مرئی از لیست سلکتورها — با تایپ انسانی."""
    for sel in sels or []:
        try:
            loc = page.locator(sel).first
            if await loc.count() and await loc.is_visible():
                try:
                    await loc.fill("", timeout=3000)  # اگر چیزی از قبل تایپ شده بود، پاک شود
                except Exception:
                    pass
                await htype(page, sel, value)
                return True
        except Exception:
            continue
    return False

def _on_login_url(platform: str, url: str) -> bool:
    """آیا هنوز روی صفحهٔ ورود هستیم؟ (اگر به جای دیگری هدایت شده باشیم = از قبل وارد شده‌ایم)"""
    u = (url or "").lower()
    return any(k in u for k in ("login", "signin", "i/flow", "session"))

async def _generic_login(sess, p):
    page = await sess.ensure()
    st = settings()
    url = LOGIN_URLS[sess.platform]
    await goto(page, url)  # خطای شبکه با راهنمای فارسی پروکسی/VPN بالا می‌آید (۲.۷.۰)
    flow = LOGIN_FLOW.get(sess.platform) or {}
    c = creds().get(sess.platform) or {}
    autofill = st.get("auto_fill", True)

    # ۲.۱۱.۰ — واتساپ: نه فرمی پر می‌شود نه رمزی — ورود فقط با اسکن QR از
    # گوشی است؛ راهنمای فارسی + صبر هوشمند تا ۳ دقیقه (جدا از بقیهٔ فلوها)
    if flow.get("qr"):
        return await _wa_qr_login(page)

    # ۱) بنر «اجازهٔ کوکی»؟ بسته می‌شود تا فیلد ورود پیدا شود
    await _dismiss_cookie_walls(page)

    # ۲) از قبل وارد شده‌ایم؟ — فقط وقتی می‌گوییم که فرم ورود هم پیدا «نشود»؛
    # چون اینستاگرام گاهی از /accounts/login/ به صفحهٔ اصلی هدایت می‌کند ولی
    # فرم ورود همان‌جا رندر می‌شود (مثبت کاذبِ «از قبل وارد شده» در ۲.۸.۰)
    if not flow.get("otp") and not _on_login_url(sess.platform, page.url):
        if not await _wait_visible(page, flow.get("user") or [], 3.0):
            return {"ok": True, "message": "شما از قبل وارد این حساب شده‌اید — نیازی به ورود دوباره نیست ✅"}

    # ۳) پیام‌رسان‌ها (تلگرام/بله/روبیکا): شماره تلفن + کد پیامکی که فقط خودتان می‌زنید
    if flow.get("otp"):
        if not autofill or not c.get("username"):
            return {"ok": True, "message": "صفحهٔ ورود باز شد — شماره تلفن را در «تنظیمات ← ورود خودکار» ذخیره کنید تا خودکار تایپ شود؛ بعد دوباره «ورود» را بزنید"}
        sel = await _wait_visible(page, flow["user"], 30)
        if not sel:
            if not _on_login_url(sess.platform, page.url) and sess.platform == "telegram":
                return {"ok": True, "message": "به نظر می‌رسد از قبل وارد شده‌اید (صفحهٔ اصلی تلگرام باز است) ✅"}
            return {"ok": False, "message": "فیلد شماره تلفن دیده نشد — صفحه را در پنجرهٔ باز بررسی کنید (کپچا/چالش؟) و دوباره «ورود» را بزنید"}
        if not await _fill_first(page, [sel], c["username"]):
            return {"ok": False, "message": "شماره تلفن تایپ نشد — فیلد را در پنجرهٔ باز دستی پر کنید"}
        await hdelay(0.5, 1.1)
        clicked = await click_first(page, flow.get("submit") or OTP_SUBMIT_HINTS)
        msg = "شماره تلفن تایپ شد" + (" و دکمهٔ تأیید زده شد" if clicked else " — دکمه را خودتان بزنید")
        return {"ok": True, "message": msg + "؛ اکنون کد پیامکی را در همان پنجره وارد کنید (این مرحله فقط با خودتان ممکن است)"}

    # ۴) بدون اطلاعات ذخیره‌شده؟
    if not autofill or not (c.get("username") or c.get("password")):
        cap = await handle_captcha(page)
        m = "صفحهٔ ورود باز شد — نام کاربری/رمز در «تنظیمات ← ورود خودکار» ذخیره نشده؛ ذخیره کنید و دوباره «ورود» را بزنید"
        if cap != "none":
            m += f" | کپچا: {cap}"
        return {"ok": True, "message": m}

    # ۵) نام کاربری — با مهلت بلند صبر می‌کنیم (X/اینستاگرام روی VPN کند باز می‌شوند)
    usel = await _wait_visible(page, flow.get("user") or [], 35)
    if not usel:
        if await captcha_present(page):
            return {"ok": False, "message": "کپچا در صفحهٔ ورود ظاهر شده — اول در پنجرهٔ باز حلش کنید، بعد دوباره «ورود» را بزنید"}
        title = ""
        try:
            title = await page.title()
        except Exception:
            pass
        # لاگ تشخیصی: هرچه input در صفحه هست فهرست می‌شود تا اگر ساختار باز هم عوض شد،
        # از تب «لاگ‌ها» معلوم باشد سایت چه فیلدهایی داده (مقادیر لاگ نمی‌شوند — فقط صفات)
        try:
            dump = await page.eval_on_selector_all(
                "input",
                "els => els.slice(0, 14).map(e => (e.type || '-') + '/' + (e.name || '-') + '/' + "
                "(e.autocomplete || '-') + '/' + ((e.getAttribute('aria-label') || e.placeholder || '-').slice(0, 28)) + '/' + "
                "((e.offsetWidth || e.offsetHeight || e.getClientRects().length) ? 'vis' : 'hidden'))")
            log("🔍 فیلدهای موجود در صفحه: " + " | ".join(dump), "info")
        except Exception:
            pass
        extra = f" (عنوان صفحه: «{title[:60]}»)" if title else ""
        return {"ok": False, "message": "فیلد ورود دیده نشد — صفات فیلدهای صفحه در لاگ ثبت شد؛ چند ثانیه بعد دوباره «ورود» را بزنید" + extra +
                " و اگر باز نشد، راهنمای پروکسی در تب «راهنما» را بخوانید"}
    filled: List[str] = []
    if c.get("username"):
        if await _fill_first(page, [usel], c["username"]):
            filled.append("نام کاربری")
        else:
            log("⚠️ تایپ نام کاربری ناموفق بود", "warn")

    # ۶) توییتر/X دومرحله‌ای است: یوزرنیم → «بعدی» → رمز → «ورود»
    if flow.get("next"):
        await hdelay(0.5, 1.2)
        if not await click_first(page, flow["next"]):
            return {"ok": False, "message": "در X بعد از نام کاربری، دکمهٔ «بعدی» پیدا نشد — در پنجره خودتان ادامه دهید و بعد دوباره «ورود» را بزنید"}
        psel = await _wait_visible(page, flow["pass"], 25)
        if not psel:
            return {"ok": False, "message": "فیلد رمز X ظاهر نشد — ممکن است X «بررسی هویت» (شماره/یوزرنیم) خواسته باشد؛ در پنجره خودتان کامل کنید"}
        if c.get("password"):
            if await _fill_first(page, [psel], c["password"]):
                filled.append("رمز عبور")
            else:
                log("⚠️ تایپ رمز X ناموفق بود", "warn")
        await hdelay(0.6, 1.4)
        clicked = await click_first(page, flow.get("submit") or [])
        if not clicked:
            log("دکمهٔ ورود X پیدا نشد — خودتان بزنید", "warn")
        return {"ok": True, "message": "فرم X پر شد" + (" و دکمهٔ ورود زده شد" if clicked else "؛ دکمه را خودتان بزنید") +
                " — اگر چالش یا کد تأیید خواست، در همان پنجره وارد کنید"}

    # ۷) رمز عبور
    if c.get("password") and flow.get("pass"):
        psel = await _wait_visible(page, flow["pass"], 15)
        if psel:
            if await _fill_first(page, [psel], c["password"]):
                filled.append("رمز عبور")
            else:
                log("⚠️ تایپ رمز عبور ناموفق بود", "warn")
        else:
            log("فیلد رمز پیدا نشد — شاید صفحهٔ دیگری باز شده (کد تأیید/چالش)", "warn")

    # ۸) دکمهٔ ورود
    await hdelay(0.6, 1.4)
    clicked = False
    base = (page.url or "").lower()  # آدرس قبل از کلیک — برای تشخیص هدایت بعد از ورود
    if flow.get("submit"):
        clicked = await click_first(page, flow["submit"])
        if not clicked:
            log("دکمهٔ ورود پیدا نشد — خودتان دکمه را بزنید", "warn")

    # ۹) نتیجه — تا ۱۵ ثانیه واچ می‌کنیم: هدایت = ورود کامل؛ کپچا؛ OTP؛ رمز نادرست
    outcome = "unknown"
    if clicked:
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            await asyncio.sleep(1.0)
            try:
                u = (page.url or "").lower()
            except Exception:
                u = base
            if "login" not in u and "signin" not in u and "i/flow" not in u and u != base:
                outcome = "in"
                break
            if await captcha_present(page):
                outcome = "captcha"
                break
            try:
                if await page.locator(flow.get("otp_field") or "___none___").count():
                    outcome = "otp"
                    break
            except Exception:
                pass
        if outcome == "unknown":
            try:
                body = (await page.inner_text("body"))[:3000].lower()
                if any(k in body for k in ("incorrect", "نادرست", "wrong password", "اشتباه است", "sorry, your password")):
                    outcome = "badpass"
            except Exception:
                pass

    if clicked and outcome == "captcha":
        cap = await handle_captcha(page)  # اگر تنظیم شده، منتظر حل (دستی/خودکار) می‌ماند
        return {"ok": True, "message": "کپچا ظاهر شد و فرم پر و ارسال شده — در پنجره حلش کنید" + (f" (وضعیت: {cap})" if cap != "none" else "")}
    if clicked and outcome == "in":
        return {"ok": True, "message": "ورود انجام شد ✅ (" + "، ".join(filled) + " پر و دکمهٔ ورود زده شد) — خوش آمدید!"}
    if clicked and outcome == "otp":
        return {"ok": True, "message": "نام کاربری و رمز پر و ارسال شد؛ حالا صفحهٔ «کد تأیید (OTP)» باز شده — کد را در همان پنجره وارد کنید"}
    if clicked and outcome == "badpass":
        return {"ok": False, "message": "سایت گفت رمز یا نام کاربری درست نیست — «تنظیمات ← ورود خودکار» را درست کنید و دوباره «ورود» را بزنید"}
    if clicked:
        return {"ok": True, "message": "دکمهٔ ورود زده شد — نتیجه در پنجرهٔ باز معلوم می‌شود؛ اگر کد تأیید یا چالش خواست، همان‌جا کامل کنید"}
    return {"ok": True, "message": "فرم ورود باز و پر شد" + (f": {'، '.join(filled)}" if filled else "") +
            " — دکمهٔ ورود پیدا نشد و خودتان باید بزنید"}

for _pid2 in PLAT_IDS:
    ACTION_IMPL[(_pid2, "login")] = _generic_login

async def _ensure_count(p) -> int:
    try:
        return max(1, int(p.get("count") or 1))
    except Exception:
        return 1

# ---------------------------------------------------------------- موتور لایک مقاوم (۲.۱۰.۰)
# چرا بازنویسی شد؟ گزارش کاربر «لایک کار نمی‌کند» — سه علت واقعی:
#   ①) چک نمی‌شد اصلاً وارد شده‌اید یا نه (فید بدون لاگین = هیچ دکمه‌ای نیست
#      و نتیجه «لایک انجام شد: ۰» بود)؛
#   ②) دکمهٔ لایک در «کل صفحه» جست‌وجو می‌شد → دکمهٔ بخش‌های جانبی
#      (لایکِ کامنت/صفحه/پیشنهاد) به‌جای پستِ فید کلیک می‌شد؛
#   ③) سلکتورِ «شاملِ Like» دکمهٔ «Liked» (پستِ قبلاً لایک‌شده!) را هم
#      می‌گرفت — یعنی بعضی وقت‌ها لایکِ شما را «برداشتن» می‌کرد.
# موتور جدید: چک لاگین → انتظار برای بارگیری فید → لایکِ پست‌به‌پست
# (جست‌وجو فقط داخل همان پست) → سلکتورهای دقیق فارسی/انگلیسی → تأیید
# بعد از کلیک (دکمه به «برداشتن پسند/Unlike» تغییر کرد؟) → اسکرول تدریجی.

NOT_LOGGED_IN_LIKE = ("به نظر می‌رسد وارد این پلتفرم نشده‌اید — اول در تب «پلتفرم‌ها» دکمهٔ «ورود» "
                      "را بزنید (اطلاعات در «تنظیمات ← ورود خودکار») و بعد دوباره لایک را اجرا کنید")

# سلکتورهای هر پلتفرم: posts = کانتینر پست‌های فید (به‌ترتیب اولویت)؛
# like = دکمهٔ لایکِ لایک‌نشده؛ unlike = نشانهٔ «این پست لایک شده» (برای تأیید).
LIKE_ENGINES: Dict[str, Dict[str, List[str]]] = {
    "instagram": {
        # نکتهٔ مهم: دکمهٔ اصلی لایکِ فید داخل <section> نوار اکشن است؛
        # سلکتورهای سکشن‌دار اول امتحان می‌شوند تا لایکِ کامنت‌ها زده نشود.
        "posts": ["article", "main article"],
        "like": [
            "section svg[aria-label='Like']", "section svg[aria-label='پسندیدن']",
            "section div[role='button']:has(svg[aria-label='Like'])",
            "section div[role='button']:has(svg[aria-label='پسندیدن'])",
            "svg[aria-label='Like']", "svg[aria-label='پسندیدن']",
            "div[role='button'][aria-label='Like']", "div[role='button'][aria-label='پسندیدن']",
            "button[aria-label='Like']", "button[aria-label='پسندیدن']",
        ],
        "unlike": ["svg[aria-label='Unlike']", "svg[aria-label='برداشتن پسند']",
                   "svg[aria-label='لغو پسندیدن']", "div[role='button'][aria-label='Unlike']",
                   "div[role='button'][aria-label='برداشتن پسند']"],
    },
    "twitter": {
        "posts": ["article[data-testid='tweet']", "article"],
        "like": ["button[data-testid='like']", "button[aria-label^='Like']",
                 "button[aria-label^='پسندیدن']"],
        "unlike": ["button[data-testid='unlike']", "button[aria-label^='Unlike']",
                   "button[aria-label^='برداشتن پسند']"],
    },
    "facebook": {
        # پست‌های فید role=article با aria-posinset دارند (کامنت‌های تودرتو ندارند)؛
        # دکمهٔ لایک دقیقاً 'Like' است نه «شامل Like» — چون 'Liked' هم شاملش می‌شود!
        "posts": ["div[role='article'][aria-posinset]", "div[role='article']"],
        "like": ["div[role='button'][aria-label='Like']", "div[role='button'][aria-label='پسندیدن']",
                 "div[aria-label='Like']", "div[aria-label='پسندیدن']",
                 "div[role='button']:text-is('Like')", "div[role='button']:text-is('پسندیدن')"],
        "unlike": ["div[aria-label^='Liked']", "div[aria-label^='پسندیدم']",
                   "div[role='button'][aria-label^='Unlike']", "div[role='button'][aria-label^='برداشتن']"],
    },
    "linkedin": {
        # برچسب لایک داینامیک است («Like John's post») → با ^ (شروع‌شونده) می‌گیریم
        "posts": ["div[data-id^='urn:li:activity']", "div.feed-shared-update-v2", "article"],
        "like": ["button[aria-label^='Like']", "button[aria-label^='پسندیدن']",
                 "div[role='button'][aria-label^='Like']", "div[role='button'][aria-label^='پسندیدن']"],
        "unlike": ["button[aria-label^='Unlike']", "button[aria-label^='برداشتن پسند']",
                   "button[aria-label^='لغو پسندیدن']", "div[role='button'][aria-label^='Unlike']"],
    },
}

# نشانه‌های «وارد نشده» در آدرس صفحه برای هر پلتفرم
LOGIN_URL_MARKERS = {
    "instagram": ("/accounts/login", "/login"),
    "twitter": ("/login", "/i/flow", "/session"),
    "facebook": ("/login", "/login.php"),
    "linkedin": ("authwall", "/login", "/signin", "/checkpoint"),
}

async def _looks_logged_out(page, markers: List[str]) -> bool:
    """آیا کاربر وارد نشده است؟ (آدرس صفحه روی لاگین است یا فرم رمز نمایان است)"""
    try:
        u = (page.url or "").lower()
    except Exception:
        u = ""
    if any(m in u for m in markers):
        return True
    # اینستاگرام گاهی فرم ورود را روی آدرس اصلی رندر می‌کند (باگ ۲.۹.۰) → فرم رمز = لاگین نیست
    try:
        pw = page.locator("input[type='password']")
        for i in range(min(await pw.count(), 3)):
            try:
                if await pw.nth(i).is_visible():
                    return True
            except Exception:
                continue
    except Exception:
        pass
    return False

async def _wait_feed(page, post_sels: List[str], timeout: float = 25) -> Optional[str]:
    """صبر برای بارگیری فید — اولین سلکتوری که پستِ مرئی دارد را برمی‌گرداند."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for sel in post_sels:
            try:
                locs = page.locator(sel)
                for i in range(min(await locs.count(), 5)):
                    try:
                        if await locs.nth(i).is_visible():
                            return sel
                    except Exception:
                        continue
            except Exception:
                continue
        await asyncio.sleep(0.8)
    return None

async def _like_click_in(post, sels: List[str]) -> bool:
    """کلیک اولین دکمهٔ مرئیِ «لایک» فقط داخل خودِ پست — نه کل صفحه."""
    for sel in sels:
        try:
            locs = post.locator(sel)
            for i in range(min(await locs.count(), _SEL_CAP)):
                try:
                    if await locs.nth(i).is_visible():
                        try:
                            await locs.nth(i).scroll_into_view_if_needed(timeout=3000)
                        except Exception:
                            pass
                        await hdelay(0.3, 0.9)  # مکث انسانی قبل از کلیک
                        await locs.nth(i).click(timeout=6000)
                        return True
                except Exception:
                    continue
        except Exception:
            continue
    return False

async def _like_is_verified(post, unlike_sels: List[str]) -> bool:
    """بعد از کلیک: آیا دکمه به حالت «لایک‌شده» (Unlike/برداشتن پسند) تغییر کرد؟"""
    for sel in unlike_sels:
        try:
            locs = post.locator(sel)
            for i in range(min(await locs.count(), _SEL_CAP)):
                try:
                    if await locs.nth(i).is_visible():
                        return True
                except Exception:
                    continue
        except Exception:
            continue
    return False

async def _like_feed(page, count: int, dmin: float, dmax: float, post_sel: str,
                     like_sels: List[str], unlike_sels: List[str], plat: str) -> int:
    """پیمایش فید و لایکِ پست‌به‌پست — پست‌های لایک‌شده رد می‌شوند (سلکتورِشان
    دیگر Like نیست)؛ هر بار که پست‌های فعلی تمام شد، اسکرول برای پست‌های بعدی."""
    done = 0
    stalled = 0
    while done < count and stalled < 3:
        posts = page.locator(post_sel)
        n = await posts.count()
        before = done
        for i in range(n):
            if done >= count:
                break
            try:
                post = posts.nth(i)
                if not await post.is_visible():
                    continue
                if await _like_click_in(post, like_sels):
                    done += 1
                    await asyncio.sleep(random.uniform(1.2, 2.4))
                    verified = await _like_is_verified(post, unlike_sels)
                    log(f"❤ لایک {done} از {plat}{' ✓' if verified else ''}")
                    await hdelay(dmin, dmax)
            except Exception as e:
                log(f"⚠ لایکِ {plat} (پست {i + 1}): {_short_err(e)}", "warn")
        if done >= count:
            break
        # اسکرول تدریجی → بارگیری پست‌های بعدی فید
        await page.mouse.wheel(0, random.randint(600, 1200))
        await hdelay(1.8, 3.6)
        new_n = await page.locator(post_sel).count()
        if done == before and new_n <= n:
            stalled += 1  # نه پست تازه‌ای آمد نه لایکی انجام شد
        else:
            stalled = 0
    return done

async def _run_like(sess, p, platform: str, home: str, max_count: int,
                    dmin_def: float, dmax_def: float) -> Dict[str, Any]:
    """اجرای مشترک اکشن لایک برای هر ۴ پلتفرم (موتور ۲.۱۰.۰)."""
    page = await sess.ensure()
    count = min(max_count, await _ensure_count(p))
    dmin, dmax = float(p.get("delay_min", dmin_def)), float(p.get("delay_max", dmax_def))
    eng = LIKE_ENGINES[platform]
    plat_fa = {"instagram": "اینستاگرام", "twitter": "توییتر (X)", "facebook": "فیسبوک",
               "linkedin": "لینکدین"}[platform]
    await goto(page, home)
    if await _looks_logged_out(page, list(LOGIN_URL_MARKERS.get(platform, ("/login",)))):
        return {"ok": False, "message": NOT_LOGGED_IN_LIKE}
    post_sel = await _wait_feed(page, eng["posts"])
    if not post_sel:
        if await _looks_logged_out(page, list(LOGIN_URL_MARKERS.get(platform, ("/login",)))):
            return {"ok": False, "message": NOT_LOGGED_IN_LIKE}
        return {"ok": False,
                "message": f"فید {plat_fa} در ۲۵ ثانیه بارگیری نشد — چند ثانیه بعد دوباره لایک را اجرا کنید؛ "
                           "اگر اصلاً باز نمی‌شود، راهنمای پروکسی را در تب «راهنما» بخوانید"}
    done = await _like_feed(page, count, dmin, dmax, post_sel, eng["like"], eng["unlike"], plat_fa)
    if done:
        msg = f"لایک انجام شد: {done}" + (f" از {count}" if done < count else "")
        if done < count:
            msg += " — پست لایک‌نشدنیِ دیگری در فید نبود (احتمالاً همه از قبل لایک شده‌اند)"
        return {"ok": True, "message": msg}
    return {"ok": False,
            "message": "هیچ پستِ لایک‌نشدنی پیدا نشد — یا همهٔ پست‌های فید از قبل لایک شده‌اند یا فید خالی است؛ "
                       "کمی بعد یا با تعداد کمتر دوباره تلاش کنید"}

# ----- اینستاگرام
@action("instagram", "follow")
async def ig_follow(sess, p):
    page = await sess.ensure()
    count = await _ensure_count(p)
    dmin, dmax = float(p.get("delay_min", 35)), float(p.get("delay_max", 120))
    raw = (p.get("target") or "").strip()
    targets = [t.strip().lstrip("@") for t in re.split(r"[,\n]", raw) if t.strip()]
    if len(targets) == 1 and targets[0].lower().startswith("hashtag:"):
        tag = targets[0].split(":", 1)[1].strip().lstrip("#")
        targets = await _collect_users_from_links(
            page, f"https://www.instagram.com/explore/tags/{urllib.parse.quote(tag)}/",
            r"^/([A-Za-z0-9._]+)/(?:p|reel)/", count,
            skip=("explore", "p", "reel", "accounts", "direct", "stories", "about"))
        if not targets:
            return {"ok": False, "message": "از این هشتگ کاربری پیدا نشد"}
    if not targets:
        return {"ok": False, "message": "کاربری مشخص نشده است"}
    done, failed = 0, []
    for u in targets[:count]:
        try:
            await goto(page, f"https://www.instagram.com/{u}/")
            if await click_first(page, ["button:has-text('Follow')", "button:has-text('دنبال کردن')",
                                        "button:has-text('پیگیری')", "button:has-text('Follow')"]):
                done += 1
                log(f"➕ فالو شد: @{u}")
            else:
                failed.append(u)
                log(f"⚠ دکمهٔ فالو برای @{u} پیدا نشد", "warn")
        except Exception as e:
            failed.append(u)
            log(f"⚠ خطا در فالو @{u}: {e}", "warn")
        if len(targets) > 1:
            await hdelay(dmin, dmax)
    msg = f"فالو انجام شد: {done} از {min(count, len(targets))}"
    if failed:
        msg += f" | ناموفق: {', '.join(failed[:5])}"
    return {"ok": done > 0, "message": msg}

@action("instagram", "like")
async def ig_like(sess, p):
    # موتور ۲.۱۰.۰ — چک ورود + لایک پست‌به‌پست فقط داخل article + تأیید
    return await _run_like(sess, p, "instagram", "https://www.instagram.com/", 20, 20, 60)

@action("instagram", "comment")
async def ig_comment(sess, p):
    page = await sess.ensure()
    target = (p.get("target") or "").strip().lstrip("@")
    text = p.get("text") or ""
    count = await _ensure_count(p)
    if not target or not text:
        return {"ok": False, "message": "کاربر و متن کامنت لازم است"}
    dmin, dmax = float(p.get("delay_min", 60)), float(p.get("delay_max", 180))
    done = 0
    try:
        await goto(page, f"https://www.instagram.com/{target}/")
        for i in range(count):
            posts = page.locator("a[href*='/p/'], a[href*='/reel/']")
            if await posts.count() <= i:
                break
            await posts.nth(i).click(timeout=8000)
            await hdelay(1.5, 3)
            if await click_first(page, ["svg[aria-label='Comment']", "svg[aria-label='نظر دادن']"]):
                pass
            if await click_first(page, ["textarea[placeholder*='comment']", "textarea[placeholder*='نظر']",
                                        "textarea[aria-label*='Add a comment']", "textarea"]):
                await hdelay(0.4, 1)
                await page.keyboard.type(text)
                await asyncio.sleep(random.uniform(0.5, 1.2))
                await page.keyboard.press("Enter")
                done += 1
                log(f"💬 کامنت {done} ارسال شد")
            await page.go_back(wait_until="domcontentloaded")
            await hdelay(dmin, dmax)
    except Exception as e:
        log(f"⚠ خطا در کامنت: {e}", "warn")
    return {"ok": done > 0, "message": f"کامنت ارسال شد: {done}"}

@action("instagram", "post_photo")
async def ig_post_photo(sess, p):
    page = await sess.ensure()
    path = _media_path(p.get("media"))
    if not path:
        return {"ok": False, "message": "ابتدا فایل رسانه را از تب «رسانه‌ها» یا دکمه آپلود بارگذاری کنید"}
    await goto(page, "https://www.instagram.com/")
    await click_first(page, ["svg[aria-label='New post']", "svg[aria-label='پست جدید']",
                             "a[href='/create/style/']", "svg[aria-label='Create']"], timeout=4000)
    inputs = page.locator("input[type=file]")
    ok = False
    for i in range(await inputs.count()):
        inp = inputs.nth(i)
        accept = (await inp.get_attribute("accept") or "").lower()
        if "image" in accept or "video" in accept or not accept:
            await inp.set_input_files(path)
            ok = True
            break
    if not ok:
        return {"ok": False, "message": "ورودی فایل اینستاگرام پیدا نشد"}
    await hdelay(2, 4)
    for _ in range(2):
        await click_first(page, ["button:has-text('Next')", "button:has-text('بعدی')",
                                 "button:has-text('التالي')"], timeout=4000)
        await hdelay(1.5, 3)
    if p.get("text"):
        if await click_first(page, ["div[role='textbox']", "textarea[aria-label*='caption']",
                                    "textarea[placeholder*='caption']"], timeout=4000):
            await page.keyboard.type(p["text"])
            await asyncio.sleep(1)
    if await click_first(page, ["button:has-text('Share')", "button:has-text('اشتراک‌گذاری')",
                               "button:has-text('به اشتراک گذاشتن')"], timeout=10000):
        await asyncio.sleep(3)
        return {"ok": True, "message": "پست عکس ارسال شد ✅"}
    return {"ok": False, "message": "دکمه اشتراک‌گذاری پیدا نشد — پست را دستی تمام کنید"}

# ۲.۱۰.۰ — اکشن «post_story» اینستاگرام حذف شد: اینستاگرام اجازهٔ انتشار استوری از
# نسخهٔ وب را نمی‌دهد (تأیید با تحقیق: فقط اپ موبایل یا Meta Business Suite برای
# اکانت تجاری). به همین دلیل ig_post_story حذف شد؛ استوری از وب فقط برای فیسبوک است.

@action("instagram", "search")
async def ig_search(sess, p):
    page = await sess.ensure()
    await goto(page, f"https://www.instagram.com/explore/search/keyword/?q={urllib.parse.quote(p.get('query',''))}")
    return {"ok": True, "message": "جستجو انجام شد"}

# ----- توییتر
@action("twitter", "follow")
async def tw_follow(sess, p):
    page = await sess.ensure()
    count = await _ensure_count(p)
    dmin, dmax = float(p.get("delay_min", 30)), float(p.get("delay_max", 90))
    targets = [t.strip().lstrip("@") for t in re.split(r"[,\n]", p.get("target") or "") if t.strip()]
    if len(targets) == 1 and targets[0].lower().startswith("hashtag:"):
        tag = targets[0].split(":", 1)[1].lstrip("#")
        targets = await _collect_users_from_links(
            page, f"https://x.com/search?q={urllib.parse.quote(tag)}&f=user",
            r"^/([A-Za-z0-9_]+)$", count, skip=("home", "explore", "notifications", "messages",
                                                "i", "search", "settings", "compose", "login"))
    done = 0
    for u in targets[:count]:
        try:
            await goto(page, f"https://x.com/{u}")
            if await click_first(page, ["[data-testid$='-follow']", "button:has-text('Follow')",
                                        "button[aria-label*='Follow' i]"]):
                done += 1
                log(f"➕ فالو شد: @{u}")
        except Exception as e:
            log(f"⚠ فالو {u}: {e}", "warn")
        if len(targets) > 1:
            await hdelay(dmin, dmax)
    return {"ok": done > 0, "message": f"فالو انجام شد: {done} از {min(count, len(targets))}"}

@action("twitter", "like")
async def tw_like(sess, p):
    # موتور ۲.۱۰.۰ — data-testid مستقل از زبان است + چک ورود
    return await _run_like(sess, p, "twitter", "https://x.com/home", 20, 20, 60)

@action("twitter", "tweet")
async def tw_tweet(sess, p):
    page = await sess.ensure()
    await goto(page, "https://x.com/compose/post")
    await hdelay(2, 4)
    if await click_first(page, ["div[data-testid='tweetTextarea_0']", "div[role='textbox']"]):
        await page.keyboard.type(p.get("text") or "")
        await hdelay(0.8, 1.6)
        path = _media_path(p.get("media"))
        if path:
            await page.locator("input[data-testid='fileInput']").set_input_files(path)
            await hdelay(2, 4)
        if await click_first(page, ["[data-testid='tweetButton']", "[data-testid='tweetButtonInline']"],
                             timeout=10000):
            await asyncio.sleep(3)
            return {"ok": True, "message": "توییت ارسال شد ✅"}
    return {"ok": False, "message": "ارسال توییت ناموفق بود"}

@action("twitter", "retweet")
async def tw_retweet(sess, p):
    page = await sess.ensure()
    await goto(page, p.get("target") or "https://x.com/home")
    await hdelay(1.5, 3)
    if await click_first(page, ["[data-testid='retweet']", "button[aria-label*='Repost' i]"]):
        await hdelay(0.5, 1.2)
        await click_first(page, ["[data-testid='retweetConfirm']", "button:has-text('Repost')",
                                 "button:has-text('بازنشر')"])
        return {"ok": True, "message": "بازنشر انجام شد ✅"}
    return {"ok": False, "message": "دکمه بازنشر پیدا نشد"}

@action("twitter", "search")
async def tw_search(sess, p):
    page = await sess.ensure()
    await goto(page, f"https://x.com/search?q={urllib.parse.quote(p.get('query',''))}")
    return {"ok": True, "message": "جستجو انجام شد"}

# ----- تلگرام / بله / روبیکا (پیام‌رسان‌ها)
async def _msg_join(sess, p, base: str):
    page = await sess.ensure()
    target = (p.get("target") or "").strip().lstrip("@")
    if not target:
        return {"ok": False, "message": "نام کانال لازم است"}
    if target.startswith("http"):
        await goto(page, target)
    else:
        await goto(page, f"{base}/{target}")
    await hdelay(2, 4)
    if await click_first(page, ["button:has-text('Join')", "button:has-text('Subscribe')",
                                "button:has-text('عضویت')", "div[role='button']:has-text('Join')",
                                "button:has-text('View Channel')", "a:has-text('Preview channel')"],
                         timeout=8000):
        await asyncio.sleep(2)
        return {"ok": True, "message": f"عضویت در {target} انجام/آغاز شد ✅"}
    return {"ok": True, "message": f"صفحهٔ {target} باز شد — اگر عضویت خودکار نشد، دکمه را دستی بزنید"}

async def _msg_send(sess, p, web_url: str):
    page = await sess.ensure()
    target = (p.get("target") or "").strip().lstrip("@")
    text = p.get("text") or ""
    if not target or not text:
        return {"ok": False, "message": "گیرنده و متن پیام لازم است"}
    await goto(page, web_url)
    await hdelay(3, 5)
    if await click_first(page, ["input[type='search']", "input[placeholder*='Search']",
                                "input[aria-label*='Search' i]", "button[aria-label*='Search' i]"],
                         timeout=6000):
        await asyncio.sleep(1)
        await page.keyboard.type(target, delay=90)
        await asyncio.sleep(2.5)
        await page.keyboard.press("Enter")
        await hdelay(2, 4)
    if await click_first(page, ["div[contenteditable='true']", ".message-input", "textarea"], timeout=8000):
        await page.keyboard.type(text)
        await asyncio.sleep(0.6)
        await page.keyboard.press("Enter")
        await asyncio.sleep(1.5)
        return {"ok": True, "message": f"پیام به {target} ارسال شد ✅"}
    return {"ok": False, "message": "کادر پیام پیدا نشد — از رابط وب دستی ادامه دهید"}

@action("telegram", "join_channel")
async def tg_join(sess, p):
    return await _msg_join(sess, p, "https://t.me")

@action("telegram", "send_message")
async def tg_send(sess, p):
    return await _msg_send(sess, p, "https://web.telegram.org")

@action("telegram", "search")
async def tg_search(sess, p):
    page = await sess.ensure()
    await goto(page, "https://web.telegram.org")
    await hdelay(3, 5)
    if await click_first(page, ["input[type='search']", "button[aria-label*='Search' i]"]):
        await page.keyboard.type(p.get("query") or "")
        return {"ok": True, "message": "جستجوی تلگرام انجام شد"}
    return {"ok": False, "message": "کادر جستجو پیدا نشد"}

@action("bale", "join_channel")
async def bale_join(sess, p):
    return await _msg_join(sess, p, "https://ble.ir")

@action("bale", "send_message")
async def bale_send(sess, p):
    return await _msg_send(sess, p, "https://ble.ir")

@action("rubika", "join_channel")
async def rubika_join(sess, p):
    return await _msg_join(sess, p, "https://rubika.ir")

@action("rubika", "send_message")
async def rubika_send(sess, p):
    return await _msg_send(sess, p, "https://web.rubika.ir")

# ----- واتساپ وب (۲.۱۱.۰) — ورود با QR + ارسال پیام به مخاطب/گروه
WA_URL = "https://web.whatsapp.com"

# نشانه‌های «وارد شده»: هرکدام مرئی بود یعنی فهرست چت‌ها آماده است.
# (دو سلکتور اول همان جعبهٔ جستجوی چت‌ها در نسخه‌های مختلف وب واتساپ‌اند)
WA_READY_SELS = [
    "div[data-testid='chat-list-search'] div[contenteditable='true']",
    "div[contenteditable='true'][data-tab='3']",
    "#side div[aria-label='Chats']", "#side div[aria-label='فهرست گفتگوها']",
    "#side div[aria-label='Chat list']", "#side div[aria-label='چت‌ها']",
    "div[data-testid='chat-list']",
]
# نشانه‌های صفحهٔ «اسکن QR» (وقتی هنوز وارد نشده‌ایم)
WA_QR_SELS = [
    "canvas[aria-label*='Scan this QR code' i]",
    "div[data-ref]",
    "canvas[aria-label*='QR' i]",
    "div[data-testid='qrcode']",
]
# جعبهٔ نوشتن پیام — داخل footer چتِ باز (data-tab در نسخه‌های مختلف عوض می‌شود؛
# سلکتورهای ساختاری «داخل فوترِ چتِ باز» پایدارترند)
WA_MSGBOX_SELS = [
    "#main footer div[contenteditable='true']",
    "footer div[data-testid='conversation-compose-box-input']",
    "div[data-testid='conversation-compose-box-input']",
    "footer div[contenteditable='true']",
]
# دکمهٔ ارسال (برای وقتی Enter جواب نداد)
WA_SEND_SELS = [
    "button[data-testid='send']", "button[aria-label='Send']", "button[aria-label='ارسال']",
    "footer button span[data-icon='send']", "footer button span[data-icon='wds-ic-send-filled']",
]
# نام چتِ بازشده در هدر — برای مطمئن شدن اینکه پیام به همان مخاطبِ هدف می‌رود
WA_HEADER_SELS = [
    "#main header span[title]", "#main header div[title]",
    "#main header span[dir='auto']", "#main header div[dir='auto'] span",
    "header[data-testid='chat-header'] span[title]",
]

async def _wa_logged_in(page) -> bool:
    """آیا فهرست چت‌های واتساپ آماده است؟ (= وارد شده‌ایم)"""
    for sel in WA_READY_SELS:
        try:
            locs = page.locator(sel)
            for i in range(min(await locs.count(), 3)):
                if await locs.nth(i).is_visible():
                    return True
        except Exception:
            continue
    return False

async def _wa_qr_login(page, wait_s: int = 180) -> Dict[str, Any]:
    """ورود واتساپ فقط با اسکن QR از گوشی ممکن است (نه نام کاربری، نه رمز).
    ما صفحه را باز می‌کنیم، راهنمای فارسی می‌دهیم و تا wait_s ثانیه صبر می‌کنیم
    تا کاربر با گوشی اسکن کند — بعد نتیجه را روشن اعلام می‌کنیم.
    بعد از اولین ورود، سشن داخل پروفایل مرورگر ذخیره می‌شود و دفعات بعد
    اسکن لازم نیست (مثل خودِ واتساپ دسکتاپ)."""
    if await _wa_logged_in(page):
        return {"ok": True, "message": "شما از قبل وارد واتساپ هستید — فهرست چت‌ها آماده است ✅"}
    if await _first_visible(page, WA_QR_SELS) is not None:
        log("📱 صفحهٔ اسکن QR واتساپ باز شد — منتظر اسکن با گوشی… (تا ۳ دقیقه)", "info")
        deadline = time.monotonic() + wait_s
        while time.monotonic() < deadline:
            if await _wa_logged_in(page):
                log("✅ QR اسکن شد — ورود واتساپ کامل شد")
                return {"ok": True, "message": "QR اسکن شد و ورود کامل شد ✅ — سشن ذخیره می‌شود و دفعات بعد نیازی به اسکن نیست"}
            await asyncio.sleep(1.5)
        return {"ok": False, "message": f"تا {wait_s} ثانیه اسکن QR انجام نشد — صفحهٔ واتساپ هنوز باز است؛ "
                "با گوشی: واتساپ ← تنظیمات ← دستگاه‌های متصل ← اتصال دستگاه، و کد را اسکن کنید؛ بعد دوباره «ورود» را بزنید"}
    # نه فهرست چت‌ها هست نه QR — احتمالاً حالت «اتصال با شماره تلفن» یا صفحهٔ لودینگ
    return {"ok": False, "message": "صفحهٔ واتساپ باز شد ولی کد QR دیده نشد — در پنجرهٔ باز بررسی کنید "
            "(اگر حالت «اتصال با شماره تلفن» باز شده، همان‌جا شماره را وارد کنید یا صفحه را تازه‌سازی کنید) و بعد دوباره «ورود» را بزنید"}

async def _wa_search_open_chat(page, target: str) -> bool:
    """جستجوی مخاطب/گروه در نوار کناری و باز کردن اولین نتیجه —
    همان کاری که خودتان با جستجو می‌کنید. نام باید در واتساپ شما موجود/ذخیره باشد.
    ⚠️ قبل از تایید، نام چتِ بازشده با هدف تطبیق داده می‌شود — اگر جستجو نتیجه‌ای
    نداشت، واتساپ چتِ قبلی را باز نگه می‌دارد و پیام نباید به چت اشتباه برود."""
    box = await _wait_visible(page, WA_READY_SELS[:2], 8)
    if not box:
        log("⚠️ جعبهٔ جستجوی واتساپ پیدا نشد — شاید هنوز وارد نشده‌اید", "warn")
        return False
    try:
        await page.locator(box).click(timeout=4000)
    except Exception:
        return False
    await hdelay(0.4, 0.9)
    # پاک کردن جستجوی قبلی — انسان هم همین کار را می‌کند (Ctrl+A + Delete)؛
    # واتساپ متنِ جستجوی بی‌نتیجه را در جعبه نگه می‌دارد و بدون پاک‌کردن،
    # نام جدید به نام قبلی می‌چسبد و چیزی پیدا نمی‌شود (کشف در تست ۲.۱۱.۰)
    await page.keyboard.press("Control+a")
    await hdelay(0.12, 0.3)
    await page.keyboard.press("Delete")
    await hdelay(0.15, 0.35)
    await page.keyboard.type(target, delay=65)
    await hdelay(1.3, 2.2)  # نتایج جستجو بیایند
    # نتیجه‌ای هست؟ — اگر نه، چتِ قبلی همان‌جا باز می‌ماند و کلیک نکردن بهتر است
    n_res = 0
    for sel in ("#side div[role='listitem']", "div[data-testid='cell-frame-container']"):
        try:
            locs = page.locator(sel)
            for i in range(min(await locs.count(), 5)):
                if await locs.nth(i).is_visible():
                    n_res += 1
        except Exception:
            continue
    if n_res == 0:
        log(f"⚠️ «{target}» در جستجوی واتساپ پیدا نشد — ارسال به آن انجام نمی‌شود", "warn")
        return False
    # اولین نتیجه — کاری که خودتان با کلیک می‌کنید؛ اگر کلیک نشد،
    # با کیبورد: پایین + Enter (هر دو انسانی‌اند)
    clicked = await click_first(page, ["#side div[role='listitem']",
                                      "div[data-testid='cell-frame-container']",
                                      "#side div[title]"], timeout=5000)
    if not clicked:
        await page.keyboard.press("ArrowDown")
        await hdelay(0.25, 0.5)
        await page.keyboard.press("Enter")
    await hdelay(1.2, 2.2)  # چت باز شود
    # جعبهٔ پیام آماده است؟
    if await _wait_visible(page, WA_MSGBOX_SELS, 10) is None:
        return False
    # 🛡 تطبیق نام چتِ بازشده با هدف — از ارسال به چت اشتباه جلوگیری می‌کند
    # (سازگار با ذخیرهٔ «علی» برای «علی رضایی» و برعکس)
    header = ""
    for sel in WA_HEADER_SELS:
        try:
            locs = page.locator(sel)
            for i in range(min(await locs.count(), 3)):
                if await locs.nth(i).is_visible():
                    t = (await locs.nth(i).get_attribute("title") or
                         (await locs.nth(i).inner_text())).strip()
                    if t:
                        header = t
                        break
        except Exception:
            continue
        if header:
            break
    if header:
        t_norm, h_norm = target.strip().lower(), header.strip().lower()
        words = [w for w in re.split(r"\s+", t_norm) if len(w) >= 2]
        match = (t_norm in h_norm or h_norm in t_norm or
                 any(w in h_norm for w in words))
        if not match:
            log(f"⚠️ چتِ بازشده «{header}» با هدف «{target}» یکی نیست — ارسال لغو شد (حفاظت از چت اشتباه)", "warn")
            return False
    return True

async def _wa_type_message(page, text: str) -> bool:
    """تایپ پیام در کادر چت با باز + ارسال. Enter سطر جدید را می‌شکند نه
    می‌فرستد (در واتساپ وب Enter = ارسال) — پس بین سطرها Shift+Enter می‌زنیم،
    دقیقاً مثل خودتان. ارسال با Enter؛ اگر نشد با دکمهٔ ارسال؛ در آخر چک
    می‌کنیم کادر واقعاً خالی شده (نشانهٔ ارسال‌شدن)."""
    box = await _wait_visible(page, WA_MSGBOX_SELS, 10)
    if not box:
        return False
    try:
        await page.locator(box).click(timeout=4000)
    except Exception:
        return False
    await hdelay(0.3, 0.7)
    lines = [ln for ln in text.split("\n")]
    for i, ln in enumerate(lines):
        if ln:
            await page.keyboard.type(ln, delay=55)
        if i < len(lines) - 1:
            await page.keyboard.press("Shift+Enter")
    await hdelay(0.45, 1.0)  # مکث انسانی بعد از نوشتن، قبل از فرستادن
    await page.keyboard.press("Enter")
    await asyncio.sleep(1.1)
    # کادر خالی شده؟ = ارسال شد. اگر نه، دکمهٔ ارسال را امتحان می‌کنیم.
    if not await _wa_box_has_text(page):
        return True
    if await click_first(page, WA_SEND_SELS, timeout=4000):
        await asyncio.sleep(1.1)
        return not await _wa_box_has_text(page)
    return False

async def _wa_box_has_text(page) -> bool:
    """آیا در کادر پیام متنِ باقی‌مانده هست؟ (خالی = ارسال شده)"""
    for sel in WA_MSGBOX_SELS:
        try:
            locs = page.locator(sel)
            for i in range(min(await locs.count(), 3)):
                if await locs.nth(i).is_visible():
                    if (await locs.nth(i).inner_text()).strip():
                        return True
        except Exception:
            continue
    return False

@action("whatsapp", "send_message")
async def wa_send(sess, p):
    """ارسال پیام واتساپ به یک یا چند مخاطب/گروه (نام‌ها با ویرگول).
    نام باید در واتساپ شما موجود باشد (مخاطب ذخیره‌شده/گروه عضو‌شده) —
    دقیقاً مثل جستجوی دستی خودتان. فاصلهٔ انسانی بین گیرنده‌ها رعایت می‌شود."""
    page = await sess.ensure()
    text = (p.get("text") or "").strip()
    targets = [t.strip() for t in re.split("[،,]", p.get("target") or "") if t.strip()]
    if not targets or not text:
        return {"ok": False, "message": "گیرنده (نام مخاطب/گروه) و متن پیام هر دو لازم‌اند"}
    await goto(page, WA_URL)
    await hdelay(2.5, 4)
    if not await _wa_logged_in(page):
        return {"ok": False, "message": "به واتساپ وارد نشده‌اید — اول در تب «پلتفرم‌ها» دکمهٔ «ورود» را بزنید و "
                "QR را با گوشی اسکن کنید (واتساپ ← تنظیمات ← دستگاه‌های متصل ← اتصال دستگاه)؛ بعد دوباره ارسال پیام را اجرا کنید"}
    sent: List[str] = []
    failed: List[str] = []
    for ti, t in enumerate(targets):
        try:
            opened = await _wa_search_open_chat(page, t)
            done = await _wa_type_message(page, text) if opened else False
        except Exception as e:  # noqa
            log(f"⚠️ ارسال به {t} خطا داد: {_short_err(e)}", "warn")
            done = False
        (sent if done else failed).append(t)
        if done:
            log(f"✅ پیام واتساپ به «{t}» ارسال شد")
        else:
            log(f"⚠️ پیام به «{t}» ارسال نشد (چت باز نشد یا دکمهٔ ارسال کار نکرد)", "warn")
        if ti < len(targets) - 1:
            await hdelay(8, 15)  # فاصلهٔ انسانی بین گیرنده‌ها — انبوه = پرچم قرمز واتساپ
    if not sent:
        return {"ok": False, "message": "پیام به هیچ‌کدام از گیرنده‌ها ارسال نشد — نام مخاطب/گروه را دقیقاً "
                "همان‌طور که در واتساپ ذخیره شده وارد کنید (فهرست نتایج جستجو را باز می‌کنیم؛ نتیجه‌ای نبود، پیامی نمی‌رود)"}
    msg = f"پیام به {len(sent)} گیرنده ارسال شد ✅"
    if failed:
        msg += f" — برای اینها ارسال نشد: {'، '.join(failed)}"
    return {"ok": True, "message": msg}

# ----- فیسبوک
@action("facebook", "friend_request")
async def fb_friend(sess, p):
    page = await sess.ensure()
    count = await _ensure_count(p)
    dmin, dmax = float(p.get("delay_min", 45)), float(p.get("delay_max", 150))
    target = (p.get("target") or "").strip()
    if not target:
        return {"ok": False, "message": "پروفایل لازم است"}
    if not target.startswith("http"):
        targets = await _collect_users_from_links(
            page, f"https://www.facebook.com/search/people/?q={urllib.parse.quote(target)}",
            r"^/([A-Za-z0-9.\-]+)$", count, skip=("login", "watch", "marketplace", "gaming"))
        targets = [t for t in targets if t not in ("profile.php",)]
        if not targets:
            return {"ok": False, "message": "در جستجو کسی پیدا نشد"}
    else:
        targets = [target]
    done = 0
    for u in targets[:count]:
        try:
            await goto(page, u if u.startswith("http") else f"https://www.facebook.com/{u}")
            if await click_first(page, ["[aria-label*='افزودن دوست']", "[aria-label*='Add Friend' i]",
                                        "button:has-text('Add Friend')"]):
                done += 1
                log(f"👥 درخواست دوستی: {u}")
        except Exception as e:
            log(f"⚠ دوستی {u}: {e}", "warn")
        if len(targets) > 1:
            await hdelay(dmin, dmax)
    return {"ok": done > 0, "message": f"درخواست دوستی: {done}"}

@action("facebook", "like")
async def fb_like(sess, p):
    # موتور ۲.۱۰.۰ — سلکتور دقیق 'Like' (نه شاملِ آن که «Liked» را هم می‌گرفت)
    return await _run_like(sess, p, "facebook", "https://www.facebook.com/", 15, 20, 60)

@action("facebook", "comment")
async def fb_comment(sess, p):
    page = await sess.ensure()
    target = p.get("target") or ""
    if not target:
        return {"ok": False, "message": "لینک پست لازم است"}
    await goto(page, target)
    if await click_first(page, ["div[role='button'][aria-label*='Comment']", "span:has-text('Comment')"],
                         timeout=4000):
        pass
    if await click_first(page, ["div[role='textbox']", "textarea"], timeout=8000):
        await page.keyboard.type(p.get("text") or "")
        await asyncio.sleep(1)
        await page.keyboard.press("Enter")
        return {"ok": True, "message": "کامنت ارسال شد ✅"}
    return {"ok": False, "message": "کادر کامنت پیدا نشد"}

@action("facebook", "post_photo")
async def fb_post_photo(sess, p):
    page = await sess.ensure()
    path = _media_path(p.get("media"))
    if not path:
        return {"ok": False, "message": "ابتدا فایل رسانه را بارگذاری کنید"}
    await goto(page, "https://www.facebook.com/")
    await hdelay(2, 3)
    inputs = page.locator("input[type=file][accept*='image']")
    if await inputs.count():
        await inputs.first.set_input_files(path)
        await hdelay(2, 4)
    if await click_first(page, ["div[role='textbox']", "div[aria-label*=\"چه خبر\"]"], timeout=6000):
        if p.get("text"):
            await page.keyboard.type(p["text"])
        await asyncio.sleep(1)
        if await click_first(page, ["span:has-text('Post')", "span:has-text('انتشار')",
                                    "[aria-label*='Post' i]"], timeout=8000):
            return {"ok": True, "message": "پست فیسبوک ارسال شد ✅"}
    return {"ok": False, "message": "ارسال پست ناموفق — از خود سایت ادامه دهید"}

@action("facebook", "post_story")
async def fb_post_story(sess, p):
    """۲.۱۰.۰ — فیسبوک تنها پلتفرمی است که استوری (عکس) از نسخهٔ وب می‌پذیرد.
    فلو: facebook.com/stories → «Create story» → «Create photo story» → انتخاب
    فایل → «Share story»؛ با سلکتورهای فارسی/انگلیسی و پیام‌های کمکی."""
    page = await sess.ensure()
    path = _media_path(p.get("media"))
    if not path:
        return {"ok": False, "message": "ابتدا فایل رسانه (عکس) را از تب «رسانه‌ها» یا دکمهٔ آپلود بارگذاری کنید"}
    if str(path).lower().endswith((".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v")):
        return {"ok": False, "message": "نسخهٔ وب فیسبوک فقط استوری «عکس» می‌پذیرد — ویدیو را از اپ فیسبوک استوری کنید"}
    await goto(page, "https://www.facebook.com/stories")
    if await _looks_logged_out(page, list(LOGIN_URL_MARKERS["facebook"])):
        return {"ok": False, "message": NOT_LOGGED_IN_LIKE}
    await hdelay(2, 4)
    # ۱) دکمهٔ «ایجاد استوری» (Create story) — روی صفحهٔ /stories
    await click_first(page, [
        "div[role='button'][aria-label='Create story']", "div[aria-label='Create story']",
        "div[role='button']:has-text('Create story')", "span:has-text('Create story')",
        "div[role='button'][aria-label='ایجاد استوری']", "div[role='button']:has-text('ایجاد استوری')",
        "span:has-text('ایجاد استوری')", "a[aria-label*='Create story' i]"], timeout=8000)
    await hdelay(1.5, 3)
    # ۲) انتخاب «استوری عکس» (Create photo story)
    await click_first(page, [
        "div[role='button']:has-text('Create photo story')", "span:has-text('Create photo story')",
        "div:has-text('Create photo story')", "span:has-text('استوری عکس')",
        "div[role='button']:has-text('استوری عکس')", "div:has-text('استوری عکس')"], timeout=5000)
    await hdelay(1, 2)
    # ۳) ورودی فایل (بعضی نسخه‌ها مستقیم روی صفحهٔ /stories هستند)
    inputs = page.locator("input[type=file]")
    ok = False
    for i in range(await inputs.count()):
        inp = inputs.nth(i)
        accept = ((await inp.get_attribute("accept") or "")).lower()
        try:
            if "image" in accept or not accept:
                await inp.set_input_files(path)
                ok = True
                break
        except Exception:
            continue
    if not ok:
        return {"ok": False, "message": "ورودی فایل استوری فیسبوک پیدا نشد — دیالوگ «Create story» را در پنجرهٔ باز "
                                        "دستی باز کنید، گزینهٔ «Create photo story» را بزنید و عکس را انتخاب کنید"}
    await hdelay(2.5, 4)
    # ۴) دکمهٔ اشتراک‌گذاری استوری
    if await click_first(page, [
            "div[role='button'][aria-label='Share story']", "span:has-text('Share story')",
            "div[role='button']:has-text('Share story')", "span:has-text('Post to story')",
            "div[role='button']:has-text('Post to story')", "div[role='button'][aria-label='اشتراک‌گذاری استوری']",
            "span:has-text('اشتراک‌گذاری استوری')", "div[role='button']:has-text('اشتراک‌گذاری استوری')",
            "button:has-text('Share story')"], timeout=12000):
        await asyncio.sleep(3)
        return {"ok": True, "message": "استوری فیسبوک ارسال شد ✅"}
    return {"ok": False, "message": "عکس بارگذاری شد ولی دکمهٔ «اشتراک‌گذاری استوری» پیدا نشد — از همان پنجرهٔ باز، دکمه را دستی بزنید"}

# ----- لینکدین
@action("linkedin", "connect")
async def li_connect(sess, p):
    page = await sess.ensure()
    count = await _ensure_count(p)
    dmin, dmax = float(p.get("delay_min", 60)), float(p.get("delay_max", 180))
    target = (p.get("target") or "").strip()
    if not target:
        return {"ok": False, "message": "پروفایل لازم است"}
    if target.startswith("http"):
        targets = [target]
    else:
        targets = await _collect_users_from_links(
            page, f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(target)}",
            r"^/in/([A-Za-z0-9.\-]+)$", count)
        if not targets:
            return {"ok": False, "message": "در جستجو کسی پیدا نشد"}
    done = 0
    for u in targets[:count]:
        try:
            await goto(page, u if u.startswith("http") else f"https://www.linkedin.com/in/{u}")
            if await click_first(page, ["button:has-text('اتصال')", "button:has-text('Connect')",
                                        "button[aria-label*='Connect' i]"]):
                done += 1
                log(f"🤝 اتصال: {u}")
                await click_first(page, ["button:has-text('ارسال')", "button:has-text('Send')",
                                         "button[type='submit']"], timeout=4000)
        except Exception as e:
            log(f"⚠ اتصال {u}: {e}", "warn")
        if len(targets) > 1:
            await hdelay(dmin, dmax)
    return {"ok": done > 0, "message": f"درخواست اتصال: {done}"}

@action("linkedin", "like")
async def li_like(sess, p):
    # موتور ۲.۱۰.۰ — برچسب داینامیک («Like John's post») با شروع‌شونده گرفته می‌شود
    return await _run_like(sess, p, "linkedin", "https://www.linkedin.com/feed/", 15, 20, 60)

@action("linkedin", "comment")
async def li_comment(sess, p):
    page = await sess.ensure()
    target = p.get("target") or ""
    if not target:
        return {"ok": False, "message": "لینک پست لازم است"}
    await goto(page, target)
    if await click_first(page, ["button[aria-label*='Comment' i]"], timeout=4000):
        pass
    if await click_first(page, ["div[role='textbox']", "textarea"], timeout=8000):
        await page.keyboard.type(p.get("text") or "")
        await asyncio.sleep(1)
        await page.keyboard.press("Enter")
        return {"ok": True, "message": "کامنت ارسال شد ✅"}
    return {"ok": False, "message": "کادر کامنت پیدا نشد"}

@action("linkedin", "post")
async def li_post(sess, p):
    page = await sess.ensure()
    await goto(page, "https://www.linkedin.com/feed/")
    await hdelay(2, 3)
    if await click_first(page, ["button:has-text('Start a post')", "button:has-text('شروع یک پست')",
                                "button:has-text('ایجاد پست')"], timeout=6000):
        await hdelay(1.5, 3)
        path = _media_path(p.get("media"))
        if path:
            await click_first(page, ["button[aria-label*='Add photo']", "button[aria-label*='media' i]"],
                              timeout=4000)
            inputs = page.locator("input[type=file]")
            if await inputs.count():
                await inputs.first.set_input_files(path)
                await hdelay(2, 4)
        if await click_first(page, ["div[role='textbox']", "textarea"], timeout=6000):
            await page.keyboard.type(p.get("text") or "")
            await asyncio.sleep(1)
            if await click_first(page, ["button:has-text('Post')", "button:has-text('انتشار')"],
                                 timeout=10000):
                return {"ok": True, "message": "پست لینکدین ارسال شد ✅"}
    return {"ok": False, "message": "ارسال پست ناموفق — از خود سایت ادامه دهید"}

# ---------------------------------------------------------------- اجرای اکشن
async def run_action(platform: str, action_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    global CURRENT_RUN, LAST_RESULT
    if platform not in PLAT_IDS:
        return {"ok": False, "message": "پلتفرم نامعتبر"}
    acts = [a["id"] for a in ACTIONS.get(platform, [])]
    if action_id not in acts:
        return {"ok": False, "message": "اکشن نامعتبر"}
    params = dict(params or {})
    async with LOCKS[platform]:
        CURRENT_RUN = {"platform": platform, "action": action_id,
                       "started_at": datetime.now().strftime("%H:%M:%S")}
        try:
            fn = ACTION_IMPL.get((platform, action_id))
            if not fn:
                return {"ok": False, "message": "این اکشن پیاده‌سازی نشده"}
            log(f"▶ اجرای «{action_id}» روی {platform} …")
            res = await fn(SESSIONS[platform], params)
            ok = bool(res.get("ok", False))
            LAST_RESULT = {"platform": platform, "action": action_id, "ok": ok,
                           "message": res.get("message", ""), "at": datetime.now().strftime("%H:%M:%S")}
            log(("✅" if ok else "❌") + " " + res.get("message", ""), "info" if ok else "error")
            return res
        except Exception as e:
            LAST_RESULT = {"platform": platform, "action": action_id, "ok": False,
                           "message": f"خطا: {e}", "at": datetime.now().strftime("%H:%M:%S")}
            log(f"❌ خطا در «{action_id}» ({platform}): {e}", "error")
            return LAST_RESULT
        finally:
            CURRENT_RUN = None
            today = datetime.now().strftime("%Y-%m-%d")
            if STATS["date"] != today:
                STATS.update(date=today, runs=0, success=0, fail=0)
            STATS["runs"] += 1
            if LAST_RESULT and LAST_RESULT.get("ok"):
                STATS["success"] += 1
            else:
                STATS["fail"] += 1

# ---------------------------------------------------------------- زمان‌بند
class Scheduler:
    def __init__(self):
        self._task: Optional[asyncio.Task] = None

    def start(self):
        if not self._task:
            self._task = asyncio.create_task(self._loop())

    @staticmethod
    def compute_next(s: Dict[str, Any], now: Optional[datetime] = None) -> datetime:
        now = now or datetime.now()
        t = s.get("timing", {})
        if t.get("type") == "interval":
            base = now + timedelta(minutes=float(t.get("minutes", 30)))
            j = float(t.get("jitter", 0) or 0)
            if j > 0:
                base += timedelta(seconds=random.uniform(0, j * 60))
        elif t.get("type") == "daily":
            hours = sorted(int(h) for h in t.get("hours", []) or [10])
            minute = int(t.get("minute", 0) or 0)
            cands = []
            for h in hours:
                try:
                    cands.append(now.replace(hour=h, minute=minute, second=0, microsecond=0))
                except ValueError:
                    continue
            fut = [c for c in cands if c > now]
            base = fut[0] if fut else (cands[0] + timedelta(days=1) if cands else now + timedelta(days=1))
        elif t.get("type") == "once":
            try:
                base = datetime.fromisoformat(t.get("at", ""))
            except Exception:
                base = now + timedelta(hours=1)
        else:
            base = now + timedelta(hours=1)
        return base

    async def _loop(self):
        log("⏰ سرویس زمان‌بندی فعال شد")
        while True:
            try:
                now = datetime.now()
                data = load_schedules()
                changed = False
                for s in data:
                    if not s.get("enabled") or s.get("id") in RUNNING_SCHED:
                        continue
                    nr = s.get("next_run")
                    if nr:
                        try:
                            due = datetime.fromisoformat(nr)
                        except Exception:
                            due = None
                        if due and due <= now:
                            s["last_run"] = now.isoformat(timespec="seconds")
                            s["next_run"] = self.compute_next(s).isoformat(timespec="seconds")
                            changed = True
                            if _night_now():
                                log("🌙 مکث شبانهٔ فعال است (۱ تا ۷ بامداد) — اجرای این دور رد شد", "warn")
                            else:
                                asyncio.create_task(self._run(s))
                if changed:
                    save_schedules(data)
                    await broadcast({"type": "schedules"})
            except Exception as e:
                log(f"خطای زمان‌بند: {e}", "error")
            await asyncio.sleep(15)

    async def _run(self, s: Dict[str, Any]):
        RUNNING_SCHED.add(s["id"])
        try:
            if s.get("type") == "ai_report":
                log(f"🔔 زمان گزارش ماموریت «{s.get('title') or ''}» رسید")
                await AGENTS.finalize(s.get("mission_id") or "")
            elif s.get("type") == "macro":
                # ۲.۱۵.۰ — پلتفرم مؤثر را خودِ فایل ماکرو تعیین می‌کند (لحظهٔ ضبط)
                log(f"⏰ اجرای زمان‌بندی پخش ماکرو «{s.get('macro')}» روی {s['platform']}")
                await _macro_replay(s["platform"], s.get("macro") or "")
            else:
                log(f"⏰ اجرای زمان‌بندی «{s.get('title') or s['action']}» روی {s['platform']}")
                params = dict(s.get("params") or {})
                pacing = s.get("pacing") or {}
                params.setdefault("delay_min", pacing.get("delay_min", 35))
                params.setdefault("delay_max", pacing.get("delay_max", 120))
                await run_action(s["platform"], s["action"], params)
        finally:
            RUNNING_SCHED.discard(s["id"])
            await broadcast({"type": "schedules"})

SCHEDULER = Scheduler()

# ---------------------------------------------------------------- هوش مصنوعی (۲.۳.۰)
AGENTS = AgentSystem()

async def _agent_add_schedule(entry: Dict[str, Any]) -> Dict[str, Any]:
    """افزودن زمان‌بندی از طرف ایجنت هوشمند (با id و next_run)."""
    entry = dict(entry)
    entry.setdefault("id", uuid.uuid4().hex[:10])
    entry.setdefault("created", datetime.now().isoformat(timespec="seconds"))
    entry.setdefault("last_run", None)
    entry["next_run"] = Scheduler.compute_next(entry).isoformat(timespec="seconds")
    data = load_schedules()
    data.append(entry)
    save_schedules(data)
    await broadcast({"type": "schedules"})
    return entry

# ---------------------------------------------------------------- ۲.۴.۰ — پاسخ‌گوی دایرکت + چاپخانهٔ رسانه
DMAUTO = DMAuto()

def _dm_provider_model():
    ai = settings().get("ai", {})
    return ai.get("provider", "zai"), (ai.get("model") or "glm-4.6")

DMAUTO.configure(
    get_settings=settings,
    save_settings=lambda st: save_json(F_SETTINGS, st),
    get_session=get_session,
    llm_chat=llm_chat,
    llm_provider_model=_dm_provider_model,
    log=log,
    hdelay=hdelay,
    htype=htype,
    press_enter=lambda page: page.keyboard.press("Enter"),
)

MEDIA_JOBS: Dict[str, Dict[str, Any]] = {}

def _job_public(job: Dict[str, Any]) -> Dict[str, Any]:
    return {k: job.get(k) for k in ("id", "kind", "title", "status", "progress", "step",
                                   "created", "results", "error", "dry_run", "proposals")}

async def _job_update(job: Dict[str, Any], pct: Any, step: str) -> None:
    try:
        job["progress"] = int(pct)
    except Exception:
        pass
    job["step"] = str(step)
    job["log"].append({"t": datetime.now().strftime("%H:%M:%S"), "msg": str(step)})
    job["log"] = job["log"][-40:]
    await broadcast({"type": "ai_job", "job": _job_public(job)})

def _job_progress_cb(job: Dict[str, Any]):
    """کال‌بک پیشرفت برای توابعی که callback همگام می‌گیرند (مثل ai_media)."""
    def cb(pct, msg):
        try:
            job["progress"] = int(pct)
        except Exception:
            pass
        job["step"] = str(msg)
        job["log"].append({"t": datetime.now().strftime("%H:%M:%S"), "msg": str(msg)})
        job["log"] = job["log"][-40:]
        try:
            asyncio.get_running_loop().create_task(broadcast({"type": "ai_job", "job": _job_public(job)}))
        except RuntimeError:
            pass
    return cb

def _spawn_media_job(kind: str, title: str, coro_factory) -> Dict[str, Any]:
    jid = "j" + uuid.uuid4().hex[:10]
    job: Dict[str, Any] = {"id": jid, "kind": kind, "title": title[:80], "status": "running",
                           "progress": 0, "step": "شروع…", "created": datetime.now().isoformat(timespec="seconds"),
                           "results": [], "error": "", "log": []}
    MEDIA_JOBS[jid] = job

    async def _run() -> None:
        try:
            await coro_factory(job)
            job["status"] = "done"
            job["progress"] = 100
        except asyncio.CancelledError:
            job["status"] = "cancelled"
        except Exception as e:  # noqa
            job["status"] = "failed"
            job["error"] = str(e)
            log(f"❌ کارِ {kind} ناموفق بود: {e}", "error")
        await broadcast({"type": "ai_job", "job": _job_public(job)})
        await broadcast({"type": "media"})

    asyncio.create_task(_run())
    return job

async def _agent_media_images(prompts: List[str], count: int, size: str, mid: str = "") -> Dict[str, Any]:
    """ساخت عکس از طرف ایجنت خودمختار — نتیجهٔ {files: []}."""
    ai = settings().get("ai", {})
    img_cfg = ai.get("image") or {}
    files: List[str] = []
    for pr in list(prompts)[:max(1, count)]:
        try:
            res = await ai_media.generate_image(ai, pr, provider=img_cfg.get("provider", "zai"),
                                                model=img_cfg.get("model", ""), size_key=size)
            files.append(res["file"])
            log(f"🎨 ایجنت عکس ساخت: {res['file']}", "ok")
        except Exception as e:  # noqa
            log(f"⚠ ساخت عکس ناموفق: {e}", "warn")
    return {"files": files}

async def _agent_media_video(topic: str, seconds: int, voice: str, aspect: str) -> Dict[str, Any]:
    """چاپخانهٔ ویدیو از طرف ایجنت خودمختار."""
    ai = settings().get("ai", {})
    vid = ai.get("video") or {}
    return await ai_media.generate_video(
        llm_json, ai, topic=topic, provider=ai.get("provider", "zai"),
        model=ai.get("model") or "glm-4.6", voice=voice or vid.get("voice", "fa-IR-FaridNeural"),
        aspect=aspect or vid.get("aspect", "9:16"), seconds=int(seconds or vid.get("seconds", 45)),
        material=vid.get("material", "ai"), motion=vid.get("motion", "zoom"))

AGENTS.configure(
    run_action=run_action,
    add_schedule=_agent_add_schedule,
    get_settings=settings,
    save_settings=lambda st: save_json(F_SETTINGS, st),
    broadcast=broadcast,
    log=log,
    media_images=lambda: [m["name"] for m in media_list() if m.get("image")],
    active_platforms=lambda: PLAT_IDS,
    generate_media_images=_agent_media_images,
    generate_media_video=_agent_media_video,
    dm_status=lambda: {"running": DMAUTO.running(), "stats": DMAUTO.stats()},
    dm_configure=DMAUTO.save_cfg,
    dm_round=DMAUTO.round,
)

# ---------------------------------------------------------------- API
app = FastAPI(title="ParsAgent Panel")
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

@app.on_event("startup")
async def on_startup():
    # فقط زمان‌بند فعال می‌شود — ضبط ماکرو هرگز خودکار شروع نمی‌شود
    SCHEDULER.start()
    AGENTS.recover()
    log("🖥 پنل ParsAgent ۲.۴.۰ آماده است — تب «🧠 هوش مصنوعی»: ماموریت خودمختار + ساخت عکس/ویدیو + پاسخ‌گوی دایرکت")

@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/api/ready")
async def ready():
    return {"ok": True}

@app.get("/api/options")
async def options():
    return {"platforms": PLATFORMS, "actions": ACTIONS, "guide": GUIDE, "safe_delay": SAFE_DELAY}

@app.get("/api/state")
async def state():
    plats = {}
    for pid, s in SESSIONS.items():
        plats[pid] = {"open": s.open,
                      "url": (s.page.url if s.page and s.page.url.startswith("http") else ""),
                      "recording": s.recording}
    sched = []
    for s in load_schedules():
        item = dict(s)
        item["running"] = s["id"] in RUNNING_SCHED
        sched.append(item)
    today = datetime.now().strftime("%Y-%m-%d")
    if STATS["date"] != today:
        STATS.update(date=today, runs=0, success=0, fail=0)
    rec = next(((pid, s) for pid, s in SESSIONS.items() if s.recording), None)
    return {
        "now": datetime.now().isoformat(timespec="seconds"),
        "platforms": plats,
        "schedules": sched,
        "macro": {"recording": bool(rec), "platform": rec[0] if rec else None,
                  "events": sum(len(s.rec_events) for s in SESSIONS.values()),
                  "dropped_panel": sum(s.rec_dropped_panel for s in SESSIONS.values()),
                  "dropped_foreign": sum(s.rec_dropped_foreign for s in SESSIONS.values()),
                  # ۲.۱۵.۰ — پخشِ جاری: دکمهٔ «توقف پخش» و چیپ وضعیت پنل
                  "playing": (({"platform": MACRO_PLAY["platform"], "name": MACRO_PLAY["name"]}
                               if (MACRO_PLAY["task"] is not None and not MACRO_PLAY["task"].done()) else None)),
                  "saved": macro_names()},
        "stats": dict(STATS),
        "current_run": CURRENT_RUN,
        "last_result": LAST_RESULT,
        "media_count": len(media_list()),
    }

@app.post("/api/quickrun")
async def quickrun(body: Dict[str, Any]):
    res = await run_action(body.get("platform", ""), body.get("action", ""), body.get("params") or {})
    return res

@app.post("/api/platforms/{pid}/close")
async def close_platform(pid: str):
    if pid not in PLAT_IDS:
        raise HTTPException(404)
    async with LOCKS[pid]:
        s = SESSIONS[pid]
        s.recording = False
        await s.close()
    log(f"🔒 مرورگر {pid} بسته شد")
    return {"ok": True}

# ----- رسانه‌ها
@app.post("/api/media/upload")
async def media_upload(files: List[UploadFile] = File(...)):
    saved = []
    for f in files:
        safe = re.sub(r"[^\w.\-\u0600-\u06FF]+", "_", f.filename or "file")[:90] or "file"
        name = f"{int(time.time() * 1000) % 100000000}_{safe}"
        data = await f.read()
        (MEDIA_DIR / name).write_bytes(data)
        saved.append(name)
    log(f"📤 {len(saved)} فایل بارگذاری شد")
    return {"ok": True, "saved": saved, "media": media_list()}

@app.get("/api/media")
async def get_media():
    return {"media": media_list()}

@app.delete("/api/media/{name}")
async def del_media(name: str):
    f = MEDIA_DIR / Path(name).name
    if f.exists():
        f.unlink()
        log(f"🗑 حذف شد: {name}")
    return {"ok": True, "media": media_list()}

# ----- تنظیمات
@app.get("/api/settings")
async def get_settings():
    return settings()

@app.post("/api/settings")
async def post_settings(body: Dict[str, Any]):
    st = settings()
    for k, v in body.items():
        if k in ("general", "stealth", "captcha", "ai") and isinstance(v, dict):
            st[k].update(v)
            if k == "stealth" and "per_platform" in v:
                st["stealth"]["per_platform"].update(v["per_platform"])
        elif k in st and not isinstance(v, dict):
            st[k] = v
    save_json(F_SETTINGS, st)
    log("💾 تنظیمات ذخیره شد")
    return {"ok": True, "settings": st}

@app.get("/api/credentials")
async def get_credentials():
    out = {}
    for pid in PLAT_IDS:
        c = creds().get(pid) or {}
        out[pid] = {"username": c.get("username", ""), "has_password": bool(c.get("password"))}
    return out

@app.post("/api/credentials")
async def post_credentials(body: Dict[str, Any]):
    allc = creds()
    pid = body.get("platform")
    if pid not in PLAT_IDS:
        raise HTTPException(400, "پلتفرم نامعتبر")
    c = dict(allc.get(pid) or {})
    c["username"] = body.get("username", c.get("username", ""))
    pw = body.get("password")
    if pw:  # خالی یعنی «بدون تغییر»
        c["password"] = pw
    if body.get("clear_password"):
        c.pop("password", None)
    allc[pid] = c
    save_json(F_CREDS, allc)
    log(f"🔑 اطلاعات ورود {pid} ذخیره شد (فقط روی همین سیستم)")
    return {"ok": True}

# ----- زمان‌بندی‌ها
@app.get("/api/schedules")
async def get_schedules():
    return {"schedules": load_schedules()}

@app.post("/api/schedules")
async def create_schedule(body: Dict[str, Any]):
    jtype = (body.get("type") or "action").strip()
    pid = body.get("platform")
    if pid not in PLAT_IDS:
        raise HTTPException(400, "پلتفرم نامعتبر")
    timing = body.get("timing") or {"type": "interval", "minutes": 60}
    if timing.get("type") == "interval" and float(timing.get("minutes", 0)) < 1:
        raise HTTPException(400, "حداقل فاصله ۱ دقیقه")
    if jtype == "macro":
        mname = (body.get("macro") or "").strip()
        safe = re.sub(r"[^\w\u0600-\u06FF\-]+", "_", mname)
        if not safe or not (MACROS_DIR / f"{safe}.json").exists():
            raise HTTPException(400, "ماکرویی با این نام پیدا نشد — اول در تب «ضبط ماکرو» ذخیره‌اش کنید")
        s = {
            "id": uuid.uuid4().hex[:10],
            "title": (body.get("title") or "").strip() or f"پخش ماکرو {mname}",
            "type": "macro", "platform": pid, "macro": mname, "action": "macro",
            "params": {}, "timing": timing, "pacing": {},
            "enabled": True,
            "created": datetime.now().isoformat(timespec="seconds"),
            "last_run": None, "next_run": None,
        }
    else:
        act = body.get("action")
        if not any(a["id"] == act for a in ACTIONS.get(pid, [])):
            raise HTTPException(400, "پلتفرم یا اکشن نامعتبر")
        s = {
            "id": uuid.uuid4().hex[:10],
            "title": (body.get("title") or "").strip() or f"{act} روی {pid}",
            "platform": pid, "action": act,
            "params": body.get("params") or {},
            "timing": timing,
            "pacing": body.get("pacing") or {},
            "enabled": True,
            "created": datetime.now().isoformat(timespec="seconds"),
            "last_run": None,
            "next_run": None,
        }
    s["next_run"] = Scheduler.compute_next(s).isoformat(timespec="seconds")
    data = load_schedules()
    data.append(s)
    save_schedules(data)
    log(f"📅 زمان‌بندی «{s['title']}» ساخته شد")
    await broadcast({"type": "schedules"})
    return {"ok": True, "schedule": s}

@app.post("/api/schedules/{sid}/toggle")
async def toggle_schedule(sid: str):
    data = load_schedules()
    for s in data:
        if s["id"] == sid:
            s["enabled"] = not s.get("enabled", True)
            s["next_run"] = (Scheduler.compute_next(s).isoformat(timespec="seconds")
                             if s["enabled"] else None)
            save_schedules(data)
            log(f"زمان‌بندی «{s['title']}» {'فعال' if s['enabled'] else 'غیرفعال'} شد")
            await broadcast({"type": "schedules"})
            return {"ok": True, "enabled": s["enabled"]}
    raise HTTPException(404)

@app.delete("/api/schedules/{sid}")
async def delete_schedule(sid: str):
    data = load_schedules()
    data = [s for s in data if s["id"] != sid]
    save_schedules(data)
    log("🗑 زمان‌بندی حذف شد")
    await broadcast({"type": "schedules"})
    return {"ok": True}

@app.post("/api/schedules/{sid}/run")
async def run_schedule_now(sid: str):
    for s in load_schedules():
        if s["id"] == sid:
            asyncio.create_task(SCHEDULER._run(s))
            return {"ok": True}
    raise HTTPException(404)

# ----- ماکرو
# ۲.۱۵.۰ — وضعیت پخشِ جاری: دکمهٔ «توقف پخش» این پرچم را بالا می‌آورد و
# حلقهٔ پخش بین رخدادها/داخل مکث‌ها چکش می‌کند؛ در /api/state هم نمایش
# داده می‌شود تا پنل دکمهٔ توقف و چیپ «در حال پخش» را نشان بدهد.
MACRO_PLAY: Dict[str, Any] = {"task": None, "stop": False, "platform": None, "name": None}


def _macro_path(name: str) -> Path:
    """مسیر فایل ماکرو (با همان پاک‌سازی نام که قبلاً inline بود)."""
    return MACROS_DIR / (re.sub(r"[^\w\u0600-\u06FF\-]+", "_", name or "") + ".json")


def _macro_load(f: Path) -> Dict[str, Any]:
    """بارگذاری ماکرو — فرمت ۲.۱۵.۰ ({platform, saved_at, events}) و فرمت قدیمی (لیست رخدادها)."""
    try:
        raw = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return {"platform": "", "events": []}
    if isinstance(raw, dict):
        return {"platform": str(raw.get("platform") or ""), "events": list(raw.get("events") or [])}
    return {"platform": "", "events": list(raw)}


async def _wsleep(sec: float) -> bool:
    """مکث بین رخدادهای پخش، قابل‌قطع با دکمهٔ «توقف پخش» — True = توقف خواسته شد."""
    end = time.monotonic() + sec
    while True:
        if MACRO_PLAY["stop"]:
            return True
        rem = end - time.monotonic()
        if rem <= 0:
            return False
        await asyncio.sleep(min(0.2, rem))


def _pick_replay_page(sess: "BotSession", pid: str):
    """۲.۱۵.۰ — تبِ شروع پخش: اولین تبِ زنده روی دامنهٔ خود پلتفرم، وگرنه اولین تبِ زنده."""
    doms = PLATFORM_DOMAINS.get(pid) or []
    try:
        pages = list(sess.context.pages)
    except Exception:
        return None
    for pg in pages:
        try:
            if pg.is_closed():
                continue
            if any(d in (pg.url or "").lower() for d in doms):
                return pg
        except Exception:
            continue
    for pg in pages:
        try:
            if not pg.is_closed():
                return pg
        except Exception:
            continue
    return None


async def _macro_replay(pid: str, name: str) -> Dict[str, Any]:
    """پخش مشترک ماکرو — هم برای دکمهٔ «اجرا» و هم برای زمان‌بندی‌ها.

    ۲.۱۵.۰ — چهار درخواست کاربر:
      ۱) «برای استاپ پخش هم دکمه بذار»: POST /api/macro/stop-run پرچم
         MACRO_PLAY["stop"] را بالا می‌آورد؛ حلقهٔ پخش بین رخدادها و داخل
         مکث‌ها (چانک ۰.۲ ثانیه) چکش می‌کند و همان‌جا قطع می‌شود.
      ۲) «دراپ‌داون پخش لازم نیست»: پلتفرم از خودِ فایل ماکرو (لحظهٔ ضبط)
         خوانده می‌شود و روی همان اجرا می‌شود؛ فقط ماکروهای قدیمیِ بدون
         پلتفرم از پارامتر pid استفاده می‌کنند.
      ۳) «وقتی ماکرو شروع می‌شه بره به صفحهٔ اصلی اون پلتفرم»: تبِ مرورگر
         قبل از پخش به صفحهٔ اصلی همان پلتفرم می‌رود — قبلاً صفحهٔ خالی
         می‌ماند و هیچ رخدادی پیدا نمی‌شد.
      ۴) «وقتی پخش تموم می‌شه یا توقف رو می‌زنم، پنجرهٔ مرورگر بسته بشه»:
         sess.close() در پایان/توقف پخش؛ و اگر کاربر خودش مرورگر را بسته
         باشد، ensure() خودش را درمان می‌کند و دیگر خطا نمی‌دهد.

    ۲.۱۴.۰ — پخش مقاوم: هر رخداد دامنهٔ ضبط‌شدنش را دارد (origin)؛ صفحهٔ
    درست از بین تب‌های مرورگر پیدا می‌شود و عنصر در همهٔ فریم‌ها (قاب‌های
    فرعی مثل جعبهٔ چت داخل iframe) جستجو می‌شود. رخداد ناموفق دیگر بی‌صدا
    رد نمی‌شود — شمرده می‌شود و دلیلش به کاربر گفته می‌شود.
    """
    f = _macro_path(name)
    if not f.exists():
        return {"ok": False, "message": "ماکرو پیدا نشد"}
    data = _macro_load(f)
    events = data.get("events") or []
    stored = data.get("platform") or ""
    if stored in PLAT_IDS and stored != pid:
        log(f"↩ پلتفرم این ماکرو از لحظهٔ ضبط «{stored}» است — روی همان اجرا می‌شود (نه {pid})")
        pid = stored
    if pid not in PLAT_IDS:
        return {"ok": False, "message": "پلتفرم این ماکرو مشخص نیست — در تب «ضبط ماکرو» روی همان پلتفرم دوباره ضبط کنید"}
    if not events:
        return {"ok": False, "message": "این ماکرو خالی است — دوباره ضبط کنید"}
    other = MACRO_PLAY["task"]
    if other is not None and not other.done():
        return {"ok": False, "message": "هم اکنون یک ماکرو در حال پخش است — اول دکمهٔ «توقف پخش» را بزنید یا منتظر بمانید"}
    MACRO_PLAY.update(stop=False, platform=pid, name=name)
    MACRO_PLAY["task"] = asyncio.current_task()
    stopped = False
    try:
        async with LOCKS[pid]:
            sess = SESSIONS[pid]
            try:
                page = await sess.ensure()
            except Exception as e:
                return {"ok": False,
                        "message": f"باز شدن مرورگر ممکن نشد: {_short_err(e)} — تنظیمات ← عمومی ← «مرورگر ترجیحی» را روی «خودکار» بگذارید"}
            page = _pick_replay_page(sess, pid) or page
            # ۳) شروع پخش = صفحهٔ اصلی همان پلتفرم (درخواست کاربر؛ قبلاً صفحهٔ خالی می‌ماند)
            home = next((p["url"] for p in PLATFORMS if p["id"] == pid), "")
            if home and not MACRO_PLAY["stop"]:
                log(f"🌐 شروع پخش: رفتن به صفحهٔ اصلی {pid} — {home}")
                try:
                    await page.goto(home, wait_until="domcontentloaded", timeout=45000)
                except Exception as e:
                    log(f"⚠ صفحهٔ اصلی کامل باز نشد ({_short_err(e)}) — به هر حال پخش را ادامه می‌دهیم؛ اگر سایت نیامد، پروکسی/شبکه را بررسی کنید", "warn")
                try:
                    await page.bring_to_front()
                except Exception:
                    pass
            log(f"▶ پخش ماکرو «{name}» ({len(events)} رخداد) روی {pid}")
            done, failed = 0, 0
            for idx, ev in enumerate(events, 1):
                if MACRO_PLAY["stop"]:
                    stopped = True
                    break
                try:
                    # ۱) صفحهٔ درست: تبِ هم‌دامنه با لحظهٔ ضبط (وگرنه همان صفحهٔ فعلی)
                    origin = str(ev.get("origin") or "")
                    if origin and sess.context:
                        want_host = origin.split("//")[-1].rstrip("/")
                        for pg in sess.context.pages:
                            try:
                                if want_host and want_host in (pg.url or ""):
                                    page = pg
                                    break
                            except Exception:
                                continue
                    sel = str(ev.get("sel") or "")
                    if not sel:
                        continue
                    # ۲) عنصر در قاب اصلی یا یکی از فریم‌های فرعی
                    loc = None
                    for fr in page.frames:
                        try:
                            cand = fr.locator(sel)
                            if await cand.count() > 0:
                                loc = cand.first
                                break
                        except Exception:
                            continue
                    if loc is None:
                        failed += 1
                        log(f"⚠ رخداد {idx}: عنصر پیدا نشد — {sel[:80]}", "warn")
                        continue
                    t = ev.get("t")
                    if t == "click":
                        await loc.click(timeout=8000)
                    elif t == "input":
                        await loc.fill(str(ev.get("v") or ""), timeout=8000)
                    elif t == "key":
                        await loc.press(str(ev.get("k") or "Enter"), timeout=8000)
                    else:
                        continue
                    done += 1
                    if await _wsleep(random.uniform(0.35, 0.9)):
                        stopped = True
                        break
                except Exception as e:  # noqa
                    failed += 1
                    log(f"⚠ رخداد {idx} اجرا نشد: {_short_err(e)}", "warn")
                    continue
            if stopped:
                msg = f"پخش متوقف شد — {done} از {len(events)} رخداد اجرا شد"
            else:
                msg = f"{done} از {len(events)} رخداد اجرا شد"
                if failed:
                    msg += f" — {failed} رخداد اجرا نشد (صفحه/عنصر پیدا نشد — صفحه را مثل لحظهٔ ضبط باز کنید)"
            # ۴) بستن پنجرهٔ مرورگرِ همان پلتفرم بعد از پایان/توقف پخش (درخواست کاربر)
            try:
                await sess.close()
                log(f"🔒 {'توقف' if stopped else 'پایان'} پخش — پنجرهٔ مرورگر {pid} بسته شد")
            except Exception:
                pass
            log(f"پخش ماکرو تمام شد: {msg}")
            return {"ok": True, "message": msg, "stopped": stopped}
    finally:
        MACRO_PLAY.update(task=None, stop=False, platform=None, name=None)


def _rec_origin_ok(pid: str, ev: Dict[str, Any]) -> bool:
    """۲.۱۴.۰ — آیا این رویداد در دامنهٔ خودِ پلتفرم رخ داده است؟

    درخواست کاربر: «ماکرو فقط در پنجرهٔ مرورگر شبکهٔ اجتماعی ضبط شود،
    نه بقیهٔ پنجره‌ها». رویدادهای پنلِ باز‌شده داخل همان مرورگر
    (localhost) و سایت‌های بی‌ربط (تب‌های دیگر) نادیده گرفته می‌شوند —
    دکمهٔ «توقف ضبط» هم دیگر هرگز داخل ماکرو ضبط نمی‌شود.
    """
    origin = str(ev.get("origin") or "")
    try:
        host = (urllib.parse.urlparse(origin).hostname or "").lower()
    except Exception:
        host = ""
    if host in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
        return False
    allowed = PLATFORM_DOMAINS.get(pid) or []
    if not allowed or not host:
        return True  # ماکروهای قدیمی بدون origin یا پلتفرمِ بدون فهرست دامنه
    return any(host == d or host.endswith("." + d) for d in allowed)


async def _rec_handler(source, arg: str = ""):
    try:
        ev = json.loads(arg)
    except Exception:
        return
    pid = None
    for p_, s_ in SESSIONS.items():
        if s_.recording:
            pid = p_
            break
    if not pid:
        return
    sess = SESSIONS[pid]
    # ۲.۱۴.۰ — فیلتر پنجره/دامنه: کلیک روی پنل یا سایت‌های دیگر ضبط نمی‌شود
    if not _rec_origin_ok(pid, ev):
        origin = str(ev.get("origin") or "")
        try:
            host = (urllib.parse.urlparse(origin).hostname or "").lower()
        except Exception:
            host = ""
        if host in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
            sess.rec_dropped_panel += 1
        else:
            sess.rec_dropped_foreign += 1
        return
    sess.rec_events.append(ev)

@app.post("/api/macro/start")
async def macro_start(body: Dict[str, Any]):
    pid = body.get("platform")
    if pid not in PLAT_IDS:
        raise HTTPException(400, "پلتفرم نامعتبر")
    sess = await get_session(pid)
    if sess.recording:
        return {"ok": True, "message": "ضبط از قبل فعال است"}
    try:
        if not sess._exposed:
            await sess.context.expose_binding("__pa_rec", _rec_handler)
            sess._exposed = True
        await sess.context.add_init_script(RECORDER_JS)
        for pg in sess.context.pages:
            try:
                await pg.evaluate(RECORDER_JS)
            except Exception:
                pass
        sess.rec_events = []
        sess.rec_dropped_panel = 0
        sess.rec_dropped_foreign = 0
        sess.recording = True
        dom = (PLATFORM_DOMAINS.get(pid) or [""])[0]
        log(f"🔴 ضبط ماکرو روی {pid} شروع شد — فقط کارهایی که در پنجرهٔ مرورگرِ "
            f"{dom} انجام می‌دهید ضبط می‌شود؛ کلیک روی پنل و سایت‌های دیگر نادیده گرفته می‌شود")
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "message": f"شروع ضبط ناموفق: {e}"}

@app.post("/api/macro/stop")
async def macro_stop(body: Dict[str, Any]):
    pid = body.get("platform")
    name = (body.get("name") or "").strip() or f"macro-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    safe = re.sub(r"[^\w\u0600-\u06FF\-]+", "_", name)
    if pid not in PLAT_IDS or not SESSIONS[pid].recording:
        return {"ok": False, "message": "ضبط فعالی روی این پلتفرم نیست"}
    sess = SESSIONS[pid]
    sess.recording = False
    # ۲.۱۴.۰ — دابل‌چک نهایی: رویدادِ خارج از دامنه/پنل اگر به هر دلیلی از
    # فیلتر _rec_handler رد شده باشد، اینجا حذف می‌شود (دکمهٔ توقف و...)
    events = [ev for ev in sess.rec_events if _rec_origin_ok(pid, ev)]
    dropped = len(sess.rec_events) - len(events)
    # ۲.۱۵.۰ — پلتفرمِ لحظهٔ ضبط داخل فایل ذخیره می‌شود؛ پخش دیگر دراپ‌داون
    # ندارد و از همین فیلد می‌فهمد روی کدام پلتفرم اجرا شود (درخواست کاربر:
    # «پایین بنویسه این ضبط مربوط به چه پلتفرمیه»)
    save_json(MACROS_DIR / f"{safe}.json",
              {"platform": pid, "saved_at": datetime.now().isoformat(timespec="seconds"), "events": events})
    n = len(events)
    sess.rec_events = []
    extra = f" — {dropped} رویداد خارج از پلتفرم نادیده گرفته شد" if dropped else ""
    log(f"⏹ ضبط متوقف شد — ماکرو «{safe}» با {n} رخداد ذخیره شد{extra}")
    return {"ok": True, "saved": safe, "events": n, "dropped": dropped}

@app.get("/api/macro/list")
async def macro_list():
    # ۲.۱۵.۰ — پلتفرم هر ماکرو هم برمی‌گردد (macro_names هر دو فرمت را می‌خواند)
    return {"macros": macro_names()}

@app.post("/api/macro/run")
async def macro_run(body: Dict[str, Any]):
    # ۲.۱۵.۰ — پلتفرم فقط برای ماکروهای قدیمی (بدون پلتفرمِ ذخیره‌شده)
    # به‌کار می‌رود؛ پلتفرم ذخیره‌شده در فایل ماکرو همیشه برنده است.
    pid, name = (body.get("platform") or ""), body.get("name")
    if not _macro_path(name).exists():
        raise HTTPException(404, "ماکرو پیدا نشد")
    return await _macro_replay(pid, name)

@app.post("/api/macro/stop-run")
async def macro_stop_run():
    """۲.۱۵.۰ — توقف پخشِ در حال اجرا (دکمهٔ «⏹ توقف پخش» پنل).

    فقط پرچم را بالا می‌آورد؛ حلقهٔ پخش — که مکث‌هایش را در چانک ۰.۲
    ثانیه می‌خوابد — حداکثر چند ثانیه بعد قطع می‌شود، پنجرهٔ مرورگرِ
    پلتفرم را می‌بندد و نتیجه را به همان دکمهٔ «اجرا» برمی‌گرداند.
    """
    t = MACRO_PLAY.get("task")
    if t is None or t.done():
        return {"ok": False, "message": "پخشی در حال اجرا نیست"}
    MACRO_PLAY["stop"] = True
    log("⏹ دستور توقف پخش ماکرو صادر شد — پخش قطع و پنجرهٔ مرورگر بسته می‌شود")
    return {"ok": True, "message": "در حال توقف پخش… — پنجرهٔ مرورگر هم بسته می‌شود"}

@app.delete("/api/macro/{name}")
async def macro_delete(name: str):
    f = _macro_path(name)
    if f.exists():
        f.unlink()
        log(f"🗑 ماکرو «{name}» حذف شد")
    return {"ok": True}

# ----- تست بات
@app.post("/api/test-bot")
async def test_bot(body: Dict[str, Any]):
    pid = body.get("platform") or "instagram"
    if pid not in PLAT_IDS:
        raise HTTPException(400)
    st = settings()
    checks: List[Dict[str, Any]] = []
    try:
        sess = await get_session(pid)
        page = sess.page
        await page.goto("about:blank")
    except Exception as e:
        return {"ok": False, "checks": [{"name": "راه‌اندازی مرورگر", "ok": False,
                                         "detail": f"باز نشد: {e} — playwright را نصب/به‌روز کنید"}]}
    stealth_on = st["stealth"]["enabled"] and st["stealth"].get("per_platform", {}).get(pid, True)
    checks.append({"name": "راه‌اندازی مرورگر با پروفایل دائمی",
                   "ok": True, "detail": f"پروفایل: profiles/{pid}"})
    r = await page.evaluate("""() => {
        const webgl = (() => { try { const c = document.createElement('canvas');
            const g = c.getContext('webgl') || c.getContext('experimental-webgl');
            return g ? (g.getParameter(37445) + ' | ' + g.getParameter(37446)) : ''; } catch(e){ return 'err'; } })();
        const cvs1 = (() => { try { const a = document.createElement('canvas'); a.width=60; a.height=20;
            const x = a.getContext('2d'); x.fillText('ParsAgent', 4, 12); return a.toDataURL().length; } catch(e){ return 0; } })();
        const cvs2 = (() => { try { const a = document.createElement('canvas'); a.width=60; a.height=20;
            const x = a.getContext('2d'); x.fillText('ParsAgent', 4, 12); return a.toDataURL().length; } catch(e){ return 0; } })();
        let audio = 'ok';
        try { const c2 = new OfflineAudioContext(1, 64, 44100); const b = c2.createBuffer(1, 64, 44100); b.getChannelData(0); } catch(e) { audio = 'err'; }
        let fonts = 'n/a';
        try { fonts = (document.fonts.check('12px Arial') ? 'Y' : 'N') + '/' + (document.fonts.check('12px zzzNotAFont123') ? 'Y' : 'N'); } catch(e) {}
        const nativeTs = (() => { try { return Function.prototype.toString.call(navigator.permissions.query).includes('native'); } catch(e) { return false; } })();
        return {
            webdriver: String(navigator.webdriver),
            languages: (navigator.languages || []).join(','),
            plugins: navigator.plugins.length,
            ua: navigator.userAgent,
            webgl: webgl, canvasLen: cvs1, stable: (cvs1 === cvs2 && cvs1 > 0),
            audio: audio, fonts: fonts, nativeTs: nativeTs,
            chrome: (typeof window.chrome === 'object' && !!window.chrome.runtime),
            cores: navigator.hardwareConcurrency, mem: navigator.deviceMemory,
        };
    }""")
    if not stealth_on:
        checks.append({"name": "ضد شناسایی (Stealth)", "ok": False,
                       "detail": "برای این پلتفرم خاموش است — از تنظیمات روشن کنید"})
    else:
        cfg = st["stealth"]
        checks.append({"name": "مخفی کردن navigator.webdriver", "ok": r["webdriver"] in ("undefined", "false"),
                       "detail": f"مقدار فعلی: {r['webdriver']}"})
        checks.append({"name": "زبان‌های مرورگر فارسی", "ok": "fa-IR" in r["languages"],
                       "detail": r["languages"] or "خالی"})
        checks.append({"name": "شبیه‌سازی پلاگین‌ها", "ok": r["plugins"] > 0,
                       "detail": f"تعداد: {r['plugins']}"})
        checks.append({"name": "window.chrome کامل (runtime/app)", "ok": bool(r["chrome"]),
                       "detail": "یک مرورگر واقعی همیشه window.chrome.runtime دارد"})
        checks.append({"name": "پوشاندن کارت گرافیک (WebGL)", "ok": "ANGLE" in r["webgl"] or "Intel" in r["webgl"],
                       "detail": r["webgl"] or "خوانده نشد"})
        checks.append({"name": "نویز پایدار Canvas (دو خواندن یکسان)", "ok": bool(r["stable"]),
                       "detail": f"اثر انگشت باید بین اجراها ثابت بماند — {r['canvasLen']} بایت"})
        checks.append({"name": "نویز صدا (AudioContext)", "ok": r["audio"] == "ok",
                       "detail": "خواندن getChannelData بدون خطا"})
        checks.append({"name": "ماسک فونت‌ها", "ok": str(r["fonts"]).startswith("Y/N"),
                       "detail": f"فونت رایج/ساختگی: {r['fonts']}"})
        checks.append({"name": "مشخصات سخت‌افزار واقع‌نما", "ok": r["cores"] in (4, 6, 8, 12, 16),
                       "detail": f"CPU: {r['cores']} هسته · RAM: {r['mem']}GB (پایدار برای این پروفایل)"})
        checks.append({"name": "کلاک native بودن توابع (toString)", "ok": bool(r["nativeTs"]),
                       "detail": "توابع وصله‌شده باید native به نظر برسند"})
        headless_bad = "HeadlessChrome" in r["ua"]
        checks.append({"name": "UA بدون کلمه Headless", "ok": not headless_bad,
                       "detail": ("شامل Headless است — حالت بدون رابط را خاموش کنید" if headless_bad
                                  else r["ua"][:60] + "…")})
    checks.append({"name": "تنظیمات انسانی (تایپ/فاصله/موس)",
                   "ok": bool(st["stealth"].get("human_typing") and st["stealth"].get("human_delays")),
                   "detail": "تایپ حرف‌به‌حرف + فاصلهٔ تصادفی + مسیر منحنی موس"})
    log(f"🧪 تست بات روی {pid} اجرا شد")
    ok_all = all(c["ok"] for c in checks)
    return {"ok": ok_all, "checks": checks}

# ----- هوش مصنوعی (۲.۳.۰)
@app.get("/api/ai/catalog")
async def ai_catalog():
    return AGENTS.catalog()

@app.get("/api/ai/models")
async def ai_live_models(provider: str = ""):
    """۲.۱۴.۰ — فهرست مدل‌های «همین لحظه» از خود سرویس (GET /models).

    دکمهٔ «🔄 مدل‌های زنده» پنل اینجا وصل است؛ سرویس‌ها مدل‌های قدیمی را
    حذف می‌کنند (خطای 404) و کاتالوگ ایستا کهنه می‌شود — اینجا فهرست با
    کلید خود کاربر مستقیم از سرویس خوانده می‌شود.
    """
    from ai_agent import fetch_models
    provider = (provider or "").strip()
    if not provider:
        return {"ok": False, "models": [], "message": "نام سرویس خالی است"}
    try:
        models = await fetch_models(settings().get("ai", {}), provider)
        return {"ok": True, "models": models,
                "message": f"{len(models)} مدل زنده از سرویس آمد"}
    except Exception as e:
        return {"ok": False, "models": [], "message": str(e)}

@app.post("/api/ai/test")
async def ai_test(body: Dict[str, Any]):
    try:
        return await AGENTS.test((body.get("provider") or "").strip())
    except Exception as e:
        return {"ok": False, "message": str(e)}

@app.post("/api/ai/chat")
async def ai_chat(body: Dict[str, Any]):
    messages = [{"role": m.get("role") or "user", "content": str(m.get("content") or "")}
                for m in (body.get("messages") or []) if m.get("content")][-14:]
    if not messages:
        raise HTTPException(400, "پیامی برای ارسال نیست")
    try:
        return await AGENTS.chat((body.get("provider") or "").strip(),
                                 (body.get("model") or "").strip(), messages)
    except Exception as e:
        return {"ok": False, "reply": "", "message": str(e)}

@app.get("/api/ai/missions")
async def ai_missions():
    return {"missions": AGENTS.list_missions()}

@app.post("/api/ai/missions")
async def ai_create_mission(body: Dict[str, Any]):
    instruction = (body.get("instruction") or "").strip()
    if not instruction:
        raise HTTPException(400, "متن ماموریت خالی است")
    try:
        m = await AGENTS.create_mission(instruction, body.get("provider"),
                                        body.get("model"), body.get("autonomy"))
        return {"ok": True, "mission": AGENTS.summarize(m)}
    except Exception as e:
        return {"ok": False, "message": str(e)}

@app.get("/api/ai/missions/{mid}")
async def ai_mission_detail(mid: str):
    m = AGENTS.store.get(mid)
    if not m:
        raise HTTPException(404, "ماموریت پیدا نشد")
    return {"mission": AGENTS.summarize(m)}

@app.post("/api/ai/missions/{mid}/control")
async def ai_mission_control(mid: str, body: Dict[str, Any]):
    try:
        return await AGENTS.control(mid, (body.get("cmd") or "").strip())
    except Exception as e:
        return {"ok": False, "message": str(e)}

# ----- ۲.۴.۰ — چاپخانهٔ رسانه (عکس/ویدیو) و پاسخ‌گوی دایرکت
@app.get("/api/ai/image-providers")
async def ai_image_catalog():
    ai = settings().get("ai", {})
    keys = ai.get("api_keys") or {}
    providers = []
    for pid, p in ai_media.IMAGE_PROVIDERS.items():
        providers.append({
            "id": pid, "name": p["name"], "note": p["note"],
            "has_key": (not p.get("key_field")) or bool(keys.get(p["key_field"])),
            "models": p["models"],
        })
    return {"providers": providers, "sizes": ai_media.SIZES}

@app.get("/api/ai/voices")
async def ai_voices():
    return {"voices": ai_media.VOICES, "aspects": ai_media.ASPECTS,
            "video_defaults": settings().get("ai", {}).get("video", {})}

@app.post("/api/ai/image")
async def ai_image(body: Dict[str, Any]):
    prompt = (body.get("prompt") or "").strip()
    if not prompt:
        raise HTTPException(400, "توضیح عکس (پرامپت) خالی است")
    count = max(1, min(4, int(body.get("count") or 1)))
    size = (body.get("size") or "square").strip()
    ai = settings().get("ai", {})
    img_cfg = ai.get("image") or {}
    provider = (body.get("provider") or "").strip() or img_cfg.get("provider", "zai")
    model = (body.get("model") or "").strip() or img_cfg.get("model", "")

    async def _factory(job: Dict[str, Any]) -> None:
        for i in range(count):
            await _job_update(job, 5 + int(90 * i / count), f"🎨 ساخت عکس {i + 1} از {count} …")
            res = await ai_media.generate_image(ai, prompt, provider=provider, model=model, size_key=size)
            job["results"].append({"file": res["file"], "url": res["url"]})

    job = _spawn_media_job("image", prompt[:60], _factory)
    # پیش‌فرض‌ها را ذخیره کنیم تا دفعهٔ بعد همان تنظیمات باشد
    ai.setdefault("image", {})["provider"] = provider
    ai["image"]["model"] = model
    st = settings(); st["ai"] = ai; save_json(F_SETTINGS, st)
    return {"ok": True, "job": _job_public(job)}

@app.post("/api/ai/video")
async def ai_video(body: Dict[str, Any]):
    topic = (body.get("topic") or "").strip()
    if not topic:
        raise HTTPException(400, "موضوع ویدیو خالی است")
    ai = settings().get("ai", {})
    vid = ai.get("video") or {}
    voice = (body.get("voice") or "").strip() or vid.get("voice", "fa-IR-FaridNeural")
    aspect = (body.get("aspect") or "").strip() or vid.get("aspect", "9:16")
    seconds = max(15, min(180, int(body.get("seconds") or vid.get("seconds", 45))))
    material = (body.get("material") or "").strip() or vid.get("material", "ai")
    motion = (body.get("motion") or "").strip() or vid.get("motion", "zoom")

    async def _factory(job: Dict[str, Any]) -> None:
        res = await ai_media.generate_video(
            llm_json, ai, topic=topic, provider=ai.get("provider", "zai"),
            model=ai.get("model") or "glm-4.6", voice=voice, aspect=aspect,
            seconds=seconds, material=material, motion=motion,
            progress=_job_progress_cb(job))
        job["results"].append({"file": res["file"], "url": res["url"], "cover": res.get("cover"),
                                "scenes": res.get("scenes", []), "duration": res.get("duration")})

    job = _spawn_media_job("video", topic[:60], _factory)
    return {"ok": True, "job": _job_public(job)}

@app.get("/api/ai/jobs")
async def ai_jobs():
    jobs = sorted(MEDIA_JOBS.values(), key=lambda j: j["created"], reverse=True)[:20]
    return {"jobs": [_job_public(j) for j in jobs]}

@app.get("/api/ai/jobs/{jid}")
async def ai_job_detail(jid: str):
    job = MEDIA_JOBS.get(jid)
    if not job:
        raise HTTPException(404, "کار پیدا نشد")
    return {"job": _job_public(job)}

@app.get("/api/ai/dmreply")
async def dmreply_get():
    return {"config": DMAUTO.cfg(), "running": DMAUTO.running(), "stats": DMAUTO.stats()}

@app.post("/api/ai/dmreply")
async def dmreply_post(body: Dict[str, Any]):
    cfg = DMAUTO.cfg()
    for k in ("dry_run", "daily_cap", "max_per_round", "round_minutes",
              "min_reply_gap_min", "persona", "tone"):
        if k in body:
            cfg[k] = body[k]
    if isinstance(body.get("active_hours"), list) and len(body["active_hours"]) == 2:
        cfg["active_hours"] = [int(body["active_hours"][0]), int(body["active_hours"][1])]
    if isinstance(body.get("platforms"), dict):
        cfg["platforms"] = {pid: bool(body["platforms"].get(pid)) for pid in PLAT_IDS}
    DMAUTO.save_cfg(cfg)
    return {"ok": True, "config": cfg, "running": DMAUTO.running()}

@app.post("/api/ai/dmreply/start")
async def dmreply_start():
    return DMAUTO.start()

@app.post("/api/ai/dmreply/stop")
async def dmreply_stop():
    return DMAUTO.stop()

@app.post("/api/ai/dmreply/dryrun")
async def dmreply_dryrun(body: Dict[str, Any]):
    pid = (body.get("platform") or "").strip()
    if pid not in PLAT_IDS:
        raise HTTPException(400, "پلتفرم نامعتبر")
    try:
        return await DMAUTO.round(pid, dry_run=True)
    except Exception as e:
        return {"ok": False, "message": str(e)}

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    WS_CLIENTS.add(ws)
    try:
        for e in LOGS[-40:]:
            await ws.send_text(json.dumps({"type": "log", **e}, ensure_ascii=False))
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        WS_CLIENTS.discard(ws)

if __name__ == "__main__":
    # ۲.۱۴.۰ — مدلِ ذخیره‌شده اگر توسط سرویس حذف شده باشد (مثل
    # llama-3.3-70b-versatile روی Groq)، یک‌بار برای همیشه با جایگزین رسمی
    # عوض و ذخیره می‌شود تا هیچ فراخوانی روی مدل مرده گیر نکند.
    try:
        from ai_agent import DEAD_MODELS
        _st = settings()
        _ai = _st.get("ai", {})
        _prov, _model = _ai.get("provider") or "", _ai.get("model") or ""
        if _prov and _model and _model in DEAD_MODELS.get(_prov, {}):
            _new = DEAD_MODELS[_prov][_model]
            _ai["model"] = _new
            _st["ai"] = _ai
            save_json(F_SETTINGS, _st)
            log(f"♻️ مدل «{_model}» توسط {_prov} حذف شده بود — مدل جایگزین «{_new}» "
                "خودکار انتخاب و ذخیره شد (خطای 404 دیگر تکرار نمی‌شود)", "warn")
    except Exception:
        pass
    print(f"ParsAgent panel → http://127.0.0.1:{PORT}")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
