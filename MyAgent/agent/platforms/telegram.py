"""Telegram Web (K) module — messages, channel posts, group announcements.

Login strategy
    First run: the agent opens web.telegram.org and waits while you scan the
    QR code (or enter phone + the code that Telegram texts you — typed in the
    same console). The persistent profile then keeps the session alive.

Telegram's web app is an SPA — elements appear asynchronously, so every
selector below waits with a generous timeout before failing.
"""

from typing import Optional

from playwright.sync_api import TimeoutError as PWTimeout

from platforms.base import BasePlatform


class Telegram(BasePlatform):
    name = "telegram"
    base_url = "https://web.telegram.org/k/"

    SEARCH_INPUT = ["input.search-input", "#search-input",
                    "input[placeholder*='Search']", "input[placeholder*='جست']"]
    CHAT_INPUT = ["div.input-message-input",
                  "div[contenteditable='true'].input-message-input",
                  "textarea.input-message-input"]
    LOGIN_PHONE = ["input[name='phone_number']"]
    LOGIN_CODE = ["input[autocomplete='one-time-code']", "input[name='login_code']"]

    # ------------------------------------------------------------------ #
    def is_logged_in(self) -> bool:
        try:
            self.page.goto(self.base_url, wait_until="domcontentloaded",
                           timeout=30_000)
        except Exception:
            pass
        self.pause(2.0, 3.0)
        return self.try_selectors("chat_list", [
            "ul#chatlist-container", "div.chatlist", "div.chat-item",
        ], timeout_each=4_000) is not None

    def login(self, phone: Optional[str] = None) -> None:
        """Phone + console-typed code (QR scan also possible by hand)."""
        page = self.open()
        if self.is_logged_in():
            self.log.info("already logged in (profile session)")
            return
        phone = phone or self.cfg.get("phone")
        if phone:
            sel = self.try_selectors("phone", self.LOGIN_PHONE, timeout_each=8_000)
            if sel:
                self.engine.type(page, sel, phone, secret=True)
                self.pause(0.4, 0.9)
                self.engine.press(page, "Enter")
        code = input("🔑 Telegram login code: ").strip()
        sel = self.try_selectors("code", self.LOGIN_CODE, timeout_each=15_000)
        if not sel:
            self.shot("tg_code")
            raise RuntimeError("Telegram: code input not found")
        self.engine.type(page, sel, code, secret=True)
        self.pause(2.0, 3.5)
        if phone and self.engine.exists("input[name='login_password']", timeout=5_000):
            pw = input("🔑 Telegram 2FA password: ").strip()
            self.engine.type(page, "input[name='login_password']", pw, secret=True)
            self.pause(1.5, 2.5)
        self.engine.export_session(self.page, "telegram")
        self.log.info("✔ telegram login finished")

    # ------------------------------------------------------------------ #
    def _open_chat(self, chat: str) -> None:
        """Focus an existing conversation by its title (contact/channel/group)."""
        page = self.page
        sel = self.try_selectors("search", self.SEARCH_INPUT, timeout_each=8_000)
        if not sel:
            self.shot("tg_search")
            raise RuntimeError("Telegram: search box not found")
        self.engine.click(page, sel)
        self.engine.type(page, sel, chat)
        self.pause(1.2, 2.4)
        self.engine.press(page, "ArrowDown")
        self.pause(0.2, 0.5)
        self.engine.press(page, "Enter")
        self.pause(0.8, 1.6)
        self.log.info("chat focused → %s", chat)

    def send_message(self, chat: str, text: str) -> None:
        self._open_chat(chat)
        page = self.page
        box = self.try_selectors("chat_input", self.CHAT_INPUT, timeout_each=8_000)
        if not box:
            self.shot("tg_input")
            raise RuntimeError("Telegram: message input not found")
        self.engine.type(page, box, text)
        self.pause(0.3, 0.7)
        self.engine.press(page, "Enter")
        self.pause(0.8, 1.4)
        self.log.info("✔ message sent to %r", chat)
        self.toast("✈️ پیام تلگرام ارسال شد")

    def post_channel(self, channel: str, text: str, image: Optional[str] = None) -> None:
        """Publish to a channel where you are an admin."""
        self._open_chat(channel)
        page = self.page
        box = self.try_selectors("chat_input", self.CHAT_INPUT, timeout_each=8_000)
        if not box:
            self.shot("tg_channel_input")
            raise RuntimeError("Telegram: channel input not found")

        if image:
            attach = page.locator("input[type='file']").first
            attach.wait_for(state="attached", timeout=8_000)
            attach.set_input_files(image)
            self.pause(1.5, 3.0)          # wait for the upload preview
            box = self.try_selectors("caption", self.CHAT_INPUT) or box

        self.engine.type(page, box, text)
        self.pause(0.3, 0.7)
        self.engine.press(page, "Enter")
        self.pause(1.0, 1.8)
        self.log.info("✔ channel post published to %r", channel)

    def send_group_message(self, group: str, text: str) -> None:
        self.send_message(group, text)
