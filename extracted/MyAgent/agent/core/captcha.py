# -*- coding: utf-8 -*-
"""حل خودکار کپچا — سازگار با پروتکل 2Captcha / RuCaptcha
================================================================

اگر سرویس دهندهٔ کپچا در تنظیمات پنل پیکربندی شده باشد (کلید API)،
«ورود خودکار» هر کپچایی که سرراه باشد همان‌جا حل می‌کند:

  • reCAPTCHA v2 (چک‌باکس من ربات نیستم)
  • reCAPTCHA v3 (نامرئی)
  • hCaptcha
  • Cloudflare Turnstile
  • FunCaptcha / Arkose
  • کپچای تصویری (عکس) — شامل کپچاهای سایت‌های ایرانی

فقط کتابخانهٔ استاندارد (urllib) استفاده می‌شود — نیازی به پکیج جدید نیست.
کلید API را از 2captcha.com بگیر (پولی و ارزان) یا سرویس مشابه با همین
پروتکل (rucaptcha و …). همه‌چیز فقط بین سیستم خودت و سرویس کپچا است.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

from core.logger import get_logger

log = get_logger("captcha")

PROVIDERS = {
    "2captcha": "https://2captcha.com",
    "rucaptcha": "https://rucaptcha.com",
}


class CaptchaSolver:
    """کلاینت پروتکل in.php/res.php (سازگار با 2captcha و کلون‌هایش)."""

    def __init__(self, cfg: Dict[str, Any] | None = None,
                 proxy: Optional[str] = None):
        cfg = cfg or {}
        self.api_key = str(cfg.get("api_key") or "").strip()
        self.base = (str(cfg.get("base_url") or "").strip() or
                     PROVIDERS.get(str(cfg.get("provider") or "2captcha"),
                                   "https://2captcha.com")).rstrip("/")
        self.timeout = float(cfg.get("timeout_s") or 180)
        self.poll = max(2.0, float(cfg.get("poll_interval_s") or 5))
        self.auto_solve = bool(cfg.get("auto_solve", True))
        self.proxy = proxy

    # ------------------------------------------------------------------ #
    @property
    def available(self) -> bool:
        return bool(self.api_key) and bool(self.base)

    def _call(self, path: str, params: Dict[str, Any],
              data: Optional[bytes] = None) -> Dict[str, Any]:
        qs = {"key": self.api_key, "json": 1}
        qs.update({k: v for k, v in params.items() if v is not None})
        url = f"{self.base}/{path}"
        body = data if data is not None else urllib.parse.urlencode(qs).encode()
        if data is not None:                       # POST multipart برای body های بزرگ
            boundary = "----parsagent" + str(int(time.time()))
            parts = []
            for k, v in qs.items():
                parts.append(f"--{boundary}\r\nContent-Disposition: form-data; "
                             f"name=\"{k}\"\r\n\r\n{v}\r\n".encode())
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; "
                         f"name=\"file\"; filename=\"blob\"\r\n"
                         f"Content-Type: application/octet-stream\r\n\r\n".encode())
            parts.append(data)
            parts.append(f"\r\n--{boundary}--\r\n".encode())
            body = b"".join(parts)
            req = urllib.request.Request(url, data=body, method="POST")
            req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        else:
            req = urllib.request.Request(url, data=body, method="POST")
        with urllib.request.urlopen(req, timeout=40) as resp:  # noqa: S310
            return json.loads(resp.read().decode("utf-8", "replace"))

    # ------------------------------------------------------------------ #
    def _solve(self, label: str, params: Dict[str, Any]) -> str:
        if not self.available:
            raise RuntimeError("کلید API سرویس کپچا تنظیم نشده است")
        if self.proxy:
            params.setdefault("proxy", self.proxy)
            params.setdefault("proxytype", "HTTP")
        t0 = time.time()
        r = self._call("in.php", params)
        if r.get("status") != 1:
            raise RuntimeError(f"ارسال {label} به سرویس شکست خورد: {r.get('request')}")
        cid = str(r.get("request"))
        log.info("کپچای %s به سرویس سپرده شد (id=%s) — در حال حل…", label, cid)
        while time.time() - t0 < self.timeout:
            time.sleep(self.poll)
            d = self._call("res.php", {"action": "get", "id": cid})
            if d.get("status") == 1:
                log.info("✔ کپچای %s حل شد (%.0f ثانیه)", label, time.time() - t0)
                return str(d.get("request"))
            req = str(d.get("request"))
            if req.upper() != "CAPCHA_NOT_READY":
                raise RuntimeError(f"سرویس کپچا خطا داد: {req}")
        raise RuntimeError(f"مهلت حل کپچای {label} تمام شد ({self.timeout:.0f}s)")

    # ------------------------------ انواع کپچا ------------------------------ #
    def solve_recaptcha_v2(self, sitekey: str, pageurl: str) -> str:
        return self._solve("reCAPTCHA v2", {
            "method": "userrecaptcha", "googlekey": sitekey, "pageurl": pageurl})

    def solve_recaptcha_v3(self, sitekey: str, pageurl: str,
                           action: str = "", min_score: float = 0.3) -> str:
        return self._solve("reCAPTCHA v3", {
            "method": "userrecaptcha", "version": "v3", "googlekey": sitekey,
            "pageurl": pageurl, "action": action or None,
            "min_score": min_score})

    def solve_hcaptcha(self, sitekey: str, pageurl: str) -> str:
        return self._solve("hCaptcha", {
            "method": "hcaptcha", "sitekey": sitekey, "pageurl": pageurl})

    def solve_turnstile(self, sitekey: str, pageurl: str) -> str:
        return self._solve("Turnstile", {
            "method": "turnstile", "sitekey": sitekey, "pageurl": pageurl})

    def solve_funcaptcha(self, publickey: str, pageurl: str) -> str:
        return self._solve("FunCaptcha", {
            "method": "funcaptcha", "publickey": publickey, "pageurl": pageurl})

    def solve_image(self, image_b64: str) -> str:
        """کپچای تصویری — متن داخل عکس را برمی‌گرداند."""
        import base64 as _b64
        raw = _b64.b64decode(image_b64)
        if not self.available:
            raise RuntimeError("کلید API سرویس کپچا تنظیم نشده است")
        qs = {"key": self.api_key, "json": 1, "method": "base64"}
        url = f"{self.base}/in.php"
        boundary = "----parsagent" + str(int(time.time()))
        parts = []
        for k, v in qs.items():
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; "
                         f"name=\"{k}\"\r\n\r\n{v}\r\n".encode())
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; "
                     f"name=\"body\"; filename=\"cap.png\"\r\n"
                     f"Content-Type: application/octet-stream\r\n\r\n".encode())
        parts.append(raw)
        parts.append(f"\r\n--{boundary}--\r\n".encode())
        req = urllib.request.Request(url, data=b"".join(parts), method="POST")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        with urllib.request.urlopen(req, timeout=40) as resp:  # noqa: S310
            r = json.loads(resp.read().decode("utf-8", "replace"))
        if r.get("status") != 1:
            raise RuntimeError(f"ارسال کپچای تصویری شکست خورد: {r.get('request')}")
        cid = str(r.get("request"))
        t0 = time.time()
        while time.time() - t0 < self.timeout:
            time.sleep(self.poll)
            d = self._call("res.php", {"action": "get", "id": cid})
            if d.get("status") == 1:
                log.info("✔ کپچای تصویری حل شد: «%s»", d.get("request"))
                return str(d.get("request"))
            req_ = str(d.get("request"))
            if req_.upper() != "CAPCHA_NOT_READY":
                raise RuntimeError(f"سرویس کپچا خطا داد: {req_}")
        raise RuntimeError("مهلت حل کپچای تصویری تمام شد")


# --------------------------------------------------------------------------- #
# تشخیص و تزریق کپچا در صفحه (سطح Playwright)
# --------------------------------------------------------------------------- #
_CAPTCHA_SELECTORS = [
    ("recaptcha", "iframe[src*='google.com/recaptcha']"),
    ("recaptcha", "iframe[src*='recaptcha/api']"),
    ("hcaptcha", "iframe[src*='hcaptcha.com']"),
    ("turnstile", "iframe[src*='challenges.cloudflare.com']"),
    ("funcaptcha", "iframe[src*='arkoselabs']"),
    ("funcaptcha", "iframe[src*='funcaptcha']"),
]

_IMAGE_CAPTCHA_SEL = "img[src*='captcha' i], img[id*='captcha' i], img[class*='captcha' i]"
_IMAGE_INPUT_SEL = ("input[name*='captcha' i], input[id*='captcha' i], "
                    "input[placeholder*='کد' i], input[autocomplete='one-time-code']")

_EXTRACT_KEY_JS = """() => {
  const el = document.querySelector('[data-sitekey]');
  if (el && el.getAttribute('data-sitekey')) return el.getAttribute('data-sitekey');
  const html = document.documentElement.innerHTML;
  let m = html.match(/(?:sitekey|data-sitekey)["'\\s:=]+([0-9a-zA-Z_-]{20,})/);
  if (m) return m[1];
  for (const f of document.querySelectorAll(
      'iframe[src*="recaptcha"],iframe[src*="hcaptcha"],'
      + 'iframe[src*="turnstile"],iframe[src*="arkoselabs"]')) {
    try {
      const u = new URL(f.src);
      const k = u.searchParams.get('k') || u.searchParams.get('sitekey')
              || u.searchParams.get('pk');
      if (k) return k;
    } catch (e) {}
  }
  return null;
}"""

_INJECT_TOKEN_JS = """([kind, token]) => {
  let n = 0;
  const setTA = (sel) => {
    for (const el of document.querySelectorAll(sel)) {
      el.textContent = token; el.value = token; el.dispatchEvent(new Event('input'));
      el.dispatchEvent(new Event('change')); n++;
    }
  };
  if (kind === 'recaptcha') {
    setTA('#g-recaptcha-response, textarea[name="g-recaptcha-response"]');
  } else if (kind === 'hcaptcha') {
    setTA('textarea[name="h-captcha-response"], textarea[name="g-recaptcha-response"]');
  } else if (kind === 'turnstile') {
    setTA('[name="cf-turnstile-response"], textarea[name="g-recaptcha-response"]');
  } else if (kind === 'funcaptcha') {
    return true;
  }
  try {
    const cb = document.querySelector('[data-callback]');
    if (cb) {
      const fn = window[cb.getAttribute('data-callback')];
      if (typeof fn === 'function') fn(token);
    }
  } catch (e) {}
  return n > 0;
}"""


def detect_captcha(page) -> Optional[Dict[str, Any]]:
    """اگر در صفحهٔ فعلی کپچا هست، نوع و sitekey آن را برمی‌گرداند."""
    try:
        for kind, sel in _CAPTCHA_SELECTORS:
            if page.locator(sel).count() > 0:
                sitekey = None
                try:
                    sitekey = page.evaluate(_EXTRACT_KEY_JS)
                except Exception:
                    pass
                return {"kind": kind, "sitekey": sitekey,
                        "url": page.url}
        # کپچای تصویری
        if page.locator(_IMAGE_CAPTCHA_SEL).count() > 0:
            return {"kind": "image", "sitekey": None, "url": page.url}
    except Exception:
        pass
    return None


def solve_page_captcha(page, solver: CaptchaSolver) -> Dict[str, Any]:
    """کپچای صفحهٔ فعلی را تشخیص + حل + تزریق می‌کند. خروجی گزارش فارسی."""
    cap = detect_captcha(page)
    if not cap:
        return {"found": False, "solved": False}
    kind, sitekey, url = cap["kind"], cap.get("sitekey"), cap["url"]
    if not solver or not solver.available:
        log.warning("کپچای %s شناسایی شد ولی سرویس حل کپچا فعال نیست", kind)
        return {"found": True, "solved": False, "kind": kind,
                "reason": "سرویس حل کپچا فعال نیست (تنظیمات → حل کپچا)"}
    if not solver.auto_solve:
        return {"found": True, "solved": False, "kind": kind,
                "reason": "حل خودکار در تنظیمات خاموش است"}

    log.info("🤖 کپچای %s شناسایی شد — در حال حل خودکار…", kind)
    try:
        if kind == "recaptcha":
            token = solver.solve_recaptcha_v2(sitekey or "", url)
        elif kind == "hcaptcha":
            token = solver.solve_hcaptcha(sitekey or "", url)
        elif kind == "turnstile":
            token = solver.solve_turnstile(sitekey or "", url)
        elif kind == "funcaptcha":
            token = solver.solve_funcaptcha(sitekey or "", url)
        elif kind == "image":
            b64 = page.evaluate(
                """(sel) => {
                  const img = document.querySelector(sel);
                  if (!img) return null;
                  const c = document.createElement('canvas');
                  c.width = img.naturalWidth || img.width || 160;
                  c.height = img.naturalHeight || img.height || 60;
                  const ctx = c.getContext('2d');
                  ctx.drawImage(img, 0, 0, c.width, c.height);
                  return c.toDataURL('image/png').split(',')[1];
                }""", _IMAGE_CAPTCHA_SEL)
            if not b64:
                return {"found": True, "solved": False, "kind": kind,
                        "reason": "تصویر کپچا خوانده نشد"}
            answer = solver.solve_image(b64)
            filled = page.evaluate(
                """([ans, sel]) => {
                  const el = document.querySelector(sel);
                  if (!el) return false;
                  el.value = ans;
                  el.dispatchEvent(new Event('input', {bubbles: true}));
                  el.dispatchEvent(new Event('change', {bubbles: true}));
                  return true;
                }""", [answer, _IMAGE_INPUT_SEL])
            return {"found": True, "solved": bool(filled), "kind": kind,
                    "answer": answer}
        else:
            return {"found": True, "solved": False, "kind": kind,
                    "reason": "نوع کپچا پشتیبانی نمی‌شود"}
    except Exception as exc:
        log.warning("حل کپچا شکست خورد: %s", exc)
        return {"found": True, "solved": False, "kind": kind,
                "reason": str(exc)[:200]}

    # تزریق توکن کپچاهای غیر تصویری
    try:
        ok = page.evaluate(_INJECT_TOKEN_JS, [kind, token])
    except Exception:
        ok = False
    log.info("✔ توکن %s تزریق شد (نوشته در %s فیلد)", kind, "چند" if ok else "هیچ")
    return {"found": True, "solved": True, "kind": kind,
            "injected": bool(ok), "token_prefix": str(token)[:12] + "…"}
