#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ParsAgent Launcher — لانچر گرافیکی نصب و اجرا
====================================================

این همان «دکمهٔ روشن/خاموش» پارس‌ایجنت است:

  ۱) بازش کن (دابل‌کلیک روی ParsAgent.bat یا اجرای python launcher.py)
  ۲) دکمهٔ «نصب پیش‌نیازها» فقط بار اول لازم است
  ۳) دکمهٔ «اجرای سرور» را بزن → سرور محلی بالا می‌آید و پنل کنترل
     به‌صورت خودکار در مرورگر باز می‌شود (http://127.0.0.1:8765)

سرور فقط روی همین سیستم در دسترس است؛ هیچ داده‌ای جایی ارسال نمی‌شود.

نسخهٔ ۲.۱۵.۰ — کنترل کامل پخش ماکرو (چهار درخواست کاربر):
  • دکمهٔ «⏹ توقف پخش» در تب ضبط ماکرو — پرچم توقف بین رخدادها و داخل
    مکث‌ها (چانک ۰.۲ ثانیه) چک می‌شود و پخش همان‌جا قطع می‌شود.
  • دراپ‌داون پخش حذف شد — پلتفرمِ هر ماکرو از لحظهٔ ضبط ذخیره و در
    ردیف خودش نشان داده می‌شود؛ پخش روی همان اجرا می‌شود (قبلاً انتخاب
    پلتفرم، وسط پُل ۳ ثانیه‌ای state، به گزینهٔ اول برمی‌گشت).
  • شروع پخش = رفتن تب مرورگر به صفحهٔ اصلی همان پلتفرم (قبلاً صفحهٔ
    خالی می‌ماند و سایت باز نمی‌شد).
  • پایان یا توقف پخش = بسته شدن خودکار پنجرهٔ مرورگرِ همان پلتفرم؛ و
    اگر کاربر خودش مرورگر را بسته باشد، ensure() خودش را درمان می‌کند
    و دیگر تا ری‌استارت خطای «Target … has been closed» نمی‌دهد.
  • (تغییرها در panel_server.py و پنل)

نسخهٔ ۲.۱۴.۰ — رفع خطای 404 مدل‌ها + تعمیر کامل ضبط/پخش ماکرو:
  • گزارش کاربر: «خطای 404 — The model llama-3.3-70b-versatile does not
    exist or you do not have access to it» — Groq این مدل‌ها را برای
    کلیدهای معمولی بسته است (فقط Enterprise، از آگوست ۲۰۲۶). سه لایهٔ
    رفع: کاتالوگ با مدل‌های رسمی جدید (GPT-OSS 120B/20B، Qwen 3.8)؛
    مدلِ مردهٔ ذخیره‌شده خودکار با جایگزین رسمی عوض می‌شود؛ دکمهٔ
    «🔄 مدل‌های زنده» در پنل — فهرست مدل‌ها مستقیم از خود سرویس.
  • ماکرو (گزارش کاربر: «ضبط و پخش درست کار نمی‌کند؛ هنگام خاموش کردن
    ضبط نشود؛ فقط در پنجرهٔ مرورگرِ شبکهٔ اجتماعی ضبط شود»):
    متنِ تایپ‌شده در جعبه‌های چت contentEditable ضبط می‌شود (قبلاً هرگز
    ضبط نمی‌شد!)، Enter ضبط می‌شود، ضبط فقط در دامنهٔ همان پلتفرم است
    (کلیک روی پنل/دکمهٔ توقف و سایت‌های دیگر نادیده گرفته می‌شود) و
    پخش مقاوم شد (تب درست + جستجو در فریم‌ها + اعلام دلیل خطا).
  • (تغییرها در ai_agent.py / ai_media.py / panel_server.py و پنل)

نسخهٔ ۲.۱۳.۰ — رفع خطای 403 سرویس‌های هوش مصنوعی در ایران:
  • گزارش کاربر: موقع «نوشتن فیلم‌نامهٔ صحنه‌ها» (چاپخانهٔ ویدیو) خطای
    «403 از سرویس هوش مصنوعی — Forbidden» از گروک/Groq و صفحهٔ HTML 403
    از جمینای می‌آمد — علت: این سرویس‌ها درخواست از IP ایران را کلاً رد
    می‌کنند و درخواست‌های پایتون به‌تنهایی از VPN مرورگر عبور نمی‌کنند.
  • فیلد جدید «پروکسی فراخوانی سرویس‌ها» (تنظیمات ← هوش مصنوعی): همهٔ
    فراخوانی‌های AI از آن عبور می‌کنند؛ خالی = خودکار (System Proxy
    ویندوز، با رفع باگ قدیمی آدرسِ https:// پروکسی لوکال).
  • دکمهٔ «🔌 تست اتصال» کنار همان فیلد + پیام خطای فارسی راه‌حل‌دار
    برای 403/401/429 + سرویس جدید: xAI Grok (گروک).
  • (تغییرها در ai_agent.py / ai_media.py / panel_server.py و پنل)

نسخهٔ ۲.۱۲.۰ — رفع کامل «سازنده و چاپ پول» (ساخت عکس/ویدیو با AI):
  • مدل درست Z.ai (glm-image — خطای 1211)، پیام فارسیِ موجودی (1113)،
    نصب خودکار کتابخانه‌های رسانه (edge-tts و…)، تلاش مجدد خودکار
    قطع‌شدن‌ها (WinError 10054) و صف/توکن Pollinations (خطای 402).
  • REQUIRED لانچر حالا ماژول‌های رسانه را هم چک می‌کند (قبلاً فقط
    ۴ ماژول قدیمی را چک می‌کرد و کاربر ارتقایافته هرگز edge-tts نصب نمی‌شد).

نسخهٔ ۲.۱۱.۰ — دو درخواست کاربر (واتساپ وب + تغییرات شفاف):
  • پلتفرم هشتم: واتساپ وب (web.whatsapp.com) — ورود با راهنمای گام‌به‌گامِ
    اسکن QR و صبر هوشمند تا ۳ دقیقه (برنامه خودش می‌فهمد کی اسکن شد)؛
    اکشن «ارسال پیام به مخاطب/گروه» با چند گیرنده و فاصلهٔ انسانی؛
    پاسخ‌گوی دایرکت و تولید محتوای AI برای واتساپ هم اضافه شد.
  • کادر «🎉 چه چیز تازه است؟» در بالای پنل — فهرست تغییرات هر نسخه
    حالا موقع باز شدن پنل دیده می‌شود (پاسخ به گزارش «۲.۱۰ همون ۲.۹ بود،
    تغییری دیدم نشد»: تغییرها بودند ولی داخل کد پنهان بودند).

نسخهٔ ۲.۱۰.۰ — سه درخواست کاربر (تغییرات در panel_server.py و پنل):
  • موتور لایک هر ۴ پلتفرم (اینستاگرام/توییتر/فیسبوک/لینکدین) از نو نوشته
    شد: چک ورود، جست‌وجوی دکمه فقط داخل همان پست، سلکتور دقیق (دیگر
    «Liked» پستِ لایک‌شده را نمی‌گیرد و لایک را برنمی‌دارد)، فارسی+انگلیسی،
    تأیید بعد از کلیک و اسکرول تدریجی.
  • اکشن «انتشار استوری» بعد از تحقیق اصلاح شد: اینستاگرام اجازهٔ استوری از
    نسخهٔ وب را نمی‌دهد → حذف شد؛ فیسبوک تنها پلتفرمی است که استوری عکس از
    وب می‌پذیرد → اکشن برایش اضافه شد (ویدیو فقط از اپ).
  • زیر هر فیلد کلید API در «تنظیمات ← هوش مصنوعی» دکمهٔ «؟» با آموزش
    گام‌به‌گام و لینک مستقیم ساختن کلید برای همان سرویس اضافه شد.

نسخهٔ ۲.۹.۰ — تعمیر دو باگ گزارش‌شده (تغییرات در panel_server.py و پنل):
  • «گروه ۴ — فعال برای کدام پلتفرم‌ها؟» در تنظیمات کار نمی‌کرد: کلیک روی
    چیپ‌ها دوبار تاگل می‌شد (رفتار پیش‌فرض <label> + کد دستی) و همیشه به
    حالت اول برمی‌گشت — با preventDefault رفع شد.
  • «فیلد ورود دیده نشد» روی اینستاگرام با اینکه فرم واقعاً باز بود:
    همهٔ نتایجِ هر سلکتور چک می‌شوند (نه فقط اولی — نسخهٔ مخفی فیلد،
    نسخهٔ مرئی را بلاک می‌کرد)، سلکتورهای فارسی (چون زبان مرورگر fa-IR
    است و سایت‌ها لیبل فارسی می‌دهند) و «اولین فیلد متنی مرئی داخل فرم»
    به‌عنوان آخرین راه اضافه شد؛ اگر باز هم نشد، صفات فیلدهای صفحه
    در تب «لاگ‌ها» ثبت می‌شود.

نسخهٔ ۲.۸.۰ — نصب هوشمند روی سیستم خام:
  • اگر لانچر با پایتون free-threaded (فایلی مثل python3.13t) باز شده
    باشد، خودش پایتونِ استانداردِ سیستم را پیدا می‌کند و با آن
    بازگشایی می‌شود — دیگر هیچ تلاش کامپایل Rust/C++ (خطای maturin /
    link.exe / «Microsoft Visual C++ 14.0 or greater is required») پیش
    نمی‌آید؛ چون pip فقط wheel آماده نصب می‌کند.
  • اگر سیستم هیچ پایتون استانداردی نداشت: دکمهٔ «🐍 پایتون استاندارد»
    (یا  python launcher.py --install-python) نسخهٔ ۳.۱۲ را از python.org
    دانلود و خاموش نصب می‌کند (~۲۶ مگابایت، بدون نیاز به ادمین) و بعد
    لانچر خودش با پایتون جدید ادامه می‌دهد.
  • نصب اینترنتی حالا فقط از wheel آماده انجام می‌شود (--only-binary)
    و اگر ایندکس پیش‌فرض جواب نداد، خودکار با آینه‌های جایگزین
    (Tsinghua / Aliyun — بدون فیلترشکن) دوباره تلاش می‌کند.
  • ParsAgent.bat حالا اول از py launcher استفاده می‌کند که هرگز
    نسخهٔ t (free-threaded) را انتخاب نمی‌کند.

نسخهٔ ۲.۷.۰ — مرورگر، پروکسی و ورود خودکار:
  • پنل: خطاهای شبکه (ERR_CONNECTION_CLOSED و…) با راهنمای فارسی پروکسی/VPN;
    پروکسی سیستم ویندوز (v2rayN و مثل آن) خودکار روی مرورگر اعمال می‌شود.
  • پنل: زنجیرهٔ مرورگر Edge → Chrome → Chromium (نصب خودکار با آینه) + Firefox;
    ورود خودکار همهٔ ۷ پلتفرم اصلی از نو (بنر کوکی، فلو X، تشخیص لاگین‌شده، OTP) — واتساپ (۲.۱۱.۰) با اسکن QR.
  • تغییر آن نسخه فقط در panel_server.py و static/index.html بود.

نسخهٔ ۲.۵.۰ — نصب آفلاین بدون اینترنت (همه‌چیز داخل همین فایل):
  • «💾 ساخت بستهٔ آفلاین» → همهٔ پیش‌نیازها به‌صورت wheel آماده +
    (اختیاری) مرورگر کرومیوم، داخل پوشهٔ پروژه در offline_bundle/
    ذخیره می‌شوند. بعد کل پوشهٔ پروژه را هرجا ببرید، اینترنت نمی‌خواهد.
  • «📀 نصب آفلاین» → روی هر سیستمِ بدون اینترنت، نصب کامل فقط از
    روی همان پوشه انجام می‌شود — بدون حتی یک بایت دانلود.
  • ناسازگاری‌ها (نسخهٔ پایتون، ۳۲/۶۴ بیتی، free-threaded مثل cp313t،
    فضای دیسک) قبل از نصب با پیام فارسی واضح اعلام می‌شوند، نه با
    خطای عجیب کامپایلر Rust.
  • حالت کنسلی برای حرفه‌ای‌ها:
        python launcher.py --build-bundle [--no-browsers]
        python launcher.py --install-offline
        python launcher.py --install-python

این فایل فقط از کتابخانهٔ استاندارد پایتون استفاده می‌کند؛ پس حتی روی
سیستم کاملاً خام (بدون هیچ pip install) بالا می‌آید و می‌تواند خودش را
با بستهٔ آفلاین تعمیر کند.
"""

from __future__ import annotations

import importlib.util
import json
import os
import platform
import queue
import re
import shutil
import subprocess
import sys
import sysconfig
import tempfile
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path
from tkinter import BOTH, BOTTOM, END, LEFT, RIGHT, X, BooleanVar, messagebox, scrolledtext
import tkinter as tk

BASE = Path(__file__).resolve().parent
HOST, PORT = "127.0.0.1", 8765
PANEL_URL = f"http://{HOST}:{PORT}"
HEALTH_URL = f"{PANEL_URL}/api/ready"

APP_VERSION = "2.15.0"

# ── بستهٔ آفلاین ────────────────────────────────────────────────────
BUNDLE_DIR = BASE / "offline_bundle"
WHEELS_DIR = BUNDLE_DIR / "wheels"
PW_MIRROR = "https://cdn.npmmirror.com/binaries/playwright"

# ── نصب هوشمند (۲.۸.۰) ─────────────────────────────────────────────
# پایتون استانداردی که در نبودِ هیچ پایتونِ سازگاری، خودکار نصب می‌شود.
# (۳.۱۲ = بیشترین پشتیبانی wheel در همهٔ پکیج‌های پروژه)
PY_STD_VERSION = "3.12.10"
PY_STD_URL = f"https://www.python.org/ftp/python/{PY_STD_VERSION}/python-{PY_STD_VERSION}-amd64.exe"

# زنجیرهٔ ایندکس‌های pip: اول پیش‌فرض PyPI؛ اگر نشد آینه‌های چین
# (در ایران بدون فیلترشکن هم مستقیم باز هستند و سریع‌اند).
PIP_MIRRORS = [
    None,  # ایندکس پیش‌فرض pypi.org
    "https://pypi.tuna.tsinghua.edu.cn/simple",
    "https://mirrors.aliyun.com/pypi/simple/",
]

# ماژول‌هایی که سرور پنل لازم دارد (نامِ ماژول ≠ نامِ پکیج pip)
# ۲.۱۲.۰ — ماژول‌های چاپخانهٔ رسانه (edge-tts/Pillow/…) هم اضافه شدند؛
# قبلاً فقط ۴ مورد چک می‌شد و کاربرِ ارتقایافته از نسخهٔ قدیمی، هرگز
# edge-tts را نصب نمی‌کرد ← خطای «کتابخانهٔ edge-tts نصب نیست».
REQUIRED = {
    "fastapi": "سرور وب پنل",
    "uvicorn": "اجرای سرور",
    "multipart": "آپلود فایل (پکیج: python-multipart)",
    "playwright": "اتوماسیون مرورگر",
    # ── چاپخانهٔ رسانه (ساخت عکس/ویدیو با AI — از ۲.۴.۰ در requirements بود ولی چک نمی‌شد)
    "edge_tts": "گویندگی فارسی ویدیو (پکیج: edge-tts)",
    "PIL": "رندر زیرنویس روی ویدیو (پکیج: Pillow)",
    "arabic_reshaper": "رسم‌الخط فارسی زیرنویس (پکیج: arabic-reshaper)",
    "bidi": "جهت راست‌به‌چپ متن (پکیج: python-bidi)",
    "imageio_ffmpeg": "ترکیب ویدیو (پکیج: imageio-ffmpeg)",
}

NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

# ── رفع باگ گیرکردن ──────────────────────────────────────────────
# در ویندوز، urllib از پروکسیِ سیستمی (VPN و…) پیروی می‌کند و درخواستِ
# 127.0.0.1 می‌تواند داخل پروکسی گیر کند و هرگز به سرور محلی نرسد.
# این اوپنر بدون هیچ پروکسی، مستقیم به سرور محلی وصل می‌شود:
_DIRECT = urllib.request.build_opener(urllib.request.ProxyHandler({}))


COLORS = {
    "bg": "#0b1220", "panel": "#111a2c", "card": "#16213a",
    "line": "#243356", "fg": "#dbe4f0", "muted": "#8fa3c0",
    "acc": "#10b981", "acc2": "#34d399", "warn": "#f59e0b", "err": "#f43f5e",
    "sky": "#38bdf8", "log_bg": "#060b16",
}
TAG_COLORS = {
    "ts": "#475569", "srv": "#7dd3fc", "pip": "#c4b5fd", "ok": "#34d399",
    "warn": "#fbbf24", "err": "#fb7185", "info": "#cbd5e1",
}


# ══════════════════════════════════════════════════════════════════ #
#  نصب هوشمند (۲.۸.۰) — تشخیص/تعویض/نصب پایتونِ استاندارد
# ══════════════════════════════════════════════════════════════════ #

def _console_log(kind: str, msg: str):
    print(f"[{kind}] {msg}", flush=True)


def _cprint(msg: str):
    """چاپ امن در کنسول — وقتی خروجی استاندارد نیست (pythonw) بی‌صدا رد می‌شود."""
    try:
        if sys.stdout:
            print(msg, flush=True)
    except Exception:
        pass


# کد یک‌خطی که داخل مفسرِ کاندید اجرا می‌شود تا نسخه و نوعش مشخص شود
_PROBE_CODE = (
    "import sys,sysconfig,json;"
    "print(json.dumps({'v':list(sys.version_info[:3]),"
    "'gil':int(sysconfig.get_config_var('Py_GIL_DISABLED') or 0),"
    "'soabi':sysconfig.get_config_var('SOABI') or ''}))"
)

# مسیرهای ویندوزیِ فایل exe داخل خروجی‌های py -0p و where
_WIN_EXE_RE = re.compile(r"[A-Za-z]:\\[^\s\"'*<>|?]+?\.exe", re.IGNORECASE)


def _py_probe(exe: str) -> dict | None:
    """اطلاعات یک مفسر پایتون: نسخه و اینکه free-threaded است یا نه.

    None یعنی این exe پایتونِ قابل استفاده نیست (خراب، Store stub و…).
    """
    try:
        out = subprocess.run([exe, "-c", _PROBE_CODE], capture_output=True,
                             text=True, timeout=25, creationflags=NO_WINDOW)
        if out.returncode != 0:
            return None
        data = json.loads(out.stdout.strip().splitlines()[-1])
        soabi = data.get("soabi") or ""
        return {
            "v": tuple(int(x) for x in data.get("v", (0, 0, 0))),
            "ft": bool(data.get("gil")) or soabi.split("-")[0].endswith("t"),
        }
    except Exception:
        return None


def _add_uniq(lst: list, exe: str) -> None:
    try:
        p = str(Path(exe))
    except Exception:
        return
    if p and p.lower() not in [x.lower() for x in lst]:
        lst.append(p)


def _candidate_interpreters() -> list:
    """فهرست مفسرهای پایتونِ احتمالی این سیستم."""
    exes: list = []
    # ۱) کنار مفسر فعلی — python3.13t.exe همیشه همزدهٔ python.exe استاندارد
    #    در همان پوشه نصب می‌شود؛ اگر باشد این سریع‌ترین راه است.
    try:
        cur_dir = Path(sys.executable).resolve().parent
        for name in ("python.exe", "python3.exe"):
            if (cur_dir / name).is_file():
                _add_uniq(exes, str(cur_dir / name))
    except Exception:
        pass
    # ۲) py launcher (خروجیِ py -0p مسیر همهٔ نسخه‌ها را دارد)
    try:
        out = subprocess.run(["py", "-0p"], capture_output=True, text=True,
                             timeout=20, creationflags=NO_WINDOW)
        for m in _WIN_EXE_RE.findall(out.stdout or ""):
            if "windowsapps" not in m.lower():
                _add_uniq(exes, m)
    except Exception:
        pass
    # ۳) همهٔ pythonهای روی PATH
    if os.name == "nt":
        try:
            out = subprocess.run(["where", "python"], capture_output=True,
                                 text=True, timeout=15, creationflags=NO_WINDOW)
            for line in (out.stdout or "").splitlines():
                line = line.strip().strip('"')
                if line.lower().endswith(".exe") and "windowsapps" not in line.lower():
                    _add_uniq(exes, line)
        except Exception:
            pass
    else:
        for tool in ("python3", "python"):
            w = shutil.which(tool)
            if w:
                _add_uniq(exes, w)
    # ۴) مسیرهای نصب رایج ویندوز
    roots = []
    la = os.environ.get("LOCALAPPDATA")
    if la:
        roots.append(Path(la) / "Programs" / "Python")
    for var in ("ProgramFiles", "ProgramFiles(x86)"):
        v = os.environ.get(var)
        if v:
            roots.append(Path(v) / "Python")
    for root in roots:
        try:
            for sub in root.glob("Python3*"):
                exe = sub / "python.exe"
                if exe.is_file():
                    _add_uniq(exes, str(exe))
        except Exception:
            pass
    return exes


def find_standard_python() -> str | None:
    """بهترین پایتونِ استاندارد (غیر free-threaded) سیستم — یا None.

    ترجیح: بالاترین نسخهٔ ۳.۱۰ تا ۳.۱۳ (بیشترین پشتیبانی wheel)؛
    اگر نبود، هر پایتون استانداردِ بالاتر از ۳.۱۰.
    """
    best_safe, v_safe = None, ()
    best_any, v_any = None, ()
    for exe in _candidate_interpreters():
        info = _py_probe(exe)
        if not info or info["ft"]:
            continue
        v = info["v"]
        if v < (3, 10, 0):
            continue
        if v > v_any:
            best_any, v_any = exe, v
        if (3, 10, 0) <= v <= (3, 13, 999):
            if v > v_safe:
                best_safe, v_safe = exe, v
    return best_safe or best_any


def _reexec(exe: str, args: list) -> None:
    """بازگشایی همین لانچر با مفسر استاندارد — پروسهٔ فعلی جایگزین می‌شود."""
    os.environ["PARSAGENT_SWITCHED"] = "1"   # جلوگیری از حلقهٔ تکرار
    os.execv(exe, [exe, str(BASE / "launcher.py"), *args])


def _download(url: str, dest: Path, log=_console_log) -> None:
    """دانلود فایل با پیشرفت؛ اول با پروکسی سیستم (VPN)، بعد مستقیم."""
    last_err = None
    for opener in (urllib.request.build_opener(), _DIRECT):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ParsAgent"})
            with opener.open(req, timeout=120) as r, open(dest, "wb") as f:
                total = int(r.headers.get("Content-Length") or 0)
                got = 0
                while True:
                    chunk = r.read(4 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
                    got += len(chunk)
                    if total:
                        log("info", f"دانلود… {got * 100 // total}٪ "
                                    f"({_human(got)} از {_human(total)})")
                    else:
                        log("info", f"دانلود… {_human(got)}")
            if dest.stat().st_size < 5_000_000:
                raise RuntimeError("فایل ناقص دانلود شد")
            return
        except Exception as exc:
            last_err = exc
            try:
                dest.unlink()
            except Exception:
                pass
    raise RuntimeError(f"دانلود ناموفق بود: {last_err}")


def install_standard_python(log=_console_log) -> str:
    """دانلود و نصبِ خاموش پایتون استاندارد — مسیر مفسرِ جدید را برمی‌گرداند.

    اگر از قبل پایتون استانداردی روی سیستم باشد، فقط همان مسیر را
    برمی‌گرداند (هیچ چیزی دانلود نمی‌شود).
    """
    existing = find_standard_python()
    if existing:
        log("ok", f"پایتون استاندارد از قبل موجود است: {existing}")
        return existing
    if os.name != "nt":
        raise RuntimeError("نصب خودکار پایتون فقط روی ویندوز ممکن است — "
                           "نسخهٔ استاندارد را خودتان نصب کنید.")
    arch = os.environ.get("PROCESSOR_ARCHITEW6432",
                          platform.machine() or "").upper()
    if not arch.endswith("64"):
        raise RuntimeError("ویندوز این سیستم ۳۲بیتی است و نصب خودکار "
                           "پشتیبانی نمی‌شود — پایتون استاندارد را دستی از "
                           "python.org نصب کنید (تیک Add to PATH).")
    dest = Path(tempfile.gettempdir()) / f"parsagent-python-{PY_STD_VERSION}-amd64.exe"
    log("info", f"دانلود نصب‌کنندهٔ پایتون {PY_STD_VERSION} از python.org "
                f"(~۲۶ مگابایت)…")
    _download(PY_STD_URL, dest, log)
    log("info", "نصب خاموش پایتون استاندارد (۱ تا ۳ دقیقه)…")
    rc = subprocess.run(
        [str(dest), "/quiet", "InstallAllUsers=0", "PrependPath=1",
         "Include_launcher=1", "Include_test=0", "Include_doc=0"],
        timeout=900, creationflags=NO_WINDOW).returncode
    if rc not in (0, 3010):
        raise RuntimeError(f"نصب پایتون ناموفق بود (کد {rc}).")
    exe = find_standard_python()
    if not exe:
        # مسیر پیش‌فرضِ نصبِ per-user را هم مستقیم چک می‌کنیم
        la = os.environ.get("LOCALAPPDATA")
        if la:
            folder = f"Python{PY_STD_VERSION.rsplit('.', 1)[0].replace('.', '')}"
            guess = Path(la) / "Programs" / "Python" / folder / "python.exe"
            if guess.is_file() and _py_probe(str(guess)):
                exe = str(guess)
    if not exe:
        raise RuntimeError("نصب انجام شد ولی پایتون استاندارد پیدا نشد — "
                           "لانچر را یک بار ببند و دوباره باز کن.")
    log("ok", f"پایتون استاندارد نصب شد: {exe}")
    return exe


# ══════════════════════════════════════════════════════════════════ #
#  هستهٔ آفلاین (۲.۵.۰) — ساخت بسته و نصب بدون اینترنت
# ══════════════════════════════════════════════════════════════════ #

def _findable(name: str) -> bool:
    """آیا ماژول قابل ایمپورت است؟ (مقاوم به ماژول‌های بی-spec)"""
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return name in sys.modules


def check_missing() -> list:
    return [m for m in REQUIRED if not _findable(m)]


def _human(n) -> str:
    x = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if x < 1024:
            return f"{x:.1f} {unit}"
        x /= 1024
    return f"{x:.1f} PB"


def _dir_size(p: Path) -> int:
    if not p.exists():
        return 0
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def _python_tag() -> str:
    return f"cp{sys.version_info[0]}{sys.version_info[1]}"


def _is_free_threaded() -> bool:
    """تشخیص پایتون free-threaded (مثل cp313t) که با wheelهای معمولی
    سازگار نیست — همان خطای عجیب «کامپایل Rust» که دیدید."""
    soabi = sysconfig.get_config_var("SOABI") or ""
    if soabi.split("-")[0].endswith("t"):
        return True
    try:
        return bool(int(sysconfig.get_config_var("Py_GIL_DISABLED") or 0))
    except Exception:
        return False


def _browsers_cache() -> Path:
    """محل کش مرورگرهای Playwright روی این سیستم."""
    env = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if env:
        return Path(env)
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "ms-playwright"
    return Path.home() / ".cache" / "ms-playwright"


def bundle_available() -> bool:
    return WHEELS_DIR.is_dir() and (BUNDLE_DIR / "requirements.txt").is_file()


def read_bundle_info():
    p = BUNDLE_DIR / "bundle_info.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def compat_problems(info) -> list:
    """لیست ناسازگاری‌های سیستم فعلی با بستهٔ ساخته‌شده (خالی = مشکلی نیست)."""
    probs = []
    if _is_free_threaded():
        probs.append("پایتون این سیستم از نوع free-threaded است (شناسه‌ای مثل cp313t). "
                     "wheelهای این بسته با آن سازگار نیستند؛ با دکمهٔ «🐍 پایتون "
                     "استاندارد» لانچر (یا  python launcher.py --install-python) "
                     "نسخهٔ استاندارد را نصب/انتخاب کنید تا نصب ادامه یابد.")
    if info:
        if info.get("platform") and info["platform"] != platform.system():
            probs.append(f"بسته برای {info['platform']} ساخته شده ولی این سیستم "
                        f"{platform.system()} است.")
        mine = _python_tag()
        if info.get("python_tag") and mine != info["python_tag"]:
            probs.append(f"پایتون این سیستم {mine} است ولی بسته برای "
                        f"{info['python_tag']} ساخته شده — همان نسخهٔ پایتون را نصب کنید.")
        bits = 64 if platform.architecture()[0].startswith("64") else 32
        if info.get("bitness") and bits != info["bitness"]:
            probs.append(f"پایتون این سیستم {bits} بیتی است ولی بسته {info['bitness']} بیتی "
                         "ساخته شده است.")
    return probs


def disk_msg() -> str | None:
    """اگر فضای دیسک برای نصبِ بسته کافی نباشد، پیام فارسی برمی‌گرداند."""
    if not BUNDLE_DIR.is_dir():
        return None
    need = int(_dir_size(BUNDLE_DIR) * 1.15) + 50 * 1024 * 1024
    free = shutil.disk_usage(BASE).free
    if free < need:
        return (f"فضای خالی درایو کافی نیست — حجم بسته {_human(_dir_size(BUNDLE_DIR))} "
                f"است ولی فقط {_human(free)} آزاد دارید (خطای os error 112). "
                "اول فضا آزاد کنید.")
    return None


def _run_stream(cmd, log=_console_log, env=None) -> int:
    """اجرای فرمان با استریم زندهٔ خروجی در لاگ؛ کد خروج را برمی‌گرداند."""
    try:
        p = subprocess.Popen(
            [str(c) for c in cmd], cwd=str(BASE),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
            env=env or os.environ, creationflags=NO_WINDOW)
    except Exception as exc:
        log("err", f"اجرای فرمان ناموفق بود: {exc}")
        return 1
    for line in p.stdout:
        log("pip", line.rstrip())
    return p.wait()


def _has_chromium() -> bool:
    cache = _browsers_cache()
    return cache.is_dir() and any(cache.glob("chromium-*"))


def build_offline_bundle(include_browsers: bool = True, log=_console_log) -> str:
    """ساخت بستهٔ آفلاین داخل پروژه. خلاصه را برمی‌گرداند؛ در خطا RuntimeError."""
    req = BASE / "requirements.txt"
    if not req.is_file():
        raise RuntimeError("فایل requirements.txt کنار launcher.py پیدا نشد.")

    need_gb = 2.5 if include_browsers else 1.2
    free_gb = shutil.disk_usage(BASE).free / 1024 ** 3
    if free_gb < need_gb:
        raise RuntimeError(f"فضای خالی کافی نیست — حداقل {need_gb:.1f} گیگابایت لازم است "
                           f"ولی الان {free_gb:.1f} گیگابایت آزاد است (خطای os error 112).")

    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    WHEELS_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(req, BUNDLE_DIR / "requirements.txt")

    # --- ۱) دانلود همهٔ پیش‌نیازها به‌صورت wheel آماده ---------------
    log("info", "۱) دانلود پیش‌نیازها به‌صورت wheel آماده (چند دقیقه)…")
    base = [sys.executable, "-m", "pip", "download", "-r", str(req),
            "-d", str(WHEELS_DIR), "--progress-bar", "off"]
    rc = _run_stream(base + ["--only-binary=:all:"], log=log)
    if rc != 0:
        log("warn", "دانلود با محدودیت wheel-only نشد؛ تلاش مجدد بدون محدودیت…")
        rc = _run_stream(base, log=log)
        if rc != 0:
            raise RuntimeError("دانلود پکیج‌ها از اینترنت ناموفق بود.")
        log("warn", "بعضی پکیج‌ها سورس‌اند و ممکن است روی سیستم مقصد کامپایلر بخواهند.")
    # خود pip هم داخل بسته باشد
    _run_stream([sys.executable, "-m", "pip", "download", "pip",
                 "-d", str(WHEELS_DIR), "--only-binary=:all:",
                 "--progress-bar", "off"], log=log)

    # --- ۲) مرورگر کرومیوم (اختیاری) --------------------------------
    if include_browsers:
        log("info", "۲) آماده‌سازی مرورگر کرومیوم…")
        if not _findable("playwright"):
            log("info", "نصب موقت playwright از روی wheelهای تازه دانلودشده…")
            rc = _run_stream([sys.executable, "-m", "pip", "install", "--no-index",
                              "--find-links", str(WHEELS_DIR), "playwright",
                              "--progress-bar", "off"], log=log)
            if rc != 0:
                raise RuntimeError("نصب playwright از روی wheelها ناموفق بود.")
        if not _has_chromium():
            log("warn", "کرومیوم نصب نیست؛ دانلود از آینهٔ npmmirror (بدون فیلترشکن)…")
            env = {**os.environ, "PLAYWRIGHT_DOWNLOAD_HOST": PW_MIRROR}
            rc = _run_stream([sys.executable, "-m", "playwright", "install", "chromium"],
                             log=log, env=env)
            if rc != 0:
                raise RuntimeError("دانلود کرومیوم ناموفق بود.")
        src = _browsers_cache()
        if not src.is_dir():
            raise RuntimeError(f"پوشهٔ مرورگرهای Playwright پیدا نشد: {src}")
        dst = BUNDLE_DIR / "ms-playwright"
        dst.mkdir(parents=True, exist_ok=True)
        kept = [d.name for d in src.iterdir()
                if d.is_dir() and (d.name.startswith("chromium") or d.name.startswith("ffmpeg"))]
        if not kept:
            raise RuntimeError("در کش Playwright هیچ مرورگری برای کپی پیدا نشد.")
        for name in kept:
            shutil.copytree(src / name, dst / name, dirs_exist_ok=True)
        log("ok", "مرورگرها داخل بسته کپی شدند: " + "، ".join(kept))
    else:
        log("warn", "مرورگر داخل بسته نشد (حالت سبک) — نصب آفلاین بعداً از "
                   "Edge/Chrome خود ویندوز استفاده می‌کند.")

    # --- ۳) شناسنامهٔ بسته ------------------------------------------
    info = {
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "python_tag": _python_tag(),
        "soabi": sysconfig.get_config_var("SOABI"),
        "bitness": 64 if platform.architecture()[0].startswith("64") else 32,
        "with_browsers": include_browsers,
        "created": time.strftime("%Y-%m-%d %H:%M"),
        "app_version": APP_VERSION,
    }
    (BUNDLE_DIR / "bundle_info.json").write_text(
        json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")

    n_whl = len(list(WHEELS_DIR.glob("*.whl")))
    w = _dir_size(WHEELS_DIR)
    b = _dir_size(BUNDLE_DIR / "ms-playwright")
    return (f"تعداد wheelها: {n_whl}\n"
            f"حجم wheelها: {_human(w)}\n"
            + (f"حجم مرورگرها: {_human(b)}\n" if b else "")
            + f"حجم کل بسته: {_human(w + b)}\n"
            f"محل بسته: {BUNDLE_DIR}")


def install_from_bundle(log=_console_log):
    """نصب کامل از بستهٔ آفلاین — بدون حتی یک بایت اینترنت.
    برمی‌گرداند: (موفق؟، لیست ماژول‌های همچنان نصب‌نشده)"""
    log("info", "نصب آفلاین از پوشهٔ offline_bundle (بدون اینترنت)…")
    rc = _run_stream([sys.executable, "-m", "pip", "install",
                      "--no-index", "--find-links", str(WHEELS_DIR),
                      "-r", str(BUNDLE_DIR / "requirements.txt"),
                      "--progress-bar", "off"], log=log)
    if rc != 0:
        log("err", "نصب پکیج‌ها از بسته ناموفق بود (لاگ بالا را ببینید).")
        return False, check_missing()

    src = BUNDLE_DIR / "ms-playwright"
    if src.is_dir():
        dst = _browsers_cache()
        dst.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            if item.is_dir():
                shutil.copytree(item, dst / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dst / item.name)
        log("ok", f"مرورگرها در محل Playwright کپی شدند: {dst}")
    else:
        log("warn", "بسته شامل مرورگر نیست — از Edge/Chrome خود ویندوز استفاده می‌شود.")

    missing = check_missing()
    for m in REQUIRED:
        log("ok" if m not in missing else "err",
            f"ماژول {m}: " + ("نصب شد ✓" if m not in missing else "هنوز نصب نیست ✗"))
    return (not missing), missing


def server_up(timeout: float = 1.0) -> bool:
    """بررسی سلامت سرور — همیشه مستقیم و بدون پروکسی"""
    try:
        with _DIRECT.open(HEALTH_URL, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False


class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ParsAgent — لانچر")
        self.geometry("800x640")
        self.minsize(700, 560)
        self.configure(bg=COLORS["bg"])

        self.proc: subprocess.Popen | None = None
        self.installing = False
        self.stop_flag = False
        self.server_ready = False
        # صف امن نخ→رابط: در برخی سیستم‌ها (ویندوز/لینوکس) فراخوانی after از
        # نخِ دیگر بی‌صدا نادیده گرفته می‌شود و همین باعث «گیرکردن» لانچر
        # می‌شد؛ همهٔ به‌روزرسانی‌های UI از این صف در نخ اصلی اجرا می‌شوند.
        self.ui_q: "queue.Queue" = queue.Queue()

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(60, self._pump)
        self.after(200, self.on_start)

    # ------------------------------------------------------------------ #
    # پل امن نخ→رابط کاربری
    # ------------------------------------------------------------------ #
    def _pump(self):
        """در نخ اصلی اجرا می‌شود و کارهای صف‌شدهٔ نخ‌های دیگر را انجام می‌دهد"""
        try:
            while True:
                fn = self.ui_q.get_nowait()
                try:
                    fn()
                except Exception:
                    pass
        except queue.Empty:
            pass
        self.after(60, self._pump)

    def post(self, fn):
        """اجرای امن یک تابع در نخ اصلی — از هر نخی قابل فراخوانی است"""
        self.ui_q.put(fn)

    # ------------------------------------------------------------------ #
    # UI
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        # --- هدر
        header = tk.Frame(self, bg="#080e1a")
        header.pack(fill=X)
        tk.Label(header, text="🤖 ParsAgent", font=("Segoe UI", 21, "bold"),
                 bg="#080e1a", fg=COLORS["acc"]).pack(anchor="e", padx=18,
                                                      pady=(14, 0))
        tk.Label(header, text="لانچر نصب و اجرای پنل کنترل — نسخهٔ ۲.۱۵.۰",
                 font=("Segoe UI", 10), bg="#080e1a",
                 fg=COLORS["muted"]).pack(anchor="e", padx=18, pady=(0, 14))

        # --- نوار وضعیت
        status_bar = tk.Frame(self, bg=COLORS["panel"])
        status_bar.pack(fill=X, padx=14, pady=(12, 6))
        self.status_dot = tk.Label(status_bar, text="●", font=("Segoe UI", 12),
                                    bg=COLORS["panel"], fg=COLORS["muted"])
        self.status_dot.pack(side=RIGHT, padx=10, pady=8)
        self.status_lbl = tk.Label(status_bar, text="در حال بررسی وضعیت…",
                                   font=("Segoe UI", 11, "bold"),
                                   bg=COLORS["panel"], fg=COLORS["fg"])
        self.status_lbl.pack(side=RIGHT)
        self.link_lbl = tk.Label(status_bar, text=PANEL_URL,
                                 font=("Segoe UI", 10, "underline"),
                                 bg=COLORS["panel"], fg=COLORS["sky"],
                                 cursor="hand2")
        self.link_lbl.pack(side=LEFT, padx=10, pady=8)
        self.link_lbl.bind("<Button-1>", lambda e: self.open_panel())

        # --- دکمه‌های اصلی
        btns = tk.Frame(self, bg=COLORS["bg"])
        btns.pack(fill=X, padx=14, pady=6)
        self.btn_run = self._big_button(btns, "🚀  اجرای سرور", self.start_server,
                                        bg=COLORS["acc"], fg="#04120c",
                                        font=("Segoe UI", 13, "bold"))
        self.btn_run.pack(side=RIGHT, fill=X, expand=True, padx=(0, 8), ipady=10)
        self.btn_panel = self._big_button(btns, "🌐  باز کردن پنل", self.open_panel,
                                          bg=COLORS["card"], fg=COLORS["fg"])
        self.btn_panel.pack(side=RIGHT, fill=X, expand=True, padx=8, ipady=10)
        self.btn_stop = self._big_button(btns, "⛔  توقف سرور", self.stop_server,
                                         bg=COLORS["card"], fg=COLORS["fg"])
        self.btn_stop.pack(side=RIGHT, fill=X, expand=True, padx=8, ipady=10)

        # --- دکمه‌های ابزار
        tools = tk.Frame(self, bg=COLORS["bg"])
        tools.pack(fill=X, padx=14, pady=(2, 4))
        self.btn_install = self._tool_button(tools, "📦  نصب پیش‌نیازها",
                                              self.install_deps,
                                              bg="#1d2c1f", fg=COLORS["acc2"])
        self.btn_install.pack(side=RIGHT, padx=(0, 8))
        self.btn_pw = self._tool_button(tools, "🧭  نصب کرومیوم (آینه)",
                                        self.install_browser,
                                        bg=COLORS["card"], fg=COLORS["fg"])
        self.btn_pw.pack(side=RIGHT, padx=8)
        self.btn_pystd = self._tool_button(tools, "🐍  پایتون استاندارد",
                                           self.install_python_clicked,
                                           bg="#1d2c1f", fg=COLORS["acc2"])
        self.btn_pystd.pack(side=RIGHT, padx=8)
        self.btn_clear = self._tool_button(tools, "🧹  پاک‌سازی لاگ",
                                           self.clear_log,
                                           bg=COLORS["card"], fg=COLORS["muted"])
        self.btn_clear.pack(side=RIGHT, padx=8)

        # --- ابزارهای آفلاین (۲.۵.۰)
        offline = tk.Frame(self, bg=COLORS["bg"])
        offline.pack(fill=X, padx=14, pady=(0, 8))
        self.var_browsers = BooleanVar(value=True)
        self.btn_bundle = self._tool_button(offline, "💾  ساخت بستهٔ آفلاین",
                                            self.build_offline,
                                            bg="#1d2c1f", fg=COLORS["acc2"])
        self.btn_bundle.pack(side=RIGHT, padx=(0, 8))
        self.btn_offinstall = self._tool_button(offline, "📀  نصب آفلاین",
                                                self.install_offline_clicked,
                                                bg=COLORS["card"], fg=COLORS["sky"])
        self.btn_offinstall.pack(side=RIGHT, padx=8)
        self.chk_browsers = tk.Checkbutton(
            offline, text="مرورگر کرومیوم داخل بسته (~۷۰۰MB)",
            variable=self.var_browsers, font=("Segoe UI", 9),
            bg=COLORS["bg"], fg=COLORS["muted"],
            selectcolor=COLORS["card"], activebackground=COLORS["bg"],
            activeforeground=COLORS["fg"], cursor="hand2")
        self.chk_browsers.pack(side=LEFT, padx=6)

        # --- جعبه لاگ
        self.txt = scrolledtext.ScrolledText(
            self, bg=COLORS["log_bg"], fg=COLORS["fg"], relief="flat",
            font=("Consolas", 9), state="disabled", wrap="word", borderwidth=0)
        self.txt.pack(fill=BOTH, expand=True, padx=14, pady=(2, 8))
        for tag, color in TAG_COLORS.items():
            self.txt.tag_configure(tag, foreground=color)

        # --- فوتر
        footer = tk.Frame(self, bg="#080e1a")
        footer.pack(fill=X, side=BOTTOM)
        tk.Label(footer,
                 text="سرور فقط روی همین سیستم (127.0.0.1) در دسترس است — "
                      "نیازی به اینترنت ندارد",
                 font=("Segoe UI", 9), bg="#080e1a",
                 fg=COLORS["muted"]).pack(side=RIGHT, padx=14, pady=8)
        self.ws_dot = tk.Label(footer, text="○ پنل: بسته", font=("Segoe UI", 9),
                               bg="#080e1a", fg=COLORS["muted"])
        self.ws_dot.pack(side=LEFT, padx=14, pady=8)

        self.set_running(False, unknown=True)

    def _big_button(self, parent, text, cmd, bg, fg, font=("Segoe UI", 11)):
        b = tk.Label(parent, text=text, bg=bg, fg=fg, font=font,
                     cursor="hand2", padx=14, pady=6)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.config(
            bg=COLORS["acc2"] if bg == COLORS["acc"] else "#1c2a4a"))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    def _tool_button(self, parent, text, cmd, bg, fg):
        b = tk.Label(parent, text=text, bg=bg, fg=fg, font=("Segoe UI", 10),
                     cursor="hand2", padx=12, pady=6)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.config(bg="#1c2a4a"))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    # ------------------------------------------------------------------ #
    # لاگ
    # ------------------------------------------------------------------ #
    def log(self, kind: str, msg: str):
        ts = time.strftime("%H:%M:%S")
        self.txt.configure(state="normal")
        self.txt.insert(END, f"[{ts}] ", "ts")
        self.txt.insert(END, (msg or "") + "\n", kind if kind in TAG_COLORS else "info")
        self.txt.see(END)
        self.txt.configure(state="disabled")

    def clear_log(self):
        self.txt.configure(state="normal")
        self.txt.delete("1.0", END)
        self.txt.configure(state="disabled")

    def _lg(self, kind: str, msg: str):
        """لاگ امن از داخل نخ‌های کاری"""
        self.post(lambda k=kind, m=msg: self.log(k, m))

    def set_status(self, text: str, color: str):
        self.status_lbl.config(text=text, fg=color)
        self.status_dot.config(fg=color)

    def set_running(self, running: bool, unknown: bool = False):
        if unknown:
            self.set_status("در حال بررسی…", COLORS["muted"])
            return
        if running:
            self.btn_run.config(fg="#3f7c66")
            self.btn_stop.config(fg=COLORS["err"])
            self.btn_panel.config(fg=COLORS["sky"])
            self.ws_dot.config(text="● پنل: روشن", fg=COLORS["acc"])
            self.set_status("سرور در حال اجرا — پنل آماده است", COLORS["acc"])
        else:
            self.btn_run.config(fg=COLORS["fg"])
            self.btn_stop.config(fg=COLORS["muted"])
            self.btn_panel.config(fg=COLORS["muted"])
            self.ws_dot.config(text="○ پنل: بسته", fg=COLORS["muted"])
            self.set_status("سرور خاموش است", COLORS["muted"])

    # ------------------------------------------------------------------ #
    # شروع
    # ------------------------------------------------------------------ #
    def on_start(self):
        self.log("info", "به لانچر پارس‌ایجنت خوش آمدی 👋")
        self.log("info", f"پوشه پروژه: {BASE}")
        if _is_free_threaded():
            # (main قبل از باز شدن GUI سعی در تعویض مفسر کرده و نشده است)
            self.log("err", "⚠ پایتونِ فعلی free-threaded است (مثل python3.13t) — "
                            "پکیج‌ها برای آن نسخهٔ آماده ندارند؛ همان خطاهای "
                            "کامپایل Rust/C++ (maturin/link.exe).")
            self.set_status("پایتون ناسازگار — نسخهٔ استاندارد لازم است",
                            COLORS["err"])
            self.after(600, self._handle_free_threaded)
            return
        missing = check_missing()
        if missing:
            names = "، ".join(
                f"{m} ({REQUIRED[m]})" for m in missing)
            self.log("warn", f"ماژول‌های نصب‌نشده: {names}")
            self.set_status(f"نیاز به نصب: {len(missing)} ماژول", COLORS["warn"])
            self.after(400, lambda: self._ask_install_smart(missing))
        else:
            self.log("ok", "همه پیش‌نیازها نصب هستند ✓")
            self.set_running(False)
            if server_up(0.6):
                self.log("ok", "سرور از قبل روشن است — پنل در دسترس است")
                self.server_ready = True
                self.set_running(True)

    def _ask_install_smart(self, missing):
        """اگر بستهٔ آفلاین کنار پروژه بود، اول نصب بدون اینترنت پیشنهاد می‌شود."""
        if bundle_available():
            if messagebox.askyesno(
                    "نصب آفلاین",
                    "برای اجرای پنل چند پکیج لازم است:\n\n"
                    + "\n".join(f"• {m} — {REQUIRED[m]}" for m in missing)
                    + "\n\nپوشهٔ بستهٔ آفلاین (offline_bundle) کنار پروژه پیدا شد.\n"
                      "نصب بدون اینترنت از همین بسته انجام شود؟"):
                self.install_offline_clicked(auto_start=True)
                return
            self.log("info", "برای نصب اینترنتی، دکمهٔ «📦 نصب پیش‌نیازها» را بزن")
            return
        self._ask_install(missing)

    def _ask_install(self, missing):
        if messagebox.askyesno(
                "نصب پیش‌نیازها",
                "برای اجرای پنل چند پکیج لازم است:\n\n"
                + "\n".join(f"• {m} — {REQUIRED[m]}" for m in missing)
                + "\n\nهم‌اکنون نصب شوند؟ (به اینترنت نیاز دارد)"):
            self.install_deps()
        else:
            self.log("warn", "بدون این ماژول‌ها سرور اجرا نمی‌شود")

    # ------------------------------------------------------------------ #
    # پایتون استاندارد (۲.۸.۰)
    # ------------------------------------------------------------------ #
    def _handle_free_threaded(self):
        """رفع خودکار پایتون free-threaded: تعویض یا نصب نسخهٔ استاندارد."""
        better = find_standard_python()
        if better:
            if messagebox.askyesno(
                    "تعویض پایتون",
                    "این لانچر با پایتون free-threaded (نسخهٔ t) باز شده که با\n"
                    "پکیج‌های پارس‌ایجنت سازگار نیست (همان خطاهای کامپایل Rust/C++).\n\n"
                    f"پایتون استاندارد روی همین سیستم پیدا شد:\n{better}\n\n"
                    "لانچر همین حالا با آن باز شود؟"):
                self.log("info", f"بازگشایی لانچر با پایتون استاندارد: {better}")
                self.stop_flag = True
                args = list(sys.argv[1:])
                self.post(lambda: _reexec(better, args))
            return
        if messagebox.askyesno(
                "پایتون ناسازگار",
                "تنها پایتونِ این سیستم نسخهٔ free-threaded است (مثل 3.13t)\n"
                "و پکیج‌های پارس‌ایجنت برای آن نسخهٔ آماده ندارند — همان\n"
                "خطاهای کامپایل Rust/C++ (maturin / link.exe) که دیدید.\n\n"
                "نسخهٔ استاندارد پایتون همین حالا دانلود و نصب شود؟\n\n"
                "• حدود ۲۶ مگابایت از python.org (فیلتر نیست)\n"
                "• نصب خاموش، بدون نیاز به ادمین\n"
                "• بعد از نصب، لانچر خودش با پایتون جدید ادامه می‌دهد"):
            self.install_python_clicked()

    def install_python_clicked(self):
        """دانلود/انتخاب پایتون استاندارد — رفع خطای free-threaded مثل cp313t."""
        if self.installing:
            messagebox.showinfo("مشغول", "یک نصب/ساخت دیگر در جریان است")
            return
        if not _is_free_threaded():
            ver = ".".join(map(str, sys.version_info[:3]))
            messagebox.showinfo(
                "پایتون سازگار است",
                "پایتونِ فعلی همین حالا استاندارد و سازگار است:\n\n"
                f"{sys.executable}\nنسخهٔ {ver} — نیازی به نصب نیست.")
            return
        if self.proc and self.proc.poll() is None:
            messagebox.showwarning("در حال اجرا",
                                   "اول سرور را متوقف کن، بعد نصب را بزن")
            return
        self.installing = True
        self.set_status("در حال نصب پایتون استاندارد…", COLORS["sky"])
        self.log("info", "شروع نصب پایتون استاندارد…")

        def work():
            try:
                exe = install_standard_python(self._lg)
                args = list(sys.argv[1:])
                self.post(lambda: self._python_installed(exe, args))
            except Exception as exc:
                self.post(lambda e=exc: self._offline_failed("نصب پایتون", e))
        threading.Thread(target=work, daemon=True).start()

    def _python_installed(self, exe: str, args: list):
        self.installing = False
        self.set_status("پایتون استاندارد آماده شد ✓", COLORS["acc"])
        self.log("ok", f"پایتون استاندارد آماده است: {exe}")
        if messagebox.askyesno(
                "پایتون آماده شد ✓",
                "پایتون استاندارد آماده است:\n\n"
                f"{exe}\n\nلانچر الان با پایتون جدید بازگشایی شود؟\n"
                "(نصب پیش‌نیازها از همان‌جا ادامه می‌یابد)"):
            self.stop_flag = True
            self.post(lambda: _reexec(exe, args))

    # ------------------------------------------------------------------ #
    # نصب (اینترنتی)
    # ------------------------------------------------------------------ #
    def _run_async(self, cmd, env=None, on_done=None, cwd=None):
        def work():
            try:
                p = subprocess.Popen(
                    cmd, cwd=str(cwd or BASE),
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace",
                    env=env or os.environ, creationflags=NO_WINDOW)
                for line in p.stdout:
                    self.post(lambda l=line: self.log("pip", l.rstrip()))
                code = p.wait()
                self.post(lambda: on_done(code == 0) if on_done else None)
            except Exception as exc:
                self.post(lambda: self.log("err", f"خطا: {exc}"))
                self.post(lambda: on_done(False) if on_done else None)
        threading.Thread(target=work, daemon=True).start()

    def install_deps(self):
        """نصب اینترنتی پیش‌نیازها — فقط از wheel آماده، با آینه‌های جایگزین.

        (۲.۸.۰) دیگر اجازهٔ کامپایل سورس (خطای maturin/Rust/link.exe و
        «Microsoft Visual C++ 14.0 or greater is required») داده نمی‌شود.
        """
        if self.installing:
            return
        if self.proc and self.proc.poll() is None:
            messagebox.showwarning("در حال اجرا",
                                   "اول سرور را متوقف کن، بعد نصب را بزن")
            return
        if _is_free_threaded():
            self._handle_free_threaded()
            return
        self.installing = True
        self.set_status("در حال نصب پیش‌نیازها…", COLORS["sky"])
        self.log("info", "شروع نصب پیش‌نیازها (ممکن است چند دقیقه طول بکشد)…")
        self.log("info", "فقط پکیج‌های آماده (wheel) نصب می‌شوند — دیگر هیچ "
                         "کامپایل Rust/C++ در کار نیست.")
        self._pip_attempt(0)

    def _pip_attempt(self, idx: int):
        """تلاش نصب با wheel-only؛ زنجیرهٔ ایندکس:
        پیش‌فرض PyPI → آینهٔ Tsinghua → آینهٔ Aliyun."""
        if idx >= len(PIP_MIRRORS):
            self._install_failed()
            return
        if idx > 0:
            self.log("info", f"تلاش مجدد با آینهٔ جایگزین {idx} …")
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt",
               "--disable-pip-version-check", "--only-binary=:all:"]
        if PIP_MIRRORS[idx]:
            cmd += ["-i", PIP_MIRRORS[idx]]
        self._run_async(cmd, env=env,
                        on_done=lambda ok, i=idx: self._pip_done(ok, i))

    def _pip_done(self, ok: bool, idx: int):
        if not check_missing():
            self._after_install(True)
            return
        self._pip_attempt(idx + 1)

    def _install_failed(self):
        self.installing = False
        missing = check_missing()
        self.set_status("نصب ناقص", COLORS["err"])
        self.log("err", "نصب این پیش‌نیازها ممکن نشد: " + "، ".join(missing))
        pyv = ".".join(map(str, sys.version_info[:3]))
        self.log("err", f"پایتون فعلی: {pyv} ({_python_tag()})")
        hints = [
            "راه‌های رفع:",
            "• هر ۳ ایندکس خودکار امتحان شد: PyPI + دو آینهٔ چین (Tsinghua/Aliyun).",
            f"• اگر نسخهٔ پایتون {pyv} خیلی جدید/قدیمی است، ۳.۱۲ یا ۳.۱۳ "
            "پیشنهاد می‌شود؛ با دکمهٔ «🐍 پایتون استاندارد» نسخهٔ سازگار نصب می‌شود.",
            "• اینترنت/فیلترینگ: اگر VPN داری، روشن کن و دوباره «نصب پیش‌نیازها» را بزن.",
            "• یا روی یک سیستم اینترنت‌دار «💾 ساخت بستهٔ آفلاین» را بساز و "
            "اینجا «📀 نصب آفلاین» کن.",
        ]
        for h in hints:
            self.log("info", h)
        messagebox.showerror(
            "نصب ناقص",
            "این ماژول‌ها نصب نشدند:\n" + "، ".join(missing)
            + "\n\n" + "\n".join(hints))

    def _after_install(self, ok: bool):
        self.installing = False
        missing = check_missing()
        if not missing:
            self.log("ok", "نصب کامل شد ✓ — حالا «اجرای سرور» را بزن")
            self.set_running(False)
            if messagebox.askyesno("نصب کامل",
                                   "همه پیش‌نیازها نصب شد ✓\n\nسرور الان اجرا شود؟"):
                self.start_server()
        else:
            self.log("err", "بعضی ماژول‌ها هنوز نصب نشده‌اند: "
                     + "، ".join(missing))
            self.set_status("نصب ناقص", COLORS["err"])

    def install_browser(self):
        """نصب کرومیوم Playwright از آینهٔ چینی (بدون فیلترشکن).

        فقط وقتی لازم است که نه Edge داشته باشی نه Chrome —
        لانچر مقاوم خودکار اول از مرورگرهای نصب‌شده استفاده می‌کند.
        """
        if messagebox.askyesno(
                "نصب کرومیوم",
                "کرومیوم باندل Playwright از آینهٔ npmmirror دانلود شود؟\n\n"
                "نکته: اگر روی ویندوزت Edge یا Chrome نصب است،\n"
                "این مرحله اصلاً لازم نیست — ایجنت خودش از همان‌ها استفاده می‌کند."):
            self.log("info", f"نصب کرومیوم از آینه: {PW_MIRROR}")
            env = {**os.environ, "PLAYWRIGHT_DOWNLOAD_HOST": PW_MIRROR,
                   "PYTHONIOENCODING": "utf-8"}
            self._run_async(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                env=env, on_done=lambda ok: self.log(
                    "ok" if ok else "err",
                    "نصب کرومیوم تمام شد ✓" if ok
                    else "نصب کرومیوم ناموفق بود — لاگ بالا را ببین"))

    # ------------------------------------------------------------------ #
    # ابزارهای آفلاین (۲.۵.۰)
    # ------------------------------------------------------------------ #
    def build_offline(self):
        if self.installing:
            messagebox.showinfo("مشغول", "یک نصب/ساخت دیگر در جریان است")
            return
        if self.proc and self.proc.poll() is None:
            messagebox.showwarning("در حال اجرا",
                                   "اول سرور را متوقف کن، بعد بسته را بساز")
            return
        include = self.var_browsers.get()
        if not messagebox.askyesno(
                "ساخت بستهٔ آفلاین",
                "همهٔ پیش‌نیازها به‌صورت wheel آماده"
                + (" + مرورگر کرومیوم" if include else "")
                + " داخل پوشهٔ پروژه (offline_bundle) ذخیره شوند؟\n\n"
                  "برای انتقال به سیستم بدون اینترنت است؛ دانلودها چند دقیقه "
                  "طول می‌کشد."):
            return
        self.installing = True
        self.set_status("در حال ساخت بستهٔ آفلاین…", COLORS["sky"])
        self.log("info", "شروع ساخت بستهٔ آفلاین…")

        def work():
            try:
                summary = build_offline_bundle(include, self._lg)
                self.post(lambda: self._bundle_done(summary))
            except Exception as exc:
                self.post(lambda e=exc: self._offline_failed("ساخت بسته", e))
        threading.Thread(target=work, daemon=True).start()

    def _bundle_done(self, summary: str):
        self.installing = False
        self.set_status("بستهٔ آفلاین آماده شد", COLORS["acc"])
        self.log("ok", "بستهٔ آفلاین ساخته شد ✓")
        messagebox.showinfo(
            "ساخت بسته ✓",
            "بستهٔ آفلاین ساخته شد ✅\n\n" + summary +
            "\n\nکل پوشهٔ پروژه را به سیستم مقصد کپی کن و در همان‌جا "
            "«📀 نصب آفلاین» را بزن (یا:  python launcher.py --install-offline)")

    def _offline_failed(self, what: str, exc: Exception):
        self.installing = False
        self.set_status(f"{what} ناموفق", COLORS["err"])
        self.log("err", f"{what} ناموفق: {exc}")
        messagebox.showerror(what, str(exc))

    def install_offline_clicked(self, auto_start: bool = False):
        if self.installing:
            messagebox.showinfo("مشغول", "یک نصب/ساخت دیگر در جریان است")
            return
        if self.proc and self.proc.poll() is None:
            messagebox.showwarning("در حال اجرا",
                                   "اول سرور را متوقف کن، بعد نصب را بزن")
            return
        if not bundle_available():
            messagebox.showerror(
                "بسته پیدا نشد",
                "پوشهٔ offline_bundle کنار پروژه نیست.\n"
                "اول روی یک سیستم اینترنت‌دار با «💾 ساخت بستهٔ آفلاین» "
                "آن را بساز و کل پوشهٔ پروژه را انتقال بده.")
            return
        probs = compat_problems(read_bundle_info())
        if probs and not messagebox.askyesno(
                "⚠ ناسازگاری بسته",
                "با این بستهٔ آفلاین ناسازگاری وجود دارد:\n\n"
                + "\n".join(probs)
                + "\n\nبه‌هرحال ادامه بدهی؟"):
            self.log("warn", "نصب آفلاین به دلیل ناسازگاری لغو شد")
            return
        msg = disk_msg()
        if msg:
            messagebox.showerror("فضای دیسک", msg)
            return
        self.installing = True
        self.set_status("در حال نصب آفلاین (بدون اینترنت)…", COLORS["sky"])
        self.log("info", "شروع نصب آفلاین…")

        def work():
            try:
                ok, missing = install_from_bundle(self._lg)
                self.post(lambda: self._offinstall_done(ok, missing, auto_start))
            except Exception as exc:
                self.post(lambda e=exc: self._offline_failed("نصب آفلاین", e))
        threading.Thread(target=work, daemon=True).start()

    def _offinstall_done(self, ok: bool, missing: list, auto_start: bool):
        self.installing = False
        if ok:
            self.set_running(False)
            self.log("ok", "نصب آفلاین کامل شد ✓")
            if auto_start or messagebox.askyesno(
                    "نصب کامل ✓",
                    "همهٔ پیش‌نیازها بدون اینترنت نصب شد ✓\n\nسرور الان اجرا شود؟"):
                self.start_server()
        else:
            self.set_status("نصب ناقص", COLORS["err"])
            self.log("err", "این ماژول‌ها هنوز نصب نیستند: " + "، ".join(missing))
            messagebox.showerror("نصب ناقص",
                                 "این ماژول‌ها نصب نشدند:\n" + "، ".join(missing))

    # ------------------------------------------------------------------ #
    # اجرای سرور
    # ------------------------------------------------------------------ #
    def start_server(self):
        if self.installing:
            messagebox.showinfo("در حال نصب",
                                "صبر کن نصب پیش‌نیازها تمام شود")
            return
        if self.proc and self.proc.poll() is None:
            self.log("info", "سرور از قبل در حال اجراست — پنل باز می‌شود")
            webbrowser.open(PANEL_URL)
            return
        # اگر سرورِ دیگری (مثلاً از اجرای قبلی) روی پورت روشن است:
        if server_up(0.8):
            self.log("ok", "یک نسخه از سرور روی این پورت در حال اجراست — پنل باز می‌شود")
            self.server_ready = True
            self.set_running(True)
            webbrowser.open(PANEL_URL)
            return
        if check_missing():
            self._ask_install_smart(check_missing())
            return

        self.server_ready = False
        self.log("info", f"راه‌اندازی سرور پنل روی {PANEL_URL} …")
        self.set_status("در حال راه‌اندازی سرور…", COLORS["sky"])
        env = {**os.environ, "PYTHONIOENCODING": "utf-8",
               "NO_COLOR": "1",
               "NO_PROXY": "127.0.0.1,localhost",
               "no_proxy": "127.0.0.1,localhost"}
        try:
            # خروجی سرور گرفته می‌شود تا هر خطری در لاگ لانچر دیده شود
            self.proc = subprocess.Popen(
                [sys.executable, "-u", str(BASE / "panel_server.py")],
                cwd=str(BASE), stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                errors="replace", env=env, creationflags=NO_WINDOW)
        except Exception as exc:
            self.log("err", f"اجرای سرور ناموفق: {exc}")
            self.set_status("اجرای سرور ناموفق", COLORS["err"])
            return

        self.log("ok", f"پروسهٔ سرور شروع شد (PID {self.proc.pid}) — منتظر آماده‌شدن…")
        threading.Thread(target=self._pipe_logs, daemon=True).start()
        threading.Thread(target=self._wait_until_up, daemon=True).start()

    def _pipe_logs(self):
        """خروجی زندهٔ سرور در لاگ لانچر (خطاها دیگر مخفی نیستند)"""
        proc = self.proc
        if not proc or not proc.stdout:
            return
        for line in proc.stdout:
            if self.stop_flag:
                break
            self.post(lambda l=line: self.log("srv", l.rstrip()))
        code = proc.wait()

        def done():
            if self.stop_flag:
                return
            if self.server_ready:
                self.set_running(False)
                self.log("warn", f"پروسهٔ سرور تمام شد (کد {code})")
            else:
                self.set_status("❌ سرور بالا نیامد — لاگ بالا را ببینید", COLORS["err"])
                self.log("err", f"سرور قبل از آماده‌شدن بسته شد (کد {code})")
                self.log("info", "راهنما: خروجی سرور در همین لاگ بالاست؛ "
                         "برای جزئیات بیشتر این را در ترمینال اجرا کن:  python panel_server.py")
        self.post(done)

    def _wait_until_up(self):
        for _ in range(180):                        # حداکثر ~۹۰ ثانیه
            if self.stop_flag or self.server_ready:
                return
            if self.proc and self.proc.poll() is not None:
                return                              # خطا در _pipe_logs گزارش می‌شود
            if server_up(0.8):
                self.post(self._on_server_up)
                return
            time.sleep(0.5)
        if self.stop_flag or self.server_ready:
            return

        def fail():
            self.set_status("سرور در ۹۰ ثانیه پاسخ نداد", COLORS["err"])
            self.log("err", "سرور در ۹۰ ثانیه آماده نشد — چند نکته:")
            self.log("info", "• لاگ بالا را ببین؛ اگر خطای ماژول است، «نصب پیش‌نیازها» را بزن")
            self.log("info", "• اگر پنل قبلاً در مرورگر باز بوده، «🌐 باز کردن پنل» را امتحان کن")
            self.log("info", "• شاید پورت 8765 اشغال است: با  set PANEL_PORT=8800  و اجرای مجدد امتحان کن")
            self.log("info", "• راه نهایی: در ترمینال  python panel_server.py  را اجرا کن تا خطا کامل دیده شود")
        self.post(fail)

    def _on_server_up(self):
        self.server_ready = True
        self.log("ok", f"سرور آماده است ✓ — باز کردن پنل: {PANEL_URL}")
        self.set_running(True)
        self.after(500, lambda: webbrowser.open(PANEL_URL))

    def stop_server(self):
        if not (self.proc and self.proc.poll() is None):
            self.log("info", "سرور در حال اجرا نیست")
            self.set_running(False)
            return
        self.log("warn", "در حال توقف سرور (مرورگرهای باز هم بسته می‌شوند)…")
        try:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(self.proc.pid)],
                    capture_output=True, creationflags=NO_WINDOW)
            else:
                self.proc.terminate()
        except Exception as exc:
            self.log("err", f"توقف ناموفق: {exc}")
        self.server_ready = False

    def open_panel(self):
        if server_up(0.8):
            webbrowser.open(PANEL_URL)
        else:
            messagebox.showinfo("سرور خاموش است",
                                "اول دکمهٔ «اجرای سرور» را بزن")

    # ------------------------------------------------------------------ #
    def on_close(self):
        if self.proc and self.proc.poll() is None:
            if messagebox.askyesno(
                    "سرور در حال اجراست",
                    "با بستن لانچر، سرور و پنل هم خاموش شوند؟",
                    icon="question"):
                self.stop_flag = True
                self.stop_server()
        self.destroy()


# ══════════════════════════════════════════════════════════════════ #
#  حالت کنسلی — بدون رابط گرافیکی
# ══════════════════════════════════════════════════════════════════ #

def _console_mode(argv: list) -> int | None:
    """اگر یکی از سوییچ‌های کنسلی خواسته شده بود، اجرا و کد خروج را برگردان؛
    اگر GUI لازم است None."""
    if "--build-bundle" in argv:
        include = "--no-browsers" not in argv
        try:
            print(build_offline_bundle(include, _console_log))
            print("\n✅ بستهٔ آفلاین ساخته شد.")
            return 0
        except Exception as exc:
            print(f"[err] {exc}")
            return 1
    if "--install-offline" in argv:
        if not bundle_available():
            print("[err] پوشهٔ offline_bundle کنار پروژه پیدا نشد.")
            return 1
        probs = compat_problems(read_bundle_info())
        if probs:
            for p in probs:
                print(f"[err] {p}")
            return 1
        msg = disk_msg()
        if msg:
            print(f"[err] {msg}")
            return 1
        ok, _missing = install_from_bundle(_console_log)
        return 0 if ok else 1
    if "--install-python" in argv:
        try:
            exe = install_standard_python(_console_log)
            print()
            print("✅ پایتون استاندارد آماده است:")
            print(f"   {exe}")
            print("حالا لانچر را دوباره اجرا کن (ParsAgent.bat یا "
                  "python launcher.py) تا نصب پیش‌نیازها ادامه یابد.")
            return 0
        except Exception as exc:
            print(f"[err] {exc}")
            return 1
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    return None


def main() -> int:
    args = sys.argv[1:]
    # ── تعویض خودکار مفسر ناسازگار (۲.۸.۰) ─────────────────────────
    # اگر لانچر با پایتون free-threaded (مثل python3.13t) باز شده باشد،
    # همان‌جا با پایتون استانداردِ سیستم بازگشایی می‌شود تا نصبِ
    # پیش‌نیازها هرگز به کامپایل Rust/C++ نرسد.
    if ("--install-python" not in args and _is_free_threaded()
            and not os.environ.get("PARSAGENT_SWITCHED")):
        better = find_standard_python()
        if better:
            _cprint("[info] پایتون free-threaded شناسایی شد؛ "
                    "ادامه با پایتون استاندارد:")
            _cprint(f"       {better}")
            try:
                _reexec(better, args)
            except OSError as exc:
                _cprint(f"[warn] بازگشایی با پایتون استاندارد نشد ({exc}) — "
                        "ادامه با همین پایتون…")
        else:
            _cprint("[err] پایتون این سیستم free-threaded است (مثل 3.13t) و "
                    "نسخهٔ استانداردی روی سیستم پیدا نشد.")
            _cprint("[info] چاره:  python launcher.py --install-python")
            _cprint("       (یا دکمهٔ «🐍 پایتون استاندارد» در لانچر گرافیکی)")
    code = _console_mode(args)
    if code is not None:
        return code
    Launcher().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
