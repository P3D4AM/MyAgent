# -*- coding: utf-8 -*-
"""ذخیره‌گاه محلی حساب‌های پلتفرم‌ها — data/credentials.json
================================================================

برای «ورود خودکار» از پنل: نام کاربری / ایمیل / شماره + رمز + (اختیاری) کلید
TOTP دو مرحله‌ای برای اینستاگرام/توییتر/فیسبوک/لینکدین. برای پلتفرم‌های
پیام‌رسان ایرانی (بله/روبیکا/ایتا/تلگرام) فقط شماره موبایل کافی است؛ کد SMS
را خودت در پنجرهٔ مرورگر بازشده وارد می‌کنی (پیامک به گوشی خودت می‌آید).

نکتهٔ امنیتی:
  فایل به‌صورت متن ساده روی «فقط سیستم خودت» ذخیره می‌شود و پنل هم رمزها را
  هرگز به مرورگر نمی‌فرستد (فقط «ذخیره شده ✓»). اگر می‌خواهی فایل را جابه‌جا
  کنی، مسیر data/credentials.json است. رمزها را با هیچ‌کس به اشتراک نگذار.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import struct
import time
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
CREDENTIALS_PATH = ROOT / "data" / "credentials.json"

FIELDS: Dict[str, List[str]] = {
    # پلتفرم‌های کاربر/رمز
    "instagram": ["username", "password", "totp_secret"],
    "twitter": ["username", "password", "totp_secret"],
    "facebook": ["username", "password", "totp_secret"],
    "linkedin": ["username", "password", "totp_secret"],
    # پیام‌رسان‌ها: شماره (تلگرام: رمز ابری اختیاری)
    "telegram": ["username", "password"],
    "bale": ["username"],
    "rubika": ["username"],
    "eitaa": ["username"],
}


def load() -> Dict[str, Dict[str, str]]:
    try:
        data = json.loads(CREDENTIALS_PATH.read_text(encoding="utf-8"))
        return {k: v for k, v in data.items() if isinstance(v, dict)} \
            if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save(data: Dict[str, Dict[str, str]]) -> None:
    CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_platform(platform: str) -> Dict[str, str]:
    """اعتبارنامه‌های یک پلتفرم: credentials.json و بعد config.json (سازگاری CLI)."""
    rec = dict(load().get(platform) or {})
    if not any(rec.get(f) for f in FIELDS.get(platform, ["username", "password"])):
        cfg_path = ROOT / "config.json"
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            legacy = (cfg.get("platforms") or {}).get(platform) or {}
            for k in ("username", "email", "phone", "password"):
                if legacy.get(k) and not rec.get("username" if k != "password" else "password"):
                    rec[k] = legacy[k]
            if legacy.get("phone") and not rec.get("username"):
                rec["username"] = legacy["phone"]
        except Exception:
            pass
    return rec


def set_platform(platform: str, fields: Dict[str, Optional[str]]) -> Dict[str, str]:
    """ذخیره/به‌روزرسانی — مقدار None یعنی دست نزن، رشتهٔ خالی یعنی پاک کن."""
    if platform not in FIELDS:
        raise ValueError(f"پلتفرم ناشناخته: {platform}")
    data = load()
    rec = data.get(platform) or {}
    for f in FIELDS[platform]:
        v = fields.get(f)
        if v is None:                       # ارسال نشده → بدون تغییر
            continue
        v = str(v).strip()
        if v:
            rec[f] = v
        else:
            rec.pop(f, None)
    if rec:
        data[platform] = rec
    else:
        data.pop(platform, None)
    _save(data)
    return rec


def clear_platform(platform: str) -> bool:
    data = load()
    existed = data.pop(platform, None) is not None
    if existed:
        _save(data)
    return existed


def masked() -> Dict[str, Dict[str, object]]:
    """نمای امن برای پنل — رمز هرگز ارسال نمی‌شود، فقط اینکه هست یا نه."""
    out: Dict[str, Dict[str, object]] = {}
    for pid in FIELDS:
        rec = load().get(pid) or {}
        out[pid] = {
            "username": rec.get("username") or "",
            "has_password": bool(rec.get("password")),
            "has_totp": bool(rec.get("totp_secret")),
        }
    return out


# --------------------------------------------------------------------------- #
# TOTP — تولید کد دو مرحله‌ای بدون هیچ وابستگی (HMAC-SHA1 استاندارد RFC 6238)
# --------------------------------------------------------------------------- #
def _b32_decode(secret: str) -> bytes:
    s = "".join(c for c in secret.upper() if c.isalnum())
    s += "=" * ((8 - len(s) % 8) % 8)
    return base64.b32decode(s, casefold=True)


def totp_code(secret: str, period: int = 30, digits: int = 6,
              t: Optional[float] = None) -> str:
    """کد ۶ رقمی فعلی از کلید TOTP (مثل Google Authenticator)."""
    key = _b32_decode(secret.strip().replace(" ", ""))
    counter = struct.pack(">Q", int((t or time.time()) // period))
    digest = hmac.new(key, counter, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = (struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF) \
        % (10 ** digits)
    return str(code).zfill(digits)
