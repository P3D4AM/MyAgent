"""Browser engine — code-level web automation without touching mouse/keyboard.

This is the recommended engine for social networks and websites:

  * drives Chromium through Playwright at the DOM/network level
  * resilient launcher (تحریم‌مقاوم): tries the *installed* Edge first, then
    the *installed* Chrome, then the bundled Playwright Chromium — see
    FALLBACK_CHANNELS below. Windows 10/11 always ships Edge, so ParsAgent
    keeps working even when `playwright install` was blocked with a 403
    (sanctioned CDN).
  * one persistent browser profile per platform → logins survive restarts
    and never mix between instagram / telegram / bale / …
  * stealth injection → hides `navigator.webdriver` and other automation leaks
  * human-like typing & randomized delays (anti-detection)
  * optional proxy, custom user-agent and viewport
  * error screenshots saved under logs/shots/ for post-mortem debugging

While this engine works you can keep using your PC — no input is simulated.
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.sync_api import BrowserContext, Page, sync_playwright, TimeoutError as PWTimeout

from core.logger import get_logger
from core.stealth import build_stealth_js, resolve_modules, stealth_launch_args

log = get_logger("browser")

ROOT = Path(__file__).resolve().parent.parent
PROFILES_DIR = ROOT / "data" / "profiles"
SESSIONS_DIR = ROOT / "data" / "sessions"
SHOTS_DIR = ROOT / "logs" / "shots"

# --------------------------------------------------------------------------- #
# Resilient launcher — «معماری مقاوم به تحریم»
#
# اولویت انتخاب مرورگر:
#   1) "msedge"    → Edge نصب‌شده خود ویندوز (روی Win10/11 همیشه هست، بدون دانلود)
#   2) "chrome"    → Chrome نصب‌شده کاربر
#   3) "chromium"  → کرومیوم باندل Playwright (نیازمند نصب)
#
# اگر CDN رسمی روی IP شما 403 داد (پیام AccessDenied)، نگران نباشید:
# راه ۱ و ۲ اصلاً دانلود نمی‌خواهند؛ راه ۳ هم با install_browsers.bat یا
# `python main.py install` از آینه چینی (بدون فیلترشکن) نصب می‌شود.
#
# قابل تنظیم در config.json:
#   browser.channel          → اجبار یک کانال خاص (مثلاً "msedge")
#   browser.channel_fallbacks → ترتیب دلخواه (پیش‌فرض: همین تاپل)
# --------------------------------------------------------------------------- #
FALLBACK_CHANNELS = ("msedge", "chrome", "chromium")

LAUNCH_HELP_FA = (
    "\nراه‌حل‌ها:\n"
    "  1) مطمئن شوید Microsoft Edge یا Chrome روی ویندوز نصب است\n"
    "     (پارس‌ایجنت به‌صورت خودکار از همان استفاده می‌کند).\n"
    "  2) کرومیوم Playwright را از آینه نصب کنید (بدون فیلترشکن):\n"
    "       install_browsers.bat        یا        python main.py install\n"
    "  3) یا فیلترشکن/پروکسی را روشن کنید و دوباره اجرا کنید."
)


class BrowserLaunchError(RuntimeError):
    """وقتی هیچ‌کدام از کانال‌های fallback نتوانستند مرورگر را باز کنند."""

    def __init__(self, report: List[str]):
        details = ""
        if report:
            details = "خطاهای هر کانال:\n  " + "\n  ".join(report) + "\n"
        super().__init__(f"{details}{LAUNCH_HELP_FA}")


# موتور ضد شناسایی v2 — core/stealth.py:
#   • آرگومان‌های لانچ (AutomationControlled و …)
#   • init-script ماژولار (webdriver / chrome.runtime / canvas / webgl / …)
#   • اثر انگشت پایدار برای هر پروفایل (seed مشتق از نام پروفایل)
STEALTH_JS = build_stealth_js  # سازگاری با نام قبلی


class BrowserEngine:
    """Playwright wrapper tuned for social-network automation.

    چند-پروفایلی: هر پلتفرم یک persistent context مستقل زیر
    data/profiles/<platform> می‌گیرد تا لاگین‌ها بین اجراها حفظ شوند و
    بین پلتفرم‌ها تداخل نکنند. کانتکست‌ها به‌صورت تنبل (lazy) و با اولین
    استفاده از use_profile()/new_page() باز می‌شوند.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cfg = config.get("browser", {})
        human = config.get("human", {})
        self.human_enabled: bool = human.get("enabled", True)
        self.type_min, self.type_max = human.get("typing_delay_ms", [35, 95])
        self.pause_min = human.get("min_delay_s", 0.35)
        self.pause_max = human.get("max_delay_s", 1.4)
        self.stealth_cfg = config.get("stealth") or {}

        self._pw = None
        self._headless: bool = self.cfg.get("headless", False)
        self._contexts: Dict[str, BrowserContext] = {}
        self._active: Optional[str] = None
        self.pages: List[Page] = []
        self.channel: Optional[str] = None   # کانال برنده: msedge | chrome | chromium

    # ------------------------------------------------------------------ #
    # channel resolution
    # ------------------------------------------------------------------ #
    def _channels(self) -> List[Optional[str]]:
        """ترتیب کانال‌ها برای تلاش — قابل‌تنظیم از config.json."""
        forced = self.cfg.get("channel")
        if forced:
            return [None if forced == "chromium" else forced]
        wanted = self.cfg.get("channel_fallbacks") or list(FALLBACK_CHANNELS)
        # در API پایتونِ Playwright، channel=None یعنی کرومیوم باندل‌شده
        return [None if c == "chromium" else c for c in wanted]

    # ------------------------------------------------------------------ #
    # lifecycle
    # ------------------------------------------------------------------ #
    def start(self, headless: Optional[bool] = None, profile: Optional[str] = None,
              lazy: bool = False) -> "BrowserEngine":
        """Playwright را راه می‌اندازد و (مگر با lazy=True) پروفایل را باز می‌کند.

        profile: نام پروفایل ماندگار — معمولاً نام پلتفرم (instagram، telegram، …)
                 None یعنی پروفایل پیش‌فرض از config (main).
        lazy:    فقط Playwright را بالا می‌آورد؛ کانتکست با اولین
                 use_profile()/new_page() باز می‌شود.
        """
        self._headless = self.cfg.get("headless", False) if headless is None else headless
        self._pw = sync_playwright().start()
        if not lazy:
            self._launch_context(profile or "main")
        return self

    def use_profile(self, profile: str) -> BrowserContext:
        """سوئیچ به پروفایل ماندگار یک پلتفرم؛ در صورت نبود، لانچش می‌کند."""
        ctx = self._launch_context(profile)
        self._active = profile
        return ctx

    def _launch_context(self, profile: str) -> BrowserContext:
        """Launch (or reuse) the persistent context of one profile."""
        if profile in self._contexts:
            return self._contexts[profile]
        if self._pw is None:
            raise BrowserLaunchError(["playwright is not started — call start() first"])

        if profile == "main":
            profile_dir = ROOT / self.cfg.get("user_data_dir", "data/profiles/main")
        else:
            profile_dir = PROFILES_DIR / profile
        profile_dir.mkdir(parents=True, exist_ok=True)

        args = stealth_launch_args(resolve_modules(self.stealth_cfg, self.cfg))
        proxy = self.cfg.get("proxy")
        stealth_js = build_stealth_js(self.config, profile)

        report: List[str] = []
        for channel in self._channels():
            label = channel or "chromium"
            try:
                ctx = self._pw.chromium.launch_persistent_context(
                    user_data_dir=str(profile_dir),
                    channel=channel,
                    headless=self._headless,
                    args=args,
                    ignore_default_args=["--enable-automation"],
                    viewport=self.cfg.get("viewport"),
                    user_agent=self.cfg.get("user_agent"),
                    slow_mo=self.cfg.get("slow_mo_ms", 0),
                    proxy={"server": proxy} if proxy else None,
                    locale="fa-IR",
                    timezone_id="Asia/Tehran",
                )
                if stealth_js:
                    ctx.add_init_script(stealth_js)
                self._contexts[profile] = ctx
                self._active = profile
                self.channel = label
                log.info("✦ browser up — channel=%s profile=%s headless=%s proxy=%s "
                         "stealth=%s", label, profile, self._headless, bool(proxy),
                         "✓" if stealth_js else "خاموش")
                return ctx
            except Exception as exc:
                first_line = str(exc).splitlines()[0] if str(exc) else repr(exc)
                report.append(f"{label}: {first_line}")
                log.debug("channel %s failed for profile %s → %s",
                          label, profile, first_line)
        raise BrowserLaunchError(report)

    @property
    def _context(self) -> BrowserContext:
        """Active context — اگر هنوز چیزی باز نشده، پروفایل main را باز می‌کند."""
        if self._active is None or self._active not in self._contexts:
            self._launch_context("main")
        return self._contexts[self._active]

    def close(self) -> None:
        try:
            for p in self.pages:
                p.close()
        except Exception:
            pass
        profiles = list(self._contexts)
        for profile in profiles:
            try:
                self._contexts[profile].close()
            except Exception:
                pass
        self._contexts.clear()
        self._active = None
        if self._pw:
            self._pw.stop()
        log.info("browser engine closed (%s profile(s): %s)",
                 len(profiles), ", ".join(profiles) or "-")

    # ------------------------------------------------------------------ #
    # profile inspection — used by the web panel (server.py)
    # ------------------------------------------------------------------ #
    def open_profiles(self) -> List[str]:
        """نام پروفایل‌هایی که الان کانتکست باز دارند (بدون لانچ جدید)."""
        return list(self._contexts)

    def close_profile(self, profile: str) -> bool:
        """بستن کانتکست فقط یک پروفایل — بقیهٔ پروفایل‌ها باز می‌مانند."""
        ctx = self._contexts.pop(profile, None)
        if ctx is None:
            return False
        try:
            ctx.close()
        except Exception:
            pass
        if self._active == profile:
            self._active = None
        try:
            self.pages = [p for p in self.pages if not p.is_closed()]
        except Exception:
            pass
        log.info("profile closed: %s", profile)
        return True

    def __enter__(self) -> "BrowserEngine":
        return self if self._pw is not None else self.start()

    def __exit__(self, *exc) -> None:
        self.close()

    # ------------------------------------------------------------------ #
    # pages & navigation
    # ------------------------------------------------------------------ #
    def new_page(self) -> Page:
        """Open a page in the *active* profile (auto-opens main if needed)."""
        page = self._context.new_page()
        self.pages.append(page)
        return page

    def goto(self, page: Page, url: str, retries: int = 3) -> Page:
        for attempt in range(1, retries + 1):
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=45_000)
                log.info("→ %s", url)
                self.human_pause(0.8, 2.0)
                return page
            except PWTimeout:
                log.warning("goto timeout (%s) try %s/%s", url, attempt, retries)
                if attempt == retries:
                    raise
        return page

    # ------------------------------------------------------------------ #
    # human-like interaction primitives
    # ------------------------------------------------------------------ #
    def human_pause(self, min_s: Optional[float] = None,
                    max_s: Optional[float] = None) -> None:
        if not self.human_enabled:
            return
        lo = min_s if min_s is not None else self.pause_min
        hi = max_s if max_s is not None else self.pause_max
        time.sleep(random.uniform(lo, hi))

    def click(self, page: Page, selector: str, timeout: int = 15_000) -> None:
        page.wait_for_selector(selector, state="visible", timeout=timeout)
        page.locator(selector).first.hover()
        self.human_pause(0.2, 0.6)
        page.locator(selector).first.click()
        log.info("click %s", selector)

    def click_text(self, page: Page, text: str, timeout: int = 15_000) -> None:
        loc = page.get_by_text(text, exact=False).first
        loc.wait_for(state="visible", timeout=timeout)
        loc.click()
        log.info("click text %r", text)

    def type(self, page: Page, selector: str, text: str, secret: bool = False,
             timeout: int = 15_000) -> None:
        """Fill an input — char by char with randomized delay in human mode."""
        page.wait_for_selector(selector, state="visible", timeout=timeout)
        locator = page.locator(selector).first
        locator.click()
        if secret:
            locator.fill(text)                      # no per-char cadence for secrets
            log.info("typed •••••••• into %s", selector)
            return
        locator.fill("")
        if self.human_enabled:
            for ch in text:
                page.keyboard.type(ch, delay=random.randint(self.type_min, self.type_max))
            log.info("typed %s chars into %s", len(text), selector)
        else:
            locator.fill(text)

    def press(self, page: Page, key: str) -> None:
        page.keyboard.press(key)
        log.info("key %s", key)

    def wait_for(self, page: Page, selector: str, timeout: int = 20_000) -> None:
        page.wait_for_selector(selector, state="visible", timeout=timeout)
        log.info("found %s", selector)

    def exists(self, page: Page, selector: str, timeout: int = 3_000) -> bool:
        try:
            page.wait_for_selector(selector, state="attached", timeout=timeout)
            return True
        except PWTimeout:
            return False

    def scroll(self, page: Page, amount: int = 600) -> None:
        page.mouse.wheel(0, amount)
        self.human_pause(0.3, 0.8)

    def screenshot(self, page: Page, tag: str = "debug") -> str:
        SHOTS_DIR.mkdir(parents=True, exist_ok=True)
        path = SHOTS_DIR / f"{datetime.now():%H%M%S}_{tag}.png"
        page.screenshot(path=str(path), full_page=False)
        log.info("📸 screenshot → %s", path)
        return str(path)

    # ------------------------------------------------------------------ #
    # session portability
    # ------------------------------------------------------------------ #
    def export_session(self, page: Page, name: str) -> Path:
        """Dump storage_state (cookies + localStorage) → data/sessions/<name>.json."""
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        path = SESSIONS_DIR / f"{name}.json"
        path.write_text(
            json.dumps(page.context.storage_state(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        log.info("session exported → %s", path)
        return path

    def import_session(self, name: str) -> bool:
        """Load cookies from a previously exported state into the active context."""
        path = SESSIONS_DIR / f"{name}.json"
        if path.exists():
            state = json.loads(path.read_text(encoding="utf-8"))
            cookies = state.get("cookies", [])
            if cookies:
                self._context.add_cookies(cookies)
            log.info("session imported ← %s (%s cookies)", path, len(cookies))
            return True
        return False
