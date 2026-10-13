# -*- coding: utf-8 -*-
"""Shared base for every social-platform module.

Each platform module gets a live BrowserEngine + the global config and
implements login() plus its own high-level actions (post, message, follow…).

Common conventions across all platforms:
  * selectors are tried as a list of candidates (UIs change constantly)
  * every action takes human pauses between steps (anti-detection)
  * on unexpected states a screenshot is saved to logs/shots/

New in v1.2 — «ورود خودکار»:
  BasePlatform.auto_login(creds, solver) یک فلوی عمومی است که برای همهٔ
  پلتفرم‌ها کار می‌کند: باز کردن سایت → پر کردن نام کاربری/شماره → دکمهٔ
  بعدی → رمز → ارسال → حل خودکار کپچا (اگر سرویس فعال باشد) → کد دو
  مرحله‌ای (TOTP خودکار اگر کلید ذخیره شده) → پاک‌کردن دیالوگ «ذخیره
  اطلاعات ورود» → بررسی موفقیت.
"""

from typing import Any, Dict, List, Optional

from playwright.sync_api import Page

from core.browser_engine import BrowserEngine
from core.captcha import solve_page_captcha
from core.credentials import totp_code
from core.logger import get_logger
from core.notify import notify


# --------------------------------------------------------------------------- #
# سلکتورهای ورود هر پلتفرم (با کاندیداهای متعدد — DOM‌ها مرتب عوض می‌شوند)
# --------------------------------------------------------------------------- #
LOGIN_SELECTORS: Dict[str, Dict[str, List[str]]] = {
    "instagram": {
        "user": ["input[name='username']", "input[type='text']"],
        "pass": ["input[name='password']", "input[type='password']"],
        "next": ["button[type='button']:has-text('Next')",
                 "button[type='button']:has-text('بعدی')",
                 "div[role='button']:has-text('Next')"],
        "submit": ["button[type='submit']:has-text('Log in')",
                   "button[type='submit']:has-text('ورود')",
                   "button[type='submit']", "div[role='button']:has-text('Log in')"],
        "code": ["input[name='verificationCode']"],
    },
    "twitter": {
        "user": ["input[autocomplete='username']", "input[name='text']",
                 "input[type='text']"],
        "pass": ["input[type='password']", "input[name='password']"],
        "next": ["button[data-testid='oauthNextButton']",
                 "button:has-text('Next')", "button:has-text('بعدی')"],
        "submit": ["button[data-testid='LoginForm_Login_Button']",
                   "button[type='submit']", "button:has-text('Log in')"],
        "code": ["input[name='text']", "input[autocomplete='onetimecode']",
                 "input[autocomplete='one-time-code']"],
    },
    "telegram": {
        "user": ["input.input", "input[type='tel']",
                 "input[placeholder*='Phone']", "input[placeholder*='تلفن']"],
        "pass": ["input[type='password']", "input.journal-input"],
        "submit": ["button.btn-primary", "button[type='submit']",
                   "button:has-text('NEXT')", "button:has-text('بعدی')"],
        "code": ["input.otp-input", "input[inputmode='numeric']",
                 "input[autocomplete='one-time-code']"],
    },
    "facebook": {
        "user": ["input#email", "input[name='email']", "input[id='email']",
                 "input[type='email']", "input[type='tel']"],
        "pass": ["input#pass", "input[name='pass']", "input[type='password']"],
        "submit": ["button#loginbutton", "button[name='login']",
                   "button[type='submit']", "input[type='submit']"],
        "code": ["input[name='approval_code']", "input[autocomplete='one-time-code']"],
    },
    "linkedin": {
        "user": ["input#username", "input[name='session_key']",
                 "input[type='email']", "input[type='text']"],
        "pass": ["input#password", "input[name='session_password']",
                 "input[type='password']"],
        "submit": ["button[type='submit']", "button:has-text('Sign in')",
                   "button:has-text('ورود')"],
        "code": ["input#verification_code", "input[autocomplete='one-time-code']"],
    },
    "bale": {
        "user": ["input[type='tel']", "input[name='phone']",
                 "input[placeholder*='Phone']", "input[placeholder*='موبایل']"],
        "pass": ["input[type='password']"],
        "submit": ["button[type='submit']", "button.login-btn",
                   "button:has-text('Login')", "button:has-text('ورود')"],
        "code": ["input[inputmode='numeric']", "input[autocomplete='one-time-code']"],
    },
    "rubika": {
        "user": ["input[type='tel']", "input[name='phone']",
                 "input[placeholder*='موبایل']", "input[placeholder*='Phone']"],
        "pass": ["input[type='password']"],
        "submit": ["button[type='submit']", "button:has-text('ورود')",
                   "button:has-text('Next')"],
        "code": ["input[inputmode='numeric']", "input[autocomplete='one-time-code']"],
    },
    "eitaa": {
        "user": ["input[type='tel']", "input[name='phone']",
                 "input[placeholder*='موبایل']"],
        "pass": ["input[type='password']"],
        "submit": ["button[type='submit']", "button:has-text('ورود')"],
        "code": ["input[inputmode='numeric']", "input[autocomplete='one-time-code']"],
    },
}

# دیالوگ‌های بعد از ورود («اطلاعات ورود ذخیره شود؟» → الان نه)
SAVE_INFO_TEXTS = ["Not now", "الان نه", "Not Now", "Save Info", "ذخیره اطلاعات",
                   "بعداً", "Later", "Skip", "رد کردن"]


class BasePlatform:
    name: str = "base"
    base_url: str = ""

    def __init__(self, engine: BrowserEngine, config: Dict[str, Any]):
        self.engine = engine
        self.config = config
        self.cfg: Dict[str, Any] = config.get("platforms", {}).get(self.name, {})
        self.log = get_logger(self.name)
        self._page: Optional[Page] = None

    # ------------------------------------------------------------------ #
    @property
    def page(self) -> Page:
        if self._page is None:
            self._page = self.engine.new_page()
            self.engine.goto(self._page, self.base_url)
        return self._page

    def open(self) -> Page:
        """(Re)open the platform's web app."""
        self._page = self.engine.new_page()
        self.engine.goto(self._page, self.base_url)
        return self._page

    # ------------------------------------------------------------------ #
    # helpers for subclasses
    # ------------------------------------------------------------------ #
    def try_selectors(self, action: str, selectors: List[str],
                      timeout_each: int = 6_000) -> Optional[str]:
        """Return the first selector that shows up, else None."""
        for sel in selectors:
            try:
                self.page.wait_for_selector(sel, state="visible",
                                            timeout=timeout_each)
                self.log.debug("%s → selector ok: %s", action, sel)
                return sel
            except Exception:
                continue
        return None

    def pause(self, min_s: float = 0.6, max_s: float = 1.8) -> None:
        self.engine.human_pause(min_s, max_s)

    def shot(self, tag: str = "") -> str:
        return self.engine.screenshot(self.page, tag or f"{self.name}_error")

    def toast(self, message: str) -> None:
        notify("ParsAgent", message)

    # ------------------------------------------------------------------ #
    # ورود خودکار — فلوی عمومی همهٔ پلتفرم‌ها (پنل وب)
    # ------------------------------------------------------------------ #
    def auto_login(self, creds: Dict[str, str], solver=None) -> Dict[str, Any]:
        """ورود خودکار با اعتبارنامه‌های ذخیره‌شده + حل کپچا + TOTP.

        creds: {"username":…, "password":…, "totp_secret":…} (از data/credentials.json)
        solver: core.captcha.CaptchaSolver یا None
        خروجی: {"ok", "steps", "captcha", "needs"} — needs یعنی «کد SMS/تأیید
        لازم است» که کاربر باید در همان پنجرهٔ باز وارد کند.
        """
        steps: List[str] = []
        sels = LOGIN_SELECTORS.get(self.name) or {}
        user_val = creds.get("username") or creds.get("email") or creds.get("phone")
        pass_val = creds.get("password")
        if not user_val:
            raise RuntimeError(
                "نام کاربری/شماره‌ای برای این پلتفرم ذخیره نشده — "
                "از تنظیمات → «حساب‌ها و ورود خودکار» پرش کن")

        page = self._page
        if page is None or page.is_closed():
            page = self.open()
            steps.append("مرورگر با پروفایل ماندگار باز شد")
        else:
            try:
                page.goto(self.base_url, wait_until="domcontentloaded",
                          timeout=45_000)
            except Exception:
                pass
        self.pause(1.0, 2.0)

        # ۰) شاید از قبل داخل هستیم
        try:
            if self.is_logged_in():
                self.log.info("✔ از قبل وارد شده بودی — نیازی به ورود نیست")
                return {"ok": True, "already_logged_in": True,
                        "steps": ["از قبل وارد شده بودی ✓"], "captcha": None,
                        "needs": None}
        except Exception:
            pass

        # ۱) فیلد نام کاربری / شماره
        usel = self.try_selectors("login_user", sels.get("user", []),
                                  timeout_each=9_000)
        if not usel:
            self.shot("autologin_no_user_field")
            raise RuntimeError(
                "فیلد نام کاربری پیدا نشد — یا سایت عوض شده یا صفحهٔ ورود "
                "باز نیست؛ اسکرین‌شات در logs/shots ذخیره شد")
        self.engine.type(page, usel, str(user_val))
        steps.append("نام کاربری/شماره پر شد")
        self.pause(0.4, 0.9)

        # ۲) دکمهٔ «بعدی» (اینستاگرام/توییتر فرم دومرحله‌ای دارند)
        for nsel in sels.get("next", []):
            if self.engine.exists(page, nsel, timeout=2_200):
                try:
                    self.engine.click(page, nsel, timeout=3_000)
                    steps.append("دکمهٔ «بعدی» زده شد")
                    self.pause(0.6, 1.2)
                    break
                except Exception:
                    continue

        # ۳) رمز عبور (پلتفرم‌های شماره‌محور ممکن است نداشته باشند)
        if pass_val and sels.get("pass"):
            psel = self.try_selectors("login_pass", sels["pass"],
                                      timeout_each=6_000)
            if psel:
                self.engine.type(page, psel, pass_val, secret=True)
                steps.append("رمز عبور پر شد")
                self.pause(0.4, 0.9)

        # ۴) ارسال فرم
        submitted = False
        for ssel in sels.get("submit", []):
            if self.engine.exists(page, ssel, timeout=1_800):
                try:
                    self.engine.click(page, ssel, timeout=3_000)
                    submitted = True
                    break
                except Exception:
                    continue
        if not submitted:
            self.engine.press(page, "Enter")
        steps.append("فرم ورود ارسال شد")
        self.pause(1.8, 3.0)

        # ۵) کپچا؟
        captcha_report: Optional[Dict[str, Any]] = None
        cap = None
        try:
            from core.captcha import detect_captcha
            cap = detect_captcha(page)
        except Exception:
            cap = None
        if cap:
            self.log.info("🤖 کپچای %s در سرراه ورود بود", cap.get("kind"))
            captcha_report = solve_page_captcha(page, solver)
            if captcha_report.get("solved"):
                steps.append("کپچا حل و تزریق شد ✓")
                # بعد از کپچا معمولاً فرم باید دوباره ارسال شود
                for ssel in sels.get("submit", []):
                    if self.engine.exists(page, ssel, timeout=1_600):
                        try:
                            self.engine.click(page, ssel, timeout=3_000)
                            break
                        except Exception:
                            continue
                self.pause(1.5, 2.5)
            else:
                steps.append("کپچا حل نشد: " +
                             str(captcha_report.get("reason") or cap.get("kind")))

        # ۶) کد تأیید (SMS یا 2FA)
        code_sel = None
        for csel in (sels.get("code") or []):
            if self.engine.exists(page, csel, timeout=3_500):
                code_sel = csel
                break
        needs = None
        if code_sel:
            if creds.get("totp_secret"):
                try:
                    code = totp_code(creds["totp_secret"])
                    self.engine.type(page, code_sel, code, secret=True)
                    self.engine.press(page, "Enter")
                    steps.append("کد دو مرحله‌ای (TOTP) خودکار وارد شد ✓")
                    self.pause(1.5, 2.5)
                except Exception as exc:
                    steps.append(f"تولید کد TOTP شکست خورد: {exc}")
                    needs = "code"
            else:
                needs = "code"
                steps.append(
                    "کد تأیید لازم است — در پنجرهٔ مرورگرِ باز همان‌جا واردش کن؛ "
                    "باقی کار را خودم می‌گیرم (پروفایل ماندگار است)")
                self.pause(4.0, 6.0)

        # ۷) دیالوگ «ذخیره اطلاعات ورود؟» → «الان نه»
        for text in SAVE_INFO_TEXTS:
            try:
                btn = page.get_by_role("button", name=text).first
                btn.wait_for(state="visible", timeout=1_200)
                btn.click()
                steps.append("دیالوگ «ذخیره ورود» رد شد")
                self.pause()
            except Exception:
                continue

        self.pause(1.5, 2.5)

        # ۸) بررسی نتیجه
        try:
            ok = bool(self.is_logged_in())
        except Exception:
            ok = not self.engine.exists(
                page, (sels.get("pass") or ["input[type='password']"])[0],
                timeout=3_000)
        if ok:
            try:
                self.engine.export_session(self.page, self.name)
            except Exception:
                pass
            self.log.info("✔ ورود خودکار «%s» کامل شد", self.name)
        else:
            self.log.warning("ورود خودکار «%s» قطعی نبود — پنجره باز ماند", self.name)
        return {"ok": ok, "steps": steps, "captcha": captcha_report, "needs": needs}

    # ------------------------------------------------------------------ #
    # contract — override in subclasses
    # ------------------------------------------------------------------ #
    def login(self) -> None:
        raise NotImplementedError(f"{self.name}: login() is not implemented")

    def is_logged_in(self) -> bool:
        """Override with a cheap check (e.g. presence of the composer button)."""
        return False

    # convenience ---------------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.__class__.__name__} url={self.base_url!r}>"
